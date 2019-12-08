from uuid import uuid4

from flask import render_template, request, jsonify, redirect, flash, abort
from slugify import slugify

import datamodels
from dataforms import AjaxCSRFTokenForm
from enums import SegmentPermissionEnum, VideoTypeEnum
from utils import stubs
from .decorators import login_required, teacher_required, enrollment_required
from .blueprint import SubdomainBlueprint
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
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)
    if segment and lesson and segment.lesson_id == lesson_id:
        db = datamodels.get_session()
        db.delete(segment)
        db.commit()

        list_of_items = [l.id for l in datamodels.Segment.get_ordered_items()]
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
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
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
                "segment_type": segment.type,
                "video_type": segment.video_type.value if segment.video_type else "",
                "permission": segment.permission.value if segment.permission else "",
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
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"message": "Lesson do not match course"}), 400

    slug = "intro-video"

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"message": "Invalid CSRF token"}), 400

    db = datamodels.get_session()

    segment = lesson.intro_segment
    if segment:
        segment.url = request.form["segment_url"]
        db.add(segment)
        db.commit()
        return jsonify({"message": "Intro video updated"})

    segment = datamodels.Segment.find_by_slug(course_slug, lesson.slug, slug)
    if segment and segment.order != 0:
        slug = slug + "-" + uuid4()[:3]

    segment = datamodels.Segment(
        url=request.form["segment_url"],
        type="video",
        video_type=VideoTypeEnum.standard,
        permission=SegmentPermissionEnum.normal,
        duration_seconds=0,
        order=0,
        lesson=lesson,
        slug=slug,
        title="Intro segment",
        text=request.form.get("text_segment_content", "Intro segment video"),
    )

    db.add(segment)
    db.commit()

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
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)

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
            datamodels.Segment.find_by_slug(course.slug, lesson.slug, slug) is None
            or slug == instance.slug
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
                instance.type = "text"
                if not editing:
                    instance.duration_seconds = 0
                instance.permission = SegmentPermissionEnum.normal
            else:
                if "segment_url" not in request.form or not request.form["segment_url"]:
                    return jsonify({"message": "Segment URL is requied"}), 400

                permission = getattr(
                    SegmentPermissionEnum,
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
                instance.type = "video"
                instance.permission = permission
                instance.video_type = video_type

            db.add(instance)
            db.commit()

            response = {
                "message": "Segment {} {}".format(
                    instance.title, "edited" if editing else "added"
                )
            }

            if not editing:
                response["html"] = render_segment_list_element(
                    course=course, lesson=lesson, segment=instance
                )

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
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
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
        and datamodels.Segment.find_by_slug(course.slug, lesson.slug, segment_copy.slug)
        is None
    ):
        db = datamodels.get_session()
        db.add(segment_copy)
        db.commit()

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

    segment = datamodels.get_segment_by_slug(course_slug, lesson_slug, segment_slug)
    if not segment:
        return abort(404)

    course = datamodels.get_course_by_slug(course_slug)
    lesson = datamodels.Lesson.find_by_slug(course_slug, lesson_slug)

    data = {
        "students": stubs.student_completion,
        "active_lesson": lesson,
        "active_segment": segment,
        "course": course,
        "form": AjaxCSRFTokenForm()
    }
    return render_template("course.html", **data)
