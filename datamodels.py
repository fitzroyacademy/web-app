import json
from datetime import datetime, timedelta
from os import environ

import requests
import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import current_app as app
from flask import url_for
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from werkzeug.security import generate_password_hash, check_password_hash

from enums import VideoTypeEnum, SegmentPermissionEnum, ResourceTypeEnum

Base = declarative_base()


def dump(obj, seen=None):
    if not isinstance(obj, Base):
        if isinstance(obj, list) and len(obj) > 0 and isinstance(obj[0], Base):
            o = []
            for i in obj:
                o.append(dump(i, seen=seen))
            return o
        else:
            return obj
    seen = seen or []  # Recursion trap.
    seen.append(id(obj))
    ignored = ["metadata"]
    fields = {}
    for f in [x for x in dir(obj) if x.startswith("_") is False and x not in ignored]:
        data = getattr(obj, f)
        try:
            json.dumps(data)
            fields[f] = data
        except TypeError:
            if isinstance(data, Base):
                if id(data) in seen:
                    fields[f] = None
                else:
                    fields[f] = dump(data, seen)
            elif callable(data) and f.startswith("get_"):
                fields[f[4:]] = dump(data(), seen)
            elif isinstance(data, list):
                fields[f] = []
                for o in data:
                    if id(o) in seen:
                        fields[f].append(None)
                    else:
                        fields[f].append(dump(o, seen))
    return fields


class BaseModel(Base):
    __abstract__ = True

    @classmethod
    def find_by_id(cls, obj_id):
        session = get_session()
        return session.query(cls).filter(cls.id == obj_id).first()

    @classmethod
    def find_by_slug(cls, slug):
        session = get_session()
        if hasattr(cls, "slug"):
            return session.query(cls).filter(cls.slug == slug).first()
        else:
            raise AttributeError("Object do not has attribute slug")


class OrderedBase(BaseModel):
    __abstract__ = True

    order = sa.Column(sa.Integer)

    @classmethod
    def get_ordered_items(cls):
        session = get_session()
        return session.query(cls).filter(cls.order > 0).order_by(cls.order)

    @classmethod
    def ordered_items_for_parent(cls, parent, key):
        session = get_session()
        return (
            session.query(cls)
            .filter(getattr(cls, key) == parent.id)
            .order_by(cls.order)
        )

    @classmethod
    def reorder_items(cls, items_order):
        lessons_mapping = [
            {"id": items_order[i], "order": i + 1} for i in range(len(items_order))
        ]
        db = get_session()
        db.bulk_update_mappings(cls, lessons_mapping)
        db.commit()

    @classmethod
    def delete(cls, instance, parent=None, key=None):
        if parent:
            session = get_session()
            session.delete(instance)
            session.commit()

            list_of_items = [
                l.id
                for l in session.query(cls)
                .filter(getattr(cls, key) == parent.id)
                .order_by(cls.order)
            ]
            if list_of_items:
                cls.reorder_items(list_of_items)


