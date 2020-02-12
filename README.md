# MAGIC Web Map Inventory

Inventory of geospatial layers and web maps provided by the BAS Mapping and Geographic Information Centre (MAGIC),
visualised in Airtable.

* [view the inventory in Airtable (Internal)](https://airtable.com/tblr6gwKOLQelMXDv/viwp8xVwcRRJnoIo0?blocks=hide)

See the [Data model](#data-model) section for more information about what this inventory holds.

**Note:** This project is designed for internal use within MAGIC, but is offered to anyone with similar needs.

## Usage

### Tasks

These tasks run in a container. See the [Setup](#setup) section for setup instructions.

If running on the BAS central workstations:

```shell
$ ssh geoweb@bslws01.nerc-bas.ac.uk
$ web-map-inventory [task]
```

#### `data fetch`

Fetches information about servers, namespaces, repositories, styles, layers and layer groups from servers defined in a
data sources file. Fetched information is saved to an output data file.

Options:

* `-s`, `--data-sources-file-path`:
    * path to a data sources file
    * default: `data/sources.json`
* `-d`, `--data-output-file-path`:
    * path to a data sources file
    * default: `data/data.json`

**Note:** Currently this task results in new IDs being generated for each resource, even if it already exists. This will
lead to resources being removed and re-added unnecessarily but will always remain internally consistent.

#### `data validate`

Validates protocols offered by servers defined in a data sources file (by default `data/sources.json`).

Options:

* `-s`, `--data-sources-file-path`:
    * path to a data sources file
    * default: `data/sources.json`
* `-i`, `--data-source-identifier`:
    * identifier of a server in the data sources file
    * use special value `all` to select all data sources
* `-p`, `--validation-protocol`:
    * protocol to validate
    * default: `wms`

**Note:** Currently this task is limited to the WMS (OGC Web Map Service) protocol.

#### `airtable status`

Checks local items against Airtable to check whether they are up-to-date (current), outdated, missing or orphaned.

#### `airtable sync`

Creates, updates or removes items in Airtable to match local items.

#### `airtable reset`

Removes all data from Airtable.

### Managing data sources

Each data source is represented as an object in the `server` list in `data/sources.json` [1]. The structure of each
source depends on its type. For more general information, see the [Data sources](#data-sources) section.

[1] This file is either in the runtime path created during [Setup](#setup) or `~/.config/web-map-inventory/` on the BAS
central servers).

#### Adding new data sources

**Note:** See [Supported data sources](#supported-data-sources) for currently supported data sources.

Once added use the [`data fetch` task](#data-fetch).

#### Adding a *GeoServer* data source

| Property   | Required | Data Type | Allowed Values                                                      | Example Value                | Description                          | Notes                         |
| ---------- | -------- | --------- | ------------------------------------------------------------------- | ---------------------------- | ------------------------------------ | ----------------------------- |
| `id`       | Yes      | String    | A *ULID* (Universally Unique Lexicographically Sortable Identifier) | `01DRS53XAJNH0TNBW5161B6EWJ` | Unique identifier for server/source  | See below for how to generate |
| `label`    | Yes      | String    | Any combination of *a-Z*, *A-Z*, *0-9*, *-*, *_*                    | `a-1_A`                      | Using a short, well-known identifier | -                             |
| `hostname` | Yes      | String    | Any valid hostname                                                  | `example.com`                | -                                    | -                             |
| `type`     | Yes      | String    | `geoserver`                                                         | *See allowed value*          | -                                    | -                             |
| `port`     | Yes      | String    | Any valid port number                                               | `8080`                       | -                                    | Usually `80` or `8080`        |
| `api-path` | Yes      | String    | `/geoserver/rest`                                                   | *See allowed value*          | Defined by GeoServer                 | -                             |
| `wms-path` | Yes      | String    | `/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities`  | *See allowed value*          | Defined by GeoServer                 | -                             |
| `wfs-path` | Yes      | String    | `/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities`  | *See allowed value*          | Defined by GeoServer                 | -                             |
| `username` | Yes      | String    | Any valid GeoServer username                                        | `admin`                      | Usually the GeoServer admin user     | -                             |
| `password` | Yes      | String    | Password for GeoServer user                                         | `password`                   | Usually the GeoServer admin user     | -                             |

**Note:** Use [ulidgenerator.com](http://ulidgenerator.com) to generate ULIDs manually.

Example:

```json
{
  "id": "xxx",
  "label": "example",
  "hostname": "example.com",
  "type": "geoserver",
  "port": "80",
  "api-path": "/geoserver/rest",
  "wms-path": "/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities",
  "wfs-path": "/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities",
  "username": "admin",
  "password": "password"
}
```

## Implementation

Flask application using the [airtable-python-wrapper](https://airtable-python-wrapper.readthedocs.io) library to
interact with the Airtable API.

### Airtable

Data is synced to the
[MAGIC Maps and Layers Inventory](https://airtable.com/tblCoGkVssEe6cs0B/viwjb9FAq2FLx5BL9?blocks=hide) Base in the
[BAS MAGIC](https://airtable.com/wspXVL8SsiS5hPhob/workspace/billing) Workspace.

### Data model

This project, an inventory, consists of information held in geospatial services. The data model is intended to be
generic to support different data sources and technologies.

This data model consists of:

* **Servers**: Represent a source of geospatial information, such as an instance of a technology or a whole platform
* **Namespaces**: Represent a logical grouping of resources within a server/endpoint
* **Repositories**: Represent a data source that backs one or more layers
* **Styles**: Represent a definition for how data in a layer should be represented/presented
* **Layers**: Represent a logical unit of geospatial information
* **Layer Groups**: Represent a logical grouping of one or more layers that should be treated as a single, indivisible
  unit

It can be visualised as:

![data model visualisation](https://raw.githubusercontent.com/antarctica/web-map-inventory/master/assets/img/data-model.png)

### Data sources

Data sources are *servers* in the project [Data model](#data-model) and define connection details for APIs and services
each server type provides for fetching information about components they contain (e.g. listing *layers*).

A data sources file, `data/sources.json`, is used for recording these details. An example is available in
`data/sources.example.json`. See the [Adding a data source](#adding-new-data-sources) section for more information.

A JSON Schema, `bas_web_map_inventory/resources/json_schemas/data-sources-schema.json`, validates this file.

#### Supported data sources

* GeoServer
    * Using a combination of its admin API and WMS/WFS OGC endpoints

### Configuration

Configuration options are set within `bas_web_map_inventory/config.py`.

All [Options](#configuration-options) are defined in a `Config` base class, with per-environment sub-classes overriding
and extending these options as needed. The active configuration is set using the `FLASK_ENV` environment variable.

Most options can be [Set using environment variables or files](#setting-configuration-options).

#### Configuration options

| Option              | Required | Environments | Data Type (Cast) | Source      |  Allowed Values                                                                                             | Default Value                                                              | Example Value                                                | Description                                                                                                     | Notes                      |
| ------------------- | -------- | ------------ | ---------------- | ----------- | ----------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------- | -------------------------- |
| `FLASK_APP`         | Yes      | All          | String           | `.flaskenv` | Valid [`FLASK_APP`](https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery) value            | `manage.py`                                                                | *See default value*                                          | See [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/cli/#application-discovery)                | -                          |
| `APP_ENABLE_SENTRY` | Yes      | All          | Boolean          | `.flaskenv` | `True`/`False`                                                                                              | `False` (for *development*/*testing*), *True* (for *staging*/*production*) | `True`                                                       | Feature flag for [Error reporting](#error-reporting)                                                            | -                          |
| `SENTEY_DSN`        | Yes      | Yes          | String           | `.flaskenv` | [Sentry DSN](https://docs.sentry.io/error-reporting/quickstart/?platform=python#configure-the-sdk) for this project | `https://c69a62ee2262460f9bc79c4048ba764f@sentry.io/1832548`       | *See default value*                                          | Sentry [Data Source Name](https://docs.sentry.io/error-reporting/quickstart/?platform=python#configure-the-sdk) | This value is not a secret |
| `AIRTABLE_API_KEY`  | Yes      | All          | String           | `.env`      | Valid [AirTable API key](https://support.airtable.com/hc/en-us/articles/219046777-How-do-I-get-my-API-key-) | -                                                                          | `keyxxxxxxxxxxxxxx`                                          | AirTable API Key                                                                                                | -                          |
| `AIRTABLE_BASE_ID`  | Yes      | All          | String           | `.env`      | Valid [AirTable Base ID](https://airtable.com/api)                                                          | -                                                                          | `appxxxxxxxxxxxxxx`                                          | ID of the AirTable Base to populate/use                                                                         | -                          |

Options are set as strings and then cast to the data type listed above. See
[Environment variables](#setting-configuration-options) for information about an options 'Source'.

Flask also has a number of
[builtin configuration options](https://flask.palletsprojects.com/en/1.1.x/config/#builtin-configuration-values).

#### Setting configuration options

Variable configuration options can be set using environment variables or environment files:

| Source                   | Priority | Purpose                     | Notes                                   |
| ------------------------ | -------- | --------------------------- | --------------------------------------- |
| OS environment variables | 1st      | General/Runtime             | -                                       |
| `.env`                   | 2nd      | Secret/private variables    | Generate by copying `.env.example`      |
| `.flaskenv`              | 3rd      | Non-secret/public variables | Generate by copying `.flaskenv.example` |

**Note:** these sources are a
[Flask convention](https://flask.palletsprojects.com/en/1.1.x/cli/#environment-variables-from-dotenv).

### Error tracking

Errors in this service are tracked with Sentry:

* [Sentry dashboard](https://sentry.io/antarctica/web-map-inventory/)
* [GitLab dashboard](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/error_tracking)

Error tracking will be enabled or disabled depending on the environment. It can be manually controlled by setting the
`APP_ENABLE_SENTRY` variable in `.flaskenv`.

### Logging

Logs for this service are written to *stdout* and a log file, `/var/log/app/app.py`, depending on the environment.

File based logging can be manually controlled by setting the `APP_ENABLE_FILE_LOGGING` and `LOG_FILE_PATH` variables in
`.flaskenv`.

**Note:** If `LOG_FILE_PATH` is changed, the user in the user the container rans as must be granted suitable write
permissions.

### XML Catalogue

An [XML Catalog](https://en.wikipedia.org/wiki/XML_catalog) is used to cache XML files locally (typically XSD's for
schemas). This drastically speeds up XML parsing and removes a dependency on remote endpoints.

XML files in the catalogue are typically stored in `bas_web_map_inventory/resources/xml_schemas/`.

Different catalogue files are used for different container variants due to differences in the applications location:

* `:latest`: `./support/xml-schemas/catalogue.xml`
* `/deploy`: `provisioning/docker/catalog.xml`

In either case, the catalogue is available within the container at the conventional path, `/etc/xml/catalog`, and will
be used automatically by most XML libraries and tools (such as `lxml` and `xmllint`).

## Setup

The application for this project runs as either a Docker container or deployed as a Python package in a virtual machine.

Once setup, see the [Data sources](#managing-data-sources) and [Usage](#usage) sections for how to use and run the
application.

### Setup as a container

When setup as a container, the project can run locally or on the BAS central workstations using Podman. You will need
access to the private BAS Docker Registry (part of [gitlab.data.bas.ac.uk](https://gitlab.data.bas.ac.uk)).

**Note:** Podman support needs to be enabled on a per-account basis. Unless noted, `docker` commands listed here can be
replaced with `podman`.

```shell
$ docker login docker-registry.data.bas.ac.uk
$ docker pull docker-registry.data.bas.ac.uk/magic/web-map-inventory/deploy:stable
```

**Note:** [Other image tags](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/container_registry) are available if
you want to run pre-release versions, or a specific, previous, version.

Before you can run the container, you will need to create a runtime directory that will live outside of the container.
You will need to create the required [Configuration files](#configuration). Any generated output will also be saved
here.

```shell
$ mkdir -p ~/.config/web-map-inventory
```

#### Optional wrapper script

If using podman, a wrapper script, `support/container-wrapper/podman-wrapper.sh`, is available to make running the
container easier.

To use, copy this script enable it to be executed:

```shell
$ mkdir ~/bin
# copy `support/container-wrapper/podman-wrapper.sh` as `~/bin/web-map-inventory`
$ chmod +x ~/bin/web-map-inventory
```

Then ensure `~/bin` is part of the user's path (use `echo $PATH` to check), if it isn't edit the user's shell to include
it (these instructions assume the bash shell and the absolute path to the user's home directory is `/home/foo`):

```shell
$ vi ~/.bash_rc
# add `export PATH="/home/foo/bin:$PATH" then save the file and reload the user's shell
```

You should now be able to run `web-map-inventory` to run the container.

### Setup using Ansible

When setup using Ansible, it is assumed the target virtual machine will be used for running other Python applications
isolated by virtual environments.

**Note:** This Ansible configuration is intentionally minimal and simplistic so that it can be easily replaced or 
absorbed into a larger setup.

Virtual machines are defined in Ansible's inventory file, grouped by environment (staging and production). To setup an
environment, you will need access to the root account on each of its virtual machines:

```shell
$ cd provisioning/ansible
$ docker-compose run ansible
$ ansible-playbook site.yml --extra-vars 'target=[staging/production]'
```

Where the `target` variable sets which environment's hosts the playbook will target.

Once setup, you will need to populate the runtime directory, `/home/geoweb/.config/web-map-inventory/`,  with required 
[Configuration files](#configuration) and data output files and to deploy an application version.

## Development

```shell
$ git clone https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory
$ cd map-layer-index
```

### Development environment

The `:latest` container image is used for developing this project. It can run locally using Docker and Docker Compose:

```shell
$ docker login docker-registry.data.bas.ac.uk
$ docker-compose pull app
```

Then create/configure required [Configuration files](#configuration):

```shell
$ cp .env.example .env
$ cp .flaskenv.example .flaskenv
$ cp data/sources.example.json data/sources.json
```

To run/test application commands:

```shell
$ docker-compose run app flask [task]
```

[1] You will need access to the private BAS Docker Registry (part of
[gitlab.data.bas.ac.uk](https://gitlab.data.bas.ac.uk)) to pull this image. If you don't, you can build the relevant
image/tag locally instead.

### Code Style

PEP-8 style and formatting guidelines must be used for this project, with the exception of the 80 character line limit.

[Black](https://github.com/psf/black) is used to ensure compliance, configured in `pyproject.toml`.

To apply formatting manually:

```shell
$ docker-compose run app black bas_web_map_inventory/
```

To check compliance manually:

```shell
$ docker-compose run app black --check bas_web_map_inventory/
```

Checks are ran automatically in [Continuous Integration](#continuous-integration).

### Type hinting

Python type hints should be used for this project, with the exception of
[missing import](https://mypy.readthedocs.io/en/latest/running_mypy.html#missing-imports) errors (which can be ignored).

[MyPy](https://mypy.readthedocs.io) is used to ensure types agree (where defined), configured in `mypy.ini`.

To check usage manually:

```shell
$ docker-compose run app mypy bas_web_map_inventory/
```

Checks are ran automatically in [Continuous Integration](#continuous-integration).

### Dependencies

Python dependencies for this project are managed with [Poetry](https://python-poetry.org) in `pyproject.toml`.

The development container image installs both runtime and development dependencies. Deployment images only install
runtime dependencies.

Non-code files, such as static files, can also be included in the [Python package](#python-package) using the
`include` key in `pyproject.toml`.

To add a new (development) dependency:

```shell
$ docker-compose run app ash
$ poetry add [dependency] (--dev)
```

Then rebuild the development container and push to GitLab (GitLab will rebuild other images automatically as needed):

```shell
$ docker-compose build app
$ docker-compose push app
```

### Static security scanning

To ensure the security of this API, source code is checked against [Bandit](https://github.com/PyCQA/bandit) for issues
such as not sanitising user inputs or using weak cryptography. Bandit is configured in `.bandit`.

**Warning:** Bandit is a static analysis tool and can't check for issues that are only be detectable when running the
application. As with all security tools, Bandit is an aid for spotting common mistakes, not a guarantee of secure code.

To run checks manually:

```shell
$ docker-compose run app bandit -r .
```

Checks are ran automatically in [Continuous Integration](#continuous-integration).

### Logging

Use the Flask default logger. For example:

```python
app.logger.info('Log message')
```

When outside of a route/command use `current_app`:

```python
from flask import current_app

current_app.logger.info('Log message')
```

### XML Catalogue additions

If new functionality is added that depends on XML files, such as XSDs, it is *strongly* recommended to add them to the
[XML catalogue](#xml-catalogue), especially where they are used in tests.

Once added, you will need to rebuild and push the project Docker image (see the [Dependencies](#dependencies) section
for more information).

### Editor support

#### PyCharm

A run/debug configuration, *App*, is included in the project.

### Testing

All code in the `bas_web_map_inventory` module must be covered by tests, defined in `tests/`. This project uses
[PyTest](https://docs.pytest.org/en/latest/) which should be ran in a random order using
[pytest-random-order](https://pypi.org/project/pytest-random-order/).

To run tests manually from the command line:

```shell
$ docker-compose run app -e FLASK_ENV=testing app pytest --random-order
```

To run tests manually using PyCharm, use the included *App (Integration)* run/debug configuration.

Tests are ran automatically in [Continuous Integration](#continuous-integration).

#### Test coverage

[pytest-cov](https://pypi.org/project/pytest-cov/) is used to measure test coverage.

To prevent noise, `.coveragerc` is used to omit empty `__init__.py` files from reports.

To measure coverage manually:

```shell
$ docker-compose run app -e FLASK_ENV=testing app pytest --cov=bas_web_map_inventory --cov-fail-under=100 --cov-report=html .
```

[Continuous Integration](#continuous-integration) will check coverage automatically and fail if less than 100%.

#### Continuous Integration

All commits will trigger a Continuous Integration process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Deployment

### Python package

This project is distributed as a Python package, hosted in [PyPi](https://pypi.org/project/bas-web-map-inventory).

Source and binary packages are built and published automatically using
[Poetry](https://python-poetry.org/docs/cli/#publish) in [Continuous Delivery](#continuous-deployment).

Package versions are determined automatically using the `support/python-packaging/parse_version.py` script.

### Docker image

The project [Python package](#python-package) is available as a Docker/OCI image, hosted in the private BAS Docker
Registry (part of [gitlab.data.bas.ac.uk](https://gitlab.data.bas.ac.uk)).

### Ansible managed hosts
[Continuous Delivery](#continuous-deployment) will automatically:

Typically, [Continuous Deployment](#continuous-deployment) will deploy a suitable version of the project 
[Python package](#python-package) within each environment automatically. To do so manually:

```shell
$ cd provisioning/ansible
$ docker-compose run ansible
$ ansible-playbook deploy.yml --extra-vars 'target=[staging/production] package_name=bas-web-map-inventory package_version=[version]'
```
* build a `/deploy:latest` image for commits to the *master* branch
* build a `/deploy:release-stable` and `/deploy:release-[release]` image for tags
* deploy new images to the BAS central workstations (by running `podman pull [image]` on the workstations)

Where the `target` variable sets which environment's hosts the playbook will target and `package_version` sets which
version to install.

### Continuous Deployment

All commits will trigger a Continuous Deployment process using GitLab's CI/CD platform, configured in `.gitlab-ci.yml`.

## Release procedure

For all releases:

1. create a release branch
2. close release in `CHANGELOG.md`
3. push changes, merge the release branch into `master` and tag with version

## Feedback

The maintainer of this project is the BAS Mapping and Geographic Information Centre (MAGIC), they can be contacted at:
[servicedesk@bas.ac.uk](mailto:servicedesk@bas.ac.uk).

## Issue tracking

This project uses issue tracking, see the
[Issue tracker](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues) for more information.

**Note:** Read & write access to this issue tracker is restricted. Contact the project maintainer to request access.

## License

© UK Research and Innovation (UKRI), 2019 - 2020, British Antarctic Survey.

You may use and re-use this software and associated documentation files free of charge in any format or medium, under
the terms of the Open Government Licence v3.0.

You may obtain a copy of the Open Government Licence at http://www.nationalarchives.gov.uk/doc/open-government-licence/
