# MAGIC Web Map Inventory - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

* Support for 'Oracle' GeoServer store/repository types [#71](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/71)

### Changed

* Reformatting data file schema

### Fixed

* Removing debug code

## [0.3.1] - 2020-04-29

### Added

* Support for '3D Multi-polygon' geometries
* Support for 'geometry collection' geometries
* Additional JSON guidance

### Changed

* Improved geometry detection for vector layers (using 'geom' and 'WKB_geometry' fields in addition to 'geometry')

### Added

* Support for 'shapefile' and 'directory of shapefiles' GeoServer store/repository types [#64](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/64)

### Fixed

* Support for change in Airtable API over empty fields [#67](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/67)
* Support for empty layer group styles [#65](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/65)

## [0.3.0] - 2020-02-12

### Removed [BREAKING!]

* Proof of concept Ansible deployment support [#35](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/35)

### Changed [BREAKING!]

* Application log file path variable changed from `LOG_FILE_PATH` to `APP_LOG_FILE_PATH` [#36](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/36)

### Added

* `version` CLI command for reporting installed version [#24](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/35)
* Integration between Black and PyCharm [#56](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/56)
* GitLab release will be associated with milestones and PyPi packages through Continuous Deployment [#58](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/58)
* JSON files will be checked they are valid JSON before use [#23](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/23)
* JSON Schema for validating data resource files [#20](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/20)
* Publishing JSON Schemas for data sources and data resources [#22](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/22)
* Python 3.8 support [#21](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/21)

### Fixed

* Aborting gracefully when an inquirer prompt is cancelled [#60](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/60)
* OGC interactive protocol selection in data validate CLI command [#61](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/61)

### Changed

* File paths will be shown in their absolute form (rather than relative) to aid with debugging [#25](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/25)
* Improved integration between Sentry and GitLab [#57](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/57)

## [0.2.2] - 2020-02-12

### Added

* Ansible deployment support [#35](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/35)
* Podman deployment support [#49](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/49)

### Fixed

* Errors in XML catalogue [#39](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/39)
* Errors exporting related items in components [#44](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/44)
* Improving editor config file [#50](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/50)

### Changed

* Aligning development and deployment Dockerfiles [#38](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/38)
* Improving deployment container [#38](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/38) [#51](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/51)
* Improved Podman wrapper script [#48](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/48)

## [0.2.1] - 2020-01-02

### Fixed

* Production Docker image CD build [#27](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/27)

## [0.2.0] - 2020-01-02

### Added

* MyPy type checker [#27](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/27)
* Missing docblocks and type lints [#27](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/27)
* Deployment container [#2](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/2)
* Test coverage [#15](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/15)
* WMS validation [#13](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/13)
* Rotating log file support [#10](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/10)

### Fixed

* Correctly using JSON and XML schemas included in package with `importlib.resources`
  [#17](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/17)
  [#18](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/18)
* Excluding `tests` module in package [#17](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/17)
* Pinning package dependencies in `setup.py` [#9](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/9)
* Python package versioning
  [#7](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/7)
  [#8](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/8)
* Incorrect spelling of 'sentry' in config option [#16](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/16)

### Changed

* Switching from Pip (for dependencies) and setuptools (for packaging) to Poetry [#27](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/27)
* Switching from Flake8 to Black for PEP8 compliance/formatting [#27](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/27)
* Docker image changed to run as a non-privileged user [#11](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/11)

## [0.1.0] - 2019-11-25

### Added

* Initial project
