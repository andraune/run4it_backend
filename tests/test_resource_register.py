import pytest
from run4it.api.user.model import User, UserConfirmation
from run4it.api.user.resource import Register
from run4it.api.profile.model import Profile
from .helpers import get_response_json


@pytest.mark.usefixtures('db')
class TestRegisterResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Register)
		response = client.post(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_register_user_by_post(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "user@mail.com", "password": "password123" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 201)
		assert(response_json["accessToken"] == '') # no access until account has been activated
		assert(response_json["refreshToken"] == '')
		assert(response_json["confirmed"] == False)
		assert(response_json["email"] == 'user@mail.com')
		assert(response_json["username"] == 'theUser')

	def test_register_user_creates_userprofile(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "user@mail.com", "password": "password123" })
		assert(response.status_code == 201)
		user = User.find_by_username("theUser")
		assert(user is not None)
		assert(user.profile is not None)
		assert(user.profile.username == user.username)

	def test_register_creates_confirmation_code(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "user@mail.com", "password": "password123" })
		assert(response.status_code == 201)
		userConf = UserConfirmation.find_by_username("theUser")
		assert(userConf is not None)
		assert(len(userConf.code) >= 32)

	def test_register_user_email_required(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "password": "password123"})
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["email"] is not None)

	def test_register_user_email_format(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "invalid@format", "password": "password123"})
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["email"] is not None)

	def test_register_user_username_required(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"email": "user@mail.com", "password": "password123"})
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["username"] is not None)
	
	def test_register_user_username_length(self, api, client):
		url = api.url_for(Register)
		response1 = client.post(url, data={"username": "usr", "email": "user@mail.com", "password": "password123"})
		response_json1 = get_response_json(response1.data)
		assert(response1.status_code == 422)
		assert(response_json1["errors"]["username"] is not None)
		response2 = client.post(url, data={"username": "tooManyCharsInNam", "email": "user@mail.com", "password": "password123"})
		response_json2 = get_response_json(response2.data)
		assert(response2.status_code == 422)
		assert(response_json2["errors"]["username"] is not None)

	def test_register_user_username_invalid_chars(self, api, client):
		url = api.url_for(Register)
		response1 = client.post(url, data={"username": "_invalidFirstChar", "email": "user@mail.com", "password": "password123"})
		response2 = client.post(url, data={"username": "invalid%Name", "email": "user@mail.com", "password": "password123"})
		response3 = client.post(url, data={"username": "invalid Space", "email": "user@mail.com", "password": "password123"})
		assert(response1.status_code == 422)
		assert(response2.status_code == 422)
		assert(response3.status_code == 422)

	def test_register_user_username_valid_names(self, api, client):
		url = api.url_for(Register)
		response1 = client.post(url, data={"username": "valid_Name", "email": "user1@mail.com", "password": "password123"})
		response2 = client.post(url, data={"username": "v_As", "email": "user2@mail.com", "password": "password123"})
		response3 = client.post(url, data={"username": "validNameWith___", "email": "user3@mail.com", "password": "password123"})
		assert(response1.status_code == 201)
		assert(response2.status_code == 201)
		assert(response3.status_code == 201)

	def test_register_user_password_required(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "user@mail.com"})
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["password"] is not None)

	def test_register_user_password_length(self, api, client):
		url = api.url_for(Register)
		response = client.post(url, data={"username": "theUser", "email": "user@mail.com", "password": "penis"})
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["password"] is not None)

	def test_get_register_not_supported(self, api, client):
		url = api.url_for(Register)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_register_not_supported(self, api, client):
		url = api.url_for(Register)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_register_not_supported(self, api, client):
		url = api.url_for(Register)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
