import datamodels
from flask import session


def get_current_user():
    if 'user_id' in session:
        return datamodels.get_user(session['user_id'])
    else:
        return None


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

    def to_dict(self):
        return {'message': self.message}