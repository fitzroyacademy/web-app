import json

from functools import wraps

from flask import abort, session, redirect

from util import get_current_user

import datamodels


def login_required(function):
    """
    Decorator for views that checks that the user is logged in, raising unauthorized response if necessary.
    """

    @wraps(function)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            raise abort(401, "Unauthorized")

        return function(current_user, *args, **kwargs)

    return decorated_function


def teacher_required(function):
    """
    Decorator for views that checks if given user is a teacher of give course
    """

    @wraps(function)
    def decorated_function(user, course_slug, *args, **kwargs):
        course = datamodels.get_course_by_slug(course_slug)

        if not course or not user.teaches(course):
            raise abort(404, "No such course or you don't have permissions to edit it")

        return function(user, course, course_slug, *args, **kwargs)

    return decorated_function


def enrollment_required(function):
    # http://localhost:5000/course/fitzroy-academy/how-to-have-good-ideas

    @wraps(function)
    def decorated_function(course_slug, lesson_slug, *args, **kwargs):
        # check if user (logged in or anonymous) is enrolled
        current_user = get_current_user()
        course = datamodels.Course.find_by_slug(course_slug)
        if not current_user:
            if not course.guest_access:
                return redirect("/login")

            session_data = session.get("enrollments", "[]")
            data = json.loads(session_data)
            if course.id not in data:
                return redirect("/course/{}".format(course.slug))

        elif not course.is_student(current_user.id):
            return redirect("/course/{}".format(course.slug))

        return function(course_slug, lesson_slug, *args, **kwargs)

    return decorated_function
