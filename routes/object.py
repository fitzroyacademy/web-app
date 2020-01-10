import json

from flask import Blueprint, render_template, session

import datamodels
from charts.student_progress import get_course_progress, get_students_progress
from routes.utils import find_segment_barrier
from utils.base import get_current_user
from utils.database import dump

blueprint = Blueprint("object", __name__, template_folder="templates")


@blueprint.route("/_segment/<segment_id>")
def segment(segment_id):
    """ Returns a partial JSON dump of a Lesson Segment by ID. """

    current_user = get_current_user()

    ext = None
    if segment_id.endswith(".json"):
        ext = "json"
        segment_id = segment_id.split(".")[0]
    active_segment = datamodels.get_segment(segment_id)
    if active_segment is None:
        raise "Segment not found: %s".format(segment_id)

    course = active_segment.lesson.course
    barrier = find_segment_barrier(current_user, course)
    teaches_course = current_user.teaches(course) if current_user else False

    ordered_segments = list(course.get_ordered_segments(show_hidden=teaches_course))
    locked_segments = (
        [
            ordered_segments[i].id
            for i in range(ordered_segments.index(barrier), len(ordered_segments))
        ]
        if barrier
        else []
    )

    if not current_user:
        anon_progress = json.loads(session.get("anon_progress", "{}"))
    else:
        anon_progress = {}

    if active_segment.type == datamodels.SegmentType.text:
        html = render_template(
            "partials/segments/_text.html", active_segment=active_segment
        )
    elif active_segment.type == datamodels.SegmentType.survey:
        html = render_template(
            "partials/segments/survey/{}.html".format(active_segment.survey_type.name),
            active_segment=active_segment,
        )
    else:
        html = ""

    data = {
        "active_segment": active_segment,
        "segment_type": active_segment.type.name,
        "locked": active_segment.locked(current_user, anon_progress),
        "barrier_id": barrier.id if barrier else None,
        "barrier_type": barrier.barrier.name if barrier else None,
        "locked_segments": locked_segments,
        "html": html,
    }
    if ext == "json":
        dumped_data = dump(data["active_segment"])
        data["active_segment"] = dumped_data
        return json.dumps(data)
    return render_template("partials/course/_active_segment.html", **data)


@blueprint.route("/_lesson_resources/<lesson_id>")
def lesson_resources(lesson_id):
    """ Returns a partial JSON dump of a Lesson Resource by ID. """

    lesson = datamodels.get_lesson(lesson_id)
    course = lesson.course
    if lesson is None:
        return {"error": "Lesson not found"}
    data = {
        "students": get_students_progress(course),
        "lesson": lesson,
        "lessons": lesson.course.get_ordered_lessons(),
        "course": lesson.course,
        "active_segment": lesson.segments[0] if lesson.segments else None,
        "active_lesson": lesson,
        "course_progress": get_course_progress(course),
    }
    return render_template("partials/course/_lesson_detail.html", **data)
