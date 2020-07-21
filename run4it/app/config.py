import os


def get_environment_config():
	"""Returns Config object based on env.var. FLASK_DEBUG"""
	env_config = ProductionConfig()
	debug_flag = os.environ.get('FLASK_DEBUG', 0)

	if debug_flag:
		env_config = DevelopConfig()

	return env_config


class Config(object):
	"""Base Configuration (abstract)"""
	PROPAGATE_EXCEPTIONS = True
	ENV = "undefined"
	APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
	PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir)) # Parent, i.e. 'run4it'
	SQLALCHEMY_TRACK_MODIFICATIONS = False
	APISPEC_FORMAT_RESPONSE = False

	JWT_BLACKLIST_ENABLED = True
	JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

	CACHE_TYPE = 'simple'
	CORS_ORIGIN_WHITELIST = [
		'http://localhost:4200',
		'http://127.0.0.1:4200',
		'http://10.0.0.117:4200',
	]

	ALLOWED_UPLOAD_EXTENSIONS = { 'gpx', 'tcx' }
	

	# Define in sub-classes
	#ENV = None
	#DEBUG = False
	#TESTING = False
	#SECRET_KEY = 'some-secret'
	#SQLALCHEMY_DATABASE_URI = None
	#GPX_UPLOAD_DIR


class DevelopConfig(Config):
	"""Development Configuration"""
	ENV = "development"
	DEBUG = True
	TESTING = True
	SECRET_KEY = "very-very-top-secret"
	JWT_SECRET_KEY = "even-more-top-secreterer"
	SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(os.path.join(Config.PROJECT_ROOT, 'dev.db'))
	MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
	GPX_UPLOAD_DIR = os.path.join(Config.PROJECT_ROOT, "uploads/gpx")
	GOOGLE_API_KEY = os.environ.get("GMAPS_API_KEY", "gmaps_api_key")

class TestConfig(Config):
	"""Test Configuration"""
	ENV = "test"
	DEBUG = True
	TESTING = True
	PRESERVE_CONTEXT_ON_EXCEPTION = False
	SECRET_KEY = "very-very-top-secret"
	JWT_SECRET_KEY = "even-more-top-secreterer"
	SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(os.path.join(Config.PROJECT_ROOT, 'test.db'))
	MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
	GPX_UPLOAD_DIR = os.path.join(Config.PROJECT_ROOT, "uploads/gpx")
	GOOGLE_API_KEY = "gmaps_api_key"

class ProductionConfig(Config):
	"""Production Configuration"""
	ENV = "production"
	DEBUG = False
	TESTING = False
	SECRET_KEY = os.environ.get("RUN4IT_SECRET_KEY", "very-secret")
	JWT_SECRET_KEY = os.environ.get("RUN4IT_JWT_SECRET_KEY", "very-secreterer")
	SQLALCHEMY_DATABASE_URI = os.environ.get("RUN4IT_DB_URL", "postgresql://run4it:run4it@localhost/run4it")
	GPX_UPLOAD_DIR = os.path.join(Config.PROJECT_ROOT, "uploads/gpx")
	GOOGLE_API_KEY = os.environ.get("GMAPS_API_KEY", "gmaps_api_key")

	CORS_ORIGIN_WHITELIST = [
		'https://localhost:4200',
		'https://127.0.0.1:4200',
		'https://run4it.jonnytech.net'
	]

	MAIL_SERVER = "smtp.fastmail.com"
	MAIL_PORT = 587
	MAIL_USE_TLS = True
	MAIL_USERNAME = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
	MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
	MAIL_PASSWORD = os.environ.get("RUN4IT_FASTMAIL_PASSWORD", "password")
