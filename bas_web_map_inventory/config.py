import logging
import os

import pkg_resources

from typing import Dict
from pathlib import Path

from flask.cli import load_dotenv
from sentry_sdk.integrations.flask import FlaskIntegration
from str2bool import str2bool


class Config:
    """
    Flask configuration base class

    Includes a mixture of static and dynamic configuration options. Dynamic objects are typically set from environment
    variables (set directly or through environment files).

    See the project README for configuration option details.
    """

    ENV = os.environ.get("FLASK_ENV")
    DEBUG = False
    TESTING = False

    NAME = "bas-web-map-inventory"

    LOGGING_LEVEL = logging.WARNING

    def __init__(self):
        load_dotenv()

        self.APP_ENABLE_FILE_LOGGING = str2bool(os.environ.get("APP_ENABLE_FILE_LOGGING")) or False
        self.APP_ENABLE_SENTRY = str2bool(os.environ.get("APP_ENABLE_SENTRY")) or True

        self.LOG_FORMAT = "[%(asctime)s] %(levelname)s [%(name)s.%(funcName)s:%(lineno)d] %(message)s"
        self.LOG_FILE_PATH = Path(os.environ.get("LOG_FILE_PATH") or "/var/log/app/app.log")

        self.SENTRY_DSN = os.environ.get("SENTRY_DSN") or None

        self.AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
        self.AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return "Unknown"

    # noinspection PyPep8Naming
    @property
    def SENTRY_CONFIG(self) -> Dict:
        return {
            "dsn": self.SENTRY_DSN,
            "integrations": [FlaskIntegration()],
            "environment": self.ENV,
            "release": self.VERSION,
        }


class ProductionConfig(Config):  # pragma: no cover
    """
    Flask configuration for Production environments

    Note: This method is excluded from test coverage as its meaning would be undermined.
    """

    def __init__(self):
        super().__init__()
        self.APP_ENABLE_FILE_LOGGING = str2bool(os.environ.get("APP_ENABLE_FILE_LOGGING")) or True

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return pkg_resources.require("bas-web-map-inventory")[0].version


class DevelopmentConfig(Config):  # pragma: no cover
    """
    Flask configuration for (local) Development environments

    Note: This method is excluded from test coverage as its meaning would be undermined.
    """

    @property
    def SENTRY_CONFIG(self) -> Dict:
        _config = super().SENTRY_CONFIG
        _config["server_name"] = "Local container"

        return _config

    LOGGING_LEVEL = logging.INFO

    def __init__(self):
        super().__init__()
        self.APP_ENABLE_SENTRY = str2bool(os.environ.get("APP_ENABLE_SENTRY")) or False

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return "N/A"


class TestingConfig(Config):
    """
    Flask configuration for Testing environments
    """

    DEBUG = True
    TESTING = True

    LOGGING_LEVEL = logging.DEBUG

    def __init__(self):
        super().__init__()
        self.APP_ENABLE_FILE_LOGGING = False
        self.APP_ENABLE_SENTRY = False

    # noinspection PyPep8Naming
    @property
    def VERSION(self) -> str:
        return "N/A"
