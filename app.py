import json
import random
from flask import Flask, render_template
import sass
import stubs
import datamodels

app = Flask('FitzroyFrontend', static_url_path='')
sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.route('/')
def index():
    return render_template('welcome.html')


# --------------------------------------------------------------------------------
# Some 'static' non-functional urls for Will to play with:
# Not yet ready for backend consumption

@app.route('/mistakes')
def mistakes():
    return render_template('mistakes.html')

@app.route('/playground')
def playground():
    return render_template('playground.html')

@app.route('/course_edit')
def course_edit():
    return render_template('course_edit.html')


# --------------------------------------------------------------------------------
# Templates that are nearly ready for app-ification:

@app.route('/course_intro')
def course_intro():
    return render_template('course_intro.html')

@app.route('/login')
def login():
    return render_template('login.html')


# --------------------------------------------------------------------------------
# actually within the app now:

@app.route('/course/<cid>/<lid>/<sid>')
def course(cid, lid=None, sid=None):
	if lid is None:
		course = datamodels.get_course_by_slug(cid)
		lesson = course.lessons[0]
		segment = lesson.segments[0]
	elif sid is None:
		lesson = datamodels.get_lesson_by_slug(cid, lid)
		course = lesson.course
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
    app.debug = True
    app.run(host='0.0.0.0', port=5000)