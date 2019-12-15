from datetime import datetime, timedelta

import requests
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import url_for

from .base import BaseModel, OrderedBase, Base, get_session
from .enums import (
    VideoTypeEnum,
    SegmentPermissionEnum,
    ResourceTypeEnum,
    SegmentStatus,
    SegmentStatusThreshold,
    CourseAccess,
)
from .enrollments import CourseEnrollment, lesson_user_enrollment_association_table

from .utils import fetch_thumbnail
from .progress import SegmentUserProgress

# ToDo: remove this from here
from .institute import Institute


class Course(BaseModel):
    __tablename__ = "courses"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    picture = sa.Column(sa.String)  # URL to picture resource
    cover_image = sa.Column(sa.String, default="")
    order = sa.Column(sa.Integer)
    year = sa.Column(sa.Date)
    course_code = sa.Column(sa.String(16), unique=True)
    paid = sa.Column(sa.Boolean, default=False)
    amount = sa.Column(sa.Integer, default=0)
    guest_access = sa.Column(sa.Boolean, default=True)
    language = sa.Column(sa.String(2), default="EN")
    slug = sa.Column(sa.String(50), unique=True)
    draft = sa.Column(sa.Boolean, default=True)

    target_audience = sa.Column(sa.String(), default="")
    skill_level = sa.Column(sa.String(), default="")
    info = sa.Column(sa.String)

    visibility = sa.Column(sa.String(16), default="public")

    summary_html = sa.Column(sa.String())
    workload_summary = sa.Column(sa.String(), default="")
    workload_title = sa.Column(sa.String(), default="")
    workload_subtitle = sa.Column(sa.String(), default="")

    program_id = sa.Column(sa.Integer, sa.ForeignKey("programs.id"))
    program = orm.relationship("Program", back_populates="courses")

    institute_id = sa.Column(sa.Integer, sa.ForeignKey("institutes.id"), default=None)
    institute = orm.relationship("Institute", back_populates="courses")

    lessons = orm.relationship("Lesson", back_populates="course")

    users = orm.relationship("CourseEnrollment", back_populates="course")
    translations = orm.relationship("CourseTranslation", back_populates="course")

    preview_thumbnail = sa.Column(sa.String)

    _lessons_queryset = None

    @classmethod
    def list_public_courses(cls, institute_slug=""):
        query = cls.visibility == "public"
        if institute_slug:
            institute = Institute.find_by_slug(institute_slug)
            if institute:
                query = sa.or_(
                    cls.visibility == "public",
                    sa.and_(cls.visibility == "institute", cls.institute == institute),
                )
        return cls.objects().filter(query, cls.draft == False).all()

    def get_ordered_segments(self, only_barriers=False):
        db = get_session()

        queryset = (
            db.query(Segment)
            .join(Lesson)
            .filter(Lesson._is_deleted == False, Lesson.course_id == self.id)
        )

        if only_barriers:
            queryset = queryset.filter(Segment.permission_filter())

        return queryset.order_by(Lesson.order, Segment.order)

    @property
    def number_of_resources(self):
        return (
            Resource.objects()
            .outerjoin(Resource.lesson)
            .filter(Lesson.course_id == self.id)
            .count()
        )

    def get_ordered_lessons(self):
        return Lesson.get_ordered_items().filter(Lesson.course_id == self.id)

    def add_user(self, user, access_level=CourseAccess.student):
        CourseEnrollment.add_user(self.id, user, access_level)

    def remove_teacher(self, user_id):
        return CourseEnrollment.remove_teacher(self.id, user_id)

    def add_instructor(self, user):
        self.add_user(user, CourseAccess.teacher)

    def is_student(self, user_id):
        return CourseEnrollment.is_student(self.id, user_id)

    def enroll(self, student):
        """ Adds a user to a course with student-level access. """
        CourseEnrollment.enroll(self.id, student.id)

    @property
    def instructors(self):
        """ A unique list of users associated with this course that have teacher-level access."""
        return CourseEnrollment.instructors(self.id)

    @property
    def students(self):
        """ A unique list of users associated with this course that have student-level access."""
        return CourseEnrollment.students(self.id)

    def options(self, option):
        return getattr(self, option, False)

    @property
    def lessons_queryset(self):
        if not self._lessons_queryset:
            self._lessons_queryset = Lesson.objects().filter_by(course_id=self.id)
        return self._lessons_queryset

    @property
    def intro_lesson(self):
        return self.lessons_queryset.filter(Lesson.order == 0).first()

    @property
    def normal_lessons(self):
        return self.lessons_queryset.filter(Lesson.order > 0).order_by(Lesson.order)

    @property
    def duration_seconds(self):
        t = 0
        for lesson in self.lessons:
            t += lesson.duration_seconds
        return t

    @property
    def permalink(self):
        return url_for("course.view", slug=self.slug, institute="")

    @property
    def thumbnail(self):
        if self.cover_image:
            return self.cover_image
        elif self.lessons:
            return self.lessons[0].thumbnail

    def delete(self):
        # Safe delete the course instance and all related objects

        db = get_session()
        self._is_deleted = True
        db.add(self)

        db.query(Lesson).filter(Lesson.course_id == self.id).update(
            {Lesson._is_deleted: True}, synchronize_session=False
        )

        db.query(CourseEnrollment).filter(CourseEnrollment.course_id == self.id).update(
            {CourseEnrollment._is_deleted: True}, synchronize_session=False
        )

        # ToDo: once we swtich to different backend we can use something along this lines
        # statement = update(Segment).where(Lesson.course_id == course.id).values(_is_deleted=True)
        # db.execute(statement)
        segments = (
            db.query(Segment).join(Lesson).filter(Lesson.course_id == self.id).all()
        )
        for segment in segments:
            segment._is_deleted = True
            db.add(segment)
        db.commit()

    def user_progress(self, user):
        if len(self.lessons) is 0:
            return 100
        total = 0
        for lesson in self.lessons:
            total = total + lesson.user_progress_percent(user)
        return int(total / len(self.lessons))

    @staticmethod
    def find_by_code(code):
        return Course.objects().filter(Course.course_code == code).first()


