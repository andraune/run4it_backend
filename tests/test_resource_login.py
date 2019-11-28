import pytest
from run4it.api.user.model import User
from run4it.api.user.resource import Login
from .helpers import get_response_json, register_confirmed_user


@pytest.mark.usefixtures('db')
class TestLoginResource:

	def setup(self):
		register_confirmed_user("confirmedUser", "confirmedUser@mail.com", "confirmed123")

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Login)
		response = client.post(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_login_user_by_post(self, api, client):
		url = api.url_for(Login)
		response = client.post(url, data={"email": "confirmedUser@mail.com", "password": "confirmed123" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["accessToken"] != '')
		assert(response_json["refreshToken"] != '')
		assert(response_json["username"] == 'confirmedUser')

	def test_login_unconfirmed_user(self, api, client):
		user = User("unconfirmedUser", "unconfirmedUser@mail.com", "unconfirmed123")
		user.save()	
		url = api.url_for(Login)
		response = client.post(url, data={"email": "unconfirmedUser@mail.com", "password": "unconfirmed123" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["login"] is not None)

	def test_login_user_incorrect_password(self, api, client):
		url = api.url_for(Login)
		response = client.post(url, data={"email": "confirmedUser@mail.com", "password": "incorrect" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["login"] is not None)

	def test_get_login_not_supported(self, api, client):
		url = api.url_for(Login)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_login_not_supported(self, api, client):
		url = api.url_for(Login)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_login_not_supported(self, api, client):
		url = api.url_for(Login)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
