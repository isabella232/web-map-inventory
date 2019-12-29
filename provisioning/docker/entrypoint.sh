#!/usr/bin/env bash

set -e

export PATH="/usr/local/virtualenvs/bas_web_map_inventory/bin:$PATH";
export FLASK_APP=/home/geoweb/apps/web-map-inventory/manage.py;
export FLASK_ENV=production;

(cd /home/geoweb/apps/web-map-inventory && exec flask "$@");
