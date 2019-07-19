from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels

blueprint = Blueprint('error', __name__, template_folder='templates')


@blueprint.route('/404')
@blueprint.errorhandler(404)
def fourohfour(e):
    """ For when the user has made a mistake or the file is not found. """
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