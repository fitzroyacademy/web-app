from flask import session

import datamodels


def get_current_user():
    if "user_id" in session:
        return datamodels.get_user(session["user_id"])
    else:
        return None


def get_institute_from_url(request):
    host_url = request.host_url.split("://")[1]
    host = host_url.split(".") if host_url else []

    subdomain = host[0] if len(host) > 2 else ""

    return datamodels.Institute.find_by_slug(subdomain) if subdomain else None
