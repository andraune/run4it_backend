import json
from run4it.api.user.model import User
from run4it.api.user.resource import Login
from run4it.api.profile.model import Profile


def get_response_json(response_data):
    return json.loads(response_data.decode("utf-8"))

def register_confirmed_user(username, email, password):
	user = User(username, email, password)
	user.confirmed = True
	profile = Profile(user)
	user.save()
	profile.save()

def register_and_login_confirmed_user(username, email, password, testapi, testclient):
	register_confirmed_user(username, email, password)
	url = testapi.url_for(Login)
	response = testclient.post(url, data={"email": email, "password": password })
	response_json = get_response_json(response.data)
	return response_json["accessToken"]
