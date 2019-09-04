import os
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, flash, jsonify, current_app

import datamodels
from routes.decorators import login_required
from routes.utils import allowed_file
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
        raise InvalidUsage(
            'No such course or you don\'t have permissions to edit it')

    if request.method == "POST":
        db = datamodels.get_session()
        if 'course_target' in request.form:
            course.target_audience = request.form['course_target']
        if 'course_summary' in request.form:
            course.summary_html = request.form['course_summary']
        if 'course_name' in request.form:
            course.title = request.form['course_name']
        if 'cover_image' in request.form:
            file = request.files['file']

            if file and allowed_file(file.filename):
                now = datetime.now()
                filename = '%s.%s'.format(
                    now.strftime("%Y-%m-%d-%H-%M-%S-%f"),
                    file.filename.rsplit('.', 1)[1])
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'],
                                         filename)
                file.save(file_path)

                course.cover_image = filename

        db.add(course)
        db.commit()

        return jsonify({"success": True})

    data = {'course': course}

    return render_template('course_edit.html', **data)


@blueprint.route('/<slug>/edit/options/<option>/<on_or_off>', methods=["POST"])
@login_required
def set_options(user, slug=None, option=None, on_or_off=False):
    """ Set course options. """
    course = datamodels.get_course_by_slug(slug)

    if not course or not user.teaches(course):
        raise InvalidUsage(
            'No such course or you don\'t have permissions to edit it')

    if option not in ['draft', 'guest_access', 'paid']:
        flash('Unknown option.')
        return jsonify({"success": False, "message": "Unknown option setting."})
    if on_or_off in ['ON', 'on']:
        value = True
    elif on_or_off in ['OFF', 'off']:
        value = False
    else:
        flash('Unknown option setting.')
        return jsonify({"success": False, "message": "Unknown option setting."})
    setattr(course, option, value)

    db = datamodels.get_session()
    db.add(course)
    db.commit()

    return jsonify({"success": True})
