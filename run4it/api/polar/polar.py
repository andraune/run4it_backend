
import requests
import hmac
import hashlib
from base64 import b64encode
from flask import current_app

BASE_ACCESSLINK_URL = 'https://www.polaraccesslink.com/v3'
TOKEN_ENDPOINT = 'https://polarremote.com/v2/oauth2/token'
REGISTER_ENDPOINT = '{base}/users'.format(base=BASE_ACCESSLINK_URL)


# Authentication header contents (helpers)

def _get_basic_auth_header():
	client_id = str(current_app.config['POLAR_API_CLIENT_ID']).encode('utf-8')
	client_secret = str(current_app.config['POLAR_API_CLIENT_SECRET']).encode('utf-8')
	base64_encoded_auth_string = b64encode(b':'.join((client_id, client_secret))).strip()
	return 'Basic {b64}'.format(b64=base64_encoded_auth_string.decode('utf-8'))

def _get_bearer_auth_header(access_token):
	return 'Bearer {token}'.format(token=access_token)

def get_hmac_signature(key_str, message_bytes):
	key_bytes = bytes(key_str, 'utf-8')
	signature = ''
	try:
		signature = hmac.new(key_bytes, msg=message_bytes, digestmod=hashlib.sha256).hexdigest().lower()
	except:
		signature = '<error>'
	return signature


# Request / Response handlers

def retrieve_access_token(auth_code):
	''' Attempts to get user access token from Polar Flow, using TOKEN_ENDPOINT (POST)'''
	headers = {
		"Content-Type" : "application/x-www-form-urlencoded",
		"Accept" : "application/json",
		"Authorization" : _get_basic_auth_header()
	}
	data = {
		"grant_type" : "authorization_code",
		"code" : auth_code
	}

	try:
		result = requests.post(TOKEN_ENDPOINT, data=data, headers=headers)
		if result.status_code == 200:
			response_json = result.json()
			if ('access_token' in response_json
				and 'expires_in' in response_json
				and 'x_user_id' in response_json):
				return response_json
			else:
				return None
		else:
			return None
	except:
		return None


def register_user(token, member_id):
	''' Attemts to register user in Polar Flow access link, using REGISTER_ENDPOINT (POST)'''
	headers = {
		"Content-Type": "application/json",
		"Accept": "application/json",
		"Authorization": _get_bearer_auth_header(token)
	}
	data = {
		'member-id': member_id
	}
	
	try:
		result = requests.post(REGISTER_ENDPOINT, json=data, headers=headers)

		if result.status_code == 200:
			return True, 'user registered'
		else:
			return False, 'code {code} returned'.format(result.status_code)
	except:
		return False, 'unexpected error'

def unregister_user(token, user_id):
	''' Attemts to unregister user in Polar Flow access link, using 
	REGISTER_ENDPOINT with user_id appended (DELETE)'''
	headers = {
		'Content-Type': 'application/json',
		'Accept': 'application/json;charset=UTF-8',
		'Authorization': _get_bearer_auth_header(token)
	}

	USER_ENDPOINT = '{base}/{id}'.format(base=REGISTER_ENDPOINT, id=user_id)

	try:
		result = requests.delete(USER_ENDPOINT, headers=headers)
		return result.status_code == 204
	except:
		return False	

