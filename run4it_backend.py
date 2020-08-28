"""Application entry point"""
import logging, logging.config, yaml
from run4it.app.app import create_app
from run4it.app.config import get_environment_config
from run4it.api.api_v1 import create_api

logging.config.dictConfig(yaml.safe_load(open('logging.conf')))
app_config = get_environment_config()
app = create_app(app_config, __name__)
api = create_api(app)

if __name__ == "__main__":   
    app.run(host='0.0.0.0')
