from . import user, course, lesson, object, error, log, segment

def attach(app):
	app.register_blueprint(user.blueprint)
	app.register_blueprint(course.blueprint, url_prefix="/course")
	app.register_blueprint(lesson.blueprint, url_prefix="/course")
	app.register_blueprint(segment.blueprint, url_prefix="/course")
	app.register_blueprint(object.blueprint)
	app.register_blueprint(error.blueprint)
	app.register_blueprint(log.blueprint)