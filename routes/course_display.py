import json

from flask import render_template, session, abort, request, jsonify

import datamodels
from routes.blueprint import SubdomainBlueprint
from dataforms import AjaxCSRFTokenForm
from charts.student_progress import get_course_progress, get_students_progress
from routes.utils import (
    find_segment_barrier,
    get_session_data,
    set_session_data,
    get_survey_response_for_student,
)
from utils.base import get_current_user
from utils.database import dump
from routes.decorators import enrollment_required

blueprint = SubdomainBlueprint("course_display", __name__, template_folder="templates")


@blueprint.route("/_segment/<segment_id>")
def get_segment_object(segment_id):
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
            survey_response=get_survey_response_for_student(
                current_user, active_segment, session
            ),
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
    return render_template("partials/course/lesson_detail/index.html", **data)


@blueprint.subdomain_route(
    "/course/<course_slug>/<lesson_slug>/<segment_slug>", methods=["GET"]
)
@enrollment_required
def view(course_slug, lesson_slug, segment_slug, institute=""):
    """
    Retrieves and displays a particular course, with the specified lesson
    and segment set to be active.
    """

    segment = datamodels.find_segment_by_slugs(course_slug, lesson_slug, segment_slug)
    if not segment:
        return abort(404)

    course = datamodels.get_course_by_slug(course_slug)
    lesson = datamodels.get_lesson_by_slugs(course_slug, lesson_slug)
    data = {
        "students": get_students_progress(lesson.course),
        "active_lesson": lesson,
        "active_segment": segment,
        "survey_response": get_survey_response_for_student(
            get_current_user(), segment, session
        ),
        "course_progress": get_course_progress(lesson.course),
        "course": course,
        "form": AjaxCSRFTokenForm(),
    }
    return render_template("course.html", **data)


@blueprint.subdomain_route("/course/survey/submit", methods=["POST"])
def submit_segment_survey(institute=""):
    """
    Handle submitting survey by a student.
    """
    segment_id = request.form.get("segment_id", 0)
    segment = datamodels.Segment.find_by_id(segment_id)

    if not segment or segment.type != datamodels.SegmentType.survey:
        return jsonify({"message": "No such survey."}), 400

    free_text = request.form.get("free_text", "")
    chosen_answer = request.form.get("question_id", "")

    survey_response = datamodels.SegmentSurveyResponse(survey=segment)
    user = get_current_user()

    try:
        survey_response_data = survey_response.validate_data(
            free_text=free_text, chosen_answer=chosen_answer
        )
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    if user:
        try:
            survey_response.save_response_for_user(user)
            segment.save_user_progress(user, 100)
        except ValueError:
            return jsonify({"message": "You have already answered this question"}), 400
    else:
        data = get_session_data(session, "anon_surveys")
        data[segment_id] = survey_response_data
        set_session_data(session, "anon_surveys", data)

        data = get_session_data(session, "anon_progress")
        data[segment_id] = 100
        set_session_data(session, "anon_progress", data)

    return jsonify({"message": "Survey response saved"})
