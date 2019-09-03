import sys
from . import user, course, lesson, object, error, log, segment, pages, resource

def attach(app):
    app.register_blueprint(user.blueprint)
    app.register_blueprint(course.blueprint, url_prefix="/course")
    app.register_blueprint(lesson.blueprint, url_prefix="/course")
    app.register_blueprint(segment.blueprint, url_prefix="/course")
    app.register_blueprint(resource.blueprint, url_prefix="/resource")
    app.register_blueprint(object.blueprint)
    app.register_blueprint(error.blueprint)
    app.register_blueprint(log.blueprint)
    pages.attach_static_paths(app, 'templates/static')
    app.register_blueprint(pages.blueprint)

    @app.errorhandler(404)
    def static_fallback(e):
        return error.fourohfour(e)

    @app.errorhandler(502)
    def error_pagek(e):
        return error.fiveohtwo(e)

def dump_api(app):
    """
    Dump API methods into something vaguely resembling documentation.
    """
    docs = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint is None or '.' not in rule.endpoint:
            continue
        path = rule.endpoint.split('.')
        controller = path[0]
        action = path[1]  # No support for weird long paths.
        mod = getattr(sys.modules[__name__], controller, None)
        meth = getattr(mod, action, None)
        if mod is not None:
            if meth is not None:
                doc = meth.__doc__
            else:
                doc = 'No documentation.'
            if controller not in docs:
                docs[controller] = []
            docs[controller].append({
                'endpoint': rule.endpoint,
                'url_path': rule,
                'documentation': doc,
                'parameters': rule.arguments,
                # TODO: Perfect REST
                'methods': ", ".join(filter(lambda x: x in ["GET", "POST"], rule.methods))
            })
    return docs
