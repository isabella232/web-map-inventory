import pytest

from unittest.mock import patch


@pytest.mark.usefixtures('app', 'app_runner', 'geoserver_catalogue', 'wms_client', 'wfs_client')
def test_data_fetch_command(app, app_runner, geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        result = app_runner.invoke(
            args=['data', 'fetch', '-s', 'tests/resources/sources.json', '-d', 'tests/resources/data.json'])
        assert 'data' in app.config.keys()
        assert 'servers' in app.config['data'].keys()
        assert 'namespaces' in app.config['data'].keys()
        assert 'repositories' in app.config['data'].keys()
        assert 'styles' in app.config['data'].keys()
        assert 'layers' in app.config['data'].keys()
        assert 'layer_groups' in app.config['data'].keys()
        assert len(app.config['data']['servers']) >= 1
        assert len(app.config['data']['namespaces']) >= 1
        assert len(app.config['data']['repositories']) >= 1
        assert len(app.config['data']['styles']) >= 1
        assert len(app.config['data']['layers']) >= 1
        assert len(app.config['data']['layer_groups']) >= 1
        assert 'Fetch complete' in result.output
