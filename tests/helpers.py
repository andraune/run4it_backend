import json
from run4it.api.user.model import User
from run4it.api.user.resource import Login
from run4it.api.profile.model import Profile


def get_response_json(response_data):
    return json.loads(response_data.decode("utf-8"))

def register_confirmed_user(username, email, password, height=None, birth_date=None):
	user = User(username, email, password)
	user.confirmed = True
	profile = Profile(user)
	profile.height = height
	profile.birth_date = birth_date
	user.save()
	profile.save()

def register_and_login_confirmed_user(testapi, testclient, username, email, password, height=None, birth_date=None):
	register_confirmed_user(username, email, password, height, birth_date)
	url = testapi.url_for(Login)
	response = testclient.post(url, data={"email": email, "password": password })
	response_json = get_response_json(response.data)
	return response_json["accessToken"]

def get_authorization_header(token):
	return {'Authorization': 'Bearer {}'.format(token)}
