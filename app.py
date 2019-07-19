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
from uuid import uuid4

import routes.user
import routes.course
import routes.lesson
import routes.segment
import routes.object

app = Flask('FitzroyFrontend', static_url_path='')
app.register_blueprint(routes.user.blueprint)
app.register_blueprint(routes.course.blueprint, url_prefix="/course")
app.register_blueprint(routes.lesson.blueprint, url_prefix="/course")
app.register_blueprint(routes.segment.blueprint, url_prefix="/course")
app.register_blueprint(routes.object.blueprint)

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

@app.route('/')
def index():
    data = {'public_courses': datamodels.get_public_courses()}
    return render_template('welcome.html', **data)


# --------------------------------------------------------------------------------
# Some 'static' non-functional urls for Will to play with:
# Not yet ready for backend consumption
 

@app.route('/course_edit')
def course_edit():
    return render_template('course_edit.html')

@app.route('/404')
@app.errorhandler(404)
def fourohfour(e):
    try:
        return render_template('static'+request.path+'.html')
    except jinja2.exceptions.TemplateNotFound:
        try:
            return render_template('static'+request.path+'/index.html')
        except jinja2.exceptions.TemplateNotFound:
            return render_template('404.html'), 404

@app.errorhandler(Exception)
@app.route('/502')
def fiveohtwo(e):
    log_error(e)
    return render_template('502.html')    

# --------------------------------------------------------------------------------
# Templates that are nearly ready for app-ification:

@app.route('/code', methods=["GET", "POST"])
def code():
    error = None
    if request.method == "POST":
        c = datamodels.get_course_by_code(request.form['course_code'])
        if c is None:
            error = "Course not found."
        else:
            return redirect(c.permalink)
    if request.method == "GET" or error:
        data = {'errors': [error]}
        return render_template('code.html', **data)


# --------------------------------------------------------------------------------
# actually within the app now:


@app.route('/lessons')
def lessons():
    return render_template('lesson_chart.html')

@app.route('/event/<event_type>', methods=["POST"])
def log_event(event_type):
    user = get_current_user()
    if user is None:
        # TODO: Log anonymous user progress.
        return True
    if event_type == 'progress':
        segment_id = request.form['segment_id']
        user_id = user.id
        progress = request.form['percent']
        seg = datamodels.get_segment(segment_id)
        sup = seg.save_user_progress(user, progress)
        return json.dumps(datamodels.dump(sup))
    else:
        return event_type

@app.route('/api', methods=["GET"])
def api():
    docs = {}
    for rule in app.url_map.iter_rules():
        if rule.endpoint is None or '.' not in rule.endpoint:
            continue
        path = rule.endpoint.split('.')
        controller = path[0]
        action = path[1]  # No support for weird long paths.
        mod = getattr(routes, controller, None)
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
    return render_template('url_fors.html', controllers=docs)

if __name__ == "__main__":
    app.secret_key = "super sedcret"
    compile_sass()
    if app.debug:
        from livereload import Server, shell
        server = Server(app.wsgi_app)
        server.watch('./static/assets/scss/*', compile_sass)
        server.watch('./')
        server.serve(host='0.0.0.0',open_url=False,port=5000,debug=True)
    else:
        app.run(host='0.0.0.0', port=5000) # until we start using gunicorn
