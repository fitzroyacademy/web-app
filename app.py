import json
import random
from flask import Flask, render_template
import sass
import stubs
import models

app = Flask('FitzroyFrontend', static_url_path='')
sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.route('/')
def index():
    return render_template('welcome.html')


# Some 'static' non-functional urls for Will to play with:

@app.route('/mistakes')
def mistakes():
    return render_template('mistakes.html')

@app.route('/playground')
def playground():
    return render_template('playground.html')


# Templates that are nearly ready for app-ification:

@app.route('/course_intro')
def course_intro():
    return render_template('course_intro.html')

@app.route('/course_edit')
def course_edit():
    return render_template('course_edit.html')


# actually within the app now:

@app.route('/course/<cid>/<lid>/<sid>')
def course(cid, lid="l01", sid="seg_a"):
	course = models.get_course(cid)
	lesson = course.lessons.find(id=lid)
	segment = lesson.segments.find(id=sid)
	data = {
		'students': stubs.students,
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
	active_segment = models.get_segment(sid)
	if active_segment is None:
		raise "Segment not found: %s".format(sid)
	data = {
		'active_segment': active_segment
	}
	if ext is 'json':
		data['active_segment'] = data['active_segment'].dump()
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
	lesson = models.get_lesson(lid)
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