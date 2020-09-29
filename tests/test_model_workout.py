import pytest
import datetime as dt
from run4it.api.workout import WorkoutModel, WorkoutCategoryModel
from run4it.api.goal import GoalModel, GoalCategoryModel


@pytest.mark.usefixtures('db')
class TestWorkoutCategoryModel:
	def test_get_by_id(self):
		new_item = WorkoutCategoryModel("Running", True)
		new_item.save()
		retrieved_item = WorkoutCategoryModel.get_by_id(new_item.id)
		assert(retrieved_item == new_item)

	def test_category_name_unique(self, db):
		item = WorkoutCategoryModel("Running", True)
		item.save()

		try:
			item_new = WorkoutCategoryModel("Running", True)
			item_new.save()
		except:
			db.session.rollback()

		num_items = db.session.query(WorkoutCategoryModel).count()
		assert(num_items == 1)

	def test_find_by_name(self):
		item1 = WorkoutCategoryModel("Running", True)
		item2 = WorkoutCategoryModel("Hiking", True)
		item1.save(commit=False)
		item2.save()
		retrieved_item = WorkoutCategoryModel.find_by_name("Hiking")
		assert(retrieved_item.name == item2.name)
		retrieved_item = WorkoutCategoryModel.find_by_name("Bullshit")
		assert(retrieved_item is None)


