import pytest

from unittest.mock import patch

from bas_web_map_inventory.components import Server, Namespace, Repository, Style, Layer, LayerGroup, Servers, \
    Namespaces, Repositories, Styles, Layers, LayerGroups
from bas_web_map_inventory.components.geoserver import GeoServer

from tests.bas_web_map_inventory.conftest.components import test_server_data, test_server, test_namespace_data, \
    test_namespace, test_repository_data, test_repository, test_style_data, test_style, test_layer_data, test_layer, \
    test_layer_group_data, test_layer_group
from tests.bas_web_map_inventory.conftest.geoserver import test_geoserver_data


@pytest.mark.parametrize(
    argnames=['component', 'component_data'],
    argvalues=[
        (Server, test_server_data),
        (Namespace, test_namespace_data),
        (Repository, test_repository_data),
        (Style, test_style_data),
        (Layer, test_layer_data),
        (LayerGroup, test_layer_group_data),
    ]
)
def test_generic_component(component, component_data):
    item = component(**component_data)
    assert isinstance(item, component)


@pytest.mark.parametrize(
    argnames=['component', 'component_item'],
    argvalues=[
        (Servers, test_server),
        (Namespaces, test_namespace),
        (Repositories, test_repository),
        (Styles, test_style),
        (Layers, test_layer),
        (LayerGroups, test_layer_group)
    ]
)
def test_generic_components(component, component_item):
    collection = component()
    collection['test'] = component_item
    assert isinstance(collection, component)
    assert len(collection) == 1


@pytest.mark.usefixtures('geoserver_catalogue', 'wms_client', 'wfs_client')
def test_geoserver_component(geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        item = GeoServer(**test_geoserver_data)
        assert isinstance(item, GeoServer)

        collection = Servers()
        collection['test'] = item
        assert isinstance(collection, Servers)
        assert len(collection) == 1
