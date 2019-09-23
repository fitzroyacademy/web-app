from flask import Blueprint, render_template, request, redirect, jsonify
from slugify import slugify

import datamodels
import stubs
from dataforms import AddLessonForm
from routes.decorators import login_required, teacher_required
from routes.utils import generate_thumbnail, reorder_items

blueprint = Blueprint("lesson", __name__, template_folder="templates")


@blueprint.route("/lessons")
def lessons():
    return render_template("lesson_chart.html") @blueprint.route(
        "/<slug>/lessons/reorder", methods=["GET", "POST"]
    )


@blueprint.route("/<slug>/lessons/reorder", methods=["POST"])
@login_required
@teacher_required
def reorder_lessons(user, course, slug=None):
    return reorder_items(request, datamodels.Lesson, course.lessons)


@blueprint.route("/<slug>/lessons/add", methods=["GET", "POST"])
@login_required
@teacher_required
def course_add_lesson(user, course, slug):
    form = AddLessonForm(request.form)
    if request.method == "POST":
        if form.validate():
            lesson = datamodels.Lesson(
                title=form.title.data,
                description=form.description.data,
                course=course,
                slug=slugify(form.title.data),
            )

            lesson.order = len(course.lessons)

            if "cover_image" in request.files:
                cover_image = request.files["cover_image"]
                filename = generate_thumbnail(cover_image, "cover")
                lesson.cover_image = filename

            db = datamodels.get_session()
            db.add(lesson)
            db.commit()

            return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson.id))

    data = {"course": course, "form": form}
    return render_template("partials/course/_lesson.html", **data)


@blueprint.route("/<slug>/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def course_edit_lesson(user, course, slug, lesson_id):
    lesson = datamodels.Lesson.find_by_id(lesson_id)
    form = AddLessonForm(request.form, lesson)
    data = {
        "course": course,
        "lesson": lesson,
        "form": form,
        "introduction": lesson.intro_segment,
        "segments": lesson.normal_segments,
    }
    return render_template("partials/course/_lesson.html", **data)


@blueprint.route("/<slug>/lessons/<int:lesson_id>/delete", methods=["POST"])
@login_required
@teacher_required
def course_delete_lesson(user, course, slug, lesson_id):

    lesson = datamodels.Lesson.find_by_id(lesson_id)
    if lesson and lesson.course_id == course.id:
        db = datamodels.get_session()
        db.delete(lesson)
        db.commit()

        list_of_lessons = [l.id for l in datamodels.Lesson.get_ordered_items()]
        if list_of_lessons:
            datamodels.Lesson.reorder_items(list_of_lessons)

        return jsonify({"success_url": "/course/{}/edit".format(slug)})

    return jsonify({"success": False, "message": "Couldn't delete lesson"}), 400


@blueprint.route("<course_slug>/<lesson_slug>")
def view(course_slug, lesson_slug):
    """
    Retrieves and displays a particular course, with the specified lesson
    and its first segment set to be active.
    """
    lesson = datamodels.get_lesson_by_slug(course_slug, lesson_slug)
    if lesson is None:
        return redirect("/404")
    course = lesson.course
    segment = lesson.segments[0]
    data = {
        "students": stubs.student_completion,
        "active_lesson": lesson,
        "active_segment": segment,
        "course": course,
    }
    if course is None:
        return redirect("/404")
    return render_template("course.html", **data)
