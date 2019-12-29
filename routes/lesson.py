from uuid import uuid4

from flask import render_template, request, redirect, jsonify, flash, abort
from slugify import slugify

import datamodels
from charts.student_progress import get_course_progress, get_students_progress
from dataforms import AddLessonForm, LessonQAForm, AjaxCSRFTokenForm, AddResourceForm
from datamodels.enums import (
    ResourceTypeEnum,
    RESOURCE_CONTENT_IMG,
    VideoTypeEnum,
    SegmentBarrierEnum,
    CourseAccess,
)
from routes.decorators import login_required, teacher_required, enrollment_required
from routes.utils import reorder_items
from utils.images import generate_thumbnail
from .render_partials import render_question_answer, render_teacher, render_intro
from .blueprint import SubdomainBlueprint

blueprint = SubdomainBlueprint("lesson", __name__, template_folder="templates")


@blueprint.route("/lessons")
def lessons():
    return render_template("lesson_chart.html")


@blueprint.subdomain_route("/<course_slug>/lessons/reorder", methods=["POST"])
@login_required
@teacher_required
def reorder_lessons(user, course, course_slug=None, institute=""):
    return reorder_items(request, datamodels.Lesson, course.lessons)


@blueprint.subdomain_route("/<course_slug>/lessons/add_intro", methods=["POST"])
@login_required
@teacher_required
def course_add_edit_intro_lesson(user, course, course_slug, institute=""):
    form = AjaxCSRFTokenForm(request.form)
    intro_lesson = course.intro_lesson

    if form.validate() and "intro_lesson" in request.form:
        db = datamodels.get_session()

        slug = "intro-lesson"
        if (
            datamodels.get_lesson_by_slugs(course.slug, "intro-lesson") is not None
            and not intro_lesson
        ):
            slug = slug + "-" + str(uuid4())[:3]
        if intro_lesson:
            segment = intro_lesson.intro_segment
            segment.url = request.form["segment_url"]
            html = ""
        else:
            intro_lesson = datamodels.Lesson(
                title="Intro lesson",
                slug=slug,
                description="Intro lesson video",
                order=0,
                course=course,
            )

            db.add(intro_lesson)

            segment = datamodels.Segment(
                lesson=intro_lesson,
                order=0,
                type="video",
                barrier=SegmentBarrierEnum.normal,
                video_type=VideoTypeEnum.standard,
                url=request.form["segment_url"],
                duration_seconds=0,
                slug="intro-segment",
            )
            html = render_intro(segment)

        db.add(segment)
        db.commit()
        return jsonify({"message": "Intro lesson added", "html": html})
    else:
        return jsonify({"message": "Couldn't create intro lesson"}), 400


@blueprint.subdomain_route("/<course_slug>/lessons/add", methods=["POST"])
@login_required
@teacher_required
def add(user, course, course_slug, lesson_id=None, institute=""):
    form = AddLessonForm(request.form)

    if form.validate():
        lesson = datamodels.Lesson(course=course, order=len(course.lessons) + 1)
        lesson.title = form.title.data
        lesson.description = form.description.data
        lesson.slug = slugify(form.title.data)

        db = datamodels.get_session()
        db.add(lesson)
        db.commit()

        return redirect("/course/{}/lessons/{}/edit".format(course.slug, lesson.id))
    else:
        for error in form.errors:
            flash(error)

    return redirect("/course/{}/edit".format(course.slug))


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/edit", methods=["POST"]
)
@login_required
@teacher_required
def edit(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        raise abort(404, "No such lesson")

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

    if "title" in request.form:
        slug = slugify(request.form["title"])
        if datamodels.get_lesson_by_slugs(course_slug, slug) is not None:
            return (
                jsonify({"success": False, "message": "Use different lesson name"}),
                400,
            )
        lesson.title = request.form["title"]
        lesson.slug = slug
    if "description" in request.form:
        lesson.description = request.form["description"]
        if 3 > len(lesson.description) > 140:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Description should be no more than 140 characters.",
                    }
                ),
                400,
            )
    if "further_reading" in request.form:
        lesson.further_reading = request.form["further_reading"]
    if "cover_image" in request.form:
        cover_image = request.files["file"]
        filename = generate_thumbnail(cover_image, "cover")
        lesson.cover_image = filename

    db = datamodels.get_session()
    db.add(lesson)
    db.commit()
    return jsonify({"success": True})


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/edit", methods=["GET"]
)
@login_required
@teacher_required
def retrieve(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if not lesson:
        raise abort(404, "No such lesson")

    form = AddLessonForm(request.form, lesson)

    ordered_questions = datamodels.LessonQA.ordered_items_for_parent(
        parent=lesson, key="lesson_id"
    ).all()

    data = {
        "course": course,
        "lesson": lesson,
        "form": form,
        "introduction": lesson.intro_segment,
        "resources": lesson.ordered_resources,
        "teachers": [
            render_teacher(obj.user, course, lesson) for obj in lesson.teachers
        ],
        "segments": list(lesson.get_ordered_segments())[1:],
        "questions": [
            render_question_answer(course, lesson, question)
            for question in ordered_questions
        ],
        "resource_types": {r.name: r.value for r in ResourceTypeEnum},
        "resource_images": RESOURCE_CONTENT_IMG,
        "ajax_csrf_form": AjaxCSRFTokenForm(),
        "resource_form": AddResourceForm(),
    }

    return render_template("partials/course/_lesson.html", **data)


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/delete", methods=["POST"]
)
@login_required
@teacher_required
def course_delete_lesson(user, course, course_slug, lesson_id, institute=""):

    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)
    if lesson:
        db = datamodels.get_session()
        db.delete(lesson)
        db.commit()

        list_of_lessons = [
            l.id for l in datamodels.Lesson.get_ordered_items() if l.order != 0
        ]
        if list_of_lessons:
            datamodels.Lesson.reorder_items(list_of_lessons)

        return jsonify({"success_url": "/course/{}/edit".format(course_slug)})

    return jsonify({"success": False, "message": "Couldn't delete lesson"}), 400


