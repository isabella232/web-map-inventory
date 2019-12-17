import pytest

from unittest.mock import patch
from typing import List

from bas_web_map_inventory.utils import OGCProtocol, validate_ogc_capabilities as _validate_ogc_capabilities


# noinspection PyUnusedLocal
def validate_ogc_capabilities_valid(
    ogc_protocol:
    OGCProtocol,
    capabilities_url: str,
    multiple_errors: bool
) -> List[str]:
    capabilities_url = 'tests/resources/validate_ogc_capabilities/wms-1.3.0-valid.xml'
    return _validate_ogc_capabilities(
        ogc_protocol=ogc_protocol,
        capabilities_url=capabilities_url,
        multiple_errors=multiple_errors
    )


# noinspection PyUnusedLocal
def validate_ogc_capabilities_invalid(
    ogc_protocol:
    OGCProtocol,
    capabilities_url: str,
    multiple_errors: bool
) -> List[str]:
    capabilities_url = 'tests/resources/validate_ogc_capabilities/wms-1.3.0-invalid-multiple-invalid-extent.xml'
    return _validate_ogc_capabilities(
        ogc_protocol=ogc_protocol,
        capabilities_url=capabilities_url,
        multiple_errors=multiple_errors
    )


@pytest.mark.usefixtures('app', 'app_runner', 'geoserver_catalogue', 'wms_client', 'wfs_client')
def test_data_fetch_command(app, app_runner, geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client, \
            patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_valid):
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        result = app_runner.invoke(
            args=['data', 'fetch', '-s', 'tests/data/sources.json', '-d', 'tests/data/data.json'])
        assert result.exit_code == 0
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
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'Fetch complete' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_valid_single_source_wms(app, app_runner):
    with patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_valid):
        result = app_runner.invoke(
            args=[
                'data',
                'validate',
                '-s',
                'tests/data/sources.json',
                '-i',
                '01DRS53XAG5E85MJNYTA6WPTBM',
                '-p',
                'wms']
        )
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'validation successful 🥳' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_invalid_single_source_wms(app, app_runner):
    with patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_invalid):
        result = app_runner.invoke(
            args=[
                'data',
                'validate',
                '-s',
                'tests/data/sources.json',
                '-i',
                '01DRS53XAG5E85MJNYTA6WPTBM',
                '-p',
                'wms']
        )
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'validation failure 😞' in result.output
