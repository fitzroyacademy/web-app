from uuid import uuid4

from slugify import slugify
from flask import (
    render_template,
    request,
    redirect,
    flash,
    current_app,
    jsonify,
    abort,
    make_response
)

import datamodels
from datamodels.enums import InstitutePermissionEnum
from dataforms import AddInstituteForm, AjaxCSRFTokenForm
from routes.decorators import login_required
from routes.utils import generate_thumbnail
from routes.render_partials import render_teacher
from routes.blueprint import SubdomainBlueprint

blueprint = SubdomainBlueprint("institute", __name__, template_folder="templates")

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

            protocol = "https" if request.url.startswith("https") else "http"

            return redirect("{}://{}.{}/institute/edit".format(protocol, slug, current_app.config["SERVER_NAME"]))
        else:
            for key, value in form.errors.items():
                flash("Field {}: {}".format(key, ",".join(value)))
            data["errors"] = form.errors
    return render_template("partials/institute/_add.html", **data)


@blueprint.subdomain_route("/edit", methods=["GET"])
@login_required
def retrieve(user, institute=""):

    institute = datamodels.Institute.find_by_slug(institute)

    if institute is None:
        flash("No such institute.")
        return redirect('/')

    if not institute.is_admin(user):
        return redirect("/")

    data = {"form": AjaxCSRFTokenForm(),
            "institute": institute,
            "teachers": [render_teacher(obj, institute=institute) for obj in institute.teachers],
            "admins": [render_teacher(obj, institute=institute, user_type="admin") for obj in institute.admins],
            "managers": [render_teacher(obj, institute=institute, user_type="manager") for obj in institute.managers],
            "cover_image": institute.cover_image_url,
            "logo": institute.logo_url
            }

    return render_template("institute.html", **data)


@blueprint.subdomain_route("/edit", methods=["POST"])
@login_required
def edit(user, institute=""):

    if not institute:
        return jsonify({"success": False, "message": "Well, no. You can\'t edit this institute. :)"}), 400

    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or (not user.super_admin and not institute.is_admin(user)):
        raise abort(404, "No such institute or you don't have permissions to edit it")

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

    db = datamodels.get_session()

    if "name" in request.form and request.form["name"] != "":
        institute.name = request.form["name"]
    if "description" in request.form:
        institute.description = request.form["description"]
    if "for_who" in request.form:
        institute.for_who = request.form["for_who"]
    if "location" in request.form:
        institute.location = request.form["location"]
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

        institute.cover_image = filename
    if "logo" in request.form:
        file = request.files["file"]

        filename = generate_thumbnail(file, "square_m")
        if not filename:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Couldn't upload picture. Try again or use different file format",
                    }
                ),
                400
            )

        institute.logo = filename

    db.add(institute)
    db.commit()

    return jsonify({"success": True})


@blueprint.subdomain_route("/edit/user/remove/<int:user_id>/<access_type>", methods=["POST"])
@login_required
def remove_user(user, user_id=None, access_type="teacher", institute=""):

    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or (not user.super_admin and not institute.is_admin(user)):
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


@blueprint.subdomain_route("/edit/add/<access_level>", methods=["POST"])
@login_required
def add_user(user, institute="", access_level="teacher"):
    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or (not user.super_admin and not institute.is_admin(user)):
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

@blueprint.subdomain_route("/edit/slug", methods=["POST"])
@login_required
def change_slug(user, institute=""):
    institute = datamodels.Institute.find_by_slug(institute)

    if not institute or (not user.super_admin and not institute.is_admin(user)):
        raise abort(404, "No such institute or you don't have permissions to edit it")

    if not AjaxCSRFTokenForm(request.form).validate():
        return jsonify({"success": False, "message": "CSRF token required"}), 400

    slug = institute.slug
    db = datamodels.get_session()
    if request.method == "POST":
        if "slug" in request.form:
            slug = request.form["slug"]
            i = datamodels.Institute.find_by_slug(slug)
            if i and institute.id != i.id:
                return make_response(
                    jsonify(
                        {
                            "success": False,
                            "message": "Use different slug for this institute.",
                        }
                    ),
                    400,
                )
            if not slug:
                return (
                    jsonify({"success": False, "message": "Slug can't be empty"}),
                    400,
                )
            institute.slug = slug
            db.add(institute)
            db.commit()

    protocol = "https" if request.url.startswith("https") else "http"

    return jsonify({"redirect_url": "{}://{}.{}/institute/edit".format(protocol, slug, current_app.config["SERVER_NAME"])})
