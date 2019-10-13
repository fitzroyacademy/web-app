import json

from flask import Blueprint, render_template, session, request, url_for, redirect, flash
from sqlalchemy.exc import IntegrityError

import datamodels
from dataforms import AddUserForm, EditUserForm, LoginForm

from util import get_current_user
from .decorators import login_required

blueprint = Blueprint("user", __name__, template_folder="templates")


@blueprint.route("/user/<slug>", methods=["GET"])
def view(slug):
    """ View a user's profile. """
    user_id = slug
    user = datamodels.get_user(user_id)
    data = {"user": user, "form": EditUserForm()}
    return render_template("user.html", **data)


@blueprint.route("/edit", methods=["GET", "POST"])
@blueprint.route("/edit/<slug>", methods=["GET", "POST"])
@login_required
def edit(user, slug=None):
    """
    Edit the current user.
    """

    data = {"errors": []}
    if request.method == "POST":
        form = EditUserForm(request.form)
        if form.validate():
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.username = form.username.data
            if form.password.data:
                setattr(user, "password", form.password.data)

            db = datamodels.get_session()
            try:
                db.add(user)
                db.commit()
            except IntegrityError:
                db.rollback()
                data["errors"] = ["Wrong email address"]
        else:
            data["errors"] = form.errors
    else:
        form = EditUserForm()

    data["form"] = form

    return render_template("user_edit.html", **data)


@blueprint.route("/register", methods=["POST"])
def create():
    """
    Create a new user.
    """
    db = datamodels.get_session()
    # We'll roll in better validation with form error integration in beta; this is
    # to prevent mass assignment vulnerabilities.
    form = AddUserForm(request.form)
    data = {"errors": [], "form": form}

    user = datamodels.get_user_by_email(request.form.get("email"))
    if user is not None:
        data["errors"].append("Email address already in use.")
        return render_template("login.html", **data)

    if form.validate():
        try:
            user = datamodels.User()
            user.email = form.email.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.username = form.username.data
            setattr(user, "password", form.password.data)
        except Exception as e:
            data["errors"].append("{}".format(e))
            return render_template("login.html", **data)
        if "anon_progress" in session:
            d = json.loads(session["anon_progress"])
            user.merge_anonymous_data(d)
            session.pop("anon_progress")
        db.add(user)
        db.commit()
        session["user_id"] = user.id
        flash("Thanks for registering, " + user.full_name + "!")
    else:
        data["errors"] = form.errors
    return redirect(url_for(request.args.get("from", "index")))


@blueprint.route("/enroll/<course_slug>", methods=["POST"])
def enroll(course_slug):
    """
    Enroll a user into a course.
    """
    course = datamodels.get_course_by_slug(course_slug)
    if course is None:
        return redirect("/404")
    user = get_current_user()
    course.enroll(user)
    flash("You are now enrolled in ", course.title)
    return redirect(course.lessons[0].permalink)


@blueprint.route("/login", methods=["GET", "POST"])
def login():
    """ Validiate login and save current user to session. """
    data = {"errors": [],
            "form": LoginForm()}
    if request.method == "POST":
        form = LoginForm(request.form)
        data["form"] = form
        if form.validate():
            user = datamodels.get_user_by_email(form.email.data)
            if user is None:
                data["errors"].append("Bad username or password, try again?")
            else:
                valid = user.check_password(form.password.data)
                if not valid:
                    data["errors"].append("Bad username or password, try again?")
                else:
                    session["user_id"] = user.id
                    if "anon_progress" in session:
                        d = json.loads(session["anon_progress"])
                        user.merge_anonymous_data(d)
                        session.pop("anon_progress")
                    return redirect(request.form.get("last_page", ""))
        else:
            print(form.errors)
            data["errors"].append("Username or email and password are required")
    else:
        data["form"] = LoginForm()
    if len(data["errors"]) > 0 or request.method == "GET":
        return render_template("login.html", **data)


@blueprint.route("/logout", methods=["POST"])
@login_required
def logout(user):
    """ Clear session data, logging the current user out. """
    session.clear()
    data = {"form": LoginForm()}
    return redirect(url_for("index"))


@blueprint.route("/preference/<preference_tag>/<on_or_off>", methods=["POST"])
def set_preference(preference_tag, on_or_off):
    """ Set a user preference. """
    user = get_current_user()
    if user is None:
        return "No user"
    if preference_tag not in datamodels.PreferenceTags:
        flash("Unknown preference.")
        return "Unknown preference tag."
    if on_or_off in ["ON", "on"]:
        value = True
    elif on_or_off in ["OFF", "off"]:
        value = False
    else:
        flash("Unknown preference setting.")
        return "Unknown preference setting."
    user.set_preference(preference_tag, value)
    return ""
