import pytest
import json
from run4it.api.profile.resource import Profile


@pytest.mark.usefixtures('db')
class TestRegisterResource:

    def test_content_type_is_json(self, api, client):
        url = api.url_for(Profile)
        response = client.get(url)
        assert(response.headers["Content-Type"] == 'application/json')
