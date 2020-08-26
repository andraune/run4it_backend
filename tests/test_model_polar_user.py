"""Model unit tests."""
import pytest
from run4it.api.polar import PolarUserModel

@pytest.mark.usefixtures('db')
class TestPolarUserModel:

	def test_get_by_id(self):
		new_user = PolarUserModel(1, 'user')
		new_user.save()
		retrieved_user = PolarUserModel.get_by_id(new_user.id)
		assert(retrieved_user == new_user)

	def test_member_id_prefix(self, db):
		new_user = PolarUserModel(1, 'user')
		assert(new_user.member_id == 'R4IT_user')

	def test_member_id_unique(self, db):
		user1 = PolarUserModel(1, 'user')
		user1.save()
		try:
			user2 = PolarUserModel(2, 'user')
			user2.save()  # should fail
		except:
			db.session.rollback()
		num_users = db.session.query(PolarUserModel).count()
		assert(num_users == 1)

	def test_profile_id_unique(self, db):
		user1 = PolarUserModel(1, 'userOne')
		user1.save()
		try:
			user2 = PolarUserModel(1, 'userTwo')
			user2.save()  # should fail
		except:
			db.session.rollback()
		num_users = db.session.query(PolarUserModel).count()
		assert(num_users == 1)
	
	def test_default_values(self, db):
		new_user = PolarUserModel(1, 'user')
		new_user.save()
		assert(new_user.profile_id == 1)
		assert(new_user.polar_user_id == 0)
		assert(new_user.state is None)
		assert(new_user.access_token is None)
		assert(new_user.access_token_expires is None)
		assert(new_user.updated_at is None)
		assert(new_user.auth_url == '')
		assert(new_user.is_registered() == False)
		assert(new_user.has_valid_access_token() == False)

	def test_get_by_member_id(self, db):
		new_user = PolarUserModel(1, 'user')
		new_user.save()
		retrieved_user = PolarUserModel.find_by_member_id('R4IT_user')
		assert(retrieved_user == new_user)

	def test_get_by_state_code(self, db):
		new_user = PolarUserModel(1, 'user')
		new_user.state = 'code'
		new_user.save()
		retrieved_user = PolarUserModel.find_by_state_code('code')
		assert(retrieved_user == new_user)

	def test_generate_state_code(self, db):
		new_user = PolarUserModel(1, 'user')
		new_user.generate_state_code()
		assert(len(new_user.state) == 15)

	def test_get_by_state_code_fails_if_duplicate(self, db):
		user1 = PolarUserModel(1, 'user')
		user1.state = "code"
		user1.save(commit=False)
		user2 = PolarUserModel(2, 'another-user')
		user2.state = "code"
		user2.save()
		retrieved_user = PolarUserModel.find_by_state_code('code')
		assert(retrieved_user is None)
