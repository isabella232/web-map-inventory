import pytest

from bas_web_map_inventory import create_app

from tests.bas_web_map_inventory.conftest.geoserver import MockGeoServerCatalogue, MockWMSClient, MockWFSClient


@pytest.fixture
def app():
    app = create_app()
    return app


@pytest.fixture
@pytest.mark.usefixtures('app')
def app_runner(app):
    return app.test_cli_runner()


@pytest.fixture
def geoserver_catalogue():
    return MockGeoServerCatalogue()


@pytest.fixture
def wms_client():
    return MockWMSClient()


@pytest.fixture
def wfs_client():
    return MockWFSClient()
