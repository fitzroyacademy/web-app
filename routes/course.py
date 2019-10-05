from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import (
    abort,
    Blueprint,
    render_template,
    request,
    redirect,
    jsonify,
    make_response,
)

import datamodels
from routes.decorators import login_required, teacher_required
from routes.utils import generate_thumbnail

blueprint = Blueprint("course", __name__, template_folder="templates")


@blueprint.route("/")
def index():
    """ Shows all courses the user has access to. """
    data = {"public_courses": datamodels.get_public_courses()}
    return render_template("welcome.html", **data)


@blueprint.route("/<slug>")
def view(slug):
    """
    Retrieves and displays a course based on course slug.
    """

    # ToDo: handle accessing course that requires login
    # ToDo: course that do not have lessons will raise exception

    course = datamodels.get_course_by_slug(slug)
    if course is None:
        return redirect("/404")
    return render_template("course_intro.html", course=course)


@blueprint.route("/code", methods=["GET", "POST"])
def code():
    error = None
    if request.method == "POST":
        c = datamodels.get_course_by_code(request.form["course_code"])
        if c is None:
            error = "Course not found."
        else:
            return redirect(c.permalink)
    if request.method == "GET" or error:
        data = {"errors": [error]}
        return render_template("code.html", **data)


@blueprint.route("/<course_slug>/edit", methods=["GET", "POST"])
@login_required
def edit(user, course_slug=None):
    """
    Either retrieve a course edit view for a course given by course_slug parameter or edit a course via Ajax requests.

    :param user: a User instance passed by decorator
    :param course_slug: a unique course
    :return: html response for GET method and json response for POST
    """
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    db = datamodels.get_session()
    if request.method == "POST":
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
                amount = Decimal(request.form["amount"])
            except InvalidOperation:
                return (
                    jsonify(
                        {"success": False, "message": "Amount is not a valid number"}
                    ),
                    400,
                )

            course.amount = amount
        if "skill_level" in request.form:
            course.skill_level = request.form["skill_level"]
        if "workload_summary" in request.form:
            course.workload_summary = request.form["workload_summary"]
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
                    jsonify(
                        {"success": False, "message": "Use different course code."}
                    ),
                    400,
                )
            course.course_code = request.form["course_code"]
        if "cover_image" in request.form:
            file = request.files["file"]

            filename = generate_thumbnail(file, "cover")
            if not filename:
                return (
                    jsonify(
                        {
                            "success": False,
                            "message": "Couldn't upload picture. Try again or use different file format",
                        }
                    ),
                    400,
                )

            course.cover_image = filename

        db.add(course)
        db.commit()

        return jsonify({"success": True})

    data = {
        "course": course,
        "teachers": course.instructors,
        "introduction": course.intro_lesson,
        "lessons": course.normal_lessons,
        "cover_image": "/uploads/{}".format(course.cover_image)
        if course.cover_image and not course.cover_image.startswith("http")
        else course.cover_image,
    }

    return render_template("course_edit.html", **data)


@blueprint.route("/<course_slug>/edit/slug", methods=["POST"])
@login_required
def change_course_slug(user, course_slug=None):
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    db = datamodels.get_session()
    if request.method == "POST":
        if "course_slug" in request.form:
            c = datamodels.Course.find_by_slug(request.form["course_slug"])
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
            if not request.form["course_slug"]:
                return (
                    jsonify({"success": False, "message": "Slug can't be empty"}),
                    400,
                )
            course.slug = request.form["course_slug"]
            db.add(course)
            db.commit()

    return jsonify({"slug": course.slug})


@blueprint.route(
    "/<course_slug>/edit/remove/teacher/<int:teacher_id>", methods=["POST"]
)
@login_required
def remove_teacher(user, course_slug=None, teacher_id=None):
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


@blueprint.route("/<course_slug>/edit/add/teacher", methods=["POST"])
@login_required
def add_teacher(user, course_slug=None):
    course = datamodels.get_course_by_slug(course_slug)

    if not course or not user.teaches(course):
        raise abort(404, "No such course or you don't have permissions to edit it")

    new_teacher = datamodels.User.find_by_email(request.form["teacher_email"]) if "teacher_email" \
                                                                                  in request.form else None
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
            "teacher": {
                "id": new_teacher.id,
                "picture": new_teacher.profile_picture,
                "first_name": new_teacher.first_name,
                "last_name": new_teacher.last_name,
                "slug": course.slug,
            },
        }
    )


@blueprint.route("/<course_slug>/edit/options/<option>/<on_or_off>", methods=["POST"])
@login_required
@teacher_required
def set_options(user, course, course_slug=None, option=None, on_or_off=False):
    """ Set course options. """

    if option not in ["draft", "guest_access", "paid", "visibility"]:
        return jsonify({"success": False, "message": "Unknown option setting."}), 400

    if on_or_off in ["ON", "on", "draft", "paid"]:
        value = True
    elif on_or_off in ["OFF", "off", "live", "free"]:
        value = False
    elif on_or_off in ["public", "code", "institute"] and option == "visibility":
        value = on_or_off
    else:
        return jsonify({"success": False, "message": "Unknown option setting."}), 400

    setattr(course, option, value)

    db = datamodels.get_session()
    db.add(course)
    db.commit()

    return jsonify({"success": True})
