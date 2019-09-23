from flask import Blueprint, render_template, request, jsonify

import datamodels
import stubs
from .decorators import login_required, teacher_required
from .utils import reorder_items

blueprint = Blueprint("segment", __name__, template_folder="templates")


@blueprint.route(
    "/<slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/delete", methods=["POST"]
)
@login_required
@teacher_required
def course_delete_lesson(user, course, slug, lesson_id, segment_id):
    lesson = datamodels.Lesson.find_by_id(lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)
    if (
        segment
        and lesson
        and lesson.course_id == course.id
        and segment.lesson_id == lesson_id
    ):
        db = datamodels.get_session()
        db.delete(segment)
        db.commit()

        list_of_items = [l.id for l in datamodels.Segment.get_ordered_items()]
        if list_of_items:
            datamodels.Segment.reorder_items(list_of_items)

        return jsonify(
            {"success_url": "/course/{}/lessons/{}/edit".format(slug, lesson_id)}
        )

    return jsonify({"success": False, "message": "Couldn't delete segment"}), 400


@blueprint.route("/<slug>/lessons/<int:lesson_id>/segments/reorder", methods=["POST"])
@login_required
@teacher_required
def reorder_lessons(user, course, slug, lesson_id):
    lesson = datamodels.Lesson.find_by_id(lesson_id)
    if lesson and lesson.course_id != course.id:
        return jsonify({"succes": False, "message": "Course do not match lesson"}), 400

    return reorder_items(request, datamodels.Segment, lesson.segments)


@blueprint.route("<course_slug>/<lesson_slug>/<segment_slug>")
def view(course_slug, lesson_slug=None, segment_slug=None):
    """
    Retrieves and displays a particular course, with the specified lesson
    and segment set to be active.
    """
    if lesson_slug is None:
        course = datamodels.get_course_by_slug(course_slug)
        lesson = course.lessons[0]
        segment = lesson.segments[0]
    else:
        segment = datamodels.get_segment_by_slug(course_slug, lesson_slug, segment_slug)
        lesson = segment.lesson
        course = lesson.course
    data = {
        "students": stubs.student_completion,
        "active_lesson": lesson,
        "active_segment": segment,
        "course": course,
    }
    return render_template("course.html", **data)