class CourseTranslation(Base):
    __tablename__ = "courses_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"))
    title = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    course = orm.relationship("Course", back_populates="translations")


class Lesson(OrderedBase):
    __tablename__ = "lessons"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    active = sa.Column(sa.Boolean)
    language = sa.Column(sa.String(2))
    slug = sa.Column(sa.String(50))  # Unique in relation to parent
    cover_image = sa.Column(sa.String)  # URL to picture resource
    description = sa.Column(sa.String(140))
    further_reading = sa.Column(sa.String)

    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"))
    course = orm.relationship("Course", back_populates="lessons")

    segments = orm.relationship("Segment", back_populates="lesson")
    resources = orm.relationship("Resource", back_populates="lesson")
    questions = orm.relationship("LessonQA", back_populates="lesson")
    teachers = orm.relationship(
        "CourseEnrollment",
        secondary=lesson_user_enrollment_association_table,
        back_populates="lessons",
    )

    translations = orm.relationship("LessonTranslation", back_populates="lesson")

    _segments_queryset = None

    @property
    def previous(self):
        items = self.ordered_items_for_parent(parent=self.course, key="course_id").all()
        i = items.index(self)
        if i == 0:
            return None

        return items[i - 1]

    @property
    def next(self):
        items = self.ordered_items_for_parent(parent=self.course, key="course_id").all()
        i = items.index(self)
        if i == len(items) - 1:
            return None
        return items[i + 1]

    @property
    def last_segment(self):
        return (
            Segment.objects()
            .filter(Segment.lesson_id == self.id)
            .order_by(sa.desc(Segment.order))
            .first()
        )

    @property
    def first_segment(self):
        return Segment.ordered_items_for_parent(self, "lesson_id").first()

    @property
    def segments_queryset(self):
        if not self._segments_queryset:
            self._segments_queryset = Segment.objects().filter_by(lesson_id=self.id)
        return self._segments_queryset

    @property
    def intro_segment(self):
        return self.segments_queryset.filter(Segment.order == 0).first()

    @property
    def normal_segments(self):
        return self.segments_queryset.filter(Segment.order > 0).order_by(Segment.order)

    @property
    def ordered_resources(self):
        return Resource.ordered_items_for_parent(self, "lesson_id")

    @property
    def permalink(self):
        return url_for(
            "lesson.view",
            course_slug=self.course.slug,
            lesson_slug=self.slug,
            institute="",
        )

    @property
    def thumbnail(self):
        if self.cover_image:
            return self.cover_image_url
        elif self.segments:
            return self.segments[0].thumbnail
        return ""

    @property
    def duration_seconds(self):
        t = 0
        for seg in self.segments:
            t += seg.duration_seconds
        return t

    @property
    def strfduration(self):
        return str(timedelta(seconds=self.duration_seconds))

    def get_ordered_segments(self):
        return Segment.ordered_items_for_parent(self, "lesson_id")

    def user_progress_percent(self, user):
        if len(self.segments) is 0:
            return 100
        total = 0
        for segment in self.segments:
            total = total + segment.user_progress(user)
        return int(total / len(self.segments))

    def user_progress_list(self, user):
        output = []
        for segment in self.segments:
            output.append(segment.user_progress(user))
        return output

    @property
    def get_cover(self):
        if self.cover_image:
            if self.cover_image.startswith("http"):
                return self.cover_image
            else:
                return "/static/uploads/{}".format(self.cover_image)
        return ""

    @staticmethod
    def find_by_slug(course_slug, lesson_slug):
        q = (
            Lesson.objects()
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.slug == lesson_slug)
        )

        return q.first()

    @staticmethod
    def find_by_course_slug_and_id(course_slug, lesson_id):
        q = (
            Lesson.objects()
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.id == lesson_id)
        )
        return q.first()

    def remove_teacher(self, user_id):
        enrollment = CourseEnrollment.find_by_course_and_student(
            self.course_id, user_id
        )
        if enrollment:
            self.teachers.remove(enrollment)
            return True
        return False


