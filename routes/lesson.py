from flask import Blueprint, render_template, request, redirect, jsonify, flash, abort
from slugify import slugify

import datamodels
import stubs
from dataforms import AddLessonForm
from enums import ResourceTypeEnum, RESOURCE_CONTENT_IMG
from routes.decorators import login_required, teacher_required
from routes.utils import generate_thumbnail, reorder_items

blueprint = Blueprint("lesson", __name__, template_folder="templates")


@blueprint.route("/lessons")
def lessons():
    return render_template("lesson_chart.html") @ blueprint.route(
        "/<slug>/lessons/reorder", methods=["GET", "POST"]
    )


@blueprint.route("/<course_slug>/lessons/reorder", methods=["POST"])
@login_required
@teacher_required
def reorder_lessons(user, course, course_slug=None):
    return reorder_items(request, datamodels.Lesson, course.lessons)


@blueprint.route("/<course_slug>/lessons/add", methods=["GET", "POST"])
@login_required
@teacher_required
def course_add_lesson(user, course, course_slug):
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
        else:
            for error in form.errors:
                flash(error)
            return redirect("/course/{}/edit".format(course.slug))

    data = {"course": course, "form": form}
    return render_template("partials/course/_lesson.html", **data)


@blueprint.route("/<course_slug>/lessons/<int:lesson_id>/edit", methods=["GET", "POST"])
@login_required
@teacher_required
def course_edit_lesson(user, course, course_slug, lesson_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        raise abort(404, "No such lesson")

    form = AddLessonForm(request.form, lesson)
    data = {
        "course": course,
        "lesson": lesson,
        "form": form,
        "introduction": lesson.intro_segment,
        "resources": lesson.ordered_resources,
        "teachers": [obj.user for obj in lesson.teachers],
        "segments": lesson.normal_segments,
        "resource_types": {r.name: r.value for r in ResourceTypeEnum},
        "resource_images": RESOURCE_CONTENT_IMG,
    }
    return render_template("partials/course/_lesson.html", **data)


@blueprint.route("/<course_slug>/lessons/<int:lesson_id>/delete", methods=["POST"])
@login_required
@teacher_required
def course_delete_lesson(user, course, course_slug, lesson_id):

    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)
    if lesson:
        db = datamodels.get_session()
        db.delete(lesson)
        db.commit()

        list_of_lessons = [l.id for l in datamodels.Lesson.get_ordered_items()]
        if list_of_lessons:
            datamodels.Lesson.reorder_items(list_of_lessons)

        return jsonify({"success_url": "/course/{}/edit".format(course_slug)})

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


@blueprint.route("/<course_slug>/lessons/<int:lesson_id>/add/teacher", methods=["POST"])
@login_required
@teacher_required
def add_teacher(user, course, course_slug, lesson_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"success": False, "message": "Wrong lesson or course"}), 400

    new_teacher = (
        datamodels.User.find_by_email(request.form["teacher_email"])
        if "teacher_email" in request.form
        else None
    )

    if not new_teacher:
        return (
            jsonify({"success": False, "message": "Can't find that email sorry!"}),
            400,
        )

    if new_teacher.id in [teacher.id for teacher in lesson.teachers]:
        return (jsonify({"success": False, "message": "Teacher already added"}), 400)

    enrolment = datamodels.CourseEnrollment.find_by_course_and_student(
        course.id, new_teacher.id
    )

    if enrolment.access_level not in [
        datamodels.COURSE_ACCESS_ADMIN,
        datamodels.COURSE_ACCESS_TEACHER,
    ]:
        return (jsonify({"success": False, "message": "User must be a teacher"}), 400)

    lesson.teachers.append(enrolment)
    db = datamodels.get_session()
    db.add(lesson)
    db.commit()

    return jsonify(
        {
            "success": True,
            "message": "Successfully added!",
            "teacher": {
                "id": new_teacher.id,
                "picture": new_teacher.profile_picture,
                "first_name": new_teacher.first_name,
                "last_name": new_teacher.last_name,
                "slug": course.slug,
            },
        }
    )


@blueprint.route(
    "/<course_slug>/lessons/<int:lesson_id>/remove/teacher/<int:teacher_id>",
    methods=["POST"],
)
@login_required
@teacher_required
def remove_teacher(user, course, course_slug, lesson_id, teacher_id):
    lesson = datamodels.Lesson.find_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"success": False, "message": "Wrong lesson or course"}), 400

    if not datamodels.get_user(teacher_id):
        return jsonify({"success": False, "message": "No such teacher"}), 400

    removed = lesson.remove_teacher(teacher_id)

    return jsonify(
        {"success": removed, "teacher_id": teacher_id, "message": "Teacher removed"}
    )
