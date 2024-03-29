import re
from glob import glob

from flask import render_template, redirect

import datamodels
from dataforms import LoginForm, AjaxCSRFTokenForm
from .blueprint import SubdomainBlueprint

blueprint = SubdomainBlueprint("pages", __name__)


@blueprint.subdomain_route("/")
def index(institute=""):
    """ Shows all courses the user has access to. """
    data = {
        "public_courses": datamodels.list_public_courses(institute_slug=institute),
        "form": LoginForm(),
    }

    return render_template("welcome.html", **data)


########
# Maybe a bit too much magic; best not to look past this comment.
########


def _bind_render(s, p):
    data = {"form": None}

    def fun():
        data["form"] = AjaxCSRFTokenForm()
        return render_template("static/{}/{}.html".format(s, p), **data)

    return fun


def get_static_paths(relative_path):
    """
    Do a glob on static template files and organize them by section.
    """
    paths = {}
    for line in glob("{}/**/*.html".format(relative_path)):
        line = re.sub(r"^{}\/".format(relative_path), "", line)  # Base path
        line = re.sub(r"\.html$", "", line)  # Strip file extension
        line = line.split("/")
        if line[0] not in paths:
            paths[line[0]] = []
        paths[line[0]].append(line[1])
    return paths


def attach_static_paths(app, relative_path):
    """
    Make url_for paths for all the static pages so we can do active link
    stuff.
    """
    paths = get_static_paths(relative_path)
    for section, pages in paths.items():
        bp = SubdomainBlueprint(section, section)
        for page in pages:
            if page == "index":
                path = "/{}".format(section)
            else:
                path = "/{}/{}".format(section, page)
            f = _bind_render(section, page)
            bp.add_url_rule(path, page, f)
        app.register_blueprint(bp)

    @blueprint.route("/static")
    def sitemap():
        if app.debug is not True:
            return redirect("404")
        return render_template("static/sitemap.html", pages=paths)
