import sqlalchemy as sa
import sqlalchemy.orm as orm

from .base import BaseModel, Base, get_session
from .enums import CourseAccess


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
        return (
            CourseEnrollment.objects()
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.user_id == student_id)
            .first()
        )

    @staticmethod
    def find_students_for_course(course_id):
        return (
            CourseEnrollment.objects()
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.access_level == CourseAccess.student)
            .all()
        )

    @staticmethod
    def find_teachers_for_course(course_id):
        return (
            CourseEnrollment.objects()
            .filter(CourseEnrollment.course_id == course_id)
            .filter(CourseEnrollment.access_level == CourseAccess.teacher)
            .all()
        )

    @staticmethod
    def find_by_user(user_id):
        return (
            CourseEnrollment.objects().filter(CourseEnrollment.user_id == user_id).all()
        )

    @classmethod
    def add_user(cls, course_id, user, access_level):
        enrollment = CourseEnrollment(
            course_id=course_id, user=user, access_level=access_level
        )
        s = get_session()
        s.add(enrollment)
        s.commit()

    @classmethod
    def is_student(cls, course_id, user_id):
        return cls.find_by_course_and_student(course_id, user_id) is not None

    @classmethod
    def remove_teacher(cls, course_id, user_id):
        enrollment = cls.find_by_course_and_student(course_id, user_id)
        if enrollment:
            s = get_session()
            s.delete(enrollment)
            s.commit()
            return True
        return False

    @classmethod
    def enroll(cls, course_id, user_id):
        if get_enrollment(course_id, user_id) is None:
            enrollment = cls(
                course_id=course_id, user_id=user_id, access_level=CourseAccess.student
            )
            s = get_session()
            s.add(enrollment)
            s.commit()

    @classmethod
    def instructors(cls, course_id):
        associations = cls.find_teachers_for_course(course_id)
        return [ass.user for ass in associations]

    @classmethod
    def students(cls, course_id):
        associations = cls.find_students_for_course(course_id)
        return [ass.user for ass in associations]

    @classmethod
    def user_courses(cls, user_id):
        return [e.course for e in cls.find_by_user(user_id)]

    @classmethod
    def teaches(cls, user_id, course_id):
        e = CourseEnrollment.find_by_course_and_student(course_id, user_id)
        if e is None:
            return False
        if e.access_level == CourseAccess.teacher:
            return True
        return False

    @classmethod
    def enrolled(cls, user_id, course_id):
        e = CourseEnrollment.find_by_course_and_student(course_id, user_id)
        if e is None:
            return False
        if e.access_level == CourseAccess.student:
            return True
        return False


def get_enrollment(course_id, student_id):
    return CourseEnrollment.find_by_course_and_student(course_id, student_id)
