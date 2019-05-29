import json
import random
from flask import Flask, render_template
import sass
import stubs

app = Flask('FitzroyFrontend', static_url_path='')
sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.route('/')
def index():
    return render_template('welcome.html')

@app.route('/playground')
def playground():
    return render_template('playground.html')

@app.route('/course')
def course():
	data = {
		'students': stubs.students,
		'active_segment': stubs.segments[1],
		'course': stubs.course
	}
	return render_template('course.html', **data)

@app.route('/_segment/<sid>')
def partial_segment(sid):
	ext = None
	if sid.endswith('.json'):
		ext = "json"
		sid = sid.split('.')[0]
	active_segment = None
	for s in stubs.segments:
		if s['id'] == sid:
			active_segment = s
			break
	if s is None:
		raise "Segment not found: %s".format(sid)
	data = {
		'active_segment': active_segment
	}
	if ext is 'json':
		return json.dumps(data)
	return render_template('partials/_active_segment.html', **data)

@app.route('/_completion/<sid>')
def completion(sid):
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
	data = {
		'students': students
	}
	active = None
	for s in stubs.segments:
		# We'll need this later.
		if s['id'] == sid:
			active = s
			break
	if s is None:
		return {"error": "Segment not found"}
	return render_template('partials/_student_list.html', **data)

@app.route('/lessons')
def lessons():
    return render_template('lesson_chart.html')

if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0', port=5000)