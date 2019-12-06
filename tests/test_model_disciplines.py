import pytest
from run4it.api.discipline import DisciplineModel
from run4it.api.user import User

@pytest.mark.usefixtures('db')
class TestDisciplineModel:

	def test_get_by_id(self):
		new_discipline = DisciplineModel("10,000 m", 10000)
		new_discipline.save()
		retrieved_discipline = DisciplineModel.get_by_id(new_discipline.id)
		assert(retrieved_discipline == new_discipline)

	def test_discipline_name_unique(self, db):
		disc = DisciplineModel("discName", 1000)
		disc.save()

		try:
			disc_new = DisciplineModel("discName", 999)
			disc_new.save()

		except:
			db.session.rollback()

		num_discs = db.session.query(DisciplineModel).count()
		assert(num_discs == 1)

	def test_discipline_data(self):
		disc = DisciplineModel("10,000 m", 10000, "username")
		disc.save()
		assert(disc.id == 1)
		assert(disc.length == 10000)
		assert(disc.username == "username")

	def test_discipline_username_defaults_to_none(self):
		disc = DisciplineModel("10,000 m", 10000)
		disc.save()
		assert(disc.username is None)

	def test_discipline_find_by_name(self):
		disc = DisciplineModel("10,000 m", 10000)
		disc.save()
		retrieved_disc = DisciplineModel.find_by_name("10,000 m")
		no_disc = DisciplineModel.find_by_name("not_found")
		assert(retrieved_disc.id == disc.id)
		assert(no_disc is None)

	def test_username_column_settings(self):
		disc_username = DisciplineModel.username
		user_username = User.username
		assert(type(disc_username.type) == type(user_username.type))
		assert(disc_username.type.length == user_username.type.length)