import pytest
import datetime as dt
from run4it.api.goal import GoalModel, GoalCategoryModel
from run4it.api.workout import WorkoutCategoryModel, WorkoutModel

@pytest.mark.usefixtures('db')
class TestGoalCategoryModel:
	def test_get_by_id(self):
		new_item = GoalCategoryModel("Run Kms")
		new_item.save()
		retrieved_item = GoalCategoryModel.get_by_id(new_item.id)
		assert(retrieved_item == new_item)

	def test_category_name_not_unique(self, db):
		item = GoalCategoryModel("Distance", "km", 1)
		item.save()
		item_new = GoalCategoryModel("Distance", "km", 2)
		item_new.save()		
		num_items = db.session.query(GoalCategoryModel).count()
		assert(num_items == 2)

	def test_category_name_and_workout_category_unique(self, db):
		item = GoalCategoryModel("Distance", "km", 1)
		item.save()

		try:
			item_new = GoalCategoryModel("Distance", "km", 1)
			item_new.save()
		except:
			db.session.rollback()

		num_items = db.session.query(GoalCategoryModel).count()
		assert(num_items == 1)
	
	def test_category_unit(self, db):
		item = GoalCategoryModel("Run Kms", "km")
		item.save()
		assert(item.unit == 'km')	

	def test_category_workout_category_link(self, db):
		WorkoutCategoryModel("Running", True).save()
		item1 = GoalCategoryModel("Run Kms", "km", None)
		item1.save()
		item2 = GoalCategoryModel("Run Kms", "km", 1)
		item2.save()
		assert(item1.workout_category is None)
		assert(item2.workout_category.id == 1)

@pytest.mark.usefixtures('db')
class TestGoalModel:
	def setup(self):
		WorkoutCategoryModel("Running", True).save()
		GoalCategoryModel("RunKms", "km", 1).save(commit=False)
		GoalCategoryModel("WeightTarget").save()

	def test_setup(self, db):
		assert(db.session.query(GoalCategoryModel).count() == 2)

	def test_get_by_id(self):
		category = GoalCategoryModel.get_by_id(1)
		new_goal = GoalModel(1, category)
		new_goal.save()
		retrieved_goal = GoalModel.get_by_id(new_goal.id)
		assert(retrieved_goal == new_goal)
	
	def test_goal_category_workout_id(self):
		category1 = GoalCategoryModel.get_by_id(1)
		category2 = GoalCategoryModel.get_by_id(2)
		assert(category1.workout_category_id == 1)
		assert(category2.workout_category_id is None)

	def test_goal_category_link(self):
		category = GoalCategoryModel.get_by_id(1)
		new_goal = GoalModel(1, category)
		new_goal.save()
		assert(new_goal.category.id == 1)
		assert(new_goal.category.name == 'RunKms')
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


