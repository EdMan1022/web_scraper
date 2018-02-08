from .base_config import BaseConfig
import os


class DevelopmentConfig(BaseConfig):
    """
    Config class used for development.

    Sets debug to true, and changes the name to development config
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DEVELOPMENT_DATABASE_URI')
    DEBUG = True
