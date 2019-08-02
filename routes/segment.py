from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels

blueprint = Blueprint('segment', __name__, template_folder='templates')

@blueprint.route('<course_slug>/<lesson_slug>/<segment_slug>')
def view(course_slug, lesson_slug=None, segment_slug=None):
	"""
	Retrieves and displays a particular course, with the specified lesson
	and segment set to be active.
	"""
	if lesson_slug is None:
		course = datamodels.get_course_by_slug(course_slug)
		lesson = course.lessons[0]
		segment = lesson.segments[0]
	else:
		segment = datamodels.get_segment_by_slug(course_slug, lesson_slug, segment_slug)
		lesson = segment.lesson
		course = lesson.course
	data = {
		'students': stubs.student_completion,
		'active_lesson': lesson,	
		'active_segment': segment,
		'course': course
	}
	return render_template('course.html', **data)