import pytest
from run4it.api.api_v1 import ApiVersion
from .helpers import get_response_json


class TestApiResource:

    def test_content_type_is_json(self, api, client):
        url = api.url_for(ApiVersion)
        response = client.get(url)
        assert(response.headers["Content-Type"] == 'application/json')

    def test_get_api_version(self, api, client):
        url = api.url_for(ApiVersion)
        response = client.get(url)
        response_json = get_response_json(response.data)
        assert(response.status_code == 200)
        assert(response_json["version"] == 1)
        assert(response_json["env"] == "test")

    def test_post_api_not_supported(self, api, client):
        url = api.url_for(ApiVersion)
        response = client.post(url)
        assert(response.status_code == 405) # not allowed        

    def test_put_api_not_supported(self, api, client):
        url = api.url_for(ApiVersion)
        response = client.put(url)
        assert(response.status_code == 405) # not allowed

    def test_delete_api_not_supported(self, api, client):
        url = api.url_for(ApiVersion)
        response = client.delete(url)
        assert(response.status_code == 405) # not allowed

    def test_api_catch_404s(self, api, client):
        url = '{0}{1}'.format(api.url_for(ApiVersion), 'nonexistant-file')
        response = client.get(url)
        response_json = get_response_json(response.data)
        assert(response.status_code == 404)
        assert("URL was not found" in response_json["message"] )
