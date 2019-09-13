from datetime import datetime

from flask import abort, Blueprint, render_template, request, redirect, flash, jsonify, make_response

import datamodels
from routes.decorators import login_required
from routes.utils import generate_thumbnail

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
        raise abort(404, 'No such course or you don\'t have permissions to edit it')

    if request.method == "POST":
        db = datamodels.get_session()
        if 'year' in request.form:
            try:
                year = int(request.form['year'])
            except ValueError:
                return make_response(jsonify({'success': False, 'message': 'Year must be a number'}), 400)
            course_year = datetime(year=year, month=12, day=31).date()
            course.year = course_year
        if 'skill_level' in request.form:
            course.skill_level = request.form['skill_level']
        if 'workload_summary' in request.form:
            course.workload_summary = request.form['workload_summary']
        if 'who_its_for' in request.form:
            course.target_audience = request.form['who_its_for']
        if 'course_summary' in request.form:
            course.summary_html = request.form['course_summary']
        if 'course_name' in request.form:
            course.title = request.form['course_name']
        if 'course_description' in request.form:
            course.info = request.form['course_description']
        if 'course_slug' in request.form:
            c = datamodels.Course.find_by_slug(request.form['course_slug'])
            if c and course.id != c.id:
                return make_response(jsonify({'success': False, 'message': 'Use different slug for this course.'}), 400)
            course.slug = request.form['course_slug']
        if 'course_code' in request.form:
            c = datamodels.Course.find_by_code(request.form['course_code'])
            if c and course.id != c.id:
                return make_response(jsonify({'success': False, 'message': 'Use different course code.'}), 400)
            course.course_code = request.form['course_code']
        if 'cover_image' in request.form:
            file = request.files['file']

            filename = generate_thumbnail(file, 'cover')
            if not filename:
                return jsonify({'success': False,
                                'message': 'Couldn\'t upload picture. Try again or use different file format'}), 400

            course.cover_image = filename

        db.add(course)
        db.commit()

        return jsonify({'success': True})

    data = {'course': course,
            'teachers': course.instructors,
            'cover_image': '/uploads/{}'.format(course.cover_image) if course.cover_image and not
            course.cover_image.startswith('http') else course.cover_image
            }

    return render_template('static/course_edit_temp/index.html', **data)


@blueprint.route('/<slug>/edit/remove/teacher/<int:teacher_id>', methods=["POST"])
@login_required
def remove_teacher(user, slug=None, teacher_id=None):
    course = datamodels.get_course_by_slug(slug)

    if not course or not user.teaches(course):
        raise abort(404, 'No such course or you don\'t have permissions to edit it')

    if user.id == teacher_id:
        return jsonify({'success': False, 'message': 'You can\'t remove yourself'}), 400

    if not datamodels.get_user(teacher_id):
        return jsonify({'success': False, 'message': 'No such teacher'}), 400

    removed = course.remove_teacher(teacher_id)

    return jsonify({'success': removed})

@blueprint.route('/<slug>/edit/add/teacher', methods=["POST"])
@login_required
def add_teacher(user, slug=None):
    course = datamodels.get_course_by_slug(slug)

    if not course or not user.teaches(course):
        raise abort(404, 'No such course or you don\'t have permissions to edit it')

    new_teacher = datamodels.User.find_by_email(request.form['teacher_email'])
    print(request.form['teacher_email']);
    if not new_teacher:
        raise abort(400, 'No such user.')

    course.add_instructor(new_teacher)

    return jsonify({'success': True})


@blueprint.route('/<slug>/edit/options/<option>/<on_or_off>', methods=["POST"])
@login_required
def set_options(user, slug=None, option=None, on_or_off=False):
    """ Set course options. """
    course = datamodels.get_course_by_slug(slug)
    if not course or not user.teaches(course):
        raise abort(404, 'No such course or you don\'t have permissions to edit it')

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
