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
    APP_DIR = os.path.abspath(os.path.dirname(__file__))  # This directory
    PROJECT_ROOT = os.path.abspath(os.path.join(APP_DIR, os.pardir)) # Parent, i.e. 'run4it'
    
    # Define in sub-classes
    ENV = None



class DevelopConfig(Config):
    """Development Configuration"""
    ENV = "development"


class ProductionConfig(Config):
    """Production Configuration"""
    ENV = "production"