class LessonTranslation(Base):
    __tablename__ = "lessons_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    lesson_id = sa.Column(sa.Integer, sa.ForeignKey("lessons.id"))
    title = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    lesson = orm.relationship("Lesson", back_populates="translations")


class Segment(OrderedBase):
    __tablename__ = "lesson_segments"

    id = sa.Column(sa.Integer, primary_key=True)
    type = sa.Column(sa.String)
    video_type = sa.Column(sa.Enum(VideoTypeEnum), nullable=True)
    permission = sa.Column(sa.Enum(SegmentPermissionEnum), nullable=True)
    title = sa.Column(sa.String)
    text = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    external_id = sa.Column(sa.String)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))
    slug = sa.Column(sa.String(50))  # Unique in relation to parent
    _thumbnail = sa.Column(sa.String)  # S3 Link

    lesson_id = sa.Column(sa.Integer, sa.ForeignKey("lessons.id"))
    lesson = orm.relationship("Lesson", back_populates="segments")

    translations = orm.relationship("SegmentTranslation", back_populates="segment")

    __table_args__ = (
        sa.UniqueConstraint("lesson_id", "slug", name="_lesson_sement_uc"),
    )

    @property
    def duration(self):
        return self.duration_seconds

    @property
    def strfduration(self):
        return str(timedelta(seconds=self.duration_seconds))

    @property
    def template(self):
        return "video_wistia"

    @property
    def previous(self):
        segments = self.ordered_items_for_parent(
            parent=self.lesson, key="lesson_id"
        ).all()
        i = segments.index(self)
        previous_lesson = self.lesson.previous
        if i == 0 and previous_lesson is None:
            return None
        elif i == 0 and previous_lesson is not None:
            return previous_lesson.last_segment
        else:
            return segments[i - 1]

    @property
    def next(self):
        segments = self.ordered_items_for_parent(
            parent=self.lesson, key="lesson_id"
        ).all()
        i = segments.index(self)
        next_lesson = self.lesson.next
        if i == len(segments) - 1 and next_lesson is None:
            return None
        elif i == len(segments) - 1 and next_lesson is not None:
            return next_lesson.first_segment
        return segments[i + 1]

    def user_status(self, user, progress=None):

        if self.locked(user):
            return SegmentStatus.locked

        p = progress or self.user_progress(user)
        if p > SegmentStatusThreshold.completed:
            return SegmentStatus.completed
        if p > SegmentStatusThreshold.touched:
            return SegmentStatus.touched
        return SegmentStatus.accessible

    def locked(self, user, anonymous_progress=None):
        """ Returns True if this segment is locked for a given user. """

        if anonymous_progress is None:
            anonymous_progress = {}

        qs = self.lesson.course.get_ordered_segments().filter(
            sa.or_(
                sa.and_(Lesson.order == self.lesson.order, Segment.order < self.order),
                Lesson.order < self.lesson.order,
            )
        )

        if self.permission == SegmentPermissionEnum.hard_barrier:

            ids = [s.id for s in qs]
            if not ids:
                return False

            if user:
                qs_progress = SegmentUserProgress.objects().filter(
                    SegmentUserProgress.user_id == user.id,
                    SegmentUserProgress.segment_id.in_(ids),
                    SegmentUserProgress.progress > SegmentStatusThreshold.completed,
                )
                return qs_progress.count() != len(ids)
            else:
                for key in ids:
                    if (
                        anonymous_progress.get(str(key), 0)
                        < SegmentStatusThreshold.completed
                    ):
                        return True

                return False

        else:
            qs = qs.filter(self.permission_filter())

            barriers = list(qs)
            return (
                barriers[-1].user_progress(user) < SegmentStatusThreshold.completed
                if barriers
                else False
            )

    @classmethod
    def permission_filter(cls):
        return cls.permission.in_(
            (SegmentPermissionEnum.hard_barrier, SegmentPermissionEnum.barrier)
        )

    @property
    def permalink(self):
        return url_for(
            "segment.view",
            segment_slug=self.slug,
            lesson_slug=self.lesson.slug,
            course_slug=self.lesson.course.slug,
        )

    @property
    def thumbnail(self):
        if not self._thumbnail and self.external_id:
            self._thumbnail = fetch_thumbnail(self.external_id)
        elif not self._thumbnail:
            return "http://placekitten.com/640/360"
        return self._thumbnail

    def set_duration(self):
        self.duration_seconds = 0
        if self.external_id and "wistia.com" in self.url:
            url = "http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640".format(
                self.external_id
            )

            try:
                data = requests.get(url).json()
                self.duration_seconds = int(data["duration"])
            except (TypeError, ValueError, KeyError):
                if not self.duration_seconds:
                    self.duration_seconds = 0

    def user_progress(self, user):
        return SegmentUserProgress.user_progress(self.id, user.id if user else None)

    def save_user_progress(self, user, percent):
        return SegmentUserProgress.save_user_progress(self.id, user.id, percent)

    def find_user_progress(self, user_id):
        return SegmentUserProgress.find_user_progress(self.id, user_id)

    @classmethod
    def find_by_slug(cls, course_slug, lesson_slug, segment_slug):
        q = (
            cls.objects()
            .join(Lesson.segments)
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.slug == lesson_slug)
            .filter(cls.slug == segment_slug)
        )

        return q.first()


