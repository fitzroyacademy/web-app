from uuid import uuid4

from slugify import slugify
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
    current_app,
    jsonify,
    abort
)

import datamodels
from enums import InstitutePermissionEnum
from dataforms import AddInstituteForm, AjaxCSRFTokenForm
from routes.decorators import login_required
from routes.utils import generate_thumbnail
from routes.render_partials import render_teacher

blueprint = Blueprint("institute", __name__, template_folder="templates")


@blueprint.route("/add", methods=["GET", "POST"])
@login_required
def add(user):

    form = AddInstituteForm(request.form)
    data = {"form": form}

    if not user.super_admin:
        flash("You are not authorized to access this page.")
        return redirect("/")

    if request.method == "POST":
        if form.validate():
            slug = slugify(form.name.data)

            if datamodels.Institute.find_by_slug(slug):
                slug = slug[:46] + "-" + str(uuid4())[:3]

            institute = datamodels.Institute(
                name=form.name.data,
                description=form.description.data,
                slug=slug
            )

            if "cover_image" in request.files:
                file = request.files["cover_image"]

                filename = generate_thumbnail(file, "cover")
                if not filename:
                    flash("Couldn't save cover image")
                else:
                    institute.cover_image = filename

            db = datamodels.get_session()
            db.add(institute)
            institute.add_admin(user)
            db.commit()

            if request.url.startswith("https"):
                protocol = "https"
            else:
                protocol = "http"

            return redirect("{}://{}.{}/institute/edit".format(protocol, current_app.config["SERVER_NAME"], slug))
        else:
            for key, value in form.errors.items():
                flash("Field {}: {}".format(key, ",".join(value)))
            data["errors"] = form.errors
    return render_template("partials/institute/_add.html", **data)


@blueprint.route("/edit", methods=["GET"], subdomain="<institute>")
@login_required
def retrieve(user, institute=""):

    institute = datamodels.Institute.find_by_slug(institute)

    data = {"form": AjaxCSRFTokenForm,
            "institute": institute,
            "teachers": [render_teacher(obj, institute=institute) for obj in institute.teachers],
            "admins": [render_teacher(obj, institute=institute, user_type="admin") for obj in institute.admins],
            "managers": [render_teacher(obj, institute=institute, user_type="manager") for obj in institute.managers],
            }

    return render_template("institute.html", **data)


@blueprint.route("/edit", methods=["POST"], subdomain="<institute>")
@login_required
def edit(user, institute=""):
    pass



@blueprint.route(
    "/edit/user/remove/<int:user_id>/<access_type>", methods=["POST"], subdomain="<institute>"
)
@login_required
def remove_user(user, user_id=None, access_type="teacher", institute=""):

    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or not user.super_admin or institute.is_admin(user):
        raise abort(404, "No such institute or you don't have permissions to edit it")

    if user.id == user_id and access_type == InstitutePermissionEnum.admin.name:
        return jsonify({"success": False, "message": "You can't remove yourself from an admin role"}), 400

    user_to_remove = datamodels.get_user(user_id)
    if not user_to_remove:
        return jsonify({"success": False, "message": "No such user"}), 400


    removed = institute.remove_user(user_to_remove, access_type)

    return jsonify(
        {"success": removed, "teacher_id": user_id, "message": "User removed from role {}".format(access_type)}
    )


@blueprint.route("/edit/add/<access_level>", methods=["POST"], subdomain="<institute>")
@login_required
def add_user(user, institute="", access_level="teacher"):
    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or not user.super_admin or institute.is_admin(user):
        raise abort(404, "No such institute or you don't have permissions to edit it")

    new_user = (
        datamodels.User.find_by_email(request.form["teacher_email"])
        if "teacher_email" in request.form
        else None
    )
    if not new_user:
        return (
            jsonify({"success": False, "message": "Can't find that email sorry!"}),
            400,
        )

    access_level = getattr(InstitutePermissionEnum, access_level, None)

    if access_level is None:
        return (
            jsonify({"success": False, "message": "Wrong access level for a user"}),
            400,
        )

    users_with_given_access_level = getattr(institute, "{}s".format(access_level.name))

    if new_user.id in [user.id for user in users_with_given_access_level]:
        return (
            jsonify({"success": False, "message": "That user is already a teacher"}),
            400,
        )

    institute.add_user(new_user, access_level)

    return jsonify(
        {
            "success": True,
            "message": "Successfully added!",
            "teacher": render_teacher(new_user, institute=institute, user_type=access_level.name),
        }
    )