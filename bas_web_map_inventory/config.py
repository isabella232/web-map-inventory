import logging
import os

import pkg_resources

from typing import Dict

from flask.cli import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from str2bool import str2bool


class Config:
    ENV = os.environ.get('FLASK_ENV')
    DEBUG = False
    TESTING = False

    NAME = 'bas-web-map-inventory'

    LOGGING_LEVEL = logging.WARNING

    def __init__(self):
        load_dotenv()

        self.APP_ENABLE_SENTRY = str2bool(os.environ.get('APP_ENABLE_SENTRY')) or True
        self.AIRTABLE_API_KEY = os.environ.get('AIRTABLE_API_KEY')
        self.AIRTABLE_BASE_ID = os.environ.get('AIRTABLE_BASE_ID')

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return os.environ.get('APP_RELEASE') or 'unknown'

    # noinspection PyPep8Naming
    @property
    def SENTRY_CONFIG(self) -> Dict:
        return {
            'dsn': os.environ.get('SENTEY_DSN') or None,
            'integrations': [FlaskIntegration()],
            'environment': self.ENV,
            'release': self.VERSION
        }


class ProductionConfig(Config):
    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return pkg_resources.require("bas-web-map-inventory")[0].version


class DevelopmentConfig(Config):
    @property
    def SENTRY_CONFIG(self) -> Dict:
        _config = super().SENTRY_CONFIG
        _config['server_name'] = 'Local container'

        return _config

    LOGGING_LEVEL = logging.INFO

    def __init__(self):
        super().__init__()
        self.APP_ENABLE_SENTRY = str2bool(os.environ.get('APP_ENABLE_SENTRY')) or False

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return 'N/A'


class TestingConfig(Config):
    DEBUG = True
    TESTING = True

    LOGGING_LEVEL = logging.DEBUG

    def __init__(self):
        super().__init__()
        self.APP_ENABLE_SENTRY = False

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return 'N/A'