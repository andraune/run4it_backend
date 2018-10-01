"""Model unit tests."""
import pytest
from run4it.api.user.model import User, UserConfirmation

@pytest.mark.usefixtures('db')
class TestUserConfirmationModel:

    def test_get_by_id(self):
        new_confirmation = UserConfirmation('username')
        new_confirmation.save()
        retrieved_confirmation = UserConfirmation.get_by_id(new_confirmation.id)
        assert(retrieved_confirmation == new_confirmation)

    def test_username_unique(self, db):
        confirmation1 = UserConfirmation('confirm')
        confirmation1.save()

        try:
            confirmation2 = UserConfirmation('confirm')
            confirmation2.save()  # should fail

        except:
            db.session.rollback()

        num_confirmations = db.session.query(UserConfirmation).count()
        assert(num_confirmations == 1)
    
    def test_random_code_generation(self):
        confirmation = UserConfirmation('username')
        assert(confirmation.code is not None)
        assert(len(confirmation.code) >= 32)
    
    def test_hardcoded_code(self):
        confirmation = UserConfirmation('username', 'the_code')
        assert(confirmation.code == 'the_code')   

    def test_username_column_settings(self):
        confirmation_username = UserConfirmation.username
        user_username = User.username
        assert(type(confirmation_username.type) == type(user_username.type))
        assert(confirmation_username.type.length == user_username.type.length)