class SegmentTranslation(Base):
    __tablename__ = "lesson_segments_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    title = sa.Column(sa.String)
    duration_seconds = sa.Column(sa.Integer)
    url = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    segment = orm.relationship("Segment", back_populates="translations")


class Resource(OrderedBase):
    __tablename__ = "lesson_resources"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    url = sa.Column(sa.String)
    type = sa.Column(sa.Enum(ResourceTypeEnum), nullable=True)
    featured = sa.Column(sa.Boolean, default=False)
    language = sa.Column(sa.String(2))
    slug = sa.Column(sa.String(50))
    description = sa.Column(sa.String())
    anonymous_views = sa.Column(sa.Integer, default=0)

    lesson_id = sa.Column(sa.Integer, sa.ForeignKey("lessons.id"))
    lesson = orm.relationship("Lesson", back_populates="resources")

    @property
    def total_views(self):
        return LessonResourceUserAccess.count_access(self.id) + self.anonymous_views

    def views_by_user(self, user):
        return LessonResourceUserAccess.count_access(self.id, user.id)

    def log_user_view(self, user):
        LessonResourceUserAccess.log_user_access(self.id, user.id)

    def log_anonymous_view(self):
        self.anonymous_views += 1

    @property
    def icon(self):
        stubs = {
            "google_doc": "fa-file-alt",
            "google_sheet": "fa-file-spreadsheet",
            "google_slides": "fa-file-image",
        }
        if self.type in stubs:
            return stubs[self.type]
        return "fa-file"

    @property
    def content_type(self):
        stubs = {
            "google_doc": "Google document",
            "google_sheet": "Google spreadsheet",
            "google_slides": "Google slides",
        }
        if self.type in stubs:
            return stubs[self.type]
        return "External file"

    @property
    def content_img(self):
        stubs = {
            "google_sheet": "fas fa-file-spreadsheet",
            "google_doc": "fal fa-file-alt",
            "youtube": "fab fa-youtube",
            "pdf": "far fa-file-pdf",
        }

        if self.type and self.type.name in stubs:
            return stubs[self.type.name]
        return "fas fa-file-alt"

    @property
    def permalink(self):
        return url_for("resource.view", resource_id=self.id)


