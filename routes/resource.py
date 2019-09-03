from flask import Blueprint, redirect, abort
from util import get_current_user
import datamodels

blueprint = Blueprint('resource', __name__, template_folder='templates')

@blueprint.route('<resource_id>')
def view(resource_id):
	"""
	Proxy for resource links which logs access then redirects the user.
	"""
	resource = datamodels.Resource.find_by_id(resource_id)
	if resource is None:
		abort(404)
	user = get_current_user()
	if user is not None:
		resource.log_user_view(user)
	else:
		resource.log_anonymous_view()
	return redirect(resource.url)