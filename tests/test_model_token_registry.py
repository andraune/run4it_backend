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
