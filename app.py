import json
import random
from flask import Flask, render_template, session, request, url_for, redirect, flash
import sass
import stubs
import datamodels
import time
import re
import os
import jinja2
import random
import string
from uuid import uuid4
from os import environ
from werkzeug.routing import BuildError
import routes
import routes.course
import routes.error

app = Flask('FitzroyFrontend', static_url_path='')
routes.attach(app)

@app.route('/')
def index():
    return routes.course.index()

def compile_sass():
    sass.compile(dirname=("static/assets/scss", 'static/css'))

def log_error(error):
    print(error)

@app.context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@app.context_processor
def inject_current_section():
    print(request.path, request.path.split('/')[1])
    return dict(current_section=request.path.split('/')[1])

@app.context_processor
def inject_cache_code():
    return dict(cache_code=time.time())

@jinja2.contextfunction
def get_vars(c):
    if app.debug != True:
        return ""
    methods = []
    for k, v in c.items():
        if callable(v):
            continue
        if k in ["config", "g", "session"]:
            continue
        methods.append({'name': k, 'dump': datamodels.dump(v)})
    return methods
app.jinja_env.globals.update(get_vars=get_vars)

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store'
    return response

def get_current_user():
    if 'user_id' in session:
        return datamodels.get_user(session['user_id'])
    else:
        return None

def uuid():
    return "{}".format(uuid4().hex)
app.jinja_env.globals.update(uuid=uuid)

def url4(*args, **kwargs):
    try:
        return url_for(*args, **kwargs)
    except BuildError as e:
        if app.debug == True:
            flash("{}".format(e))
        return "#"
app.jinja_env.globals.update(url_for=url4)

def url_is(endpoint):
    return request.endpoint == endpoint
app.jinja_env.globals.update(url_is=url_is)

# This route needs to live here forever because it requires access to the app.
@app.route('/api', methods=["GET"])
def api():
    docs = routes.dump_api(app)
    return render_template('url_fors.html', controllers=docs)

if __name__ == "__main__":
    if app.debug:
        app.secret_key = 'l7j7BqOKH7' # Doesn't need to be random for local development
        from livereload import Server, shell
        server = Server(app.wsgi_app)
        server.watch('./static/assets/scss/*', compile_sass)
        server.watch('./')
        server.serve(host='0.0.0.0',open_url=False,port=5000,debug=True)
    else:
        if 'APP_SECRET_KEY' in environ and environ['APP_SECRET_KEY'] != "":
            app.secret_key = environ['APP_SECRET_KEY']
            app.run(host='0.0.0.0', port=5000) # until we start using gunicorn
        elif 'APP_SECRET_KEY' not in environ:
            raise Exception('Application running in non-local environment, but APP_SECRET_KEY environment variable not provided.')
        else:
            raise Exception('Secret key provided in APP_SECRET_KEY, but key is empty.')
