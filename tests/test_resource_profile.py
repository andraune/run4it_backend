import pytest
import datetime as dt
from run4it.api.user.resource import User
from run4it.api.profile.resource import Profile
from .helpers import get_response_json, register_confirmed_user, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestProfileResource:

	def test_content_type_is_json(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_profile_not_logged_in(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_profile_logged_in(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["username"] == 'profiler')
		assert(response_json["height"] == 179)
		assert(response_json["weight"] == 75)
		assert(str(response_json["birthDate"]) == '1980-02-29')

	def test_get_profile_data_not_set(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd")
		url = api.url_for(Profile, username="profiler")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["username"] == 'profiler')
		assert(response_json["height"] is None)
		assert(response_json["weight"] is None)
		assert(response_json["birthDate"] is None)

	def test_get_profile_for_another_user(self, api, client):
		register_confirmed_user("another", "an@other.com", "different")
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd")
		url = api.url_for(Profile, username="another")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_get_profile_for_nonexistant_user(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd")
		url = api.url_for(Profile, username="nouser")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_update_profile_not_logged_in(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.put(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_update_profile_username_not_allowed_in_json_data(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "username":"smart" }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["username"] is not None)

	def test_update_profile_height(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "height":180 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["height"] == 180)

	def test_update_profile_height_to_none(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "height":0 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["height"] is None)

	def test_update_height_out_of_range(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "height":300 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["height"] is not None)		

	def test_update_profile_weight(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "weight":76.3 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["weight"] == 76.3)

	def test_update_weight_to_none(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "weight":0 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["weight"] is None)
	
	def test_update_height_out_of_range(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "weight":1000.0 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["weight"] is not None)

	def test_update_birth_date(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "birthDate":"2001-02-03" }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["birthDate"] == '2001-02-03')		
	
	def test_update_birth_date_too_old(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "birthDate":"1899-12-31" }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["birthDate"] is not None)		

	def test_update_birth_date_future(self, api, client):
		tomorrow = dt.date.today() + dt.timedelta(days=1)
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "birthDate": str(tomorrow) }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["birthDate"] is not None)

	def test_update_many_params_in_same_request(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		response = client.put(url, data={ "birthDate":"2001-02-03", "height":180, "weight":70.1 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["birthDate"] == '2001-02-03')
		assert(response_json["height"] == 180)
		assert(response_json["weight"] == 70.1)

	def test_update_profile_actually_saved(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		profile = User.find_by_username("profiler").profile
		old_updated_at = profile.updated_at
		response = client.put(url, data={ "birthDate":"2001-02-03", "height":180, "weight":70.1 }, headers=get_authorization_header(token))
		assert(profile.height == 180)
		assert(profile.weight == 70.1)
		assert(str(profile.birth_date) == "2001-02-03")
		assert(profile.updated_at > old_updated_at)

	def test_no_update_if_no_data(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd", 179, 75.0, dt.date(1980, 2, 29))
		url = api.url_for(Profile, username="profiler")
		profile = User.find_by_username("profiler").profile
		old_updated_at = profile.updated_at
		response = client.put(url, headers=get_authorization_header(token))
		assert(response.status_code == 200)
		assert(profile.height == 179)
		assert(str(profile.birth_date) == "1980-02-29")
		assert(profile.updated_at == old_updated_at)

	def test_update_another_user_profile(self, api, client):
		register_confirmed_user("another", "an@other.com", "different")
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd")
		url = api.url_for(Profile, username="another")
		response = client.put(url, data={ "height":180 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_update_nonexistant_user_profile(self, api, client):
		token = register_and_login_confirmed_user(api, client, "profiler", "pro@filer.com", "passwd")
		url = api.url_for(Profile, username="nouser")
		response = client.put(url, data={ "height":180 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["profile"] is not None)

	def test_post_profile_not_supported(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_profile_not_supported(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

