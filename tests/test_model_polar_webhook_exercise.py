"""Model unit tests."""
import pytest
import datetime as dt
from run4it.api.polar import PolarWebhookExerciseModel

@pytest.mark.usefixtures('db')
class TestPolarWebhookExerciseModel:

	def test_get_by_id(self):
		new_exercise = PolarWebhookExerciseModel(1, 'abcd', dt.datetime.utcnow(), 'url')
		new_exercise.save()
		retrieved_exercise = PolarWebhookExerciseModel.get_by_id(new_exercise.id)
		assert(retrieved_exercise == new_exercise)

	def test_entity_id_unique(self, db):
		exercise1 = PolarWebhookExerciseModel(1, 'entity', dt.datetime.utcnow())
		exercise1.save()
		try:
			exercise2 = PolarWebhookExerciseModel(2, 'entity', dt.datetime.utcnow() + dt.timedelta(seconds=10))
			exercise2.save()  # should fail
		except:
			db.session.rollback()
		num_users = db.session.query(PolarWebhookExerciseModel).count()
		assert(num_users == 1)

	def test_get_by_polar_user_id(self, db):
		exercise1 = PolarWebhookExerciseModel(1, 'entity1', dt.datetime.utcnow())
		exercise1.save(commit=False)
		exercise2 = PolarWebhookExerciseModel(2, 'entity2', dt.datetime.utcnow())
		exercise2.save()
		my_exercise = PolarWebhookExerciseModel.find_by_polar_user_id(2)
		assert(my_exercise.id == exercise2.id)

	def test_get_not_processed(self, db):
		exercise1 = PolarWebhookExerciseModel(1, 'entity1', dt.datetime.utcnow())
		exercise1.processed = True
		exercise1.save(commit=False)
		exercise2 = PolarWebhookExerciseModel(2, 'entity2', dt.datetime.utcnow())
		exercise2.save(commit=False)
		exercise3 = PolarWebhookExerciseModel(3, 'entity3', dt.datetime.utcnow())
		exercise3.save()
		unprocessed_exercises = PolarWebhookExerciseModel.get_not_processed()
		assert(len(unprocessed_exercises) == 2)
		assert(unprocessed_exercises[0].id != exercise1.id)
		assert(unprocessed_exercises[1].id != exercise1.id)
