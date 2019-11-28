import json

from flask import Blueprint, session, request

import datamodels
from utils.database import dump

blueprint = Blueprint("log", __name__, template_folder="templates")


@blueprint.route("/event/<event_type>", methods=["POST"])
def add_event(event_type):
    """
    Log an event triggered by the current user to the database if
    it's the right type, or just some random logfile if it's not.
    """
    user = None
    if "user_id" in session:
        user = datamodels.get_user(session["user_id"])
    if event_type == "progress":
        segment_id = request.form["segment_id"]
        progress = int(request.form["percent"])
        if user is not None:
            user_id = user.id
            progress = request.form["percent"]
            seg = datamodels.get_segment(segment_id)
            sup = seg.save_user_progress(user, progress)
            d = {
              'segment_id': segment_id,
              'user_id': user_id,
              'user_status': seg.user_status(user)
            }
            return json.dumps(d)
        else:
            sess = session.get("anon_progress", "{}")
            d = json.loads(sess)
            if segment_id not in d or d[segment_id] < progress:
                d[segment_id] = progress
            session["anon_progress"] = json.dumps(d)
            d = {
              'segment_id': segment_id,
              'user_id': user_id,
              'user_status': seg.user_status(user=None, progress=progress)
            }
            return json.dumps(d)
    else:
        return event_type
