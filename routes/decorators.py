from functools import wraps

from flask import abort

from util import get_current_user


def login_required(function):
    """
    Decorator for views that checks that the user is logged in, raising unauthorized response if necessary.
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            raise abort(401, 'Unauthorized')

        return function(current_user, *args, **kwargs)
    return decorated_function