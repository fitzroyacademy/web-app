from os import environ, urandom
import logging


# A default fallback.
class Config(object):
    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)

    DEBUG = False
    TESTING = False
    SECRET_KEY = environ.get("APP_SECRET_KEY", default=urandom(16))
    DB_HOST = environ.get("DB_HOST", default=":memory:")
    DB_USER = environ.get("DB_USER", default=None)
    DB_PASSWORD = environ.get("DB_PASSWORD", default=None)
    DB_DRIVER = environ.get("DB_DRIVER", default="sqlite")
    DB_NAME = environ.get("DB_NAME", default=None)
    DB_OPTIONS = environ.get("DB_OPTIONS", default="")
    MAILGUN_API_URL = environ.get("MAILGUN_API_URL", default=None)
    MAILGUN_API_KEY = environ.get("MAILGUN_API_KEY", default=None)
    S3_BUCKET = environ.get("S3_BUCKET", default=None)
    S3_LOCATION = "http://{}.s3.amazonaws.com/".format(S3_BUCKET)
    CLOUD_FRONT_URL = "https://assets.fitzroy.academy/"
    SERVER_NAME = environ.get("SERVER_NAME", default=None)
    AUTH0_CLIENT_ID = environ.get("AUTH0_CLIENT_ID", default=None)
    AUTH0_DOMAIN = environ.get("AUTH0_DOMAIN", default=None)
    AUTH0_CLIENT_SECRET = environ.get("AUTH0_CLIENT_SECRET", default=None)
    UPLOAD_FOLDER = "static/uploads"
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET = environ.get("WTF_CSRF_SECRET", "").encode()

    @property
    def DB_URI(self):
        if self.DB_DRIVER == "sqlite":
            db_uri = "{}:///{}{}".format(self.DB_DRIVER, self.DB_HOST, self.DB_OPTIONS)
        elif self.DB_DRIVER == "postgres":
            if not self.DB_USER or not self.DB_PASSWORD or not self.DB_HOST:
                logging.critical(
                    "DB_USER, DB_PASSWORD, or DB_HOST not set. Unable to continue."
                )
                raise Exception("Unable to connect to database.")
            db_uri = "{}://{}:{}@{}".format(
                self.DB_DRIVER, self.DB_USER, self.DB_PASSWORD, self.DB_HOST
            )
            if self.DB_NAME:
                db_uri += str("/" + self.DB_NAME)
        else:
            raise Exception("DB_DRIVER set, but not sqlite or postgres.")

        log_msg = "Using {} driver with URI {}".format(self.DB_DRIVER, db_uri)
        if self.DB_PASSWORD:
            log_msg.replace(self.DB_PASSWORD, "*****", 2)
        logging.info(log_msg)
        return db_uri


class DevelopmentConfig(Config):
    DEBUG = True
    SECRET_KEY = "INSECURE_FOR_LOCAL_DEVELOPMENT"
    DB_HOST = environ.get("DB_HOST", default="dev_db.sqlite")
    DB_OPTIONS = environ.get("DB_OPTIONS", default="?check_same_thread=False")
    WTF_CSRF_SECRET = "qZeimuCyYqo27CqndJetJHx".encode()
    S3_KEY = environ.get("S3_ACCESS_KEY", default=None)


class TestingConfig(Config):
    DEBUG = False
    TESTING = True
    WTF_CSRF_ENABLED = False
    WTF_CSRF_SECRET = "qZeimuCyYqo27CqndJetJHx".encode()


class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    DB_DRIVER = environ.get("DB_DRIVER", default="postgres")
