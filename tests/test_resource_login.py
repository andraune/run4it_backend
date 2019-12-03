import pytest
import datetime as dt
from run4it.api.user.model import User
from run4it.api.user.resource import Login, LoginRefresh
from run4it.api.token import TokenRegistry
from .helpers import get_response_json, get_authorization_header, register_confirmed_user, register_and_login_confirmed_user


@pytest.mark.usefixtures('db')
class TestLoginResource:

	def setup(self):
		register_confirmed_user("confirmedUser", "confirmedUser@mail.com", "confirmed123")

	def test_login_content_type_is_json(self, api, client):
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

	def test_loginrefresh_content_type_is_json(self, api, client):
		url = api.url_for(LoginRefresh)
		response = client.post(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_loginrefresh_not_logged_in(self, api, client):
		tokens_before_req = TokenRegistry.query.count()
		url = api.url_for(LoginRefresh)
		response = client.post(url)
		response_json = get_response_json(response.data)
		tokens_after_req = TokenRegistry.query.count()
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)
		assert(tokens_before_req == tokens_after_req)

	def test_loginrefresh_logged_in(self, api, client):
		_,refreshtoken = register_and_login_confirmed_user(api, client, "refresher", "re@fresh.com", "passwd")
		url = api.url_for(LoginRefresh)
		response = client.post(url, headers=get_authorization_header(refreshtoken))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["accessToken"] != '')
		assert(response_json["refreshToken"] == '')

	def test_loginrefresh_token_generated(self, api, client):
		_,refreshtoken = register_and_login_confirmed_user(api, client, "refresher", "re@fresh.com", "passwd")
		url = api.url_for(LoginRefresh)
		tokens_before_req = TokenRegistry.query.filter_by(token_type="access").count()
		refresh_before_req = TokenRegistry.query.filter_by(token_type="refresh").count()
		client.post(url, headers=get_authorization_header(refreshtoken))
		tokens_after_req = TokenRegistry.query.filter_by(token_type="access").count()
		refresh_after_req = TokenRegistry.query.filter_by(token_type="refresh").count()
		assert((tokens_before_req + 1) == tokens_after_req)
		assert(refresh_before_req == refresh_after_req)

	def test_token_loginrefresh_revoked_refreshtoken(self, api, client):
		_,refreshtoken = register_and_login_confirmed_user(api, client, "refresher", "re@fresh.com", "passwd")
		stored_token = TokenRegistry.get_by_id(2)
		assert(stored_token.token_type == "refresh")
		stored_token.revoked = True
		stored_token.save()
		url = api.url_for(LoginRefresh)
		response = client.post(url, headers=get_authorization_header(refreshtoken))
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_loginrefresh_not_supported(self, api, client):
		url = api.url_for(LoginRefresh)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_loginrefresh_not_supported(self, api, client):
		url = api.url_for(LoginRefresh)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_loginrefresh_not_supported(self, api, client):
		url = api.url_for(LoginRefresh)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed