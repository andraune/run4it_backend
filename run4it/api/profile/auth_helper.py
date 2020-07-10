from flask_jwt_extended import get_jwt_identity
from run4it.api.templates import report_error_and_abort
from run4it.api.user import User

def get_auth_profile_or_abort(username, module_name="profile"):
	auth_username = get_jwt_identity()
	if auth_username != username:
		report_error_and_abort(422, module_name, "Profile not found")

	user = User.find_by_username(auth_username)
	if user.profile is None: # should not be possible to have a user without a profile
		report_error_and_abort(422, module_name, "Profile not found")

	return user.profile
