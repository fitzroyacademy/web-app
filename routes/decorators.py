from functools import wraps

from flask import abort

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
    def decorated_function(user, slug, *args, **kwargs):
        course = datamodels.get_course_by_slug(slug)

        if not course or not user.teaches(course):
            raise abort(404, "No such course or you don't have permissions to edit it")

        return function(user, course, slug, *args, **kwargs)

    return decorated_function
