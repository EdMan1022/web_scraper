import os
import dotenv

# Load in any environment variables
env_path = os.path.join(os.path.dirname(__file__), '.env')
dotenv.load_dotenv(env_path)


class BaseConfig(object):
    """
    Wraps the base configuration for the app
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_PRODUCTION_DATABASE_URI')
    DEBUG = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_NAME = 'fulcrum_reconciliation'

    FIREFOX_BINARY_PATH = os.environ.get('FIREFOX_BINARY_PATH')
    MEDIA_MONITORS_USERNAME = os.environ.get('MEDIA_MONITORS_USERNAME')
    MEDIA_MONITORS_PASSWORD = os.environ.get('MEDIA_MONITORS_PASSWORD')
