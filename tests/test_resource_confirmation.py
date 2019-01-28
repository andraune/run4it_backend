import pytest
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
        response = client.post(url, data={"username": "confUser", "confirmationCode": "correctConfirmationCode" })
        response_json = get_response_json(response.data)
        assert(response.status_code == 200)
        assert(response_json["accessToken"] == '') # no access until account has been activated
        assert(response_json["refreshToken"] == '')
        assert(response_json["confirmed"] == True)
        assert(response_json["email"] == 'confUser@mail.com')
        assert(response_json["username"] == 'confUser')
