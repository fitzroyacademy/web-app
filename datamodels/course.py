import sqlalchemy as sa
import sqlalchemy.orm as orm
from flask import url_for

from .base import BaseModel, Base, get_session
from .enums import CourseAccess
from .enrollments import CourseEnrollment
from .segments import Segment
from .lessons import Lesson, Resource


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

    def get_ordered_segments(self, only_barriers=False, show_hidden=True):
        db = get_session()

        queryset = (
            db.query(Segment)
            .join(Lesson)
            .filter(Lesson._is_deleted.is_(False), Lesson.course_id == self.id)
        )

        if only_barriers:
            queryset = queryset.filter(Segment.barrier_filter())

        if not show_hidden:
            queryset = queryset.filter(Segment.filter_out_hidden())

        return queryset.order_by(Lesson.order, Segment.order)

    def get_ordered_lessons(self):
        """ Get queryset of ordered lessons of the course. """
        return Lesson.ordered_items_for_parent(self)

    @property
    def intro_lesson(self):
        return self.get_ordered_lessons().filter(Lesson.order == 0).first()

    @property
    def normal_lessons(self):
        return self.get_ordered_lessons().filter(Lesson.order > 0)

    @property
    def number_of_resources(self):
        return (
            Resource.objects()
            .outerjoin(Resource.lesson)
            .filter(Lesson.course_id == self.id)
            .count()
        )

    def add_user(self, user, access_level=CourseAccess.student):
        CourseEnrollment.add_user(self.id, user, access_level)

    def remove_teacher(self, user_id):
        return CourseEnrollment.remove_teacher(self.id, user_id)

    def add_instructor(self, user):
        self.add_user(user, CourseAccess.teacher)

    def is_student(self, user_id):
        """ Checks if given user is a student of the course"""
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

    @staticmethod
    def find_lesson_by_course_slug_and_id(course_slug, lesson_id):
        q = (
            Lesson.objects()
            .join(Lesson.course)
            .filter(Course.slug == course_slug)
            .filter(Lesson.id == lesson_id)
        )
        return q.first()

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
        if len(self.lessons) == 0:
            return 100
        total = 0
        for lesson in self.lessons:
            total = total + lesson.user_progress_percent(user)
        return int(total / len(self.lessons))

    @classmethod
    def find_by_code(cls, code):
        return cls.objects().filter(cls.course_code == code).first()


class CourseTranslation(Base):
    __tablename__ = "courses_translated"

    id = sa.Column(sa.Integer, primary_key=True)
    course_id = sa.Column(sa.Integer, sa.ForeignKey("courses.id"))
    title = sa.Column(sa.String)
    language = sa.Column(sa.String(2))

    course = orm.relationship("Course", back_populates="translations")
