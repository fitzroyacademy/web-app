from .course import (
    Course,
    Segment,
    Lesson,
    LessonQA,
    LessonResourceUserAccess,
    LessonTranslation,
    CourseTranslation,
    SegmentTranslation,
    SegmentStatus,
    SegmentStatusThreshold,
    Resource,
    SegmentUserProgress,
    get_course_by_slug,
    get_course_by_code,
    get_lesson,
    get_lesson_by_slug,
    get_segment,
    get_segment_by_slug,
)
from .enrollments import CourseEnrollment, get_enrollment
from .user import UserPreference, User
from .institute import (
    Program,
    ProgramEnrollment,
    Institute,
    InstituteEnrollment,
    get_program_by_slug,
)
from .custom_settings import CustomSetting
from .base import get_session, _clear_session_for_tests


# ToDo: remove this legacy code at some point
def get_user(user_id):
    return User.find_by_id(user_id)


def get_user_by_email(email):
    return User.find_by_email(email)


__all__ = [
    "Course",
    "CourseEnrollment",
    "Segment",
    "Lesson",
    "LessonQA",
    "LessonResourceUserAccess",
    "LessonTranslation",
    "CourseTranslation",
    "SegmentTranslation",
    "SegmentStatus",
    "SegmentStatusThreshold",
    "Resource",
    "SegmentUserProgress",
    "get_course_by_slug",
    "get_course_by_code",
    "get_lesson",
    "get_lesson_by_slug",
    "get_segment",
    "get_segment_by_slug",
    "SegmentUserProgress",
    "CourseEnrollment",
    "get_enrollment",
    "UserPreference",
    "User",
    "Program",
    "ProgramEnrollment",
    "Institute",
    "InstituteEnrollment",
    "get_program_by_slug",
    "CustomSetting",
    "get_session",
    "_clear_session_for_tests",
    "get_user",
    "get_user_by_email",
]
