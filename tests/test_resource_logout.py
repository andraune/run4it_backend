import pytest
from run4it.api.user.model import User
from run4it.api.user.resource import Logout, LogoutRefresh
from run4it.api.token import TokenRegistry
from .helpers import get_response_json, get_authorization_header, register_confirmed_user, register_and_login_confirmed_user


@pytest.mark.usefixtures('db')
class TestLoginResource:

	def test_logout_content_type_is_json(self, api, client):
		url = api.url_for(Logout)
		response = client.delete(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_logout_not_logged_in(self, api, client):
		url = api.url_for(Logout)
		response = client.delete(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_logout_with_access_token(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "logout", "log@out.com", "passwd")
		url = api.url_for(Logout)
		response = client.delete(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["messages"]["logout"] is not None)

	def test_logout_with_refresh_token(self, api, client):
		_,refreshtoken = register_and_login_confirmed_user(api, client, "logout", "log@out.com", "passwd")
		url = api.url_for(Logout)
		response = client.delete(url, headers=get_authorization_header(refreshtoken))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_logout_not_supported(self, api, client):
		url = api.url_for(Logout)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_logout_not_supported(self, api, client):
		url = api.url_for(Logout)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_post_logout_not_supported(self, api, client):
		url = api.url_for(Logout)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_logoutrefresh_content_type_is_json(self, api, client):
		url = api.url_for(LogoutRefresh)
		response = client.delete(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_logoutrefresh_not_logged_in(self, api, client):
		url = api.url_for(LogoutRefresh)
		response = client.delete(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_logoutrefresh_with_refresh_token(self, api, client):
		_,refreshtoken = register_and_login_confirmed_user(api, client, "logout", "log@out.com", "passwd")
		url = api.url_for(LogoutRefresh)
		response = client.delete(url, headers=get_authorization_header(refreshtoken))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["messages"]["logout"] is not None)

	def test_logoutrefresh_with_access_token(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "logout", "log@out.com", "passwd")
		url = api.url_for(LogoutRefresh)
		response = client.delete(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_logoutrefresh_not_supported(self, api, client):
		url = api.url_for(LogoutRefresh)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_logoutrefresh_not_supported(self, api, client):
		url = api.url_for(LogoutRefresh)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_post_logoutrefresh_not_supported(self, api, client):
		url = api.url_for(LogoutRefresh)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed
