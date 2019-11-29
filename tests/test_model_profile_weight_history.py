"""Model unit tests."""

import pytest
from run4it.api.profile import Profile, ProfileWeightHistory

@pytest.mark.usefixtures('db')
class TestProfileWeightHistoryModel:

	def test_get_by_id(self):
		new_weight = ProfileWeightHistory(profile_id=1, weight=75.1)
		new_weight.save()
		retrieved_weight = ProfileWeightHistory.get_by_id(new_weight.id)
		assert(retrieved_weight == new_weight)
		assert(new_weight.profile_id == 1)
		assert(new_weight.weight == 75.1)

	def test_two_weights_for_same_profile(self):
		new_weight1 = ProfileWeightHistory(profile_id=1, weight=75.1)
		new_weight2 = ProfileWeightHistory(profile_id=1, weight=78.1)
		new_weight1.save()
		new_weight2.save()
		assert(ProfileWeightHistory.query.count() == 2)
