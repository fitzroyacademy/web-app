import datetime
from flask import Flask, render_template, request, url_for, flash, session
from util import get_current_user
import sass
import datamodels
import time
import jinja2
from uuid import uuid4
from os import environ
from werkzeug.routing import BuildError
from werkzeug.utils import import_string
import routes
import routes.course
import routes.error
import requests
import click
import boto3

app = Flask('FitzroyFrontend')

environment = environ.get("FLASK_ENV", default="")

if environment == "development":
    cfg = import_string('config.DevelopmentConfig')()
elif environment == "test":
    cfg = import_string('config.TestingConfig')()
elif environment == "production":
    cfg = import_string('config.ProductionConfig')()
else:
    app.logger.warning("FLASK_ENV not specified. Use export FLASK_ENV=development to develop locally.")
    cfg = import_string('config.Config')()

app.config.from_object(cfg)

routes.attach(app)


app.add_url_rule(app.static_url_path + '/<path:filename>',
                 endpoint='static',
                 view_func=app.send_static_file, subdomain='<institute>')

@app.url_value_preprocessor
def before_route(endpoint, values):
    # List of all endpoints that make use of subdomains in other cases remove if from parameters passed to the route

    subdomain_endpoints = ["pages.index",
                           "institute.retrieve",
                           "institute.edit",
                           "institute.add_user",
                           "institute.remove_user",
                           "institute.change_slug"
                           ]

    if endpoint not in subdomain_endpoints and values is not None:
        values.pop('institute', None)

@app.cli.command("reseed-database")
def reseed_database():
    import reseed

@app.cli.command("test-email")
@click.argument("email_to")
@click.argument("email_from")
@click.argument("subject")
@click.argument("body")
def test_email(email_to,email_from,subject,body):
    send_email(email_to,email_from,subject,body)

def send_email(email_to, email_from, subject, body):
    message_data = {'from': email_from,
       'to': email_to,
       'subject': subject,
       'html': body}
    message_data = {k: v for k, v in message_data.items() if v is not None}

    if not app.config.get('MAILGUN_API_URL') or not app.config.get('MAILGUN_API_KEY'):
        app.logger.warning('No MAILGUN_API_URL or MAILGUN_API_KEY provided. Dumping email contents: {}'.format(message_data))
        return
    
    response = requests.post("{}/messages".format(app.config.get('MAILGUN_API_URL')),
    auth=requests.auth.HTTPBasicAuth("api", app.config.get('MAILGUN_API_KEY')),
    data=message_data)
    response.raise_for_status()
    return response

@app.cli.command("test-s3")
@click.argument("file_name")
def test_s3(file_name):
    upload_to_s3(file_name)

def upload_to_s3(file_name, object_name=None):
    bucket_name = app.config.get('S3_BUCKET')
    if object_name is None:
        object_name = file_name
    if bucket_name is None:
        app.logger.warn('No S3_BUCKET specified in environment variables. File name to upload: {}'.format(object_name))
        return True
    s3_client = boto3.client('s3')
    try:
        response = s3_client.upload_file(file_name, bucket_name, object_name)
    except ClientError as e:
        app.logger.error(e)
        return False
    return True

@app.route('/')
def index():
    return routes.course.index()

def compile_sass():
    sass.compile(dirname=("static/assets/scss", 'static/css'))

@app.context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@app.context_processor
def inject_resume_video():
    segment_id = request.cookies.get('resume_segment_id', None)
    segment = datamodels.Segment.find_by_id(segment_id)
    place = request.cookies.get('resume_segment_place', None)
    return dict(last_segment=segment, last_segment_place=place)

@app.context_processor
def inject_current_section():
    app.logger.info(request.path)
    return dict(current_section=request.path.split('/')[1])

@app.context_processor
def inject_cache_code():
    return dict(cache_code=time.time())

@jinja2.contextfunction
def get_vars(c):
    if app.debug != True:
        return ""
    methods = []
    methods.append({'name': 'endpont', 'dump': request.endpoint})
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

@app.template_filter()
def join_names(users):
    if users is None:
        return ""
    names = []
    for user in users:
        names.append(user.full_name)
    return ", ".join(names)

@app.template_filter()
def cents_to_dolars(amount):
    return amount/100.0

@app.template_filter()
def format_time(seconds):
    t = str(datetime.timedelta(seconds=seconds)).split(':')
    hours = int(t[0])
    minutes = int(t[1])
    out = ""
    if hours > 0:
        out += "{} hour".format(hours)
        if hours > 1:
            out += "s"
    if hours > 0 and minutes > 0:
        out += ", "
    if minutes > 0:
        out += "{} minute".format(minutes)
        if minutes > 1:
            out += "s"
    return out

@app.template_filter()
def hhmmss(seconds):
    out = str(datetime.timedelta(seconds=seconds))
    if seconds < 3600:
        out = out[2:]

    return out if not out.startswith("0") else out[1:]

@app.template_filter()
def hhmm(seconds):
    out = str(datetime.timedelta(seconds=seconds)).split(":")
    return "{}:{}".format(out[0], out[1])

def uuid():
    return "{}".format(uuid4().hex)
app.jinja_env.globals.update(uuid=uuid)

def get_logo(*args, **kwargs):
    host_url = request.host_url.split("://")[1]
    host = host_url.split(".") if host_url else []
    if len(host) > 2:
        subdomain = host[0]
        institute = datamodels.Institute.find_by_slug(subdomain)

        if institute:
            logo_url = institute.logo_url
            if logo_url:
                return '<img src="{}">'.format(logo_url)

    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 897 1337"><path d="M896.926,417.590 L0.097,416.434 L0.056,119.532 L0.058,119.532 L0.024,119.525 L298.280,0.028 L297.542,119.532 L298.114,119.532 L298.088,119.525 L596.343,0.028 L596.792,119.532 L598.755,119.532 L598.721,119.525 L896.975,0.028 L896.926,417.590 ZM683.424,1022.533 L369.742,1023.094 L368.821,1336.982 L0.072,1335.695 L0.063,650.350 L683.424,650.350 L683.424,1022.533 ZM0.056,650.350 L0.063,650.350 L0.056,650.350 Z"></path></svg>'
app.jinja_env.globals.update(get_logo=get_logo)

def url4(*args, **kwargs):
    try:
        # For subdomains url_for is building url with server name and schema, and we would like to keep relative path.
        return url_for(*args, **kwargs).split(app.config["SERVER_NAME"])[-1]
    except BuildError as e:
        if app.debug:
            flash("{}".format(e))
        return "#"
app.jinja_env.globals.update(url_for=url4)

def url_is(*endpoints):
    return (request.endpoint in endpoints)
app.jinja_env.globals.update(url_is=url_is)

def teacher_of(course):
    current_user = get_current_user()
    return current_user and current_user.teaches(course)
app.jinja_env.globals.update(teacher_of=teacher_of)

# This route needs to live here forever because it requires access to the app.
@app.route('/api', methods=["GET"])
def api():
    docs = routes.dump_api(app)
    return render_template('url_fors.html', controllers=docs)

if __name__ == "__main__":
    app.logger.info("Building SASS")
    compile_sass()

    if app.debug:
        from livereload import Server, shell

        def ignore_func(path):
            if path.split('.')[-1] == "sqlite":
                return True
        server = Server(app.wsgi_app)
        server.watch('./static/assets/scss/*', compile_sass)
        server.watch('./', ignore=ignore_func)
        server.serve(host='0.0.0.0', open_url=False, port=5000)
    else:
        app.run(host='0.0.0.0', port=5000) # until we start using gunicorn