@blueprint.subdomain_route("<course_slug>/<lesson_slug>")
@enrollment_required
def view(course_slug, lesson_slug, institute=""):
    """
    Retrieves and displays a particular course, with the specified lesson
    and its first segment set to be active.
    """
    lesson = datamodels.get_lesson_by_slugs(course_slug, lesson_slug)
    if lesson is None:
        return redirect("/404")
    course = lesson.course

    segment = lesson.segments[0] if lesson.segments else None
    data = {
        "students": get_students_progress(course),
        "active_lesson": lesson,
        "active_segment": segment,
        "course_progress": get_course_progress(course),
        "course": course,
        "form": AjaxCSRFTokenForm(),  # need to pass this form in case of guest enrolled for a course
    }
    if course is None:
        return redirect("/404")
    return render_template("course.html", **data)


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/teacher/add", methods=["POST"]
)
@login_required
@teacher_required
def add_teacher(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

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
    elif not new_teacher.teaches(course):
        return (
            jsonify({"success": False, "message": "This user is not a teacher."}),
            400,
        )

    if new_teacher.id in [teacher.id for teacher in lesson.teachers]:
        return jsonify({"success": False, "message": "Teacher already added"}), 400

    enrolment = datamodels.CourseEnrollment.find_by_course_and_student(
        course.id, new_teacher.id
    )

    if enrolment.access_level not in [CourseAccess.admin, CourseAccess.teacher]:
        return jsonify({"success": False, "message": "User must be a teacher"}), 400

    lesson.teachers.append(enrolment)
    db = datamodels.get_session()
    db.add(lesson)
    db.commit()

    return jsonify(
        {
            "success": True,
            "message": "Successfully added!",
            "teacher": render_teacher(new_teacher, course, lesson),
        }
    )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/teacher/<int:teacher_id>/delete",
    methods=["POST"],
)
@login_required
@teacher_required
def delete_teacher(user, course, course_slug, lesson_id, teacher_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"success": False, "message": "Wrong lesson or course"}), 400

    if not datamodels.get_user(teacher_id):
        return jsonify({"success": False, "message": "No such teacher"}), 400

    removed = lesson.remove_teacher(teacher_id)

    return jsonify(
        {"success": removed, "teacher_id": teacher_id, "message": "Teacher removed"}
    )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/qa/<int:qa_id>/edit", methods=["POST"]
)
@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/qa/add", methods=["POST"]
)
@login_required
@teacher_required
def add_lesson_qa(user, course, course_slug, lesson_id, qa_id=None, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"message": "CSRF token required"}), 400

    if not lesson:
        return jsonify({"message": "Wrong lesson or course"}), 400

    form = LessonQAForm(data=request.form)

    if form.validate():
        # get instance of LessonQA
        qa = datamodels.LessonQA.find_by_lesson_and_id(lesson_id, qa_id)
        if qa is None and qa_id:
            return jsonify({"message": "Wrong question or lesson"}), 400

        if not qa:
            qa = datamodels.LessonQA(lesson=lesson, order=len(lesson.questions) + 1)

        qa.answer = form.answer.data
        qa.question = form.question.data

        db = datamodels.get_session()
        db.add(qa)
        db.commit()

        return jsonify(
            {
                "message": "Question saved",
                "html": render_question_answer(course, lesson, qa),
            }
        )

    return jsonify({"message": "Error saving questions"}), 400


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/qa/<int:qa_id>/delete", methods=["POST"]
)
@login_required
@teacher_required
def delete_lesson_qa(user, course, course_slug, lesson_id, qa_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"success": False, "message": "Wrong lesson or course"}), 400

    qa = datamodels.LessonQA.find_by_lesson_and_id(lesson_id, qa_id)
    if qa is None and qa_id:
        return jsonify({"success": False, "message": "Wrong question or lesson"}), 400

    datamodels.LessonQA.delete(qa, lesson, "lesson_id")

    return jsonify(
        {
            "success": True,
            "message": "Question deleted",
            "success_url": "/course/{}/lessons/{}/edit".format(course_slug, lesson_id),
        }
    )


@blueprint.subdomain_route(
    "/<course_slug>/lessons/<int:lesson_id>/qa/reorder", methods=["POST"]
)
@login_required
@teacher_required
def reorder_lesson_qa(user, course, course_slug, lesson_id, institute=""):
    lesson = datamodels.Course.find_lesson_by_course_slug_and_id(course.slug, lesson_id)

    if not lesson:
        return jsonify({"success": False, "message": "Wrong lesson or course"}), 400
    return reorder_items(request, datamodels.LessonQA, lesson.questions)
