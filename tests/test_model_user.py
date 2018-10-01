"""Model unit tests."""
import pytest
from run4it.api.user.model import User

@pytest.mark.usefixtures('db')
class TestUserModel:

    def test_get_by_id(self):
        new_user = User('foo', 'foo@bar.com')
        new_user.save()
        retrieved_user = User.get_by_id(new_user.id)
        assert(retrieved_user == new_user)

    def test_email_unique(self, db):
        user1 = User('new', 'new@mail.com')
        user1.save()

        try:
            user2 = User('another', 'new@mail.com')
            user2.save()  # should fail

        except:
            db.session.rollback()

        num_users = db.session.query(User).count()
        assert(num_users == 1)

    def test_username_unique(self, db):
        user1 = User('new', 'new@mail.com')
        user1.save()

        try:
            user2 = User('new', 'another@mail.com')
            user2.save()  # should fail

        except:
            db.session.rollback()

        num_users = db.session.query(User).count()
        assert(num_users == 1)

    def test_confirmed_defaults_to_false(self):
        user = User('user', 'user@mail.com')
        user.save()
        assert(user.confirmed is False)
