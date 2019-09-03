from functools import wraps
from util import get_current_user, InvalidUsage


def login_required(function):
    """
    Decorator for views that checks that the user is logged in, raising unauthorized response if necessary.
    """
    @wraps(function)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user:
            raise InvalidUsage('Unauthorized')

        return function(current_user, *args, **kwargs)
    return decorated_function