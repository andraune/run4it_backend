import json


def get_response_json(response_data):
    return json.loads(response_data.decode("utf-8"))
