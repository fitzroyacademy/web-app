import datetime

from uuid import uuid4

import jinja2
from flask import Blueprint, request

blueprint = Blueprint("filters", __name__)


@jinja2.contextfilter
@blueprint.app_template_filter()
def join_names(context, users):
    if users is None:
        return ""
    names = []
    for user in users:
        names.append(user.full_name)
    return ", ".join(names)


@jinja2.contextfilter
@blueprint.app_template_filter()
def cents_to_dolars(context, amount):
    return amount / 100.0


@jinja2.contextfilter
@blueprint.app_template_filter()
def format_time(context, seconds):
    t = str(datetime.timedelta(seconds=seconds)).split(":")
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


@jinja2.contextfilter
@blueprint.app_template_filter()
def hhmmss(context, seconds):
    out = str(datetime.timedelta(seconds=seconds))
    if seconds < 3600:
        out = out[2:]

    return out if not out.startswith("0") else out[1:]


@jinja2.contextfilter
@blueprint.app_template_filter()
def hhmm(context, seconds):
    out = str(datetime.timedelta(seconds=seconds)).split(":")
    return "{}:{}".format(out[0], out[1])


@jinja2.contextfilter
@blueprint.app_template_global()
def get_logo(institute):
    if institute:
        logo_url = institute.logo_url
        if logo_url:
            return '<img src="{}">'.format(logo_url)

    return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 897 1337"><path d="M896.926,417.590 L0.097,416.434 L0.056,119.532 L0.058,119.532 L0.024,119.525 L298.280,0.028 L297.542,119.532 L298.114,119.532 L298.088,119.525 L596.343,0.028 L596.792,119.532 L598.755,119.532 L598.721,119.525 L896.975,0.028 L896.926,417.590 ZM683.424,1022.533 L369.742,1023.094 L368.821,1336.982 L0.072,1335.695 L0.063,650.350 L683.424,650.350 L683.424,1022.533 ZM0.056,650.350 L0.063,650.350 L0.056,650.350 Z"></path></svg>'


@jinja2.contextfilter
@blueprint.app_template_global()
def uuid():
    return "{}".format(uuid4().hex)


@jinja2.contextfilter
@blueprint.app_template_global()
def url_is(*endpoints):
    return (request.endpoint in endpoints)
