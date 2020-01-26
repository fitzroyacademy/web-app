from sqlalchemy import func

from datamodels import SegmentUserProgress, get_session, Lesson, Segment, \
    CourseEnrollment
from datamodels.enums import CourseAccess


def get_course_progress(course):
    ordered_lessons = course.get_ordered_lessons()
    number_of_students = len(course.students)
    lessons_total = get_lessons_total_progress(course)
    lessons = []

    for lesson in ordered_lessons:
        progress = lessons_total.get(lesson.id, 0)
        number_of_segments = lesson.get_ordered_segments().count()
        _temp = {"lesson_id": lesson.id,
                 "number_of_segments": number_of_segments,
                 "title": lesson.title,
                 "thumbnail": lesson.thumbnail}
        if progress:
            avg_progress = int(progress * 1.0 / number_of_students / number_of_segments if number_of_segments and number_of_students else 0)
            _temp["total_progress"] = progress
            _temp["avg"] = avg_progress
        else:
            _temp["total_progress"] = 0
            _temp["avg"] = 0

        lessons.append(_temp)

    return {"number_of_students": number_of_students,
            "lessons": lessons}


def get_students_progress(course):
    ordered_lessons = [(l.id, l.get_ordered_segments().count()) for l in course.get_ordered_lessons()]
    total_number_of_segments = course.get_ordered_segments().count()
    students_total = get_students_total_progress(course)
    _students = course.students
    students = []

    for student in _students:
        _temp = {
            "id": student.id,
            "name": student.first_name,
            "picture": student.profile_picture_url,
            "admin": student.super_admin,
            "color": ""
        }
        total_student_progress = 0
        lessons_progress = []
        for lesson_id, number_of_segments in ordered_lessons:
            p = students_total.get((lesson_id, student.id), 0)
            lessons_progress.append(str(int(p * 1.0 / number_of_segments if number_of_segments else 0)))
            total_student_progress += p

        _temp["completion"] = ";".join(lessons_progress)
        _temp["progress"] = int(total_student_progress * 1.0 / total_number_of_segments if total_number_of_segments else 0)

        students.append(_temp)

    return students


def get_students_total_progress(course):
    group_by = [SegmentUserProgress.user_id, Lesson.id]
    total_progress = _base_total_query(course, group_by). \
        group_by(*group_by).all()
    return {(lesson_id, user_id): value for value, user_id, lesson_id in
            total_progress}


def get_lessons_total_progress(course):
    group_by = [Lesson.id]
    total_progress = _base_total_query(course, group_by).group_by(*group_by).all()
    return {lesson_id: value for value, lesson_id in total_progress}


def _base_total_query(course, group_by):
    session = get_session()
    queryset = session.query(func.sum(SegmentUserProgress.progress), *group_by). \
        join(Segment, SegmentUserProgress.segment_id == Segment.id).join(Lesson, Lesson.id == Segment.lesson_id). \
        join(CourseEnrollment,
             (SegmentUserProgress.user_id == CourseEnrollment.user_id) & (Lesson.course_id == CourseEnrollment.course_id)). \
        filter(Lesson.course_id == course.id). \
        filter(CourseEnrollment.access_level == CourseAccess.student)

    return queryset
