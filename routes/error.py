from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels
import jinja2

blueprint = Blueprint('error', __name__, template_folder='templates')


@blueprint.route('/404')
def fourohfour(e):
    """
    For when the user has made a mistake or the file is not found.

    This will try to find a static file that meets the request
    parameters and return a 200 if one exists.
    """
    try:
        return render_template('static'+request.path+'.html')
    except jinja2.exceptions.TemplateNotFound:
        try:
            return render_template('static'+request.path+'/index.html')
        except jinja2.exceptions.TemplateNotFound:
            return render_template('404.html'), 404

@blueprint.errorhandler(Exception)
@blueprint.route('/502')
def fiveohtwo(e):
    """ For when something bad happens to the server. """
    log_error(e)
    return render_template('502.html')   