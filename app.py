import json
import random
from flask import Flask, render_template, session, request, url_for, redirect
import sass
import stubs
import datamodels
import time
import re

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

app = Flask('FitzroyFrontend', static_url_path='')
app.debug = True

def compile_sass():
    sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@app.context_processor
def inject_current_section():
    print(request.path, request.path.split('/')[1])
    return dict(current_section=request.path.split('/')[1])

@app.context_processor
def inject_cache_code():
    return dict(cache_code=time.time())

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

def get_current_user():
    if 'user_id' in session:
        return datamodels.get_user(session['user_id'])
    else:
        return None

@app.route('/')
def index():
    return render_template('welcome.html')


# --------------------------------------------------------------------------------
# Some 'static' non-functional urls for Will to play with:
# Not yet ready for backend consumption

@app.route('/playground')
def playground():
    return render_template('playground.html')

@app.route('/mistakes')
def mistakes():
    return render_template('mistakes.html')

@app.route('/course_edit')
def course_edit():
    return render_template('course_edit.html')

@app.route('/password')
def password():
    return render_template('password.html')

@app.route('/user/<int:user_id>', methods=["GET"])
def user(user_id):
    user = datamodels.get_user(user_id)
    data = {'user': user}
    return render_template('user.html', **data)

@app.route('/user_edit', methods=["GET", "POST"])
def user_edit():
    if 'user_id' in session and session['user_id'] is not None:
        current_user = datamodels.get_user(session['user_id'])
    else:
        return 'Request denied.'
    if request.method == "POST":
        if 'email' in request.form:
            current_user.email = request.form['email']
        if 'first_name' in request.form:
            current_user.first_name = request.form['first_name']
        if 'last_name' in request.form:
            current_user.last_name = request.form['last_name']
        if 'username' in request.form:
            current_user.username = request.form['username']
    return render_template('user_edit.html')

@app.route('/404')
@app.errorhandler(404)
def fourohfour(e):
    return render_template('404.html'), 404

@app.errorhandler(Exception)
@app.route('/502')
def fiveohtwo(e):
    return render_template('502.html')    

# --------------------------------------------------------------------------------
# Templates that are nearly ready for app-ification:

@app.route('/code', methods=["GET", "POST"])
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

@app.route('/enroll/<course_slug>', methods=["POST"])
def enroll(course_slug):
    course = datamodels.get_course_by_slug(course_slug)
    if course is None:
        return redirect('/404')
    user = get_current_user()
    if user and datamodels.get_enrollment(course.id, user.id) is None:
        enrollment = datamodels.CourseEnrollment(
            course_id=course.id, user_id=user.id, access_level=1
        )
        s = datamodels.get_session()
        s.add(enrollment)
        s.commit()
    return redirect(course.lessons[0].permalink)

@app.route('/course_intro')
def course_intro():
    return render_template('course_intro.html', **kwargs)

@app.route('/login', methods=["GET", "POST"])
def login():
    data = {'errors': []}
    if request.method == "POST":
        user = datamodels.get_user_by_email(request.form.get('email'))
        if user is None:
            data['errors'].append("Bad username or password, try again?")
        else:
            valid = user.check_password(request.form.get('password'))
            if not valid:
                data['errors'].append("Bad username or password, try again?")
            else:
                session['user_id'] = user.id
                return redirect(url_for('index'))
    if len(data['errors']) > 0 or request.method == "GET":
        return render_template('login.html', **data)

@app.route('/logout', methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/user/register', methods=["POST"])
def post_register():
    return render_template('login.html')


# --------------------------------------------------------------------------------
# actually within the app now:

@app.route('/course/<slug>')
def course_preview(slug):
    course = datamodels.get_course_by_slug(slug)
    if course is None:
        return redirect('/404')
    return render_template('course_intro.html', course=course)

@app.route('/course/<cid>/<lid>')
def lesson_view(cid, lid):
    lesson = datamodels.get_lesson_by_slug(cid, lid)
    course = lesson.course
    segment = lesson.segments[0]
    data = {
        'students': stubs.student_completion,
        'active_lesson': lesson,    
        'active_segment': segment,
        'course': course
    }
    if course is None:
        return redirect('/404')
    return render_template('course.html', **data)

@app.route('/course/<cid>/<lid>/<sid>')
def lesson_segment(cid, lid=None, sid=None):
	if lid is None:
		course = datamodels.get_course_by_slug(cid)
		lesson = course.lessons[0]
		segment = lesson.segments[0]
	else:
		segment = datamodels.get_segment_by_slug(cid, lid, sid)
		lesson = segment.lesson
		course = lesson.course
	data = {
		'students': stubs.student_completion,
		'active_lesson': lesson,	
		'active_segment': segment,
		'course': course
	}
	return render_template('course.html', **data)

@app.route('/_segment/<sid>')
def partial_segment(sid):
	ext = None
	if sid.endswith('.json'):
		ext = "json"
		sid = sid.split('.')[0]
	active_segment = datamodels.get_segment(sid)
	if active_segment is None:
		raise "Segment not found: %s".format(sid)
	data = {
		'active_segment': active_segment
	}
	if ext is 'json':
		dump = datamodels.dump(data['active_segment'])
		data['active_segment'] = dump
		return json.dumps(data)
	return render_template('partials/_active_segment.html', **data)


@app.route('/_lesson_resources/<lid>')
def _lesson_resources(lid):
	students =  [
		{
			'id':'1',
			'name':'Alice',
			'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
			'progress': random.randrange(50, 100),
			'color': '#e809db',
			'admin': False
		},
		{
			'id':'2',
			'name':'Bob',
			'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
			'progress': random.randrange(10, 50),
			'color': '#0f7ff4',
			'admin': False
		},
		{
			'id':'3',
			'name':'Eve',
			'completion': ';'.join(str(v) for v in random.sample(range(100), 5)),
			'progress': random.randrange(50, 100),
			'color': '#666',
			'admin': True
		}
	]
	active = None
	lesson = datamodels.get_lesson(lid)
	if lesson is None:
		return {"error": "Lesson not found"}
	data = {
		'students': students,
		'lesson': lesson
	}
	return render_template('partials/_lesson_resources.html', **data)

@app.route('/lessons')
def lessons():
    return render_template('lesson_chart.html')

if __name__ == "__main__":
    app.secret_key = "super sedcret"
    compile_sass()
    if app.debug:
        from livereload import Server, shell
        server = Server(app.wsgi_app)
        server.watch('./static/assets/scss/*', compile_sass)
        server.watch('./')
        server.serve(open_url=False,port=5000,debug=True)
    else:
        app.run(host='0.0.0.0', port=5000) # until we start using gunicorn