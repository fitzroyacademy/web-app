from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels

import json

blueprint = Blueprint('object', __name__, template_folder='templates')

@blueprint.route('/_segment/<segment_id>')
def segment(segment_id):
	""" Returns a partial JSON dump of a Lesson Segment by ID. """
	ext = None
	if segment_id.endswith('.json'):
		ext = "json"
		segment_id = segment_id.split('.')[0]
	active_segment = datamodels.get_segment(segment_id)
	if active_segment is None:
		raise "Segment not found: %s".format(segment_id)
	data = {
		'active_segment': active_segment
	}
	if ext is 'json':
		dump = datamodels.dump(data['active_segment'])
		data['active_segment'] = dump
		return json.dumps(data)
	return render_template('partials/_active_segment.html', **data)


@blueprint.route('/_lesson_resources/<lesson_id>')
def lesson_resources(lesson_id):
	""" Returns a partial JSON dump of a Lesson Resource by ID. """
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
	lesson = datamodels.get_lesson(lesson_id)
	if lesson is None:
		return {"error": "Lesson not found"}
	data = {
		'students': students,
		'lesson': lesson
	}
	return render_template('partials/_lesson_resources.html', **data)