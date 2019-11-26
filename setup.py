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
        'OWSlib==0.19.0',
        'python-dotenv==0.10.3',
        'str2bool==1.1',
        'sentry-sdk[flask]==0.13.2',
        'ulid-py==0.0.9',
    ],
    packages=find_packages(exclude=['tests']),
    package_data={'bas_web_map_inventory': ['../APP_RELEASE.txt']},
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Development Status :: 3 - Alpha",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research"
    ],
)