@pytest.mark.usefixtures('db')
class TestGoalModelUpdateFromWorkouts:
	profile_id = 1

	def setup(self):
		WorkoutCategoryModel("Running", True).save(commit=False)
		WorkoutCategoryModel("Fitness", False).save()
		self.running_workout_category = WorkoutCategoryModel.get_by_id(1)
		self.fitness_workout_category = WorkoutCategoryModel.get_by_id(2)
		GoalCategoryModel("Cumulative distance", "km", 1).save(commit=False)
		GoalCategoryModel("Number of workouts", "#", 1).save(commit=False)
		GoalCategoryModel("Number of workouts", "#", 2).save(commit=False)
		GoalCategoryModel("Cumulative climb", "m", 1).save(commit=False)
		GoalCategoryModel("Weight loss", "kg", None).save()
		self.cumulative_distance_goal_category = GoalCategoryModel.get_by_id(1)
		self.num_of_running_workouts_goal_category = GoalCategoryModel.get_by_id(2)
		self.num_of_fitness_workouts_goal_category = GoalCategoryModel.get_by_id(3)
		self.cumulative_climb_goal_category = GoalCategoryModel.get_by_id(4)
		self.weight_loss_goal_category = GoalCategoryModel.get_by_id(5)
		two_days_ago = dt.datetime.utcnow() - dt.timedelta(days=2)
		two_days_from_now = dt.datetime.utcnow() + dt.timedelta(days=2)
		GoalModel(self.profile_id, self.cumulative_distance_goal_category, two_days_ago, two_days_from_now, 0, 100, 0).save(commit=False)
		GoalModel(self.profile_id, self.num_of_running_workouts_goal_category, two_days_ago, two_days_from_now, 0, 10, 0).save(commit=False)
		GoalModel(self.profile_id, self.num_of_fitness_workouts_goal_category, two_days_ago, two_days_from_now, 0, 10, 0).save(commit=False)
		GoalModel(self.profile_id, self.cumulative_climb_goal_category, two_days_ago, two_days_from_now, 0, 500, 0).save(commit=False)
		GoalModel(self.profile_id, self.weight_loss_goal_category, two_days_ago, two_days_from_now, 80, 70, 78).save()
		self.cumulative_distance_goal = GoalModel.get_by_id(1)
		self.running_workouts_goal = GoalModel.get_by_id(2)
		self.fitness_workouts_goal = GoalModel.get_by_id(3)
		self.cumulative_climb_goal = GoalModel.get_by_id(4)
		self.weight_loss_goal = GoalModel.get_by_id(5)
	
	def test_setup(self):
		assert(self.cumulative_distance_goal_category.workout_category_name == "Running")
		assert(self.num_of_running_workouts_goal_category.workout_category_name == "Running")
		assert(self.num_of_fitness_workouts_goal_category.workout_category_name == "Fitness")
		assert(self.cumulative_climb_goal_category.workout_category_name == "Running")
		assert(self.weight_loss_goal_category.workout_category_name == "")
		assert(self.cumulative_distance_goal.category_name == "Cumulative distance")
		assert(self.running_workouts_goal.category_name == "Number of workouts")
		assert(self.fitness_workouts_goal.category_name == "Number of workouts")
		assert(self.cumulative_climb_goal.category_name == "Cumulative climb")
		assert(self.weight_loss_goal.category_name == "Weight loss")
		assert(self.cumulative_distance_goal.start_value == 0)
		assert(self.running_workouts_goal.start_value == 0)
		assert(self.fitness_workouts_goal.start_value == 0)
		assert(self.cumulative_climb_goal.start_value == 0)
		assert(self.weight_loss_goal.start_value == 80)
	
	def test_running_workout_updates_running_goals(self):
		workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 1000, 3600, 10)
		workout.save()
		self.cumulative_distance_goal.update_from_workout(workout)
		self.running_workouts_goal.update_from_workout(workout)
		self.fitness_workouts_goal.update_from_workout(workout)
		self.cumulative_climb_goal.update_from_workout(workout)
		self.weight_loss_goal.update_from_workout(workout)
		assert(self.cumulative_distance_goal.current_value == 1) # goal has km, workout has m for distance
		assert(self.running_workouts_goal.current_value == 1)
		assert(self.fitness_workouts_goal.current_value == 0)
		assert(self.cumulative_climb_goal.current_value == 10) # workout has m for climb (elevation gain)
		assert(self.weight_loss_goal.current_value == 78)

	def test_fitness_workout_updates_fitness_goal(self):
		workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout.save()
		self.cumulative_distance_goal.update_from_workout(workout)
		self.running_workouts_goal.update_from_workout(workout)
		self.fitness_workouts_goal.update_from_workout(workout)
		self.cumulative_climb_goal.update_from_workout(workout)
		self.weight_loss_goal.update_from_workout(workout)
		assert(self.cumulative_distance_goal.current_value == 0)
		assert(self.running_workouts_goal.current_value == 0)
		assert(self.fitness_workouts_goal.current_value == 1)
		assert(self.cumulative_climb_goal.current_value == 0)
		assert(self.weight_loss_goal.current_value == 78)

	def test_several_running_workouts(self):
		workout_1 = WorkoutModel(self.profile_id, self.running_workout_category, "Running workout", dt.datetime.utcnow(), 10000, 3600, 5)
		workout_1.save(commit=False)
		workout_2 = WorkoutModel(self.profile_id, self.running_workout_category, "Running workout", dt.datetime.utcnow(), 20000, 5000, 15)
		workout_2.save()
		self.cumulative_distance_goal.update_from_workout(workout_1)
		self.running_workouts_goal.update_from_workout(workout_1)
		self.cumulative_climb_goal.update_from_workout(workout_1)
		self.cumulative_distance_goal.update_from_workout(workout_2)
		self.running_workouts_goal.update_from_workout(workout_2)
		self.cumulative_climb_goal.update_from_workout(workout_2)
		assert(self.cumulative_distance_goal.current_value == 30)
		assert(self.running_workouts_goal.current_value == 2)
		assert(self.cumulative_climb_goal.current_value == 20)

	def test_several_fitness_workouts(self):
		workout_1 = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout_1.save(commit=False)
		workout_2 = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout_2.save()
		self.fitness_workouts_goal.update_from_workout(workout_1)
		self.fitness_workouts_goal.update_from_workout(workout_2)
		assert(self.fitness_workouts_goal.current_value == 2)

	def test_workout_for_different_profile_does_not_update(self):
		workout = WorkoutModel(self.profile_id+1, self.running_workout_category, "Running workout", dt.datetime.utcnow(), 10000, 3600, 10)
		workout.save()
		self.cumulative_distance_goal.update_from_workout(workout)
		self.running_workouts_goal.update_from_workout(workout)
		self.cumulative_climb_goal.update_from_workout(workout)
		assert(self.cumulative_distance_goal.current_value == 0)
		assert(self.running_workouts_goal.current_value == 0)
		assert(self.cumulative_climb_goal.current_value == 0)

	def test_workout_before_start_date_does_not_update(self):
		workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow() - dt.timedelta(days=3), 0, 3600, 0)
		workout.save()
		self.fitness_workouts_goal.update_from_workout(workout)
		assert(self.fitness_workouts_goal.current_value == 0)

	def test_workout_after_start_date_does_not_update(self):
		workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow() + dt.timedelta(days=3), 0, 3600, 0)
		workout.save()
		self.fitness_workouts_goal.update_from_workout(workout)
		assert(self.fitness_workouts_goal.current_value == 0)

	def test_running_workout_remove_updates_running_goals(self):
		add_workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 1000, 3600, 10)
		add_workout.save(commit=False)
		remove_workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 500, 3600, 3)
		remove_workout.save()
		self.cumulative_distance_goal.update_from_workout(add_workout)
		self.running_workouts_goal.update_from_workout(add_workout)
		self.fitness_workouts_goal.update_from_workout(add_workout)
		self.cumulative_climb_goal.update_from_workout(add_workout)
		self.weight_loss_goal.update_from_workout(add_workout)
		self.cumulative_distance_goal.remove_from_workout(remove_workout)
		self.running_workouts_goal.remove_from_workout(remove_workout)
		self.fitness_workouts_goal.remove_from_workout(remove_workout)
		self.cumulative_climb_goal.remove_from_workout(remove_workout)
		self.weight_loss_goal.remove_from_workout(remove_workout)
		assert(self.cumulative_distance_goal.current_value == 0.5)
		assert(self.running_workouts_goal.current_value == 0)
		assert(self.fitness_workouts_goal.current_value == 0)
		assert(self.cumulative_climb_goal.current_value == 7)
		assert(self.weight_loss_goal.current_value == 78)

	def test_fitness_workout_remove_updates_fitness_goals(self):
		add_workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		add_workout.save(commit=False)
		remove_workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 1000, 0)
		remove_workout.save()
		self.cumulative_distance_goal.update_from_workout(add_workout)
		self.running_workouts_goal.update_from_workout(add_workout)
		self.fitness_workouts_goal.update_from_workout(add_workout)
		self.cumulative_climb_goal.update_from_workout(add_workout)
		self.weight_loss_goal.update_from_workout(add_workout)
		self.cumulative_distance_goal.remove_from_workout(remove_workout)
		self.running_workouts_goal.remove_from_workout(remove_workout)
		self.fitness_workouts_goal.remove_from_workout(remove_workout)
		self.cumulative_climb_goal.remove_from_workout(remove_workout)
		self.weight_loss_goal.remove_from_workout(remove_workout)
		assert(self.cumulative_distance_goal.current_value == 0)
		assert(self.running_workouts_goal.current_value == 0)
		assert(self.fitness_workouts_goal.current_value == 0)
		assert(self.cumulative_climb_goal.current_value == 0)
		assert(self.weight_loss_goal.current_value == 78)

	def test_several_running_workout_remove_updates_running_goals(self):
		add_workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 2100, 3600, 10)
		add_workout.save(commit=False)
		remove_workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 500, 3600, 3)
		remove_workout.save()
		self.cumulative_distance_goal.update_from_workout(add_workout)
		self.cumulative_climb_goal.update_from_workout(add_workout)
		self.cumulative_distance_goal.remove_from_workout(remove_workout)
		self.cumulative_climb_goal.remove_from_workout(remove_workout)
		self.cumulative_distance_goal.remove_from_workout(remove_workout) # remove again
		self.cumulative_climb_goal.remove_from_workout(remove_workout) # remove again
		assert(self.cumulative_distance_goal.current_value == 1.1)
		assert(self.cumulative_climb_goal.current_value == 4)

	def test_several_fitness_workout_remove_updates_fitness_goals(self):
		add_workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		add_workout.save(commit=False)
		remove_workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 1000, 0)
		remove_workout.save()
		self.fitness_workouts_goal.update_from_workout(add_workout)
		self.fitness_workouts_goal.update_from_workout(add_workout) # added again
		self.fitness_workouts_goal.update_from_workout(add_workout) # added again
		self.fitness_workouts_goal.remove_from_workout(remove_workout)
		self.fitness_workouts_goal.remove_from_workout(remove_workout) # removed again
		assert(self.fitness_workouts_goal.current_value == 1)

	def test_remove_too_much_running_doesnt_give_negative_values(self):
		remove_workout = WorkoutModel(self.profile_id, self.running_workout_category, "Run workout", dt.datetime.utcnow(), 500, 3600, 3)
		remove_workout.save()
		self.cumulative_distance_goal.remove_from_workout(remove_workout)
		self.cumulative_climb_goal.remove_from_workout(remove_workout)
		assert(self.cumulative_distance_goal.current_value == 0)
		assert(self.cumulative_climb_goal.current_value == 0)

	def test_remove_too_much_fitness_doesnt_give_negative_values(self):
		remove_workout = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 1000, 0)
		remove_workout.save()
		self.fitness_workouts_goal.remove_from_workout(remove_workout)
		assert(self.fitness_workouts_goal.current_value == 0)

	def test_workout_for_another_profile_doesnt_remove(self):
		workout_add = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout_add.save()
		workout_remove = WorkoutModel(self.profile_id+1, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow() - dt.timedelta(days=3), 0, 3600, 0)
		workout_remove.save()
		self.fitness_workouts_goal.update_from_workout(workout_add)
		self.fitness_workouts_goal.remove_from_workout(workout_remove)
		assert(self.fitness_workouts_goal.current_value == 1)

	def test_workout_before_start_date_does_not_remove(self):
		workout_add = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout_add.save()
		workout_remove = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow() - dt.timedelta(days=3), 0, 3600, 0)
		workout_remove.save()
		self.fitness_workouts_goal.update_from_workout(workout_add)
		self.fitness_workouts_goal.remove_from_workout(workout_remove)
		assert(self.fitness_workouts_goal.current_value == 1)

	def test_workout_after_start_date_does_not_remove(self):
		workout_add = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow(), 0, 3600, 0)
		workout_add.save()
		workout_remove = WorkoutModel(self.profile_id, self.fitness_workout_category, "Fitness workout", dt.datetime.utcnow() + dt.timedelta(days=3), 0, 3600, 0)
		workout_remove.save()
		self.fitness_workouts_goal.update_from_workout(workout_add)
		self.fitness_workouts_goal.update_from_workout(workout_remove)
		assert(self.fitness_workouts_goal.current_value == 1)
                                                                                                                                                                                                                                                                                                                                                                                   