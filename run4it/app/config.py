import os


def get_environment_config():
    """Returns Config object based on env.var. FLASK_DEBUG"""
    env_config = ProductionConfig()
    debug_flag = os.environ.get('FLASK_DEBUG', 0)

    if debug_flag:
        env_config = DevelopConfig()
    
    print("Environment: {0}".format(env_config.ENV))
    return env_config


class Config(object):
    """Base Configuration (abstract)"""
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir)) # Parent, i.e. 'run4it'

    # Define in sub-classes
    #ENV = None
    #DEBUG = False
    #TESTING = False
    #SECRET_KEY = 'some-secret'
    #SQLALCHEMY_DATABASE_URI = None
    #SQLALCHEMY_TRACK_MODIFICATIONS = False
    #APISPEC_FORMAT_RESPONSE = False


class DevelopConfig(Config):
    """Development Configuration"""
    ENV = "development"
    DEBUG = True
    TESTING = False
    SECRET_KEY = "very-very-top-secret"
    JWT_SECRET_KEY = "even-more-top-secreterer"
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(os.path.join(Config.PROJECT_ROOT, 'dev.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APISPEC_FORMAT_RESPONSE = False

class TestConfig(Config):
    """Test Configuration"""
    ENV = "test"
    DEBUG = True
    TESTING = True
    SECRET_KEY = "very-very-top-secret"
    JWT_SECRET_KEY = "even-more-top-secreterer"
    SQLALCHEMY_DATABASE_URI = "sqlite:///{0}".format(os.path.join(Config.PROJECT_ROOT, 'test.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APISPEC_FORMAT_RESPONSE = False

class ProductionConfig(Config):
    """Production Configuration"""
    ENV = "production"
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.environ.get("RUN4IT_SECRET_KEY", "9cef5cfe5b80f523b484d39d4d61d5994748128ce4b97d0d")
    JWT_SECRET_KEY = os.environ.get("RUN4IT_JWT_SECRET_KEY", "8e2cacb621f833324bca0a13f33f3194ca8bc7cca8ad8145")
    SQLALCHEMY_DATABASE_URI = os.environ.get("RUN4IT_DB_URL", "postgresql://localhost/run4it")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APISPEC_FORMAT_RESPONSE = False
