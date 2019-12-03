import pytest
import datetime as dt
from run4it.api.token.model import TokenRegistry
from run4it.api.token.resource import Token
from .helpers import get_response_json, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestTokenResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Token, token_id=1)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_token_not_logged_in(self, api, client):
		url = api.url_for(Token, token_id=1)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_token_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=1)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert("jti" not in response_json)
		assert(response_json["id"] == 1)
		assert(response_json["tokenType"] in ("access", "refresh"))
		assert(response_json["username"] == "tokenreader")
		assert(response_json["revoked"] == False)
		assert(response_json["expires"] is not None)

	def test_get_other_user_token(self, api, client):
		new_token = TokenRegistry('12345', 'access', 'another_user', False, dt.datetime.now() + dt.timedelta(hours=1))
		new_token.save()
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=new_token.id)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 403)
		assert(response_json["errors"]["token"] is not None)

	def test_request_nonexisting_token(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=999)
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["token"] is not None)		

	def test_delete_token_not_logged_in(self, api, client):
		url = api.url_for(Token, token_id=2)
		response = client.delete(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_delete_token_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=2)
		response = client.delete(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["message"] is not None)
		assert(TokenRegistry.get_by_id(1) is not None)
		assert(TokenRegistry.get_by_id(2) is None) # should have been deleted

	def test_delete_other_user_token(self, api, client):
		new_token = TokenRegistry('12345', 'access', 'another_user', False, dt.datetime.now() + dt.timedelta(hours=1))
		new_token.save()
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=new_token.id)
		response = client.delete(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 403)
		assert(response_json["errors"]["token"] is not None)

	def test_delete_nonexisting_token(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=999)
		response = client.delete(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["token"] is not None)

	def test_update_token_not_logged_in(self, api, client):
		url = api.url_for(Token, token_id=2)
		response = client.put(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_update_token_revoke(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=2)
		response = client.put(url, data={'revoked' : 'True'}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["revoked"] == True)

	def test_update_token_unrevoke(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		update_token = TokenRegistry.get_by_id(2)
		update_token.revoked = True
		url = api.url_for(Token, token_id=2)
		response = client.put(url, data={'revoked' : 'False'}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["revoked"] == False)

	def test_update_token_actually_saved(self, api, client):
		update_token = TokenRegistry('jti', 'access', 'tokenreader', False, dt.datetime(2001, 1, 2, 12, 11, 10, 9))
		update_token.save()
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=update_token.id)
		response = client.put(url, data={'revoked':'True','jti':'newjti','tokenType':'refresh','username':'newuser','expires':str(dt.datetime(2002, 2, 3, 16, 15, 14, 13))}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(update_token.jti == 'jti')
		assert(update_token.token_type == 'access')
		assert(update_token.username == 'tokenreader')
		assert(update_token.revoked == True)
		assert(update_token.expires == dt.datetime(2001, 1, 2, 12, 11, 10, 9))

	def test_update_other_user_token(self, api, client):
		new_token = TokenRegistry('12345', 'access', 'another_user', False, dt.datetime.now() + dt.timedelta(hours=1))
		new_token.save()
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=new_token.id)
		response = client.put(url, data={'revoked' : 'True'}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 403)
		assert(response_json["errors"]["token"] is not None)

	def test_update_nonexisting_token(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tokenreader", "token@reader.com", "passwd")
		url = api.url_for(Token, token_id=999)
		response = client.put(url, data={'revoked' : 'True'}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["token"] is not None)

	def test_post_token_not_supported(self, api, client):
		url = api.url_for(Token, token_id=1)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed
