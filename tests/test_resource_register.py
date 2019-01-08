import pytest
import json
from run4it.api.user.resource import Register


@pytest.mark.usefixtures('db')
class TestRegisterResource:

    def test_content_type_is_json(self, api, client):
        url = api.url_for(Register)
        response = client.post(url)
        assert(response.headers["Content-Type"] == 'application/json')

    
    # find out how to add data to request. Should ignore non-json content-type.
    # test a valid request, then test with invalid data.
    
    def test_username_is_required(self, api, client):
        url = api.url_for(Register)
        response = client.post(url)
        response_json = json.loads(response.data)
        assert(response.status_code == 200)
        assert(response_json["version"] == 1)

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
