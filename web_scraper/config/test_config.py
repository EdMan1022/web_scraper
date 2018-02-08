from .base_config import BaseConfig
import os


class TestConfig(BaseConfig):
    """
    Config class used for testing.

    Sets debug to true, and changes database to test one
    """

    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_TEST_DATABASE_URI')
    DEBUG = True
