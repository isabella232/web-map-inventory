import os

import sentry_sdk

from logging import Formatter
from logging.handlers import RotatingFileHandler

from flask import Flask, logging as flask_logging
from flask.cli import AppGroup
# noinspection PyPackageRequirements
from werkzeug.utils import import_string

from bas_web_map_inventory.cli import fetch as data_fetch_cmd, validate as data_validate_cmd, \
    status as airtable_status_cmd, sync as airtable_sync_cmd, reset as airtable_reset_cmd


def create_app():
    app = Flask(__name__)

    config = import_string(f"bas_web_map_inventory.config.{str(os.environ['FLASK_ENV']).capitalize()}Config")()
    app.config.from_object(config)

    if 'LOGGING_LEVEL' in app.config:
        app.logger.setLevel(app.config['LOGGING_LEVEL'])
        flask_logging.default_handler.setFormatter(Formatter(app.config['LOG_FORMAT']))
    if app.config['APP_ENABLE_FILE_LOGGING']:
        file_log = RotatingFileHandler(app.config['LOG_FILE_PATH'], maxBytes=5242880, backupCount=5)
        file_log.setLevel(app.config['LOGGING_LEVEL'])
        file_log.setFormatter(Formatter(app.config['LOG_FORMAT']))
        app.logger.addHandler(file_log)

    if app.config['APP_ENABLE_SENTRY']:
        app.logger.info('Sentry error reporting enabled')
        sentry_sdk.init(**app.config['SENTRY_CONFIG'])

    app.logger.info(f"{app.config['NAME']} ({app.config['VERSION']}) [{app.config['ENV']}]")

    data_cli_group = AppGroup('data', help='Interact with data sources.')
    app.cli.add_command(data_cli_group)
    data_cli_group.add_command(data_fetch_cmd, 'fetch')
    data_cli_group.add_command(data_validate_cmd, 'validate')

    airtable_cli_group = AppGroup('airtable', help='Interact with Airtable service.')
    app.cli.add_command(airtable_cli_group)
    airtable_cli_group.add_command(airtable_status_cmd, 'status')
    airtable_cli_group.add_command(airtable_sync_cmd, 'sync')
    airtable_cli_group.add_command(airtable_reset_cmd, 'reset')

    return app
