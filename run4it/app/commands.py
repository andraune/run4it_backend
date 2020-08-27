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
	from run4it.api.polar import PolarUserModel, PolarWebhookExerciseModel

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
	
	rows = PolarUserModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from PolarUser table'.format(rows))

	rows = PolarWebhookExerciseModel.query.delete(False)
	if rows > 0:
		print('Deleted {0} rows from PolarWebhookExercise table'.format(rows))

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

	workout_cat_run = WorkoutCategoryModel('Running', True)
	workout_cat_run.save(commit=False)
	print("Added {0}".format(workout_cat_run))
	workout_cat = WorkoutCategoryModel('Cross-country skiing', True)
	workout_cat.save(commit=False)
	print("Added {0}".format(workout_cat))
	workout_cat = WorkoutCategoryModel('Roller skiing', True)
	workout_cat.save(commit=False)
	print("Added {0}".format(workout_cat))
	workout_cat_fitness = WorkoutCategoryModel('Fitness', False)
	workout_cat_fitness.save(commit=False)
	print("Added {0}".format(workout_cat_fitness))
	db.session.commit()

	goalCatCumRun = GoalCategoryModel('Cumulative distance', 'km', 1)
	goalCatCumRun.save(commit=False)
	print("Added {0}".format(goalCatCumRun))
	goalCatWeightLoss = GoalCategoryModel('Weight loss', 'kg')
	goalCatWeightLoss.save(commit=False)
	print("Added {0}".format(goalCatWeightLoss))
	goalCatSkiingCount = GoalCategoryModel('Workout count', '#', 2)
	goalCatSkiingCount.save(commit=False)
	print("Added {0}".format(goalCatSkiingCount))
	goalCatFitnessCount = GoalCategoryModel('Workout count', '#', 4) 
	goalCatFitnessCount.save(commit=False)
	print("Added {0}".format(goalCatFitnessCount))
	goalCatCumClimb = GoalCategoryModel('Cumulative climb', 'm', 1) # running
	goalCatCumClimb.save(commit=False)
	print("Added {0}".format(goalCatCumClimb))
	db.session.commit()

	now = dt.datetime.utcnow()
	next_january = dt.datetime(now.year + 1, 1, 1)
	prev_january = dt.datetime(now.year, 1, 1)
	this_month_first = dt.datetime(now.year, now.month, 1)
	next_month_first = this_month_first + dt.timedelta(days=monthrange(this_month_first.year, this_month_first.month)[1])
	last_day_prev_month = this_month_first + dt.timedelta(days=-1)
	prev_month_first = this_month_first + dt.timedelta(days=-monthrange(last_day_prev_month.year, last_day_prev_month.month)[1])
	prev_monday = dt.datetime(now.year, now.month, now.day) + dt.timedelta(days=-now.weekday())

	# future goal
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatSkiingCount, next_january, next_january + dt.timedelta(days=100), 0, 30, 0)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatCumRun, next_month_first, next_month_first + dt.timedelta(days=monthrange(next_month_first.year, next_month_first.month)[1]), 0, 100, 0)
	goal.save(commit=False)
	print("Added {0}".format(goal))

	# active goals
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatWeightLoss, prev_monday, prev_monday + dt.timedelta(days=8), 79, 76, 77)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatCumRun, this_month_first, next_month_first, 0, 100, 22.666)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatFitnessCount, prev_january, next_january, 0, 20, 4)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatCumClimb, prev_january - dt.timedelta(days=10), next_january, 0, 8848, 2174)
	goal.save(commit=False)
	print("Added {0}".format(goal))

	# expired goals
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatCumRun, prev_month_first, this_month_first, 0, 100, 98)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	goal = GoalModel(User.find_by_username('JonnyIT').profile.id, goalCatWeightLoss, prev_month_first, this_month_first, 82, 80, 79)
	goal.save(commit=False)
	print("Added {0}".format(goal))
	db.session.commit()

	# Workouts
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_run, "Åsen run 3", dt.datetime.utcnow(), 7321, 1921, 430)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_run, "Åsen run 2", dt.datetime.utcnow()-dt.timedelta(seconds=90000), 3000, 658, 621, 'C:/mydev/run4it_backend/run4it/uploads/gpx/test.tcx', 1)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_run, "Åsen run 1", dt.datetime.utcnow()-dt.timedelta(seconds=180000), 12345, 658, 1123, 'C:/mydev/run4it_backend/run4it/uploads/gpx/test2.tcx', 1)
	workout.save(commit=False)
	print("Added {0}".format(workout))	
	db.session.commit()
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_fitness, "Fitness 1", dt.datetime.utcnow()-dt.timedelta(days=20), 0, 3600, 0)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_fitness, "Fitness 2", dt.datetime.utcnow()-dt.timedelta(days=17), 0, 3600, 0)
	workout.save(commit=False)
	print("Added {0}".format(workout))	
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_fitness, "Fitness 3", dt.datetime.utcnow()-dt.timedelta(days=15), 0, 3600, 0)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	workout = WorkoutModel(User.find_by_username('JonnyIT').profile.id, workout_cat_fitness, "Fitness 4", dt.datetime.utcnow(), 0, 3600, 0)
	workout.save(commit=False)
	print("Added {0}".format(workout))
	db.session.commit()	

	print('Application data initialized!')
	return 0
