import pytest
import datetime as dt
from run4it.api.token.resource import Token
from .helpers import get_response_json, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestTokenResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Token)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_tokens_not_logged_in(self, api, client):
		url = api.url_for(Token)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_tokens_logged_in(self, api, client):
		token = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 2) # one access token and one refresh token created at login
		