class User(BaseModel):
    __tablename__ = "users"

    id = sa.Column(sa.Integer, primary_key=True)
    username = sa.Column(sa.String(50), unique=True)
    first_name = sa.Column(sa.String)
    last_name = sa.Column(sa.String)
    email = sa.Column(sa.String, unique=True)
    phone_number = sa.Column(sa.String(15))
    dob = sa.Column(sa.Date)
    password_hash = sa.Column(sa.String(128))
    profile_picture = sa.Column(sa.String)
    bio = sa.Column(sa.String)
    super_admin = sa.Column(sa.Boolean, default=False)

    institutes = orm.relationship("InstituteEnrollment", back_populates="user")
    programs = orm.relationship("ProgramEnrollment", back_populates="user")
    course_enrollments = orm.relationship("CourseEnrollment", back_populates="user")

    @hybrid_property
    def password(self):
        return ""

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return " ".join([self.first_name, self.last_name])

    @property
    def courses(self):
        courses = []
        for enrollment in CourseEnrollment.find_by_user(self.id):
            courses.append(enrollment.course)
        return courses

    @property
    def course_progress(self):
        courses = self.courses
        if len(courses) is 0:
            return 100
        total = 0
        for course in courses:
            total = total + course.user_progress(self)
        return int(total / len(courses))

    def set_preference(self, tag, boolean):
        UserPreference.set_preference(self, tag, boolean)

    def preference(self, tag):
        pref = UserPreference.get_preference(self, tag)
        if pref is not None:
            return pref.toggled
        return False

    def merge_anonymous_data(self, data):
        for seg_id in data:
            save_segment_progress(seg_id, self.id, int(data[seg_id]))

    def teaches(self, course):
        e = CourseEnrollment.find_by_course_and_student(course.id, self.id)
        if e is None:
            return False
        if e.access_level == COURSE_ACCESS_TEACHER:
            return True
        return False

    def enrolled(self, course):
        e = CourseEnrollment.find_by_course_and_student(course.id, self.id)
        if e is None:
            return False
        if e.access_level == COURSE_ACCESS_STUDENT:
            return True
        return False

    @staticmethod
    def find_by_email(email):
        session = get_session()
        return session.query(User).filter(User.email == email).first()


PreferenceTags = [
    "emails_from_teachers",
    "emails_from_site",
    "data_research",
    "data_show_name",
    "data_show_email",
]


class UserPreference(BaseModel):
    __tablename__ = "users_preferences"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    # Corresponds to PreferenceTags list for now.
    preference = sa.Column(sa.Integer)
    toggled = sa.Column(sa.Boolean)

    @staticmethod
    def get_preference(user, preference_tag):
        if preference_tag not in PreferenceTags:
            raise Exception("Preference Unknown: {}".format(preference_tag))
        i = PreferenceTags.index(preference_tag)
        session = get_session()
        return (
            session.query(UserPreference)
            .filter(UserPreference.user_id == user.id)
            .filter(UserPreference.preference == i)
            .first()
        )

    @staticmethod
    def set_preference(user, preference_tag, boolean):
        pref = UserPreference.get_preference(user, preference_tag)
        if pref is None:
            i = PreferenceTags.index(preference_tag)
            session = get_session()
            pref = UserPreference(user_id=user.id, preference=i, toggled=boolean)
        pref.boolean = boolean
        session.add(pref)
        session.commit()


class Institute(BaseModel):
    __tablename__ = "institutes"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    logo = sa.Column(sa.String)  # URL to picture resource
    slug = sa.Column(sa.String(50), unique=True)

    users = orm.relationship("InstituteEnrollment", back_populates="institute")

    def add_user(self, user, access_level=0):
        association = InstituteEnrollment(access_level=access_level)
        association.institute = self
        association.user = user
        self.users.append(association)


class InstituteEnrollment(BaseModel):
    __tablename__ = "users_institutes"

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    institute_id = sa.Column("institute_id", sa.Integer, sa.ForeignKey("institutes.id"))
    access_level = sa.Column("access_level", sa.Integer)

    user = orm.relationship("User", back_populates="institutes")
    institute = orm.relationship("Institute", back_populates="users")


class Program(BaseModel):
    __tablename__ = "programs"

    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    slug = sa.Column(sa.String(50), unique=True)

    users = orm.relationship("ProgramEnrollment", back_populates="program")
    courses = orm.relationship("Course", back_populates="program")

    def add_user(self, user, access_level=0):
        association = ProgramEnrollment(access_level=access_level)
        association.program = self
        association.user = user
        self.users.append(association)


class ProgramEnrollment(BaseModel):
    __tablename__ = "users_programs"

    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"), primary_key=True)
    program_id = sa.Column(sa.Integer, sa.ForeignKey("programs.id"), primary_key=True)
    access_level = sa.Column(sa.Integer)

    user = orm.relationship("User", back_populates="programs")
    program = orm.relationship("Program", back_populates="users")


