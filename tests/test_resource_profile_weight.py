import pytest
import datetime as dt
from run4it.api.user.resource import User
from run4it.api.profile.resource import ProfileWeight
from .helpers import get_response_json, register_confirmed_user, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestProfileWeightHistoryResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileWeight, username="tyson")
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_profileweight_not_logged_in(self, api, client):
		url = api.url_for(ProfileWeight, username="tyson")
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_profileweight_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		url = api.url_for(ProfileWeight, username="tyson")
		profile = User.find_by_username("tyson").profile
		profile.set_weight(101.0)
		profile.save()
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]["weight"] == 101.0)

	def test_get_profileweight_no_data(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		url = api.url_for(ProfileWeight, username="tyson")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 0)

	def test_get_profileweight_several_items(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		url = api.url_for(ProfileWeight, username="tyson")
		profile = User.find_by_username("tyson").profile
		profile.set_weight(101.0)
		profile.set_weight(99.9)
		profile.set_weight(106.1)
		profile.save()
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 3)
		assert(response_json[0]["weight"] == 101.0)
		assert(response_json[1]["weight"] == 99.9)
		assert(response_json[2]["weight"] == 106.1)

	def test_get_profileweight_only_single_user_data_is_returned(self, api, client):
		register_confirmed_user("another", "an@other.com", "different")
		other_profile = User.find_by_username("another").profile
		other_profile.set_weight(66.6)
		other_profile.save()
	
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		profile = User.find_by_username("tyson").profile
		profile.set_weight(101.0)
		profile.save()

		url = api.url_for(ProfileWeight, username="tyson")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]["weight"] == 101.0)

	def test_get_profileweight_for_another_user(self, api, client):
		register_confirmed_user("another", "an@other.com", "different")
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		url = api.url_for(ProfileWeight, username="another")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_get_profileweight_for_nonexistant_user(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "tyson", "mike@tyson.com", "knockout", 178, 95.0, dt.date(1966, 6, 30))
		url = api.url_for(ProfileWeight, username="nouser")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_put_profileweight_weight_not_supported(self, api, client):
		url = api.url_for(ProfileWeight, username="profiler")
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_post_profileweight_weight_not_supported(self, api, client):
		url = api.url_for(ProfileWeight, username="profiler")
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_profileweight_not_supported(self, api, client):
		url = api.url_for(ProfileWeight, username="profiler")
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
