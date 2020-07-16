import pytest
from run4it.api.workout import WorkoutCategoryModel, WorkoutCategoryListResource
from .helpers import get_response_json


@pytest.mark.usefixtures('db')
class TestWorkoutCategoryListResource:

	def setup(self): # register some workout categories
		WorkoutCategoryModel('Running', True).save(commit=False)
		WorkoutCategoryModel('Fitness', False).save(commit=False)
		WorkoutCategoryModel('Hiking', True).save(commit=True)

	def test_content_type_is_json(self, api, client):
		url = api.url_for(WorkoutCategoryListResource)
		response = client.get(url)
		assert(response.headers["Content-Type"] == 'application/json')

	def test_get_workout_categories(self, api, client):
		url = api.url_for(WorkoutCategoryListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(len(response_json) == 3)
		assert(response_json[0]["id"] is not None)
		assert(response_json[0]["name"] is not None)
		assert(response_json[0]["supports_gps_data"] is not None)

	def test_get_workout_categories_alphabetically_sorted(self, api, client):
		url = api.url_for(WorkoutCategoryListResource)
		response = client.get(url)
		response_json = get_response_json(response.data)
		assert(response.status_code == 200)
		assert(response_json[0]["id"] == 2)
		assert(response_json[0]["name"] == "Fitness")
		assert(response_json[0]["supports_gps_data"] == False)
		assert(response_json[1]["name"] == "Hiking")
		assert(response_json[2]["name"] == "Running")

