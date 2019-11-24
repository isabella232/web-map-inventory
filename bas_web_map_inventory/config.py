import logging
import os
from typing import Dict

from flask.cli import load_dotenv


class Config:
    ENV = os.getenv('FLASK_ENV')
    DEBUG = False
    TESTING = False

    LOGGING_LEVEL = logging.WARNING

    def __init__(self):
        load_dotenv()

        self.AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
        self.AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

        return _config


class ProductionConfig(Config):
    pass


class DevelopmentConfig(Config):
    LOGGING_LEVEL = logging.INFO



class TestConfig(Config):
    DEBUG = True
    TESTING = True

    LOGGING_LEVEL = logging.DEBUG