class LessonQA(OrderedBase):
    __tablename__ = "lesson_qa"

    id = sa.Column(sa.Integer, primary_key=True)
    question = sa.Column(sa.String)
    answer = sa.Column(sa.String)

    lesson_id = sa.Column(sa.Integer, sa.ForeignKey("lessons.id"))
    lesson = orm.relationship("Lesson", back_populates="questions")

    @classmethod
    def find_by_lesson_and_id(cls, lesson_id, qa_id):
        if not isinstance(lesson_id, int) or not isinstance(qa_id, int):
            return None
        return (
            cls.objects()
            .filter(cls.lesson_id == lesson_id)
            .filter(cls.id == qa_id)
            .first()
        )


class LessonResourceUserAccess(BaseModel):
    __tablename__ = "resource_user_access"
    id = sa.Column(sa.Integer, primary_key=True)
    resource_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_resources.id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    access_date = sa.Column(sa.DateTime, default=datetime.utcnow)

    @classmethod
    def count_access(cls, resource_id, user_id=None):
        db = get_session()
        q = db.query(sa.func.count(cls.id)).filter(cls.resource_id == resource_id)
        if user_id is not None:
            q = q.filter(LessonResourceUserAccess.user_id == user_id)
        return q.all()[0][0]

    @classmethod
    def log_user_access(cls, resource_id, user_id):
        db = get_session()
        log = cls(resource_id=resource_id, user_id=user_id)
        db.add(log)
        db.commit()


def get_course_by_slug(slug):
    return Course.find_by_slug(slug)


def get_course_by_code(code):
    return Course.find_by_code(code)


def get_lesson(lesson_id):
    return Lesson.find_by_id(lesson_id)


def get_lesson_by_slug(course_slug, lesson_slug):
    return Lesson.find_by_slug(course_slug, lesson_slug)


def get_segment(segment_id):
    return Segment.find_by_id(segment_id)


def get_segment_by_slug(course_slug, lesson_slug, segment_slug):
    return Segment.find_by_slug(course_slug, lesson_slug, segment_slug)
