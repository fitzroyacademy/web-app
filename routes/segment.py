from flask import Blueprint, render_template, request, jsonify, redirect, flash
from slugify import slugify

import datamodels
import stubs
from .decorators import login_required, teacher_required
from .utils import reorder_items, clone_model
from enums import SegmentPermissionEnum, VideoTypeEnum

blueprint = Blueprint("segment", __name__, template_folder="templates")


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/delete",
    methods=["POST"],
)
@login_required
@teacher_required
def course_delete_segment(user, course, course_slug, lesson_id, segment_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)
    if (
        segment
        and lesson
        and segment.lesson_id == lesson_id
    ):
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


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/reorder", methods=["POST"]
)
@login_required
@teacher_required
def reorder_segments(user, course, course_slug, lesson_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        return jsonify({"succes": False, "message": "Course do not match lesson"}), 400

    return reorder_items(request, datamodels.Segment, lesson.segments)


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/add/<string:content_type>",
    methods=["GET", "POST"],
)
@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/edit/<string:content_type>",
    methods=["GET", "POST"],
)
@login_required
@teacher_required
def add_edit_segment(user, course, course_slug, lesson_id, content_type, segment_id=None):
    if content_type not in ["text", "video", "intro_text", "intro_video"]:
        flash("Wrong action")
        return redirect("/course/{}/edit".format(course.slug))

    template_name = (
        "_video.html" if content_type in ["video", "intro_video"] else "_text.html"
    )
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        flash("Lesson do not match course")
        return redirect("/course/{}/edit".format(course.slug))

    if segment_id:
        instance = datamodels.Segment.find_by_id(segment_id)
        if not instance or instance.lesson_id != lesson.id:
            flash("No such segment for this lesson")
            return redirect("/course/{}/edit".format(course.slug))
    else:
        instance = datamodels.Segment()
        instance.lesson_id = lesson.id

    data = {"course": course, "lesson": lesson, "content_type": content_type}

    if request.method == "POST":
        segment_name = (
            request.form["segment_name"] if "segment_name" in request.form else ""
        )
        slug = slugify(request.form["segment_name"]) if segment_name else None
        db = datamodels.get_session()


        if (
            slug and (datamodels.Segment.find_by_slug(course.slug, lesson.slug, slug) is None or slug == instance.slug)
        ):
            if not instance.id:
                if content_type in ["intro_text", "intro_video"]:
                    if (
                        db.query(datamodels.Segment)
                        .filter(
                            datamodels.Segment.lesson_id == lesson_id,
                            datamodels.Segment.order == 0,
                        )
                        .first()
                    ):
                        flash("Intro segment already exists")
                        return render_template(
                            "partials/course/{}".format(template_name), **data
                        )
                    else:
                        instance.order = 0
                else:
                    instance.order = lesson.get_ordered_segments().count() + 1

            if content_type in ["text", "intro_text"]:
                if (
                    "text_segment_content" not in request.form
                    or not request.form["text_segment_content"]
                ):
                    flash("Segment description is required")
                    return redirect(
                        "/course/{}/lessons/{}/segments/add/{}".format(
                            course.slug, lesson.id, content_type
                        )
                    )

                instance.title = request.form["segment_name"]
                instance.text = request.form["text_segment_content"]
                instance.slug = slug
                instance.type = "text"
                instance.duration_seconds = 0
                instance.permission = SegmentPermissionEnum.normal
            else:
                if "segment_url" not in request.form or not request.form["segment_url"]:
                    flash("Segment URL is required.")
                    return redirect(
                        "/course/{}/lessons/{}/segments/add".format(
                            course.slug, lesson.id
                        )
                    )

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
                instance.url=request.form["segment_url"]
                instance.slug=slug
                instance.type = "video"
                instance.duration_seconds = 0
                instance.permission = permission
                instance.video_type = video_type

            db.add(instance)
            db.commit()

            flash("Segment {} added".format(instance.title))
            return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson.id))
        else:
            flash("Can't create segment with such name.")

    if instance.id:
        data["segment"] = instance
        data["video_type"] = instance.video_type.value if instance.video_type else ''
        data["permission"] = instance.permission.value if instance.permission else ''
    else:
        data["segment"] = None
        data["video_type"] = VideoTypeEnum.standard.value
        data["permission"] = SegmentPermissionEnum.normal.value

    return render_template("partials/course/{}".format(template_name), **data)


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/segments/<int:segment_id>/copy",
    methods=["GET"],
)
@login_required
@teacher_required
def copy_segment(user, course, course_slug, lesson_id, segment_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    segment = datamodels.Segment.find_by_id(segment_id)

    if (
        not lesson
        or segment
        and segment.lesson_id != lesson.id
    ):
        flash("Lesson or segment do not match course or lesson")
        return render_template("/course/{}/edit".format(course.slug), course=course)

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
