import pytest
import datetime as dt
from run4it.api.goal import GoalModel, GoalCategoryModel

@pytest.mark.usefixtures('db')
class TestGoalCategoryModel:
	def test_get_by_id(self):
		new_item = GoalCategoryModel("Run Kms")
		new_item.save()
		retrieved_item = GoalCategoryModel.get_by_id(new_item.id)
		assert(retrieved_item == new_item)

	def test_category_name_unique(self, db):
		item = GoalCategoryModel("Run Kms")
		item.save()

		try:
			item_new = GoalCategoryModel("Run Kms")
			item_new.save()
		except:
			db.session.rollback()

		num_items = db.session.query(GoalCategoryModel).count()
		assert(num_items == 1)
	
	def test_category_unit(self, db):
		item = GoalCategoryModel("Run Kms", "km")
		item.save()
		assert(item.unit == 'km')	

@pytest.mark.usefixtures('db')
class TestGoalModel:
	def setup(self):
		GoalCategoryModel("RunKms", "km").save()
		GoalCategoryModel("WeightTarget").save()

	def test_setup(self, db):
		assert(db.session.query(GoalCategoryModel).count() == 2)

	def test_get_by_id(self):
		category = GoalCategoryModel.get_by_id(1)
		new_goal = GoalModel(1, category)
		new_goal.save()
		retrieved_goal = GoalModel.get_by_id(new_goal.id)
		assert(retrieved_goal == new_goal)

	def test_goal_category_link(self):
		category = GoalCategoryModel.get_by_id(1)
		new_goal = GoalModel(1, category)
		new_goal.save()
		assert(new_goal.category.id == 1)
		assert(new_goal.category.name == 'RunKms')
		assert(new_goal.category_name == 'RunKms')
		assert(new_goal.category_unit == 'km')

	def test_goal_category_unit_none_gives_empty_string(self):
		category = GoalCategoryModel.get_by_id(2)
		new_goal = GoalModel(1, category)
		new_goal.save()
		assert(new_goal.category.id == 2)
		assert(new_goal.category_unit == '')

	def test_two_goals_with_same_category_and_profile(self):
		category = GoalCategoryModel.get_by_id(1)
		new_goal1 = GoalModel(1, category)
		new_goal1.save()
		new_goal2 = GoalModel(1, category)
		new_goal2.save()
		assert(GoalModel.query.count() == 2)

	def test_default_start_date_and_end_date(self):
		category = GoalCategoryModel.get_by_id(1)
		now = dt.datetime.utcnow()
		item = GoalModel(1, category)
		item.save()
		assert((now - dt.timedelta(minutes=1)) < item.start_at)
		assert((now + dt.timedelta(minutes=1)) > item.start_at)
		assert((item.end_at - item.start_at).seconds <= 1)
		assert(item.duration == 1)

	def test_start_date_duration(self):
		category = GoalCategoryModel.get_by_id(1)
		start_at = dt.datetime.utcnow() + dt.timedelta(days=3)
		end_at = start_at + dt.timedelta(days=7)
		item = GoalModel(1, category, start_at, end_at)
		item.save()
		assert(item.start_at == start_at)
		assert(item.end_at == end_at)
		assert(item.duration == 7.0000)

	def test_misc_durations(self):
		category = GoalCategoryModel.get_by_id(1)
		start_at = dt.datetime(2020, 1, 1, 0, 0, 0)

		end_at = dt.datetime(2020, 1, 1, 13, 0, 0)
		item = GoalModel(1, category, start_at, end_at)
		expected_duration = round(13*60*60 / 86400, 4)
		assert(item.duration == expected_duration)

		end_at = dt.datetime(2021, 1, 1, 13, 0, 0)
		item = GoalModel(1, category, start_at, end_at)
		expected_duration = 366 + round(13*60*60 / 86400, 4)
		assert(item.duration == expected_duration)


	def test_profile_id(self):
		category = GoalCategoryModel.get_by_id(1)
		item = GoalModel(3, category)
		assert(item.profile_id == 3)
	
	def test_values(self):
		category = GoalCategoryModel.get_by_id(1)
		item = GoalModel(3, category, start_value=1, current_value=2, target_value=3)
		assert(item.start_value==1)
		assert(item.current_value==2)
		assert(item.target_value==3)
