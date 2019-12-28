import sqlalchemy as sa

from .course import Course, Lesson
from .segments import Segment
from .institute import Institute
from .user import User


def list_public_courses(institute_slug=""):
    query = Course.visibility == "public"
    if institute_slug:
        institute = Institute.find_by_slug(institute_slug)
        if institute:
            query = sa.or_(
                Course.visibility == "public",
                sa.and_(
                    Course.visibility == "institute", Course.institute == institute
                ),
            )
    return Course.objects().filter(query, Course.draft.is_(False)).all()


def find_segment_by_slugs(course_slug, lesson_slug, segment_slug):
    q = (
        Segment.objects()
        .join(Lesson.segments)
        .join(Lesson.course)
        .filter(Course.slug == course_slug)
        .filter(Lesson.slug == lesson_slug)
        .filter(Segment.slug == segment_slug)
    )

    return q.first()


def get_course_by_slug(slug):
    return Course.find_by_slug(slug)


def get_course_by_code(code):
    return Course.find_by_code(code)


def get_lesson(lesson_id):
    return Lesson.find_by_id(lesson_id)


def get_lesson_by_slugs(course_slug, lesson_slug):
    q = (
        Lesson.objects()
        .join(Lesson.course)
        .filter(Course.slug == course_slug)
        .filter(Lesson.slug == lesson_slug)
    )
    return q.first()


def get_segment(segment_id):
    return Segment.find_by_id(segment_id)


def get_user(user_id):
    return User.find_by_id(user_id)


def get_user_by_email(email):
    return User.find_by_email(email)
