import pytest

from unittest.mock import patch
from typing import List, Dict

from bas_web_map_inventory.utils import OGCProtocol, validate_ogc_capabilities as _validate_ogc_capabilities
# noinspection PyProtectedMember
from bas_web_map_inventory.cli import _make_geoserver_server

from tests.bas_web_map_inventory.conftest.geoserver import test_geoserver_catalogue_data


def make_geoserver_server(server_config: Dict[str, str]):
    geoserver = _make_geoserver_server(server_config=server_config)
    # These `populate()` methods are only defined in mock classes
    # noinspection PyUnresolvedReferences
    geoserver.client.populate(test_geoserver_catalogue_data)
    # noinspection PyUnresolvedReferences
    geoserver.wfs.populate(contents={
        'test-layer-1': {'geometry': 'point'},
        'test-namespace-1:test-layer-group-1': {'geometry': 'point'}
    })

    return geoserver


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


def prompt_all_data_sources(questions: List):
    for question in questions:
        if question.name == 'source':
            return {'source': 'All data sources'}
        elif question.name == 'protocol':
            return {'protocol': OGCProtocol.WMS}


def prompt_single_data_source(questions: List):
    for question in questions:
        if question.name == 'source':
            return {'source': '[01DRS53XAG5E85MJNYTA6WPTBM] - test-server-1'}
        elif question.name == 'protocol':
            return {'protocol': OGCProtocol.WMS}


def prompt_invalid_protocol(questions: List):
    for question in questions:
        if question.name == 'protocol':
            return {'protocol': 'invalid'}


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
                'wms'
            ]
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
                'wms'
            ]
        )
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'validation failure 😞' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_valid_single_source_all_data_sources(app, app_runner):
    with patch('bas_web_map_inventory.cli.inquirer.prompt', side_effect=prompt_all_data_sources), \
            patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_valid):

        result = app_runner.invoke(
            args=[
                'data',
                'validate',
                '-s',
                'tests/data/sources.json'
            ]
        )
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'validation successful 🥳' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_valid_single_source_single_data_sources(app, app_runner):
    with patch('bas_web_map_inventory.cli.inquirer.prompt', side_effect=prompt_single_data_source), \
            patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_valid):

        result = app_runner.invoke(
            args=[
                'data',
                'validate',
                '-s',
                'tests/data/sources.json'
            ]
        )
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert 'validation successful 🥳' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_valid_single_source_invalid_protocol(app, app_runner):
    with patch('bas_web_map_inventory.cli.inquirer.prompt', side_effect=prompt_invalid_protocol):
        result = app_runner.invoke(
            args=[
                'data',
                'validate',
                '-s',
                'tests/data/sources.json',
                '-i',
                '01DRS53XAG5E85MJNYTA6WPTBM'
            ]
        )
        assert result.exit_code == 1
        assert isinstance(result.exception, ValueError)
        assert str(result.exception) == 'Protocol [invalid] not found'


@pytest.mark.usefixtures('app', 'app_runner')
def test_data_validate_command_valid_single_source_missing_protocol_endpoint(app, app_runner):
    result = app_runner.invoke(
        args=[
            'data',
            'validate',
            '-s',
            'tests/data/sources-missing-wms-path.json',
            '-i',
            '01DRS53XAG5E85MJNYTA6WPTBM',
            '-p',
            'wms'
        ]
    )
    assert result.exit_code == 1
    assert isinstance(result.exception, KeyError)
    assert str(result.exception) == '"Property \'wms-path\' not in data source [01DRS53XAG5E85MJNYTA6WPTBM]"'


@pytest.mark.usefixtures('app', 'app_runner', 'geoserver_catalogue', 'wms_client', 'wfs_client')
def test_data_fetch_command(app, app_runner, geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client, \
            patch('bas_web_map_inventory.cli._make_geoserver_server', side_effect=make_geoserver_server), \
            patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_valid):
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        result = app_runner.invoke(
            args=['data', 'fetch', '-s', 'tests/data/sources.json', '-d', 'tests/data/data-ok.json'])
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


@pytest.mark.usefixtures('app', 'app_runner', 'geoserver_catalogue', 'wms_client', 'wfs_client')
def test_data_fetch_command_invalid_wms(app, app_runner, geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client, \
            patch('bas_web_map_inventory.cli._make_geoserver_server', side_effect=make_geoserver_server), \
            patch('bas_web_map_inventory.cli.validate_ogc_capabilities', side_effect=validate_ogc_capabilities_invalid):
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        result = app_runner.invoke(
            args=['data', 'fetch', '-s', 'tests/data/sources.json', '-d', 'tests/data/data-invalid-wms.json'])
        assert result.exit_code == 0
        assert 'data sources in tests/data/sources.json have valid syntax' in result.output
        assert '* WMS endpoint invalid, server [test-server-1] skipped' in result.output
        assert 'Fetch complete' in result.output
