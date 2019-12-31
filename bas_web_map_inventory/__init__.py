import os

import sentry_sdk

from logging import Formatter
from logging.handlers import RotatingFileHandler
from typing import Dict, Any

from flask import Flask, logging as flask_logging
from flask.cli import AppGroup

# noinspection PyPackageRequirements
from werkzeug.utils import import_string

from bas_web_map_inventory.cli import (
    fetch as data_fetch_cmd,
    validate as data_validate_cmd,
    status as airtable_status_cmd,
    sync as airtable_sync_cmd,
    reset as airtable_reset_cmd,
)


def _create_app_config() -> Dict[str, Any]:
    """
    Creates an object to use as a Flask app's configuration

    Creates an instance of a class defined in config.py specific to the application environment (e.g. production).

    This is a standalone class to aid in mocking during testing.

    :return: object for a Flask app's configuration
    """
    return import_string(f"bas_web_map_inventory.config.{str(os.environ['FLASK_ENV']).capitalize()}Config")()


def create_app() -> Flask:
    """
    Flask app factory

    Creates an instance of a Flask application. Flask configuration options are used to enable various optional features
    (such as logging to a file).

    This method is used to load routes, CLI commands and blueprints that make up the Flask application.

    :return: Flask application instance
    """
    app = Flask(__name__)

    app.config.from_object(_create_app_config())

    if "LOGGING_LEVEL" in app.config:
        app.logger.setLevel(app.config["LOGGING_LEVEL"])
        flask_logging.default_handler.setFormatter(Formatter(app.config["LOG_FORMAT"]))
    if app.config["APP_ENABLE_FILE_LOGGING"]:
        file_log = RotatingFileHandler(app.config["LOG_FILE_PATH"], maxBytes=5242880, backupCount=5)
        file_log.setLevel(app.config["LOGGING_LEVEL"])
        file_log.setFormatter(Formatter(app.config["LOG_FORMAT"]))
        app.logger.addHandler(file_log)

    if app.config["APP_ENABLE_SENTRY"]:
        app.logger.info("Sentry error reporting enabled")
        sentry_sdk.init(**app.config["SENTRY_CONFIG"])

    app.logger.info(f"{app.config['NAME']} ({app.config['VERSION']}) [{app.config['ENV']}]")

    data_cli_group = AppGroup("data", help="Interact with data sources.")
    app.cli.add_command(data_cli_group)
    data_cli_group.add_command(data_fetch_cmd, "fetch")
    data_cli_group.add_command(data_validate_cmd, "validate")

    airtable_cli_group = AppGroup("airtable", help="Interact with Airtable service.")
    app.cli.add_command(airtable_cli_group)
    airtable_cli_group.add_command(airtable_status_cmd, "status")
    airtable_cli_group.add_command(airtable_sync_cmd, "sync")
    airtable_cli_group.add_command(airtable_reset_cmd, "reset")

    return app
