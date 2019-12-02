"""Model unit tests."""
import pytest
from run4it.api.profile import Profile, ProfileWeightHistory
from run4it.api.user import User

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
