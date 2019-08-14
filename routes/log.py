from flask import Blueprint, render_template, session, request, url_for, redirect, flash
import datamodels

blueprint = Blueprint('log', __name__, template_folder='templates')

@blueprint.route('/event/<event_type>', methods=["POST"])
def add_event(event_type):
    """
    Log an event triggered by the current user to the database if
    it's the right type, or just some random logfile if it's not.
    """
    user = None
    if 'user_id' in session:
        user = datamodels.get_user(session['user_id'])
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