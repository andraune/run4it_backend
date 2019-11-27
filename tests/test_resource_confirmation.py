import pytest
import datetime as dt
from run4it.api.user.model import User, UserConfirmation
from run4it.api.user.resource import Confirmation
from .helpers import get_response_json


@pytest.mark.usefixtures('db')
class TestConfirmationResource:

	def setup(self):
		user = User("confUser", "confUser@mail.com", "password123")
		user.save()
		userConf = UserConfirmation("confUser", "correctConfirmationCode")
		userConf.save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_confirm_user_by_post(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "confUser", "confirmationCode": "correctConfirmationCode" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["accessToken"] == '') # no access until account has been activated
		assert(response_json["refreshToken"] == '')
		assert(response_json["confirmed"] == True)
		assert(response_json["email"] == 'confUser@mail.com')
		assert(response_json["username"] == 'confUser')

	def test_confirm_user_deletes_confirmation_code_record(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "confUser", "confirmationCode": "correctConfirmationCode" })
		response_json = get_response_json(response.data)
		conf_record = UserConfirmation.find_by_username("confUser")
		assert(response.status_code == 200)
		assert(conf_record is None)

	def test_confirmation_username_required(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "confirmationCode": "correctConfirmationCode" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["username"] is not None)

	def test_confirmation_code_required(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "confUser" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["confirmationCode"] is not None)

	def test_confirmation_invalid_username(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "noUser", "confirmationCode": "correctConfirmationCode" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["confirmation"] is not None)     

	def test_confirmation_valid_user_no_confirmation_registered(self, api, client):
		user = User("noConfUser", "noConfUser@mail.com", "password123")
		user.save()
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "noConfUser", "confirmationCode": "correctConfirmationCode" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["confirmation"] is not None)      

	def test_confirmation_incorrect_code(self, api, client):
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "confUser", "confirmationCode": "incorrect" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["confirmation"] is not None)

	def test_confirmation_code_expired(self, api, client):
		user = User("expiredUser", "expired@mail.com", "password123")
		user.save()        
		userConf = UserConfirmation("expiredUser", "expiredCode")
		userConf.created_at = dt.datetime.utcnow() - dt.timedelta(hours = 2)
		userConf.save()
		url = api.url_for(Confirmation)
		response = client.post(url, data={ "username": "expiredUser", "confirmationCode": "expiredCode" })
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["confirmation"] is not None)

	def test_get_register_not_supported(self, api, client):
		url = api.url_for(Confirmation)
		response = client.get(url)
		assert(response.status_code == 405) # not allowed

	def test_put_register_not_supported(self, api, client):
		url = api.url_for(Confirmation)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_register_not_supported(self, api, client):
		url = api.url_for(Confirmation)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

