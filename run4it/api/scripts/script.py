import datetime as dt
from .model import Script as ScriptModel
from run4it.api.token import TokenRegistry
from run4it.api.workout import WorkoutModel, WorkoutCategoryModel
from run4it.api.polar import PolarUserModel, PolarWebhookExerciseModel, get_exercise_data_from_url, get_exercise_fit_from_url


def script_import_polar_exercices(script_name):
    script_entry,ret_code = _init_script_execution(script_name)
    if script_entry is None:
        return ret_code
    # Script code goes here
    polar_exercises = PolarWebhookExerciseModel.get_not_processed()
    if polar_exercises is not None:
        # Loop through exercises and download exercise data
        for exercise in polar_exercises:
            polar_user = PolarUserModel.find_by_polar_user_id(exercise.polar_user_id)

            if polar_user is not None:
                exercise_json = get_exercise_data_from_url(polar_user.access_token, exercise.url)
                
                if exercise_json is not None:
                    fit_data = None
                    
                    if exercise_json['route'] == True:
                        print("Attempt to download exercise FIT for {0}".format(exercise.entity_id))
                        fit_data = get_exercise_fit_from_url(polar_user.access_token, exercise.url, exercise.entity_id)

                    new_workout_id = _create_workout_from_polar_exercise(polar_user.profile_id, exercise_json, fit_data)
                    
                    if new_workout_id > 0:
                        print("New workout created with id {0} for Polar exercise {1}".format(new_workout_id, exercise.entity_id))             
                    else:
                        print("Failed to create workout for Polar exercise {0}".format(exercise.entity_id))

                else:
                    print("Failed to retrieve data for Polar exercise {0}".format(exercise.entity_id))

            else:
                print("Skipped Polar exercise {0}, user {1} not found".format(exercise.entity_id, exercise.polar_user_id))
            
            # mark as processed if it was imported or not, we won't try again
            try:
                exercise.processed = False
                exercise.save()
            except:
                print("Failed to set Polar exercise {0} as 'processed'".format(exercise.entity_id))

    else:
        print("Error searching for Polar exercises for import".format(len(polar_exercises)))
        ret_code = 1
    # End of script code
    return _commit_script_execution(script_entry, ret_code)


def script_token_registry_purge(script_name):
    script_entry,ret_code = _init_script_execution(script_name)
    if script_entry is None:
        print("Script init failed: {name!r},{ret!r}".format(name=script_name,ret=ret_code))
        return ret_code
    # Script code goes here
    num_removed = TokenRegistry.remove_expired_tokens()
    print("Removed {0} expired token(s)".format(num_removed))
    # End of script code
    return _commit_script_execution(script_entry, ret_code)


def _init_script_execution(script_name):
	script_entry = ScriptModel.find_by_name(script_name)
	if script_entry is None:
		try:
			script_entry = ScriptModel(script_name)
		except:
			return None, -1
	script_entry.started_at = dt.datetime.utcnow()
	return script_entry, 0

def _commit_script_execution(script_entry, return_code):
	script_entry.return_code = return_code
	script_entry.completed_at = dt.datetime.utcnow()
	try:
		script_entry.save()
		return return_code
	except:
		pass
	return -2

def _create_workout_from_polar_exercise(profile_id, exercise_json, fit_data):
    category = _get_workout_category_from_polar_exercise()
    if category is None:
        print("Unable to create workout from Polar exercise, no category found ({0},{1})".format(exercise_json['category'],exercise_json['sub_category']))
        return 0
    #new_workout = WorkoutModel(profile_id, category, "Polar", exercise_json['start_at'], exercise_json['distance'], exercise_json['duration'], 0)
    return 1

def _get_workout_category_from_polar_exercise(polar_category, polar_category_detailed):
    # category examples: RUNNING
    # sub_category examples: RUNNING
    if polar_category == 'RUNNING':
        return WorkoutCategoryModel.find_by_name('Running')
    return None
