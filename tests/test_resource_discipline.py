import pytest
from run4it.api.discipline import DisciplineModel, DisciplineResource, DisciplineListResource
from .helpers import get_response_json, register_and_login_confirmed_user, get_authorization_header

@pytest.mark.usefixtures('db')
class TestDisciplineResource:

	def _create_disciplines(self, num, db):
		i = 0
		max = 100
		while i < num and i < max:
			disc = DisciplineModel("disc{}".format(i + 1), max - i)
			disc.save(False)
			i += 1
		db.session.commit()

	def test_disciplinelist_content_type_is_json(self, api, client):
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_disciplinelist_no_data(self, api, client):
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 0)		

	def test_get_disciplinelist_with_data(self, api, client):
		disc_1 = DisciplineModel("disc1", 1000, "user1")
		disc_1.save()
		
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 1)	
		assert(response_json[0]["id"] == 1)
		assert(response_json[0]["length"] == 1000)
		assert(response_json[0]["username"] == "user1")

	def test_get_disciplinelist_with_data(self, api, client):
		disc_1 = DisciplineModel("disc1", 1000, "user1")
		disc_1.save()
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 1)	
		assert(response_json[0]["id"] == 1)
		assert(response_json[0]["length"] == 1000)
		assert(response_json[0]["username"] == "user1")

	def test_create_discipines_helper(self, api, client, db):
		self._create_disciplines(10, db)
		assert(DisciplineModel.query.count() == 10)
		disc_first = DisciplineModel.get_by_id(1)
		disc_last = DisciplineModel.get_by_id(10)
		assert(disc_first.name == "disc1")
		assert(disc_first.length == 100)
		assert(disc_last.name == "disc10")
		assert(disc_last.length == 91)

	def test_disciplinelist_ordered_by_length_ascending(self, api, client, db):
		self._create_disciplines(10, db)
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 10)
		assert(response_json[0]["id"] == 10)
		assert(response_json[0]["length"] == 91)
		assert(response_json[1]["id"] == 9)
		assert(response_json[1]["length"] == 92)
		assert(response_json[9]["id"] == 1)
		assert(response_json[9]["length"] == 100)

	def test_disciplinelist_default_limit(self, api, client, db):
		self._create_disciplines(21, db)
		url = api.url_for(DisciplineListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 20) # default limit 20

	def test_disciplinelist_limit_param_large(self, api, client, db):
		self._create_disciplines(30, db)
		url = api.url_for(DisciplineListResource, limit=23)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 23) # default is 20

	def test_disciplinelist_limit_param_small(self, api, client, db):
		self._create_disciplines(10, db)
		url = api.url_for(DisciplineListResource, limit=3)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 3)

	def test_disciplinelist_pagination(self, api, client, db):
		self._create_disciplines(10, db)
		url = api.url_for(DisciplineListResource, limit=4, offset=0)
		response_json1 = get_response_json(client.get(url).data)
		url = api.url_for(DisciplineListResource, limit=4, offset=4)
		response_json2 = get_response_json(client.get(url).data)
		url = api.url_for(DisciplineListResource, limit=4, offset=8)
		response_json3 = get_response_json(client.get(url).data)
		assert(len(response_json1) == 4)
		assert(len(response_json2) == 4)
		assert(len(response_json3) == 2)
		assert(response_json1[0]["id"] == 10)
		assert(response_json1[3]["id"] == 7)
		assert(response_json2[0]["id"] == 6)
		assert(response_json2[3]["id"] == 3)
		assert(response_json3[0]["id"] == 2)
		assert(response_json3[1]["id"] == 1)

	def test_post_discipline_not_logged_in(self, api, client):
		url = api.url_for(DisciplineListResource)
		response = client.post(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_post_disciplinelist_new_discipline(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		response = client.post(url, data={ "name":"new_disc", "length":1234 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 1)
		assert(response_json["name"] == "new_disc")
		assert(response_json["length"] == 1234)
		assert(response_json["username"] == "run4it")

	def test_post_discipline_list_new_discipline_location_header(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		response = client.post(url, data={ "name":"new_disc", "length":1234 }, headers=get_authorization_header(token))
		assert(response.headers["Location"] == api.url_for(DisciplineResource, disc_id=1, _external=True))		

	def test_post_disciplinelist_new_discipline_duplicate_name(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		client.post(url, data={ "name":"new_disc", "length":1234 }, headers=get_authorization_header(token))
		response = client.post(url, data={ "name":"new_disc", "length":12345 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 409)
		assert(response_json["errors"]["discipline"] is not None)

	def test_post_disciplinelist_new_discipline_invalid_name(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		response = client.post(url, data={ "name":"d", "length":1234 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["name"] is not None)		

	def test_post_disciplinelist_new_discipline_invalid_length(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		response = client.post(url, data={ "name":"disc", "length":0 }, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["length"] is not None)

	def test_post_disciplinelist_new_discipline_missing_params(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineListResource)
		response = client.post(url, data={}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["name"] is not None)
		assert(response_json["errors"]["length"] is not None)

	def test_put_disciplinelist_not_supported(self, api, client):
		url = api.url_for(DisciplineListResource)
		response = client.put(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_disciplinelist_not_supported(self, api, client):
		url = api.url_for(DisciplineListResource)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed

	def test_get_discipline_doesnt_exist(self, api, client):
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["discipline"] is not None)

	def test_get_discipline_invalid_id(self, api, client):
		url = api.url_for(DisciplineResource, disc_id=-1)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)

	def test_get_discipline_by_id(self, api, client, db):
		self._create_disciplines(3, db)
		url = api.url_for(DisciplineResource, disc_id=2)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["id"] == 2)
		assert(response_json["name"] == "disc2")

	def test_update_discipline_not_logged_in(self, api, client):
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)		

	def test_update_discipline(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		disc = DisciplineModel("disc1", 1000, "run4it")
		disc.save()
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url, data={'name':'new_name','length':999}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json["name"] == "new_name")
		assert(response_json["length"] == 999)
		assert(response_json["username"] == "run4it")

	def test_update_discipline_other_user(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		disc = DisciplineModel("disc1", 1000, "other")
		disc.save()
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url, data={'name':'new_name','length':999}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 403)
		assert(response_json["errors"]["discipline"] is not None)

	def test_update_discipline_not_found(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url, data={'name':'new_name','length':999}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 404)
		assert(response_json["errors"]["discipline"] is not None)

	def test_update_discipline_missing_params(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		disc = DisciplineModel("disc1", 1000, "run4it")
		disc.save()
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url, data={}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["name"] is not None)
		assert(response_json["errors"]["length"] is not None)

	def test_update_discipline_invalid_params(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "run4it", "run4@it.com", "passwd")
		disc = DisciplineModel("disc1", 1000, "run4it")
		disc.save()
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.put(url, data={"name":"","length":99999999}, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 422)
		assert(response_json["errors"]["name"] is not None)
		assert(response_json["errors"]["length"] is not None)

	def test_post_discipline_not_supported(self, api, client):
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.post(url)
		assert(response.status_code == 405) # not allowed

	def test_delete_disciplinelist_not_supported(self, api, client):
		url = api.url_for(DisciplineResource, disc_id=1)
		response = client.delete(url)
		assert(response.status_code == 405) # not allowed
