"""Model unit tests."""
import pytest
import datetime as dt
from run4it.api.profile import Profile, ProfileWeightHistory
from run4it.api.user import User
from run4it.api.goal import GoalModel, GoalCategoryModel

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
		assert(new_profile.weights.count() == 2)
		assert(new_profile.weights[1].weight == 70.0)

	def test_profile_updates_weight_history_on_several_new_weights(self):
		user = User('user', 'user@mail.com')
		user.save()		
		new_profile = Profile(user)
		new_profile.set_weight(69.0)
		new_profile.set_weight(70.0)
		new_profile.set_weight(71.0)
		new_profile.save()
		assert(new_profile.weights.count() == 3)
		assert(new_profile.weights[0].weight == 69.0)
		assert(new_profile.weights[1].weight == 70.0)	
		assert(new_profile.weights[2].weight == 71.0)		

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
		GoalModel(profile.id, goal_cat, current_start_at, current_start_at + dt.timedelta(days=4)).save()
		GoalModel(profile.id, goal_cat, later_start_at, later_start_at + dt.timedelta(days=4)).save()
		GoalModel(profile.id, goal_cat, previous_start_at, previous_start_at + dt.timedelta(days=4)).save()
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
		GoalModel(profile.id, cat, start_at=adjusted_now + dt.timedelta(days=-20), end_at=adjusted_now + dt.timedelta(days=-1)).save()
		goals = profile.get_expired_goals(adjusted_now)
		assert(len(goals) == 4)
		assert(goals[0].end_at > goals[1].end_at > goals[2].end_at > goals[3].end_at)

	def test_future_goals_sorting(self):
		# should be sorted with those which have start date in closest future first
		profile = self._init_profile_with_goals()
		adjusted_now = dt.datetime.utcnow() + dt.timedelta(days=-10)
		cat = GoalCategoryModel('new').save()
		GoalModel(profile.id, cat, start_at=adjusted_now + dt.timedelta(days=1), end_at=adjusted_now + dt.timedelta(days=20)).save()
		goals = profile.get_future_goals(adjusted_now)
		assert(len(goals) == 4)
		assert(goals[0].start_at < goals[1].start_at < goals[2].start_at < goals[3].start_at)