@pytest.mark.usefixtures('db')
class TestWorkoutModel:
	def setup(self):
		WorkoutCategoryModel("Running", True).save(commit=False)
		WorkoutCategoryModel("Hiking", True).save()

	def test_setup(self, db):
		assert(db.session.query(WorkoutCategoryModel).count() == 2)

	def test_get_by_id(self):
		category = WorkoutCategoryModel.get_by_id(1)
		new_workout = WorkoutModel(1, category, "Run 1", dt.datetime.utcnow(), 1234, 234, 123)
		new_workout.save()
		retrieved_workout = WorkoutModel.get_by_id(new_workout.id)
		assert(retrieved_workout == new_workout)

	def test_workout_category_link(self):
		category = WorkoutCategoryModel.get_by_id(2)
		new_workout = WorkoutModel(1, category, "Hike 1", dt.datetime.utcnow(), 1234, 234, 123)
		new_workout.save()
		assert(new_workout.category.id == 2)
		assert(new_workout.category.name == 'Hiking')

	def test_two_goals_with_same_category_and_profile(self):
		category = WorkoutCategoryModel.get_by_id(1)
		new_workout1 = WorkoutModel(1, category, "Hike 1", dt.datetime.utcnow(), 1234, 234, 123)
		new_workout1.save()
		new_workout2 = WorkoutModel(1, category, "Hike 2", dt.datetime.utcnow(), 1234, 234, 123)
		new_workout2.save()
		assert(WorkoutModel.query.count() == 2)

	def test_default_resource_path_and_edited(self):
		category = WorkoutCategoryModel.get_by_id(1)
		new_workout = WorkoutModel(1, category, "Hike 1", dt.datetime.utcnow(), 1234, 234, 123)
		new_workout.save()
		assert(new_workout.resource_path is None)
		assert(new_workout.edited == False)
	
	def test_values(self):
		category = WorkoutCategoryModel.get_by_id(1)
		now = dt.datetime.utcnow()
		item = WorkoutModel(3, category, "Run 1", now, 1234, 234, 123, '/path/to/file.gpx', True)
		assert(item.profile_id == 3)
		assert(item.category.id == 1)
		assert(item.category_name == "Running")
		assert(item.name == "Run 1")
		assert(item.start_at == now)
		assert(item.distance == 1234)
		assert(item.duration == 234)
		assert(item.climb == 123)
		assert(item.resource_path == '/path/to/file.gpx')
		assert(item.edited == True)

	def test_pace_and_speed(self):
		category = WorkoutCategoryModel.get_by_id(1)
		new_workout1 = WorkoutModel(1, category, "Run 1", dt.datetime.utcnow(), 10000, 3600, 0)
		new_workout1.save()
		assert(new_workout1.average_speed == 10.0)
		assert(new_workout1.average_pace == "06:00")
		new_workout2 = WorkoutModel(1, category, "Run 2", dt.datetime.utcnow(), 4567, 1627, 0)
		new_workout2.save()
		assert(new_workout2.average_speed == 10.11)
		assert(new_workout2.average_pace == "05:56")

	def test_resource_file(self):
		category = WorkoutCategoryModel.get_by_id(1)
		new_workout1 = WorkoutModel(1, category, "Run 1", dt.datetime.utcnow(), 10000, 3600, 0, None)
		new_workout1.save(commit=False)
		new_workout2 = WorkoutModel(1, category, "Run 2", dt.datetime.utcnow(), 4567, 1627, 0, '/path/to/file')
		new_workout2.save()
		assert(new_workout1.resource_path is None)
		assert(new_workout1.resource_file is None)
		assert(new_workout2.resource_path == "/path/to/file")
		assert(new_workout2.resource_file == "file")

	def test_get_workouts_for_goal_excludes_too_old_and_too_new_workouts(self):
		# register category for goal, connected to "running"
		goal_category = GoalCategoryModel("Distance", "km", 1)
		goal_category.save()
		#register goal
		goal = GoalModel(1, goal_category, dt.datetime.utcnow() - dt.timedelta(days=4), dt.datetime.utcnow() + dt.timedelta(days=4))
		goal.save()
		# register workouts for workout category "Running", within goal limits
		running_category = WorkoutCategoryModel.get_by_id(1)
		run_workout_1 = WorkoutModel(1, running_category, "Run 1", dt.datetime.utcnow(), 1000, 200, 0, None, False)
		run_workout_1.save(commit=False)
		run_workout_2 = WorkoutModel(1, running_category, "Run 2", dt.datetime.utcnow() + dt.timedelta(days=1), 1000, 200, 0, None, False)
		run_workout_2.save(commit=False)
		# register workout completed before goal started
		WorkoutModel(1, running_category, "Too early", dt.datetime.utcnow() - dt.timedelta(days=5), 1000, 200, 0, None, False).save(commit=False)
		# register workout completed after goal ended
		WorkoutModel(1, running_category, "Too late", dt.datetime.utcnow() + dt.timedelta(days=5), 1000, 200, 0, None, False).save(commit=True)
		goal_workouts = WorkoutModel.get_workouts_for_goal(goal)
		assert(len(goal_workouts)==2)
		assert(goal_workouts[0] == run_workout_1)
		assert(goal_workouts[1] == run_workout_2)

	def test_get_workouts_for_goal_excludes_other_users_workouts(self):
		# register category for goal, connected to "running"
		goal_category = GoalCategoryModel("Distance", "km", 1)
		goal_category.save()
		#register goal
		goal = GoalModel(1, goal_category, dt.datetime.utcnow() - dt.timedelta(days=4), dt.datetime.utcnow() + dt.timedelta(days=4))
		goal.save()
		# register workout for workout category "Running", within goal limits
		running_category = WorkoutCategoryModel.get_by_id(1)
		run_workout_1 = WorkoutModel(1, running_category, "Run 1", dt.datetime.utcnow(), 1000, 200, 0, None, False)
		run_workout_1.save(commit=False)
		# register workout for workout category "Running", within goal limits, but other user
		run_workout_2 = WorkoutModel(2, running_category, "Run 2", dt.datetime.utcnow() + dt.timedelta(days=1), 1000, 200, 0, None, False)
		run_workout_2.save(commit=True)

		goal_workouts = WorkoutModel.get_workouts_for_goal(goal)
		assert(len(goal_workouts)==1)
		assert(goal_workouts[0] == run_workout_1)

	def test_get_workouts_for_goal_excludes_other_workout_categories(self):
		# register category for goal, connected to "running"
		goal_category = GoalCategoryModel("Distance", "km", 1)
		goal_category.save(commit=False)
		# register category for goal, not connected to "running
		goal_category_other = GoalCategoryModel("Distance", "km", 2)
		goal_category_other.save()
		#register goal
		goal = GoalModel(1, goal_category, dt.datetime.utcnow() - dt.timedelta(days=4), dt.datetime.utcnow() + dt.timedelta(days=4))
		goal.save()
		# register workout for workout category "Running", within goal limits
		running_category = WorkoutCategoryModel.get_by_id(1)
		run_workout = WorkoutModel(1, running_category, "Run", dt.datetime.utcnow(), 1000, 200, 0, None, False)
		run_workout.save(commit=False)
		# register workout for workout category "Hiking"
		hiking_category = WorkoutCategoryModel.get_by_id(2)
		hiking_workout = WorkoutModel(1, hiking_category, "Hike", dt.datetime.utcnow() + dt.timedelta(days=1), 1000, 200, 0, None, False)
		hiking_workout.save(commit=True)

		goal_workouts = WorkoutModel.get_workouts_for_goal(goal)
		assert(len(goal_workouts)==1)
		assert(goal_workouts[0] == run_workout)
