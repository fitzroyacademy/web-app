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
            "picture": student.profile_picture,
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
    total_progress = _base_total_query(course). \
        group_by(Lesson.id, SegmentUserProgress.user_id).all()
    return {(Segment.find_by_id(progress.segment_id).lesson.id, progress.user_id): value for progress, value in
            total_progress}


def get_lessons_total_progress(course):
    total_progress = _base_total_query(course).group_by(Lesson.id).all()
    return {Segment.find_by_id(progress.segment_id).lesson.id: value for progress, value in total_progress}


def _base_total_query(course):
    session = get_session()

    queryset = session.query(SegmentUserProgress, func.sum(SegmentUserProgress.progress)). \
        join(Segment).join(Lesson). \
        join(CourseEnrollment,
             (SegmentUserProgress.user_id == CourseEnrollment.user_id) & (Lesson.course_id == CourseEnrollment.course_id)). \
        filter(Lesson.course_id == course.id). \
        filter(CourseEnrollment.access_level == CourseAccess.student). \
        distinct(SegmentUserProgress.id)

    return queryset
