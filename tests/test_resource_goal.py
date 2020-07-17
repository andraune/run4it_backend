import pytest
from run4it.api.goal import GoalCategoryModel, GoalCategoryListResource
from run4it.api.workout import WorkoutCategoryModel
from .helpers import get_response_json


@pytest.mark.usefixtures('db')
class TestGoalCategoryListResource:

	def setup(self): # register some workout categories
		WorkoutCategoryModel('Running', True).save()
		GoalCategoryModel('Distance', 'km', 1).save(commit=False)
		GoalCategoryModel('Abnormal weight loss', 'kg', None).save(commit=False)
		GoalCategoryModel('Weight gain', 'kg').save(commit=True)

	def test_content_type_is_json(self, api, client):
		url = api.url_for(GoalCategoryListResource)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_goal_categories(self, api, client):
		url = api.url_for(GoalCategoryListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 3)
		assert(response_json[0]["id"] is not None)
		assert(response_json[0]["name"] is not None)
		assert(response_json[0]["unit"] is not None)
		assert(response_json[0]["workoutCategoryName"] == "")

	def test_get_goal_categories_alphabetically_sorted(self, api, client):
		url = api.url_for(GoalCategoryListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json[0]["id"] == 2)
		assert(response_json[0]["name"] == "Abnormal weight loss")
		assert(response_json[0]["unit"] == "kg")
		assert(response_json[1]["name"] == "Distance")
		assert(response_json[1]["workoutCategoryName"] == "Running")
		assert(response_json[2]["name"] == "Weight gain")

