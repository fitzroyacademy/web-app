from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels
import stubs

blueprint = Blueprint('lesson', __name__, template_folder='templates')

@blueprint.route('/lessons')
def lessons():
    return render_template('lesson_chart.html')

@blueprint.route('<course_slug>/<lesson_slug>')
def view(course_slug, lesson_slug):
    """
    Retrieves and displays a particular course, with the specified lesson
    and its first segment set to be active.
    """
    lesson = datamodels.get_lesson_by_slug(course_slug, lesson_slug)
    if lesson is None:
        return redirect('/404')
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