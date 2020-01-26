from uuid import uuid4

from datetime import datetime

from slugify import slugify
from flask import (
    abort,
    render_template,
    request,
    redirect,
    jsonify,
    make_response,
    flash,
)

from utils.base import get_current_user
from routes.blueprint import SubdomainBlueprint

import datamodels
from dataforms import AddCourseForm, AjaxCSRFTokenForm, LoginForm, AddLessonForm
from routes.decorators import login_required, teacher_required
from utils.images import generate_thumbnail

from routes.render_partials import render_teacher

blueprint = SubdomainBlueprint("course", __name__, template_folder="templates")


@blueprint.subdomain_route("/", methods=["GET"])
def index(institute=""):
    """ Shows all courses the user has access to. """
    data = {
        "public_courses": datamodels.list_public_courses(institute_slug=institute),
        "form": LoginForm(),
    }

    return render_template("welcome.html", **data)


@blueprint.subdomain_route("/<slug>")
def view(slug, institute=""):
    """
    Retrieves and displays a course based on course slug.
    """

    course = datamodels.get_course_by_slug(slug)
    user = get_current_user()
    if course is None or course.draft and not (user and user.teaches(course)):
        return redirect("/404")
    elif course.draft and len(course.lessons) == 0:
        return redirect("/course/{}/edit".format(course.slug))
    return render_template(
        "course_intro.html",
        course=course,
        form=LoginForm(),
        number_of_resources=course.number_of_resources,
    )


@blueprint.subdomain_route("/code", methods=["GET", "POST"])
def code(institute=""):
    error = None
    if request.method == "POST":
        c = datamodels.get_course_by_code(request.form["course_code"])
        user = get_current_user()
        if c is None or c.draft and not (user and user.teaches(c)):
            error = "Course not found."
        else:
            return redirect(c.permalink)
    if request.method == "GET" or error:
        data = {"errors": [error], "form": LoginForm()}
        return render_template("code.html", **data)


@blueprint.subdomain_route("/add", methods=["POST"])
@login_required
def add_course(user, institute=""):  # ToDo: use Ajax
    """
    Add a new course for a given institute given by institute parameter derived from subdomain

    :param user: a User instance passed by decorator
    :param institute: an institute subdomain
    :return: html response
    """
    form = AddCourseForm(request.form)

    if institute:
        institute = datamodels.Institute.find_by_slug(institute)

    if form.validate():
        slug = slugify(form.title.data)

        if datamodels.Course.find_by_slug(slug):
            slug = slug[:46] + "-" + str(uuid4())[:3]

        course = datamodels.Course()
        course.title = form.title.data
        course.info = form.info.data
        course.institute = institute or None
        course.course_code = str(uuid4())[:8]
        course.slug = slug
        course.save()
        course.add_instructor(user)

        return redirect("/course/{}/edit".format(slug))
    else:
        for key, value in form.errors.items():
            flash("Field {}: {}".format(key, ",".join(value)))
        return redirect("/")


@blueprint.subdomain_route("/<course_slug>/edit", methods=["POST"])
@login_required
def edit(user, course_slug=None, institute=""):
    """
    Edit a course via Ajax requests.

    :param user: a User instance passed by decorator
    :param course_slug: a unique course
    :param institute: an institute subdomain
    :return: json response
    """
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    if institute:
        institute = datamodels.Institute.find_by_slug(institute)

    db = datamodels.get_session()

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

    if "year" in request.form:
        try:
            year = int(request.form["year"])
        except ValueError:
            return make_response(
                jsonify({"success": False, "message": "Year must be a number"}), 400
            )
        course_year = datetime(year=year, month=12, day=31).date()
        course.year = course_year
    if "amount" in request.form:
        try:
            amount = int(float(request.form["amount"]) * 100)
        except ValueError:
            return (
                jsonify({"success": False, "message": "Amount is not a valid number"}),
                400,
            )

        course.amount = amount
    if "skill_level" in request.form:
        course.skill_level = request.form["skill_level"]
    if "workload_summary" in request.form:
        course.workload_summary = request.form["workload_summary"]
    if "workload_title" in request.form:
        course.workload_title = request.form["workload_title"]
    if "workload_subtitle" in request.form:
        course.workload_subtitle = request.form["workload_subtitle"]
    if "who_its_for" in request.form:
        course.target_audience = request.form["who_its_for"]
    if "course_summary" in request.form:
        course.summary_html = request.form["course_summary"]
    if "course_name" in request.form:
        course.title = request.form["course_name"]
    if "course_description" in request.form:
        course.info = request.form["course_description"]
    if "course_code" in request.form:
        c = datamodels.Course.find_by_code(request.form["course_code"])
        if c and course.id != c.id:
            return make_response(
                jsonify({"success": False, "message": "Use different course code."}),
                400,
            )
        course.course_code = request.form["course_code"]
    if "cover_image" in request.form:
        file = request.files["file"]

        try:
            filename = generate_thumbnail(file, "cover")
        except ValueError as e:
            return jsonify({"success": False, "message": str(e)}), 400

        course.cover_image = filename

    db.add(course)
    db.commit()

    return jsonify({"success": True})


