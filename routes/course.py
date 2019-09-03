from flask import Blueprint, render_template, request, redirect

import datamodels
from routes.decorators import login_required
from util import InvalidUsage

blueprint = Blueprint('course', __name__, template_folder='templates')


@blueprint.route('/')
def index():
    """ Shows all courses the user has access to. """
    data = {'public_courses': datamodels.get_public_courses()}
    return render_template('welcome.html', **data)


@blueprint.route('/<slug>')
def view(slug):
    """
    Retrieves and displays a course based on course slug.
    """

    # ToDo: handle accessing course that requires login
    # ToDo: course that do not have lessons will raise exception

    course = datamodels.get_course_by_slug(slug)
    if course is None:
        return redirect('/404')
    return render_template('course_intro.html', course=course)


@blueprint.route('/code', methods=["GET", "POST"])
def code():
    error = None
    if request.method == "POST":
        c = datamodels.get_course_by_code(request.form['course_code'])
        if c is None:
            error = "Course not found."
        else:
            return redirect(c.permalink)
    if request.method == "GET" or error:
        data = {'errors': [error]}
        return render_template('code.html', **data)


@blueprint.route('/<slug>/edit', methods=["GET", "POST"])
@login_required
def edit(user, slug=None):
    course = datamodels.get_course_by_slug(slug)

    if not course or not user.teaches(course):
        raise InvalidUsage('No such course or you don\'t have permissions to edit it')

    if request.method == "POST":
        pass

    data = {'course': course}

    return render_template('course_edit.html', **data)
