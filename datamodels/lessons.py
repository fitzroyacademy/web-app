from datetime import datetime, timedelta

import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import url_for

from .base import BaseModel, OrderedBase, Base, get_session
from .enums import ResourceTypeEnum
from .enrollments import CourseEnrollment, lesson_user_enrollment_association_table
from .segments import Segment


class Lesson(OrderedBase):
    __tablename__ = "lessons"
    order_parent_name = "course"
    order_parent_key = "course_id"

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

    def last_child(self, child):
        return child.ordered_items_for_parent(self, "lesson_id", desc=True).first()

    def first_child(self, child):
        return child.ordered_items_for_parent(self, "lesson_id").first()

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

    def get_ordered_segments_for_view(self, display_hidden=True, user=None):
        show_hidden = True
        if not display_hidden:
            show_hidden = user is not None and user.teaches(self.course)

        queryset = Segment.ordered_items_for_parent(self)
        segments = queryset.all()
        if not show_hidden:
            segments = [
                segment for segment in segments if not segment.is_hidden_segment()
            ]

        return [s for s in segments]  # just make sure that we return the same type

    def user_progress_percent(self, user):
        segments = self.segments
        if len(segments) == 0:
            return 100
        total = 0
        for segment in segments:
            total = total + segment.user_progress(user)
        return int(total / len(segments))

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


class Resource(OrderedBase):
    __tablename__ = "lesson_resources"
    order_parent_name = "lesson"
    order_parent_key = "lesson_id"

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
    order_parent_name = "lesson"
    order_parent_key = "lesson_id"

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
        log = LessonResourceUserAccess(resource_id=resource_id, user_id=user_id)
        db.add(log)
        db.commit()
