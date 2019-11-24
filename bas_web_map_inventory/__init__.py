import os

import sentry_sdk

from flask import Flask
from flask.cli import AppGroup
# noinspection PyPackageRequirements
from werkzeug.utils import import_string

from bas_web_map_inventory.cli import fetch as data_fetch_cmd, status as airtable_status_cmd, \
    sync as airtable_sync_cmd, reset as airtable_reset_cmd


def create_app():
    app = Flask(__name__)

    config = import_string(f"bas_web_map_inventory.config.{str(os.environ['FLASK_ENV']).capitalize()}Config")()
    app.config.from_object(config)

    if 'LOGGING_LEVEL' in app.config:
        app.logger.setLevel(app.config['LOGGING_LEVEL'])

    if app.config['APP_ENABLE_SENTRY']:
        sentry_sdk.init(**app.config['SENTRY_CONFIG'])

    data_cli_group = AppGroup('data', help='Interact with data sources.')
    app.cli.add_command(data_cli_group)
    data_cli_group.add_command(data_fetch_cmd, 'fetch')

    airtable_cli_group = AppGroup('airtable', help='Interact with Airtable service.')
    app.cli.add_command(airtable_cli_group)
    airtable_cli_group.add_command(airtable_status_cmd, 'status')
    airtable_cli_group.add_command(airtable_sync_cmd, 'sync')
    airtable_cli_group.add_command(airtable_reset_cmd, 'reset')

    return app
