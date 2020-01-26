from uuid import uuid4

from flask import request, jsonify, redirect, flash
from slugify import slugify
from wtforms.validators import ValidationError

import datamodels
from dataforms import AjaxCSRFTokenForm, AddSegmentForm
from datamodels.enums import SegmentBarrierEnum, VideoTypeEnum, SegmentType
from .blueprint import SubdomainBlueprint
from .decorators import login_required, teacher_required
from .render_partials import (
    render_intro,
    render_segment_list_element,
    render_segment_modal,
)
from .utils import (
    reorder_items,
    clone_model,
    set_segment_video_url,
    SurveyViewInterface,
)

blueprint = SubdomainBlueprint("segment", __name__, template_folder="templates")


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/delete",
    methods=["POST"],
)
@login_required
@teacher_required
def course_delete_segment(
    user, course, course_slug, lesson_id, segment_id, institute=""
):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)
    if segment and lesson and segment.lesson_id == lesson_id:
        db = datamodels.get_session()
        db.delete(segment)
        db.commit()

        list_of_items = [
            l.id for l in lesson.get_ordered_segments() if l.order != 0
        ]  # do not reorder intro segment

        if list_of_items:
            datamodels.Segment.reorder_items(list_of_items)

        return jsonify(
            {"success_url": "/course/{}/lessons/{}/edit".format(course_slug, lesson_id)}
        )

    return jsonify({"success": False, "message": "Couldn't delete segment"}), 400


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/reorder", methods=["POST"]
)
@login_required
@teacher_required
def reorder_segments(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return (
            jsonify({"success": False, "message": "Course does not match lesson"}),
            400,
        )

    return reorder_items(request, datamodels.Segment, lesson.segments)


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>", methods=["GET"]
)
@login_required
@teacher_required
def retrieve(user, course, course_slug, lesson_id, segment_id, institute=""):
    lesson = datamodels.Lesson.find_by_id(lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)

    if lesson and lesson.course_id == course.id and segment.lesson_id == lesson.id:
        data = {
            "segment_url": segment.url,
            "segment_type": segment.type.name,
            "video_type": segment.video_type.value if segment.video_type else "",
            "permission": segment.barrier.value if segment.barrier else "",
            "title": segment.title,
            "text": segment.text,
        }
        if segment.type == SegmentType.survey:
            writer = SurveyViewInterface(survey_type=segment.survey_type.name)
            template = segment.get_questions_template()
            data["survey_type"] = segment.survey_type.name
            data["survey_id"] = template["survey_id"]
            data["survey"] = writer.serialize_survey_data_for_view(template)
        return jsonify(data)

    return jsonify({"message": "Segment doesn't match a course lesson."}), 400


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/add/intro_video", methods=["POST"]
)
@login_required
@teacher_required
def add_edit_intro_segment(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return jsonify({"message": "Lesson do not match course"}), 400

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"message": "Invalid CSRF token"}), 400

    slug = "intro-video"

    instance = lesson.intro_segment
    editing = instance is not None
    if not instance:
        instance = datamodels.Segment(
            url=request.form["segment_url"],
            type=SegmentType.video,
            video_type=VideoTypeEnum.standard,
            barrier=SegmentBarrierEnum.normal,
            order=0,
            lesson=lesson,
            slug=slug,
            title="Intro segment",
            text=request.form.get("text_segment_content", "Intro segment video"),
        )

    segment = datamodels.find_segment_by_slugs(course_slug, lesson.slug, slug)
    if segment and segment.order != 0:
        instance.slug = slug + "-" + uuid4()[:3]

    try:
        set_segment_video_url(instance, request.form["segment_url"])
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

    instance.save()
    data = {"message": "Intro video updated"}

    if not editing:
        data = {"message": "Intro video added.", "html": render_intro(segment)}

    return jsonify(data)


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<string:content_type>",
    methods=["GET"],
)
@login_required
@teacher_required
def render_segment_content(
    user, course, course_slug, lesson_id, content_type, institute=""
):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return jsonify({"message": "Lesson do not match course"}), 400

    if content_type not in [s.name for s in SegmentType]:
        return jsonify({"message": "Wrong segment type"}), 400

    surveys = datamodels.Segment.list_types_templates()

    return jsonify(
        {"html": render_segment_modal(content_type, course, lesson, surveys)}
    )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/add/<string:content_type>",
    methods=["POST"],
)
@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/edit",
    methods=["POST"],
)
@login_required
@teacher_required
def add_edit_segment(
    user,
    course,
    course_slug,
    lesson_id,
    content_type=None,
    segment_id=None,
    institute="",
):
    if (
        content_type not in ["text", "video", "intro_video", "survey"]
        and not segment_id
    ):
        return jsonify({"message": "Wrong action"}), 400

    form = AddSegmentForm(request.form)
    if not form.validate():
        return jsonify({"message": form.errors}), 400

    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return jsonify({"message": "Lesson do not match course"}), 400

    if segment_id:  # Case of an existing segment
        instance = datamodels.Segment.find_by_id(segment_id)
        if not instance or instance.lesson_id != lesson.id:
            return jsonify({"message": "No such segment for this lesson"}), 400
        content_type = instance.type.name
    else:  # Case of a new segment
        instance = datamodels.Segment()
        instance.lesson_id = lesson.id
        instance.duration_seconds = 0

        if content_type == "intro_video":
            if datamodels.Segment.first(lesson_id=lesson_id, order=0):
                return jsonify({"message": "Intro segment already exists"}), 400
            else:
                instance.order = 0
        else:
            last_segment = lesson.last_child(instance)
            instance.order = last_segment.order + 1 if last_segment else 1

    segment_name = form.segment_name.data
    slug = slugify(segment_name)
    if not (
        slug
        and (
            datamodels.find_segment_by_slugs(course.slug, lesson.slug, slug) is None
            or slug == instance.slug
        )
    ):
        return jsonify({"message": "Can't create segment with such name."}), 400

    barrier = getattr(
        SegmentBarrierEnum, request.form.get("permissions", "normal"), "normal"
    )
    instance.barrier = barrier
    instance.title = request.form["segment_name"]
    instance.slug = slug

    if content_type == "text":
        if (
            "text_segment_content" not in request.form
            or not request.form["text_segment_content"]
        ):
            return jsonify({"message": "Segment description is required"}), 400

        instance.text = request.form["text_segment_content"]
        instance.type = SegmentType.text
    elif content_type in ["video", "video_intro"]:
        if "segment_url" not in request.form or not request.form["segment_url"]:
            return jsonify({"message": "Segment URL is requied"}), 400

        video_type = getattr(
            VideoTypeEnum, request.form.get("video_types", "standard"), "standard"
        )

        try:
            set_segment_video_url(instance, request.form["segment_url"])
        except ValueError as e:
            return jsonify({"message": str(e)}), 400
        instance.type = SegmentType.video
        instance.video_type = video_type
    elif content_type == "survey":
        survey_id = request.form.get("survey_types", None)
        instance.type = SegmentType.survey
        if not survey_id:
            return jsonify({"message": "Survey type not provided."}), 400

        reader = SurveyViewInterface(survey_id=survey_id)
        template = reader.read_questions_template_from_view(data=request.form)
        try:
            instance.save_questions_template(template)
        except (AssertionError, ValueError) as e:
            msg = str(e)
            return jsonify({"message": msg if msg else "Some error occurred"}), 400
    else:
        return jsonify({"message": "Content not supported"}), 400

    try:
        instance.save()
    except ValidationError:
        return jsonify({"message": "Chose different name for this segment."}), 400

    response = {
        "message": "Segment {} {}".format(
            instance.title, "edited" if segment_id else "added"
        ),
        "html": render_segment_list_element(
            course=course, lesson=lesson, segment=instance
        ),
        "id": instance.id,
    }

    return jsonify(response), 200


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/copy",
    methods=["GET"],
)
@login_required
@teacher_required
def copy_segment(user, course, course_slug, lesson_id, segment_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)

    if not lesson or segment and segment.lesson_id != lesson.id:
        flash("Lesson or segment do not match course or lesson")
        return redirect("/course/{}/edit".format(course.slug))

    segment_copy = clone_model(segment)
    segment_copy.title = segment.title + "_copy"
    segment_copy.slug = slugify(segment_copy.title)
    segment_copy.order = lesson.get_ordered_segments().count() + 1

    if (
        segment_copy.slug
        and datamodels.find_segment_by_slugs(
            course.slug, lesson.slug, segment_copy.slug
        )
        is None
    ):

        segment_copy.save()

        flash("Segment duplicated")

    else:
        flash("Segment for this lesson with the same slug already exists")

    return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson_id))
