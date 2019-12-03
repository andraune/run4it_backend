"""Model unit tests."""
import pytest
import datetime as dt
from run4it.api.user.model import User
from run4it.api.token.model import TokenRegistry

@pytest.mark.usefixtures('db')
class TestTokenRegistryModel:

	def test_get_by_id(self):
		new_token = TokenRegistry('jti', 'type', 'username', True, dt.datetime.utcnow())
		new_token.save()
		retrieved_token = TokenRegistry.get_by_id(new_token.id)
		assert(retrieved_token == new_token)

	def test_find_by_username(self):
		token1 = TokenRegistry('jti_1', 'type_1', 'username', True, dt.datetime.utcnow())
		token2 = TokenRegistry('jti_2', 'type_2', 'username', False, dt.datetime.utcnow() + dt.timedelta(hours=1))
		token3 = TokenRegistry('jti_1', 'type_1', 'different', True, dt.datetime.utcnow())
		token1.save(False)
		token2.save(False)
		token3.save()
		user_tokens = TokenRegistry.find_by_username('username')
		assert(len(user_tokens) == 2)

	def test_find_by_jti(self):
		token1 = TokenRegistry('jti_1', 'type_1', 'username', True, dt.datetime.utcnow())
		token2 = TokenRegistry('jti_2', 'type_2', 'username', False, dt.datetime.utcnow() + dt.timedelta(hours=1))
		token1.save(False)
		token2.save()
		retrieved = TokenRegistry.find_by_jti('jti_1')
		jti_none = TokenRegistry.find_by_jti('jti_dontexist')
		assert(retrieved.jti == 'jti_1')
		assert(jti_none is None)


	def test_values_not_nullable(self):
		assert(TokenRegistry.jti.nullable == False)
		assert(TokenRegistry.username.nullable == False)
		assert(TokenRegistry.token_type.nullable == False)
		assert(TokenRegistry.revoked.nullable == False)
		assert(TokenRegistry.expires.nullable == False)

	def test_no_unique_constraints(self, db):
		token1 = TokenRegistry('jti', 'type', 'username', True, dt.datetime.utcnow())
		token2 = TokenRegistry('jti', 'type', 'username', True, dt.datetime.utcnow())
		token1.save()
		token2.save()

		num_users = db.session.query(TokenRegistry).count()
		assert(num_users == 2)
	
	def test_username_column_settings(self):
		token_username = TokenRegistry.username
		user_username = User.username
		assert(type(token_username.type) == type(user_username.type))
		assert(token_username.type.length == user_username.type.length)
