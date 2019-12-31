from uuid import uuid4

from flask import render_template, request, jsonify, redirect, flash, abort
from slugify import slugify
from sqlalchemy.exc import IntegrityError

import datamodels
from charts.student_progress import get_course_progress, get_students_progress
from dataforms import AjaxCSRFTokenForm
from datamodels.enums import SegmentBarrierEnum, VideoTypeEnum, SegmentType
from .blueprint import SubdomainBlueprint
from .decorators import login_required, teacher_required, enrollment_required
from .render_partials import render_intro, render_segment_list_element
from .utils import reorder_items, clone_model, retrieve_wistia_id

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
            l.id for l in datamodels.Segment.get_ordered_items() if l.order != 0
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
        return jsonify(
            {
                "segment_url": segment.url,
                "segment_type": segment.type.name,
                "video_type": segment.video_type.value if segment.video_type else "",
                "permission": segment.barrier.value if segment.barrier else "",
                "title": segment.title,
                "text": segment.text,
            }
        )

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

    slug = "intro-video"

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"message": "Invalid CSRF token"}), 400

    segment = lesson.intro_segment
    if segment:
        segment.url = request.form["segment_url"]
        segment.save()
        return jsonify({"message": "Intro video updated"})

    segment = datamodels.find_segment_by_slugs(course_slug, lesson.slug, slug)
    if segment and segment.order != 0:
        slug = slug + "-" + uuid4()[:3]

    segment = datamodels.Segment(
        url=request.form["segment_url"],
        type=SegmentType.video,
        video_type=VideoTypeEnum.standard,
        barrier=SegmentBarrierEnum.normal,
        duration_seconds=0,
        order=0,
        lesson=lesson,
        slug=slug,
        title="Intro segment",
        text=request.form.get("text_segment_content", "Intro segment video"),
    )

    segment.save()

    return jsonify({"message": "Intro video added.", "html": render_intro(segment)})


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
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson do not match course"}), 400

    if segment_id:
        instance = datamodels.Segment.find_by_id(segment_id)
        if not instance or instance.lesson_id != lesson.id:
            return jsonify({"message": "No such segment for this lesson"}), 400
        editing = True
        content_type = instance.type
    else:
        instance = datamodels.Segment()
        instance.lesson_id = lesson.id
        editing = False

    if content_type not in ["text", "video", "intro_video"]:
        return jsonify({"message": "Wrong action"}), 400

    if request.method == "POST":
        segment_name = (
            request.form["segment_name"] if "segment_name" in request.form else ""
        )
        slug = slugify(request.form["segment_name"]) if segment_name else None
        db = datamodels.get_session()

        if slug and (
            datamodels.find_segment_by_slugs(course.slug, lesson.slug, slug) is None
            or slug == instance.slug
            or editing
        ):
            if not editing:
                if content_type in ["intro_text", "intro_video"]:
                    if (
                        db.query(datamodels.Segment)
                        .filter(
                            datamodels.Segment.lesson_id == lesson_id,
                            datamodels.Segment.order == 0,
                        )
                        .first()
                    ):
                        return jsonify({"message": "Intro segment already exists"}), 400
                    else:
                        instance.order = 0
                else:
                    instance.order = lesson.get_ordered_segments().count() + 1

            if content_type in ["text", "intro_text"]:
                if (
                    "text_segment_content" not in request.form
                    or not request.form["text_segment_content"]
                ):
                    return jsonify({"message": "Segment description is required"}), 400

                instance.title = request.form["segment_name"]
                instance.text = request.form["text_segment_content"]
                instance.slug = slug
                instance.type = SegmentType.text
                if not editing:
                    instance.duration_seconds = 0
                instance.barrier = SegmentBarrierEnum.normal
            else:
                if "segment_url" not in request.form or not request.form["segment_url"]:
                    return jsonify({"message": "Segment URL is requied"}), 400

                barrier = getattr(
                    SegmentBarrierEnum,
                    request.form.get("permissions", "normal"),
                    "normal",
                )
                video_type = getattr(
                    VideoTypeEnum,
                    request.form.get("video_types", "standard"),
                    "standard",
                )

                # ToDo: validate URL
                instance.title = request.form["segment_name"]
                instance.url = request.form["segment_url"]
                if "wistia.com" in instance.url:
                    instance.external_id = retrieve_wistia_id(instance.url)
                    instance.set_duration()
                elif "youtube.com" in instance.url:
                    instance.duration_seconds = 0
                else:
                    return jsonify({"message": "Wrong video provider"}), 400
                instance.slug = slug
                instance.type = SegmentType.video
                instance.barrier = barrier
                instance.video_type = video_type

            db.add(instance)
            try:
                db.commit()
            except IntegrityError:
                db.rollback()
                return (
                    jsonify({"message": "Chose different name for this segment."}),
                    400,
                )

            response = {
                "message": "Segment {} {}".format(
                    instance.title, "edited" if editing else "added"
                ),
                "html": render_segment_list_element(
                    course=course, lesson=lesson, segment=instance
                ),
                "id": instance.id,
            }

            return jsonify(response), 200
        else:
            return jsonify({"message": "Can't create segment with such name."}), 400

    return jsonify({"message": "Oh snap..."})


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


@blueprint.subdomain_route(
    "<course_slug>/<lesson_slug>/<segment_slug>", methods=["GET"]
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
        "course_progress": get_course_progress(lesson.course),
        "course": course,
        "form": AjaxCSRFTokenForm(),
    }
    return render_template("course.html", **data)
