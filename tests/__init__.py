from os import environ

environ["FLASK_ENV"] = "test"
from app import app

import logging

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