COURSE_ACCESS_STUDENT = 1
COURSE_ACCESS_TEACHER = 2
COURSE_ACCESS_ADMIN = 3


class Course(BaseModel):
    __tablename__ = "courses"

    id = sa.Column(sa.Integer, primary_key=True)
    title = sa.Column(sa.String)
    picture = sa.Column(sa.String)  # URL to picture resource
    cover_image = sa.Column(sa.String)
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

    lessons = orm.relationship("Lesson", back_populates="course")

    users = orm.relationship("CourseEnrollment", back_populates="course")
    translations = orm.relationship("CourseTranslation", back_populates="course")

    preview_thumbnail = sa.Column(sa.String)

    _lessons_queryset = None

    @classmethod
    def list_public_courses(cls):
        session = get_session()
        return (
            session.query(cls)
            .filter(
                cls.guest_access == True, cls.visibility == "public", cls.draft == False
            )
            .all()
        )

    @property
    def number_of_resources(self):
        session = get_session()
        return session.query(Resource).outerjoin(Resource.lesson).filter(Lesson.course_id == self.id).count()

    def get_ordered_lessons(self):
        return Lesson.get_ordered_items().filter(Lesson.course_id == self.id)

    def add_user(self, user, access_level=0):
        association = CourseEnrollment(access_level=access_level)
        association.course = self
        association.user = user
        self.users.append(association)

    def remove_teacher(self, user_id):
        enrollment = CourseEnrollment.find_by_course_and_student(self.id, user_id)
        if enrollment:
            s = get_session()
            s.delete(enrollment)
            s.commit()
            return True
        return False

    def add_instructor(self, user):
        self.add_user(user, COURSE_ACCESS_TEACHER)

    def options(self, option):
        return getattr(self, option, False)

    def is_student(self, user_id):
        return CourseEnrollment.find_by_course_and_student(self.id, user_id) is not None

    @property
    def lessons_queryset(self):
        if not self._lessons_queryset:
            session = get_session()
            self._lessons_queryset = session.query(Lesson).filter_by(course_id=self.id)
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
        return url_for("course.view", slug=self.slug)

    @property
    def thumbnail(self):
        if self.cover_image:
            return self.cover_image
        elif self.lessons:
            return self.lessons[0].thumbnail

    @property
    def instructors(self):
        """ A unique list of users associated with this course that
        have teacher-level access."""
        associations = CourseEnrollment.find_teachers_for_course(self.id)
        users = []
        for ass in associations:
            users.append(ass.user)
        return users

    @property
    def students(self):
        """ A unique list of users associated with this course that
        have studet-level access."""
        associations = CourseEnrollment.find_students_for_course(self.id)
        users = []
        for ass in associations:
            users.append(ass.user)
        return users

    def user_progress(self, user):
        if len(self.lessons) is 0:
            return 100
        total = 0
        for lesson in self.lessons:
            total = total + lesson.user_progress_percent(user)
        return int(total / len(self.lessons))

    def class_progress(self):
        pass

    def enroll(self, student):
        """ Adds a user to a course with student-level access. """
        if get_enrollment(self.id, student.id) is None:
            enrollment = CourseEnrollment(
                course_id=self.id,
                user_id=student.id,
                access_level=COURSE_ACCESS_STUDENT,
            )
            s = get_session()
            s.add(enrollment)
            s.commit()

    @staticmethod
    def find_by_code(code):
        session = get_session()
        return session.query(Course).filter(Course.course_code == code).first()


class CourseTranslation(Base):
    __tablename__ = "courses_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"))
    title = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    course = orm.relationship("Course", back_populates="translations")


lesson_user_enrollment_association_table = sa.Table(
    "_lesson_user_enrollment",
    Base.metadata,
    sa.Column("users_courses_id", sa.Integer, sa.ForeignKey("users_courses.id")),
    sa.Column("lessons_id", sa.Integer, sa.ForeignKey("lessons.id")),
)


