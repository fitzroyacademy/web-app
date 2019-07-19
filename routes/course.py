from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels

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
    course = datamodels.get_course_by_slug(slug)
    if course is None:
        return redirect('/404')
    return render_template('course_intro.html', course=course)

@blueprint.route('/code', methods=["GET", "POST"])
def by_code():
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

@blueprint.route('/<slug>/edit')
def edit(slug=None):
    return render_template('course_edit.html')
