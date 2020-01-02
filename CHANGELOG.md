# MAGIC Web Map Inventory - Change log

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
* Docker image changed to run as a non-privileged user 
  [#11](https://gitlab.data.bas.ac.uk/MAGIC/web-map-inventory/issues/11)

## [0.1.0] - 2019-11-25

### Added

* Initial project
