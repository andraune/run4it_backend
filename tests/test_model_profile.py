"""Model unit tests."""
import pytest
from run4it.api.profile.model import Profile
from run4it.api.user.model import User

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
		assert(new_profile.birth_date is None) 

	def test_profile_birth_date(self):
		user = User('user', 'user@mail.com')
		user.save()
		new_profile = Profile(user)
		new_profile.set_birth_date(1980, 1, 2)
		new_profile.save()
		assert(new_profile.birth_date.year == 1980)
		assert(new_profile.birth_date.month == 1)
		assert(new_profile.birth_date.day == 2)

	def test_profile_user_relationship(self):
		user = User('profileUsername', 'user@mail.com')
		user.save()
		profile = Profile(user)
		profile.save()	
		assert(profile.user is not None)
		assert(profile.user.username == 'profileUsername')	
		assert(profile.user.email == 'user@mail.com')
