from os import environ

environ['FLASK_ENV'] = 'test'

import logging
logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)