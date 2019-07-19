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
