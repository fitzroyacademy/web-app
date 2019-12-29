import json

from flask import (
    render_template,
    session,
    request,
    url_for,
    redirect,
    flash,
    abort,
    jsonify,
)
from sqlalchemy.exc import IntegrityError

import datamodels
from datamodels.enums import PreferenceTags
from dataforms import (
    AddUserForm,
    EditUserForm,
    LoginForm,
    AjaxCSRFTokenForm,
    CustomSettingForm,
)

from utils.base import get_current_user
from .decorators import login_required
from .utils import get_session_data, set_session_data
from utils.images import generate_thumbnail
from .blueprint import SubdomainBlueprint

blueprint = SubdomainBlueprint("user", __name__, template_folder="templates")


def merge_anonymous_data(user_id, data):
    for seg_id in data:
        datamodels.SegmentUserProgress.save_user_progress(
            seg_id, user_id, int(data[seg_id])
        )


@blueprint.subdomain_route("/user/<slug>", methods=["GET"])
def view(slug, institute=""):
    """ View a user's profile. """
    user_id = slug
    user = datamodels.get_user(user_id)
    data = {"user": user, "form": EditUserForm()}
    return render_template("user.html", **data)


@blueprint.subdomain_route("/edit", methods=["GET"])
@login_required
def retrieve(user, institute=""):

    return render_template("user_edit.html", **{"form": EditUserForm()})


@blueprint.subdomain_route("/edit", methods=["POST"])
@login_required
def edit(user, institute=""):
    """
    Edit the current user.
    """

    data = {"errors": [], "message": "Error while saving data"}
    db = datamodels.get_session()

    if "profile_picture" in request.form:
        form = AjaxCSRFTokenForm(request.form)
        if form.validate():
            file = request.files["file"]

            filename = generate_thumbnail(file, "square_l")
            if not filename:
                data["errors"] = ["Couldn't upload picture."]
            else:
                user.profile_picture = filename
                db.add(user)
                db.commit()
        else:
            data["errors"] = "Missing CSRF token"

        if data["errors"]:
            return jsonify(data), 400
        else:
            return jsonify({"message": "Changes saved", "errors": []})

    form = EditUserForm(request.form)
    if form.validate():
        user.email = form.email.data
        user.first_name = form.first_name.data
        user.last_name = form.last_name.data
        user.username = form.username.data
        if form.password.data:
            setattr(user, "password", form.password.data)

        try:
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            data["errors"] = ["Wrong email address"]
    else:
        data["errors"] = form.errors

    if data["errors"]:
        data["message"] = "Error while saving data"
        return jsonify(data), 400
    else:
        data["message"] = "Changes saved"
        return jsonify(data)


@blueprint.subdomain_route("/register", methods=["POST"])
def create(institute=""):
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
            user.username = user.available_username(form.username.data)
            setattr(user, "password", form.password.data)
            db.add(user)
            db.commit()
        except IntegrityError:
            db.rollback()
            flash("This username is already taken")
            return redirect(redirect(request.args.get("last_page", "/")))
        except Exception as e:
            data["errors"].append("{}".format(e))
            return render_template("login.html", **data)
        if "enrollments" in session:
            d = get_session_data(session, "enrollments")
            for course_id in d:
                course = datamodels.Course.find_by_id(int(course_id))
                if course:
                    course.enroll(user)
        if "anon_progress" in session:
            d = get_session_data(session, "anon_progress")
            merge_anonymous_data(user.id, d)
            session.pop("anon_progress")

        session["user_id"] = user.id
        flash("Thanks for registering, " + user.full_name + "!")
    else:
        data["errors"] = form.errors
    return redirect(request.args.get("from", "/"))


@blueprint.subdomain_route("/enroll/<course_slug>", methods=["POST"])
def enroll(course_slug, institute=""):
    """
    Enroll a user into a course.
    """
    course = datamodels.get_course_by_slug(course_slug)
    if course is None:
        return abort(404)

    course_code = request.form.get("course_code", "")

    if (
        course.visibility == "code"
        and course_code.lower() != course.course_code.lower()
    ):
        flash("Wrong course code")
        return redirect("/course/{}".format(course.slug))

    user = get_current_user()
    if course.guest_access and not user:  # Guest access for not log in user
        sess = session.get("enrollments", "[]")
        data = json.loads(sess)
        if course.id in data:
            return redirect(course.lessons[0].permalink)
        else:
            data.append(course.id)
            session["enrollments"] = json.dumps(data)
    elif not course.guest_access and not user:
        return redirect("/login")
    else:
        course.enroll(user)

    flash("You are now enrolled in {}".format(course.title))
    return redirect(course.lessons[0].permalink)


@blueprint.subdomain_route("/login", methods=["GET", "POST"])
def login(institute=""):
    """ Validiate login and save current user to session. """
    data = {"errors": [], "form": LoginForm()}
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
                        merge_anonymous_data(user.id, d)
                        session.pop("anon_progress")
                    return redirect(request.args.get("last_page", "/"))
        else:
            data["errors"].append("Username or email and password are required")
    else:
        data["form"] = LoginForm()
    if len(data["errors"]) > 0 or request.method == "GET":
        return render_template("login.html", **data)


@blueprint.subdomain_route("/logout", methods=["POST"])
@login_required
def logout(user, institute=""):
    """ Clear session data, logging the current user out. """
    keys = [key for key in session.keys() if key != "csrf"]
    for key in keys:
        session.pop(key)

    return redirect(url_for("course.index"))


@blueprint.subdomain_route("/preference/<preference_tag>/<on_or_off>", methods=["POST"])
@login_required
def set_preference(user, preference_tag, on_or_off, institute=""):
    """ Set a user preference. """
    if preference_tag not in PreferenceTags:
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


@blueprint.subdomain_route("/user/settings", methods=["POST"])
def set_user_setting(institute=""):
    form = CustomSettingForm(request.form)
    user = get_current_user()
    if form.validate():
        key = form.key.data
        value = form.value.data
        if key not in datamodels.CUSTOM_SETTINGS_KEYS:
            return jsonify({"message": "There is no such setting available"}), 400
        if user:
            datamodels.CustomSetting.set_setting(key, value, user)
        else:
            custom_settings = get_session_data(session, "custom_settings")
            custom_settings[key] = value
            set_session_data(session, "custom_settings", custom_settings)
        return jsonify({"key": key, "value": value})
    else:
        if "csrf_token" in form.errors:
            msg = "CSRF token missing"
        else:
            msg = "Both key and value must be provided"
        return jsonify({"message": msg}), 400


@blueprint.subdomain_route("/user/settings", methods=["GET"])
def get_user_settings(institute=""):
    user = get_current_user()
    if user:
        return jsonify(user.get_custom_settings())
    else:
        return get_session_data(session, "custom_settings")