@blueprint.subdomain_route("/<course_slug>/edit", methods=["GET"])
@login_required
def retrieve(user, course_slug=None, institute=""):
    """
    Retrieve a course edit view for a course given by course_slug parameter.

    :param user: a User instance passed by decorator
    :param course_slug: a unique course
    :param institute: an institute subdomain
    :return: html response
    """
    course = datamodels.get_course_by_slug(course_slug)
    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    data = {
        "course": course,
        "teachers": [render_teacher(obj, course) for obj in course.instructors],
        "introduction": course.intro_lesson,
        "lessons": course.normal_lessons,
        "form": AjaxCSRFTokenForm(),
        "cover_image": course.cover_image_url,
        "add_lesson_form": AddLessonForm(),
    }

    return render_template("course_edit.html", **data)


@blueprint.subdomain_route("/<course_slug>/delete", methods=["POST"])
@login_required
@teacher_required
def delete(user, course, course_slug, institute=""):
    course.delete()
    flash("Course {} deleted".format(course.title))
    return redirect("/")


@blueprint.subdomain_route("/<course_slug>/edit/slug", methods=["POST"])
@login_required
def change_course_slug(user, course_slug=None, institute=""):
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

    db = datamodels.get_session()
    if request.method == "POST":
        if "slug" in request.form:
            slug = request.form["slug"]
            c = datamodels.Course.find_by_slug(slug)
            if c and course.id != c.id:
                return make_response(
                    jsonify(
                        {
                            "success": False,
                            "message": "Use different slug for this course.",
                        }
                    ),
                    400,
                )
            if not slug:
                return (
                    jsonify({"success": False, "message": "Slug can't be empty"}),
                    400,
                )
            course.slug = slug
            db.add(course)
            db.commit()

    return jsonify({"redirect_url": "/course/{}/edit".format(course.slug)})


@blueprint.subdomain_route(
    "/<course_slug>/edit/remove/teacher/<int:teacher_id>", methods=["POST"]
)
@login_required
def remove_teacher(user, course_slug=None, teacher_id=None, institute=""):
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    if user.id == teacher_id:
        return jsonify({"success": False, "message": "You can't remove yourself"}), 400

    if not datamodels.get_user(teacher_id):
        return jsonify({"success": False, "message": "No such teacher"}), 400

    removed = course.remove_teacher(teacher_id)

    return jsonify(
        {"success": removed, "teacher_id": teacher_id, "message": "Teacher removed"}
    )


@blueprint.subdomain_route("/<course_slug>/edit/add/teacher", methods=["POST"])
@login_required
def add_teacher(user, course_slug=None, institute=""):
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

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

    if new_teacher.id in [teacher.id for teacher in course.instructors]:
        return (
            jsonify({"success": False, "message": "That user is already a teacher"}),
            400,
        )

    course.add_instructor(new_teacher)

    return jsonify(
        {
            "success": True,
            "message": "Successfully added!",
            "teacher": render_teacher(new_teacher, course),
        }
    )


@blueprint.subdomain_route(
    "/<course_slug>/edit/options/<option>/<on_or_off>", methods=["POST"]
)
@login_required
@teacher_required
def set_options(
    user, course, course_slug=None, option=None, on_or_off=False, institute=""
):
    """ Set course options. """
    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    value = None

    if option == "draft":
        if on_or_off == "live" and len(course.lessons) == 0:
            return jsonify({"success": False, "message": "Add lessons first."}), 400
        value = on_or_off == "draft"
    elif option in ["guest_access", "paid"]:
        value = on_or_off in ["ON", "on", "paid"]
    elif option == "visibility" and on_or_off in ["public", "code", "institute"]:
        value = on_or_off

    if value is None:
        return jsonify({"success": False, "message": "Unknown option setting."}), 400

    setattr(course, option, value)

    db = datamodels.get_session()
    db.add(course)
    db.commit()

    return jsonify({"success": True})
