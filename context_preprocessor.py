import time

from flask import Blueprint, request, current_app

import datamodels
from utils.base import get_current_user, get_institute_from_url

bp = Blueprint("context_preprocessor", __name__)

@bp.app_context_processor
def inject_current_user():
    return dict(current_user=get_current_user())

@bp.app_context_processor
def inject_institute():
    return dict(current_institute=get_institute_from_url(request))

@bp.app_context_processor
def inject_resume_video():
    segment_id = request.cookies.get('resume_segment_id', None)
    segment = datamodels.Segment.find_by_id(segment_id)
    place = request.cookies.get('resume_segment_place', None)
    return dict(last_segment=segment, last_segment_place=place)

@bp.app_context_processor
def inject_current_section():
    current_app.logger.info(request.path)
    return dict(current_section=request.path.split('/')[1])

@bp.app_context_processor
def inject_cache_code():
    return dict(cache_code=time.time())