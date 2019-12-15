from os import environ

import jinja2
import sass
from flask import Flask, render_template, request, url_for, flash
from werkzeug.routing import BuildError
from werkzeug.utils import import_string

import commands
import template_filters
import context_preprocessor
import routes
import routes.course
import routes.error
from utils.database import dump


app = Flask("FitzroyFrontend")

environment = environ.get("FLASK_ENV", default="")

if environment == "development":
    cfg = import_string("config.DevelopmentConfig")()
elif environment == "test":
    cfg = import_string("config.TestingConfig")()
elif environment == "production":
    cfg = import_string("config.ProductionConfig")()
else:
    app.logger.warning(
        "FLASK_ENV not specified. Use export FLASK_ENV=development to develop locally."
    )
    cfg = import_string("config.Config")()

app.config.from_object(cfg)

# Add main routes to the app
routes.attach(app)

# Register app custom commands
app.register_blueprint(commands.bp, cli_group="utils")

# Register app context processor
app.register_blueprint(context_preprocessor.bp)

# Register app template filters
app.register_blueprint(template_filters.blueprint)


app.add_url_rule(
    app.static_url_path + "/<path:filename>",
    endpoint="static",
    view_func=app.send_static_file,
    subdomain="<institute>",
)


@app.url_value_preprocessor
def before_route(endpoint, values):
    # List of all endpoints that make use of subdomains in other cases remove if from parameters passed to the route

    subdomain_endpoints = [
        "pages.index",
        "institute.retrieve",
        "institute.edit",
        "institute.add_user",
        "institute.remove_user",
        "institute.change_slug",
    ]

    if (
        endpoint
        and not any(
            [
                endpoint.startswith("lesson"),
                endpoint.startswith("user"),
                endpoint.startswith("course"),
                endpoint in subdomain_endpoints,
            ]
        )
        and values is not None
    ):
        values.pop("institute", None)


@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store"
    return response


# Those globals needs to live here forever because they require an access to the app.
@jinja2.contextfunction
def get_vars(c):
    if not app.debug:
        return ""
    methods = [{"name": "endpont", "dump": request.endpoint}]
    for k, v in c.items():
        if callable(v):
            continue
        if k in ["config", "g", "session"]:
            continue
        methods.append({"name": k, "dump": dump(v)})
    return methods


app.jinja_env.globals.update(get_vars=get_vars)


def url4(*args, **kwargs):
    try:
        # For subdomains url_for is building url with server name and schema, and we would like to keep relative path.
        return url_for(*args, **kwargs).split(app.config["SERVER_NAME"])[-1]
    except BuildError as e:
        if app.debug:
            flash("{}".format(e))
        return "#"


app.jinja_env.globals.update(url_for=url4)

# This route needs to live here forever because it requires access to the app.
@app.route("/api", methods=["GET"])
def api():
    docs = routes.dump_api(app)
    return render_template("url_fors.html", controllers=docs)


def compile_sass():
    sass.compile(dirname=("static/assets/scss", "static/css"))


if __name__ == "__main__":
    app.logger.info("Building SASS")
    compile_sass()

    if app.debug:
        from livereload import Server

        def ignore_func(path):
            if path.split(".")[-1] == "sqlite":
                return True

        server = Server(app.wsgi_app)
        server.watch("./static/assets/scss/*", compile_sass)
        server.watch("./", ignore=ignore_func)
        server.serve(host="0.0.0.0", open_url=False, port=5000)
    else:
        app.run(host="0.0.0.0", port=5000)  # until we start using gunicorn
