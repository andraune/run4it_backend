"""Model unit tests."""
import pytest
import datetime as dt
from run4it.api.profile import Profile, ProfileWeightHistory
from run4it.api.user import User
from run4it.api.goal import GoalModel, GoalCategoryModel
from run4it.api.workout import WorkoutModel, WorkoutCategoryModel

@pytest.mark.usefixtures('db')
class TestProfileModel:

	def test_get_by_id(self):
		# note: 1-to-1 relationship User<=>Profile. Thus we need a User.
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.save()
		retrieved_profile = Profile.get_by_id(new_profile.id)
		assert(retrieved_profile == new_profile)

	def test_profile_unique(self, db):
		user = User('user', 'user@mail.com')
		user.save()
		profile1 = Profile(user)
		profile1.save()

		try:
			profile2 = Profile(user)
			profile2.save()

		except:
			db.session.rollback()

		num_profiles = db.session.query(Profile).count()
		assert(num_profiles == 1)
	
	def test_profile_username(self):
		user = User('profileUsername', 'user@mail.com')
		user.save()
		profile = Profile(user)
		profile.save()
		assert(profile.username == 'profileUsername')

	def test_profile_data_defaults_to_none(self):
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.save()
		assert(new_profile.height is None)
		assert(new_profile.weight is None)
		assert(new_profile.birth_date is None) 
		assert(new_profile.weights.count() == 0)

	def test_profile_birth_date(self):
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.set_birth_date(1980, 1, 2)
		new_profile.save()
		assert(new_profile.birth_date.year == 1980)
		assert(new_profile.birth_date.month == 1)
		assert(new_profile.birth_date.day == 2)

	def test_profile_height(self):
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.set_height(180)
		new_profile.save()
		assert(new_profile.height == 180)
		new_profile.set_height(0)
		new_profile.save()
		assert(new_profile.height is None)

	def test_profile_weight(self):
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.set_weight(80)
		new_profile.save()
		assert(new_profile.weight == 80)
		new_profile.set_weight(0)
		new_profile.save()
		assert(new_profile.weight is None)

	def test_profile_updates_weight_history_on_new_weight(self):
		user = User('user', 'user@mail.com')
		user.save()		
		new_profile = Profile(user)
		new_profile.set_weight(69.0)
		new_profile.save()
		assert(new_profile.weights.count() == 1)
		assert(new_profile.weights[0].weight == 69.0)

	def test_profile_updates_weight_history_on_new_weight_but_not_when_none(self):
		user = User('user', 'user@mail.com')
		user.save()		
		new_profile = Profile(user)
		new_profile.set_weight(69.0)
		new_profile.set_weight(0)
		new_profile.set_weight(70.0)
		new_profile.save()
		assert(new_profile.weights.count() == 1)
		assert(new_profile.weights[0].weight == 70.0)

	def test_profile_updates_weight_history_on_several_new_weights(self):	# last is saved
		user = User('user', 'user@mail.com')
		user.save()		
		new_profile = Profile(user)
		new_profile.set_weight(69.0)
		new_profile.set_weight(70.0)
		new_profile.set_weight(71.0)
		new_profile.save()
		assert(new_profile.weights.count() == 1)
		assert(new_profile.weights[0].weight == 71.0)	

	def test_profile_weight_history_relationship(self):
		user = User('user', 'user@mail.com')
		user.save()		
		new_profile = Profile(user)
		new_profile.set_weight(69.0)
		new_profile.save()
		weight_history_record = ProfileWeightHistory.get_by_id(1)
		assert(weight_history_record is not None)
		assert(weight_history_record.profile_id == new_profile.id)
		assert(weight_history_record.weight == 69.0)


	def test_profile_user_relationship(self):
		user = User('profileUsername', 'user@mail.com')
		user.save()
		profile = Profile(user)
		profile.save()
		assert(profile.user is not None)
		assert(profile.user.username == 'profileUsername')	
		assert(profile.user.email == 'user@mail.com')


	def _init_profile_with_goals(self):
		user = User('user', 'user@mail.com')
		user.save()
		profile = Profile(user)
		profile.save()
		goal_cat = GoalCategoryModel('demo')
		goal_cat.save()
		previous_start_at = dt.datetime.utcnow() + dt.timedelta(days=-5)
		current_start_at = dt.datetime.utcnow() + dt.timedelta(days=-2)
		later_start_at = dt.datetime.utcnow() + dt.timedelta(days=1)
		GoalModel(profile.id, goal_cat, current_start_at, current_start_at + dt.timedelta(days=4), 0, 10, 11).save() # completed but still active positive-going
		GoalModel(profile.id, goal_cat, later_start_at, later_start_at + dt.timedelta(days=4), 0, 10, 0).save() # not completed, future
		GoalModel(profile.id, goal_cat, previous_start_at, previous_start_at + dt.timedelta(days=4), 0, 5, 4).save() # not completed, pos.going
		return profile

	def test_init_profile_with_goals(self):
		profile = self._init_profile_with_goals()
		goals = profile.goals.all()
		assert(len(goals) == 3)
		assert(goals[2].start_at < goals[0].start_at < goals[1].start_at)
		assert(len(profile.get_active_goals()) == 1)
		assert(len(profile.get_expired_goals()) == 1)
		assert(len(profile.get_future_goals()) == 1)
	
	def test_active_goals_sorting(self):
		# should be sorted with those which ends in closest future first
		profile = self._init_profile_with_goals()
		adjusted_now = dt.datetime.utcnow() + dt.timedelta(days=-2, minutes=1)
		cat = GoalCategoryModel('new').save()
		GoalModel(profile.id, cat, start_at=adjusted_now + dt.timedelta(days=-20), end_at=adjusted_now + dt.timedelta(days=20)).save()
		goals = profile.get_active_goals(adjusted_now)
		assert(len(goals) == 3)
		assert(goals[0].end_at < goals[1].end_at < goals[2].end_at)

	def test_previous_goals_sorting(self):
		# should be sorted with those which ended in closest past first
		profile = self._init_profile_with_goals()
		adjusted_now = dt.datetime.utcnow() + dt.timedelta(days=10)
		cat = GoalCategoryModel('new').save()
		GoalModel(profile.id, cat, adjusted_now + dt.timedelta(days=-20), adjusted_now + dt.timedelta(days=-1)).save()
		goals = profile.get_expired_goals(adjusted_now)
		assert(len(goals) == 4)
		assert(goals[0].end_at > goals[1].end_at > goals[2].end_at > goals[3].end_at)

	def test_future_goals_sorting(self):
		# should be sorted with those which have start date in closest future first
		profile = self._init_profile_with_goals()
		adjusted_now = dt.datetime.utcnow() + dt.timedelta(days=-10)
		cat = GoalCategoryModel('new').save()
		GoalModel(profile.id, cat, adjusted_now + dt.timedelta(days=1), adjusted_now + dt.timedelta(days=20)).save()
		goals = profile.get_future_goals(adjusted_now)
		assert(len(goals) == 4)
		assert(goals[0].start_at < goals[1].start_at < goals[2].start_at < goals[3].start_at)

	def test_get_completed_goals(self):
		# sorted with most recently ended first
		profile = self._init_profile_with_goals()
		cat = GoalCategoryModel('new').save()
		start_at = dt.datetime.utcnow() + dt.timedelta(days=-5)
		GoalModel(profile.id, cat, start_at, start_at + dt.timedelta(days=2), 10, 2, 2).save() # completed, negative-going
		GoalModel(profile.id, cat, start_at, start_at + dt.timedelta(days=3), 2, 10, 11).save() # completed, positive-going
		GoalModel(profile.id, cat, start_at + dt.timedelta(days=6), start_at + dt.timedelta(days=8), 10, 2, 2).save() # completed per se, but in future
		goals = profile.get_completed_goals()
		assert(len(goals) == 2)
		assert(goals[0].end_at > goals[1].end_at)
		assert(goals[0].id == 5)
		assert(goals[1].id == 4)

	def test_get_incompleted_goals(self):
		# sorted with most recently ended first
		profile = self._init_profile_with_goals()
		cat = GoalCategoryModel('new').save()
		start_at = dt.datetime.utcnow() + dt.timedelta(days=-5)
		GoalModel(profile.id, cat, start_at, start_at + dt.timedelta(days=2), 10, 2, 3).save() # not completed, positive-going
		goals = profile.get_incompleted_goals()
		assert(len(goals) == 2)
		assert(goals[0].end_at > goals[1].end_at)
		assert(goals[0].id == 3)
		assert(goals[1].id == 4)

	def test_get_goal_by_id(self):
		profile = self._init_profile_with_goals()
		goal1 = profile.get_goal_by_id(1)
		goal2 = profile.get_goal_by_id(2)
		goal3 = profile.get_goal_by_id(99)
		assert(goal1.id == 1)
		assert(goal2.id == 2)
		assert(goal3 is None)

	def _init_profile_with_workouts(self):
		user = User('user', 'user@mail.com')
		user.save(commit=False)
		profile = Profile(user)
		profile.save(commit=False)
		cat1 = WorkoutCategoryModel('Running', True)
		cat1.save(commit=False)
		cat2 = WorkoutCategoryModel('Swimming', True)
		cat2.save()
		WorkoutModel(profile.id, cat1, "Run 1", dt.datetime.utcnow() - dt.timedelta(days=3), 1000, 180, 10, None, False).save(commit=False)
		WorkoutModel(profile.id, cat1, "Run 2", dt.datetime.utcnow() - dt.timedelta(days=2), 1000, 180, 10, None, False).save(commit=False)
		WorkoutModel(profile.id, cat2, "Swim 1", dt.datetime.utcnow() - dt.timedelta(days=1), 100, 180, 0, None, False).save()
		return profile

	def test_init_profile_with_workouts(self):
		profile = self._init_profile_with_workouts()
		workouts = profile.get_workouts(10, 0)
		assert(len(workouts) == 3)
	
	def test_get_workouts_limit1(self):
		profile = self._init_profile_with_workouts()
		workouts = profile.get_workouts(1, 0)
		assert(len(workouts) == 1)
		assert(workouts[0].id == 3) # sorting with newest first
	
	def test_get_workouts_limit2_offset1(self):
		profile = self._init_profile_with_workouts()
		workouts = profile.get_workouts(2, 1)
		assert(len(workouts) == 2)
		assert(workouts[0].id == 2) # sorting with newest first
		assert(workouts[1].id == 1)
	
	def test_get_running_workouts(self):
		profile = self._init_profile_with_workouts()
		workouts = profile.get_workouts(10, 0, 1)
		assert(len(workouts) == 2)
		assert(workouts[0].id == 2) # newest first
		assert(workouts[1].id == 1)

	def test_get_swimming_workouts(self):
		profile = self._init_profile_with_workouts()
		workouts = profile.get_workouts(10, 0, 2)
		assert(len(workouts) == 1)
		assert(workouts[0].id == 3)

	def test_get_workout_by_id(self):
		profile = self._init_profile_with_workouts()
		workout1 = profile.get_workout_by_id(1)
		workout2 = profile.get_workout_by_id(2)
		workout3 = profile.get_workout_by_id(99)
		assert(workout1.id == 1)
		assert(workout2.id == 2)
		assert(workout3 is None)
