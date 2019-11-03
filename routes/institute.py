from uuid import uuid4

from slugify import slugify
from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    flash,
)

import datamodels
from dataforms import AddInstituteForm
from routes.decorators import login_required
from routes.utils import generate_thumbnail

blueprint = Blueprint("institute", __name__, template_folder="templates")


@blueprint.route("/add", methods=["GET", "POST"])
@login_required
def add_institute(user):

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

            return redirect("/institute/edit".format(slug))
        else:
            for key, value in form.errors.items():
                flash("Field {}: {}".format(key, ",".join(value)))
            data["errors"] = form.errors
    return render_template("partials/institute/_add.html", **data)
