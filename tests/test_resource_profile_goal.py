import pytest
import datetime as dt
from run4it.api.goal import ProfileGoalListResource, GoalCategoryModel, GoalModel
from .helpers import get_response_json, register_and_login_confirmed_user, get_authorization_header


@pytest.mark.usefixtures('db')
class TestProfileGoalListResource:

	def setup(self): # register some goals
		cat = GoalCategoryModel('RunDistance')
		cat.save()
		now = dt.datetime.utcnow()
		future_goal = GoalModel(1, cat, now + dt.timedelta(days=2), now + dt.timedelta(days=3), 0, 2, 0)
		future_goal.save(commit=False)
		active_goal1 = GoalModel(1, cat, now + dt.timedelta(days=-2), now + dt.timedelta(days=1), 0, 2, 1)
		active_goal2 = GoalModel(1, cat, now + dt.timedelta(days=-2), now + dt.timedelta(days=2), 0, 2, 2)
		active_goal1.save(commit=False)
		active_goal2.save(commit=False)
		expired_goal1 = GoalModel(1, cat, now + dt.timedelta(days=-10), now + dt.timedelta(days=-2), 0, 2, 0) # incomplete
		expired_goal2 = GoalModel(1, cat, now + dt.timedelta(days=-8), now + dt.timedelta(days=-3), 0, 2, 2) # complete
		expired_goal1.save(commit=False)
		expired_goal2.save()

	def test_content_type_is_json(self, api, client):
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_goals_not_logged_in(self, api, client):
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 401)
		assert(response_json["errors"]["auth"] is not None)

	def test_get_goals_logged_in(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 2) #active goals is default
		assert(response_json[1]['id'] == 3)

	def test_get_goals_filter_active(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="active")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 2)
		assert(response_json[1]['id'] == 3)

	def test_get_goals_filter_future(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="future")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 1)

	def test_get_goals_filter_expired(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="expired")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 2)
		assert(response_json[0]['id'] == 4)
		assert(response_json[1]['id'] == 5)

	def test_get_goals_filter_completed(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="completed")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 5)

	def test_get_goals_filter_incompleted(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(len(response_json) == 1)
		assert(response_json[0]['id'] == 4)

	def test_get_goals_duration(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json[0]['duration'] == 8)

	def test_get_goals_category(self, api, client):
		token,_ = register_and_login_confirmed_user(api, client, "jonny", "jonny@vikan.no", "jonny")
		url = api.url_for(ProfileGoalListResource, username="jonny", filter="incompleted")
		response = client.get(url, headers=get_authorization_header(token))
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)	
		assert(response_json[0]['category'] == 'RunDistance')
