"""Click commands"""
import click, os, datetime as dt
from calendar import monthrange
from flask import current_app
from flask.cli import with_appcontext


@click.command()
@with_appcontext
def init_test_data():
	"""Command used to empty database tables and fill with test data.
	Tailored to be used when running Newman test collection."""
	ret_code = 0

	if current_app.config["TESTING"] is True:
		ret_code = init_database_test_data()
	else:
		print("Command disabled when not TESTING.")

	exit(ret_code)


@click.command()
@with_appcontext
def clean():
	"""Remove *.pyc and *.pyo files"""
	for dirpath, _, filenames in os.walk('.'):
		for filename in filenames:
			if filename.endswith('.pyc') or filename.endswith('.pyo'):
				full_pathname = os.path.join(dirpath, filename)
				click.echo('Removing {}'.format(full_pathname))
				os.remove(full_pathname)  


@click.command()
def tests():
	"""Command used for running tests"""
	import pytest # noqa
	project_root = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
	test_path = os.path.join(project_root, "tests")
	ret_code = pytest.main([test_path, '--verbose'])
	exit(ret_code)


def init_database_test_data():
	print('Deleting database data ...')

	from run4it.app.database import db  # noqa
	from run4it.api.user import User, UserConfirmation # noqa
	from run4it.api.profile import Profile, ProfileWeightHistory  # noqa
	from run4it.api.token import TokenRegistry  # noqa
	from run4it.api.discipline import DisciplineModel # noqa
	from run4it.api.goal import GoalModel, GoalCategoryModel # noqa
	from run4it.api.workout import WorkoutCategoryModel, WorkoutModel #noqa

	# delete most stuff
	rows = User.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from User table'.format(rows))

	rows = Profile.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from Profile table'.format(rows))

	rows = UserConfirmation.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from UserConfirmation table'.format(rows))

	rows = TokenRegistry.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from TokenRegistry table'.format(rows))
	
	rows = ProfileWeightHistory.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from ProfileWeightHistory table'.format(rows))
	
	rows = DisciplineModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from Discipline table'.format(rows))
	
	rows = GoalModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from Goal table'.format(rows))	

	rows = GoalCategoryModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from GoalCategory table'.format(rows))
	
	rows = WorkoutModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from Workout table'.format(rows))

	rows = WorkoutCategoryModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from WorkoutCategory table'.format(rows))

	db.session.commit()

	# create test items
	user = User('existing', 'existing@user.com', 'pwd') #not confirmed
	profile = Profile(user)
	user.save(commit=False)
	profile.save(commit=False)
	print("Added {0}".format(user))

	user = User('JonnyIT', 'active@user.com', 'pwd')
	user.confirmed = True
	profile = Profile(user)
	profile.set_weight(79.1)
	profile.set_height(176)
	profile.set_birth_date(1979, 5, 1)
	user.save(commit=False)
	profile.save(commit=False)
	print("Added {0}".format(user))

	user = User('confirm', 'confirm@user.com', 'pwd')
	profile = Profile(user)
	profile.set_weight(70.1)
	user.save(commit=False)
	profile.save(commit=False)
	print("Added {0}".format(user)) 

	confirmation = UserConfirmation('confirm', 'correct')
	confirmation.save(commit=False)
	print("Added {0}".format(confirmation))

	discipline = DisciplineModel('10,000m', 10000)
	discipline.save(commit=False)
	print("Added {0}".format(discipline))
	discipline = DisciplineModel('5,000m', 5000)
	discipline.save(commit=False)
	print("Added {0}".format(discipline))
	discipline = DisciplineModel('1,500m', 1500)
	discipline.save(commit=False)
	print("Added {0}".format(discipline))

	goalcat1 = GoalCategoryModel('Distance', 'km')
	goalcat1.save(commit=False)
	print("Added {0}".format(goalcat1))
	goalcat2 = GoalCategoryModel('Weight target', 'kg')
	goalcat2.save(commit=False)
	print("Added {0}".format(goalcat2))
	db.session.commit()

	now = dt.datetime.utcnow()
	this_month_first = dt.datetime(now.year, now.month, 1)
	next_month_first = this_month_first + dt.timedelta(days=monthrange(this_month_first.year, this_month_first.month)[1])
	last_day_prev_month = this_month_first + dt.timedelta(days=-1)
	prev_month_first = this_month_first + dt.timedelta(days=-monthrange(last_day_prev_month.year, last_day_prev_month.month)[1])
	prev_monday = dt.datetime(now.year, now.month, now.day) + dt.timedelta(days=-now.weekday())

	# future goal
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalcat1, next_month_first, next_month_first + dt.timedelta(days=monthrange(next_month_first.year, next_month_first.month)[1]), 0, 100, 0)
	goal.save(commit=False)
	print("Added {0}".format(goal))

	# active goals
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalcat2, prev_monday, prev_monday + dt.timedelta(days=7), 79, 76, 77)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalcat1, this_month_first, next_month_first, 0, 100, 18)
	goal.save(commit=False)
	print("Added {0}".format(goal))

	# expired goals
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalcat1, prev_month_first, this_month_first, 0, 100, 98)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalcat2, prev_month_first, this_month_first, 82, 80, 79)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	db.session.commit()

	# Workout stuff
	workout_cat = WorkoutCategoryModel('Running', True)
	workout_cat.save(commit=False)
	print("Added {0}".format(workout_cat))
	workout_cat = WorkoutCategoryModel('Hiking', True)
	workout_cat.save()
	print("Added {0}".format(workout_cat))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat, "Åsen run", dt.datetime.utcnow(), 7321, 1921, 43)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat, "Åsen run", dt.datetime.utcnow(), 3000, 658, 0, 'C:/mydev/run4it_backend/run4it/uploads/gpx/test.tcx', 1)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	db.session.commit()

	print('Application data initialized!')
	return 0
