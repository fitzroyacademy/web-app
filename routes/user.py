import json

from flask import Blueprint, render_template, session, request, url_for, redirect, flash
from sqlalchemy.exc import IntegrityError

import datamodels
from util import get_current_user

blueprint = Blueprint("user", __name__, template_folder="templates")


@blueprint.route("/user/<slug>", methods=["GET"])
def view(slug):
    """ View a user's profile. """
    user_id = slug
    user = datamodels.get_user(user_id)
    data = {"user": user}
    return render_template("user.html", **data)


@blueprint.route("/edit", methods=["GET", "POST"])
@blueprint.route("/edit/<slug>", methods=["GET", "POST"])
def edit(slug=None):
    """
    Edit the current user.
    """
    user_id = slug
    if user_id is None and "user_id" in session:
        user = datamodels.get_user(session["user_id"])
    else:  # TODO: Admin permissions
        return redirect("/404")

    data = {"errors": []}
    if request.method == "POST":
        if "email" in request.form:
            user.email = request.form["email"]
        if "first_name" in request.form:
            user.first_name = request.form["first_name"]
        if "last_name" in request.form:
            user.last_name = request.form["last_name"]
        if "username" in request.form:
            user.username = request.form["username"]
        if "password" in request.form:
            setattr(user, "password", request.form["password"])

        db = datamodels.get_session()
        try:
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            data["errors"] = ["Wrong email address"]

    return render_template("user_edit.html", **data)


@blueprint.route("/register", methods=["POST"])
def create():
    """
    Create a new user.
    """
    db = datamodels.get_session()
    data = {"errors": []}
    # We'll roll in better validation with form error integration in beta; this is
    # to prevent mass assignment vulnerabilities.
    kwargs = {}
    valid = ["first_name", "email", "username", "last_name", "password"]
    for k in valid:
        kwargs[k] = request.form.get(k)
    user = datamodels.get_user_by_email(request.form.get("email"))
    if user is not None:
        data["errors"].append("Email address already in use.")
        return render_template("login.html", **data)
    try:
        user = datamodels.User(**kwargs)
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
    data = {"errors": []}
    if request.method == "POST":
        user = datamodels.get_user_by_email(request.form.get("email"))
        if user is None:
            data["errors"].append("Bad username or password, try again?")
        else:
            valid = user.check_password(request.form.get("password"))
            if not valid:
                data["errors"].append("Bad username or password, try again?")
            else:
                session["user_id"] = user.id
                if "anon_progress" in session:
                    d = json.loads(session["anon_progress"])
                    user.merge_anonymous_data(d)
                    session.pop("anon_progress")
                return redirect(request.form.get("last_page", ""))
    if len(data["errors"]) > 0 or request.method == "GET":
        return render_template("login.html", **data)


@blueprint.route("/logout", methods=["POST"])
def logout():
    """ Clear session data, logging the current user out. """
    session.clear()
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
