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
    ENV = "undefined"
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir)) # Parent, i.e. 'run4it'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APISPEC_FORMAT_RESPONSE = False

    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']

    # Define in sub-classes
    #ENV = None
    #DEBUG = False
    #TESTING = False
    #SECRET_KEY = 'some-secret'
    #SQLALCHEMY_DATABASE_URI = None


class DevelopConfig(Config):
    """Development Configuration"""
    ENV = "development"
    DEBUG = True
    TESTING = True
    SECRET_KEY = "very-very-top-secret"
    JWT_SECRET_KEY = "even-more-top-secreterer"
    SQLALCHEMY_DATABASE_URI = os.environ.get("RUN4IT_DB_URL", "postgresql://run4it@localhost/run4it")
    MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")

class TestConfig(Config):
    """Test Configuration"""
    ENV = "test"
    DEBUG = True
    TESTING = True
    SECRET_KEY = "very-very-top-secret"
    JWT_SECRET_KEY = "even-more-top-secreterer"
    SQLALCHEMY_DATABASE_URI = os.environ.get("RUN4IT_DBTEST_URL", "postgresql://run4it@localhost/run4it_test")
    MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")

class ProductionConfig(Config):
    """Production Configuration"""
    ENV = "production"
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("RUN4IT_SECRET_KEY", "very-secret")
    JWT_SECRET_KEY = os.environ.get("RUN4IT_JWT_SECRET_KEY", "very-secreterer")
    SQLALCHEMY_DATABASE_URI = os.environ.get("RUN4IT_DB_URL", "postgresql://run4it:run4it@localhost/run4it")
    MAIL_SERVER = "smtp.fastmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
    MAIL_DEFAULT_SENDER = os.environ.get("RUN4IT_FASTMAIL_USERNAME", "nousefor@name.com")
    MAIL_PASSWORD = os.environ.get("RUN4IT_FASTMAIL_PASSWORD", "password")