class CourseEnrollment(BaseModel):
    __tablename__ = "users_courses"
    __table_args__ = (
        sa.UniqueConstraint("course_id", "user_id", name="_course_user_enrollment"),
    )

    id = sa.Column(sa.Integer, primary_key=True)
    user_id = sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"))
    course_id = sa.Column("course_id", sa.Integer, sa.ForeignKey("courses.id"))
    access_level = sa.Column("access_level", sa.Integer)

    user = orm.relationship("User", back_populates="course_enrollments")
    course = orm.relationship("Course", back_populates="users")
    lessons = orm.relationship(
        "Lesson",
        secondary=lesson_user_enrollment_association_table,
        back_populates="teachers",
    )

    @staticmethod
    def find_by_course_and_student(course_id, student_id):
        session = get_session()
        return (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.user_id == student_id)
            .first()
        )

    @staticmethod
    def find_students_for_course(course_id):
        session = get_session()
        return (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.access_level == COURSE_ACCESS_STUDENT)
            .all()
        )

    @staticmethod
    def find_teachers_for_course(course_id):
        session = get_session()
        return (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.access_level == COURSE_ACCESS_TEACHER)
            .all()
        )

    @staticmethod
    def find_by_user(user_id):
        session = get_session()
        return (
            session.query(CourseEnrollment)
            .filter(CourseEnrollment.user_id == user_id)
            .all()
        )


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

    @orm.validates("slug")
    def validate_slug(self, key, value):
        """ TODO: Check the parent course for any duplicate lesson slugs """
        return value

    @property
    def segments_queryset(self):
        if not self._segments_queryset:
            session = get_session()
            self._segments_queryset = session.query(Segment).filter_by(
                lesson_id=self.id
            )
        return self._segments_queryset

    @property
    def intro_segment(self):
        return self.segments_queryset.filter(Segment.order == 0).first()

    @property
    def normal_segments(self):
        return self.segments_queryset.filter(Segment.order > 0).order_by(Segment.order)

    @property
    def ordered_resources(self):
        session = get_session()
        return (
            session.query(Resource)
            .filter_by(lesson_id=self.id)
            .order_by(Resource.order)
        )

    @property
    def permalink(self):
        return url_for(
            "lesson.view", course_slug=self.course.slug, lesson_slug=self.slug
        )

    @property
    def thumbnail(self):
        if self.cover_image:
            return self.cover_image
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
        return Segment.get_ordered_items().filter(Segment.lesson_id == self.id)

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
                return "/uploads/{}".format(self.cover_image)
        return ""

    @staticmethod
    def find_by_slug(course_slug, lesson_slug):
        session = get_session()
        q = (
            session.query(Lesson)
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.slug == lesson_slug)
        )
        try:
            return q.first()
        except:
            return None

    @staticmethod
    def find_by_course_slug_and_id(course_slug, lesson_id):
        session = get_session()
        q = (
            session.query(Lesson)
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.id == lesson_id)
        )
        try:
            return q.first()
        except:
            return None

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

    __table_args__ = (sa.UniqueConstraint("lesson_id", "slug", name="_lesson_sement_uc"),)

    @orm.validates("slug")
    def validate_slug(self, key, value):
        """ TODO: Check the parent lesson for any duplicate segment slugs """
        return value

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

    def user_progress(self, user):
        if user is None:
            return 0
        progress = get_segment_progress(self.id, user.id)
        if progress:
            return progress.progress
        return 0

    def save_user_progress(self, user, percent):
        return save_segment_progress(self.id, user.id, percent)

    @staticmethod
    def find_user_progress(segment_id, user_id):
        session = get_session()
        q = (
            session.query(SegmentUserProgress)
            .filter(SegmentUserProgress.segment_id == segment_id)
            .filter(SegmentUserProgress.user_id == user_id)
        )
        try:
            return q.first()
        except:
            return None

    @classmethod
    def find_by_slug(cls, course_slug, lesson_slug, segment_slug):
        session = get_session()
        q = (
            session.query(cls)
            .join(Lesson.segments)
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.slug == lesson_slug)
            .filter(cls.slug == segment_slug)
        )
        try:
            return q.first()
        except:
            return None


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
        if self.type.name in stubs:
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
        session = get_session()
        return (
            session.query(cls)
            .filter(cls.lesson_id == lesson_id)
            .filter(cls.id == qa_id)
            .first()
        )


