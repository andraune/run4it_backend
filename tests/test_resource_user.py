import pytest
import datetime as dt
from run4it.api.user.resource import UserResource
from run4it.api.profile.resource import Profile
from .helpers import get_response_json, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestUserResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(UserResource)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_user_not_logged_in(self, api, client):
		url = api.url_for(UserResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_user_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "theUser", "user@user.com", "passwd")
		url = api.url_for(UserResource)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["username"] == 'theUser')
		assert(response_json["accessToken"] == '')
		assert(response_json["refreshToken"] == '')

	def test_delete_user_not_supported(self, api, client):
		url = api.url_for(UserResource, username="theUser")
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

	def test_post_user_not_supported(self, api, client):
		url = api.url_for(UserResource, username="theUser")
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_put_user_not_supported(self, api, client):
		url = api.url_for(UserResource, username="theUser")
		response = client.put(url)
		assert(response.status_code == 405) # not allowed
