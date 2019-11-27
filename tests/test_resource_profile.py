import pytest
from run4it.api.profile.resource import Profile
from .helpers import get_response_json, register_and_login_confirmed_user


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
		token = register_and_login_confirmed_user("profiler", "pro@filer.com", "passwd", api, client)
		url = api.url_for(Profile, username="profiler")
		response = client.get(url, headers={'Authorization': 'Bearer {}'.format(token)})
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json["username"] == 'profiler')

	def test_post_profile_not_supported(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_put_login_not_supported(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_register_not_supported(self, api, client):
		url = api.url_for(Profile, username="profiler")
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

