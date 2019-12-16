from pathlib import Path
from setuptools import setup, find_packages


def _get_long_description() -> str:
    with open(Path('README.md'), 'r') as readme:
        return readme.read()


def _get_version() -> str:
    if Path('APP_RELEASE.txt').exists():
        with open(Path('APP_RELEASE.txt'), 'r') as version:
            return str(version.read()).strip()

    return 'unknown'


setup(
    name="bas-web-map-inventory",
    version=_get_version(),
    author="British Antarctic Survey",
    author_email="webapps@bas.ac.uk",
    description="Inventory of geospatial layers and web maps provided by the BAS Mapping and Geographic Information "
                "Centre (MAGIC), visualised in Airtable.",
    long_description=_get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/antarctica/web-map-inventory",
    license='Open Government Licence v3.0',
    install_requires=[
        'airtable-python-wrapper==0.12.0',
        'Flask==1.1.1',
        'geoserver-restconfig==1.0.2',
        'inquirer==2.6.3',
        'jsonschema==3.2.0',
        'lxml==4.4.2',
        'OWSlib==0.19.0',
        'python-dotenv==0.10.3',
        'sentry-sdk[flask]==0.13.5',
        'str2bool==1.1',
        'ulid-py==0.0.9',
    ],
    packages=find_packages(exclude=['tests.*', 'tests']),
    data_files=[
        (
            '',
            [
                'CHANGELOG.md',
                'CONTRIBUTING.md',
                'LICENSE.md',
                'APP_RELEASE.txt'
            ]
        ),
        (
            'resources/json-schemas',
            ['resources/json-schemas/data-sources-schema.json']
        ),
        (
            'resources/xml-schemas',
            [
                'resources/xml-schemas/wms-1.3.0.xsd',
                'resources/xml-schemas/xlink.xsd',
                'resources/xml-schemas/xml.xsd'
            ]
        )
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Development Status :: 3 - Alpha",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research"
    ],
)