class LessonResourceUserAccess(Base):
    __tablename__ = "resource_user_access"
    id = sa.Column(sa.Integer, primary_key=True)
    resource_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_resources.id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))
    access_date = sa.Column(sa.DateTime, default=datetime.utcnow)

    @staticmethod
    def count_access(resource_id, user_id=None):
        session = get_session()
        q = session.query(sa.func.count(LessonResourceUserAccess.id)).filter(
            LessonResourceUserAccess.resource_id == resource_id
        )
        if user_id is not None:
            q = q.filter(LessonResourceUserAccess.user_id == user_id)
        return q.all()[0][0]

    @staticmethod
    def log_user_access(resource_id, user_id):
        session = get_session()
        log = LessonResourceUserAccess(resource_id=resource_id, user_id=user_id)
        q = session.query(LessonResourceUserAccess).filter(
            LessonResourceUserAccess.resource_id == resource_id
        )
        session.add(log)
        session.commit()


class SegmentUserProgress(Base):
    __tablename__ = "segment_user_progress"
    id = sa.Column(sa.Integer, primary_key=True)
    progress = sa.Column(sa.Integer)
    # No complex join definition for now.
    segment_id = sa.Column(sa.Integer, sa.ForeignKey("lesson_segments.id"))
    user_id = sa.Column(sa.Integer, sa.ForeignKey("users.id"))


_session = None


def get_session():
    global _session
    if _session is None:
        engine = sa.create_engine(app.config["DB_URI"])
        Base.metadata.create_all(engine)
        Session = orm.scoped_session(orm.sessionmaker(bind=engine))
        _session = Session()
    return _session


def _clear_session_for_tests():
    global _session
    if "FLASK_ENV" not in environ or environ["FLASK_ENV"] != "test":
        raise Exception("Session clearing is for test instances only.")
    _session = None


def get_user(user_id):
    return User.find_by_id(user_id)


def get_user_by_email(email):
    return User.find_by_email(email)


def get_course_by_slug(slug):
    return Course.find_by_slug(slug)


def get_course_by_code(code):
    return Course.find_by_code(code)


def get_program_by_slug(slug):
    return Program.find_by_slug(slug)


def get_lesson(lesson_id):
    return Lesson.find_by_id(lesson_id)


def get_lesson_by_slug(course_slug, lesson_slug):
    return Lesson.find_by_slug(course_slug, lesson_slug)


def get_segment(segment_id):
    return Segment.find_by_id(segment_id)


def get_segment_by_slug(course_slug, lesson_slug, segment_slug):
    return Segment.find_by_slug(course_slug, lesson_slug, segment_slug)


def get_segment_progress(segment_id, user_id):
    return Segment.find_user_progress(segment_id, user_id)


def save_segment_progress(segment_id, user_id, percent):
    session = get_session()
    sup = get_segment_progress(segment_id, user_id)
    percent = int(percent)
    if sup is None:
        sup = SegmentUserProgress(
            segment_id=segment_id, user_id=user_id, progress=percent
        )
    elif sup.progress < percent:
        sup.progress = percent
    session.add(sup)
    session.commit()
    return sup


def get_enrollment(course_id, student_id):
    return CourseEnrollment.find_by_course_and_student(course_id, student_id)


def fetch_thumbnail(wistia_id, width=640, height=360):
    """ TODO: Put this in an S3 bucket before returning the URL. """
    url = "http://fast.wistia.net/oembed?url=http://home.wistia.com/medias/{}?embedType=async&videoWidth=640".format(
        wistia_id
    )
    data = requests.get(url).json()
    return data["thumbnail_url"].split("?")[0] + "?image_crop_resized={}x{}".format(
        width, height
    )
