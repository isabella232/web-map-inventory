import os

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '0.1.0'

# If a tagged commit, don't make a pre-release
if 'CI_COMMIT_TAG' not in os.environ:
    version = f"{ version }.dev{ os.getenv('CI_PIPELINE_ID') or None }"

setup(
    name="bas-web-map-inventory",
    version=version,
    author="British Antarctic Survey",
    author_email="webapps@bas.ac.uk",
    description="Inventory of geospatial layers and web maps provided by the BAS Mapping and Geographic Information "
                "Centre (MAGIC), visualised in Airtable.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/antarctica/web-map-inventory",
    license='Open Government Licence v3.0',
    install_requires=['airtable-python-wrapper', 'Flask', 'flask-DotEnv', 'geoserver-restconfig', 'OWSlib', 'ulid-py'],
    packages=find_packages(exclude=['tests']),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Framework :: Flask",
        "Development Status :: 3 - Alpha",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research"
    ],
)
