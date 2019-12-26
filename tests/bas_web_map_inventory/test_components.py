import pytest

from copy import deepcopy
from unittest.mock import patch

from bas_web_map_inventory.components import Server, Namespace, Repository, Style, Layer, LayerGroup, Servers, \
    Namespaces, Repositories, Styles, Layers, LayerGroups
from bas_web_map_inventory.components.geoserver import GeoServer

from tests.bas_web_map_inventory.conftest.components import test_server_data, test_server, test_namespace_data, \
    test_namespace, test_repository_data, test_repository, test_style_data, test_style, test_layer_data, test_layer, \
    test_layer_group_data, test_layer_group
from tests.bas_web_map_inventory.conftest.geoserver import test_geoserver_data, test_geoserver_catalogue_data


@pytest.mark.parametrize(
    argnames=['component', 'component_data', 'component_repr'],
    argvalues=[
        (
            Server,
            test_server_data,
            'Server <id=01DRS53XAG5E85MJNYTA6WPTBM, label=test-server-1, type=ServerType.GEOSERVER>'
        ),
        (
            Namespace,
            test_namespace_data,
            'Namespace <id=01DRS53XAGHZ63VSWDV1M4WBFG, label=test-namespace-1, server=01DRS53XAG5E85MJNYTA6WPTBM>'
        ),
        (
            Repository,
            test_repository_data,
            'Repository <id=01DRS53XAG2QEB6MYES5DZ8P7Q, label=test-repository-1, type=RepositoryType.POSTGIS>'
        ),
        (
            Style,
            test_style_data,
            'Style <id=01DRS53XAGEXJ0JWGB73FXQS04, label=test-style-1, type=StyleType.SLD>'
        ),
        (
            Layer,
            test_layer_data,
            'Layer <id=01DRS53XAHN84G0NE0YJJRWVKA, label=test-layer-1, type=LayerType.VECTOR>'
        ),
        (
            LayerGroup,
            test_layer_group_data,
            'LayerGroup <id=01DRS53XAH7TB65G8BBQZGMHYB, label=test-layer-group-1>'
        ),
    ]
)
def test_generic_component(component, component_data, component_repr):
    item = component(**component_data)
    assert isinstance(item, component)
    assert str(item) == component_repr


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


@pytest.mark.parametrize(
    argnames=['component', 'component_item'],
    argvalues=[
        (Namespaces, test_namespace),
        (Repositories, test_repository),
        (Styles, test_style),
        (Layers, test_layer)
    ]
)
def test_generic_components_get_by_label_unknown(component, component_item):
    collection = component()
    collection['test'] = component_item
    unknown_item = collection.get_by_label(label='unknown_item')
    assert unknown_item is None


def test_generic_components_get_by_label_layer_namespace():
    layers = Layers()
    layers['test'] = test_layer
    item = layers.get_by_label(label='test-layer-1', namespace_label='test-namespace-1')
    assert str(item) == 'Layer <id=01DRS53XAHN84G0NE0YJJRWVKA, label=test-layer-1, type=LayerType.VECTOR>'


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


@pytest.mark.usefixtures('geoserver_catalogue', 'wms_client', 'wfs_client')
def test_geoserver_component_unknown_workspace(geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        item = GeoServer(**test_geoserver_data)
        # These `populate()` methods are only defined in mock classes
        # noinspection PyUnresolvedReferences
        item.client.populate(data=test_geoserver_catalogue_data)
        # noinspection PyUnresolvedReferences
        item.wfs.populate(contents={'test-layer-1': {'geometry': 'point'}})
        assert isinstance(item, GeoServer)

        with pytest.raises(KeyError) as e:
            item.get_namespace(namespace_reference='invalid-namespace')
        assert 'Namespace [invalid-namespace] not found in server [test-server-1]' in str(e.value)


@pytest.mark.usefixtures('geoserver_catalogue', 'wms_client', 'wfs_client')
def test_geoserver_component_unknown_store(geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        item = GeoServer(**test_geoserver_data)
        # These `populate()` methods are only defined in mock classes
        # noinspection PyUnresolvedReferences
        item.client.populate(data=test_geoserver_catalogue_data)
        # noinspection PyUnresolvedReferences
        item.wfs.populate(contents={'test-layer-1': {'geometry': 'point'}})
        assert isinstance(item, GeoServer)

        with pytest.raises(KeyError) as e:
            item.get_repository(repository_reference='invalid-repository', namespace_reference='invalid-namespace')
        assert f"Repository [invalid-repository] not found in server [test-server-1]" in str(e.value)


@pytest.mark.usefixtures('geoserver_catalogue', 'wms_client', 'wfs_client')
def test_geoserver_component_unknown_geometry(geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        item = GeoServer(**test_geoserver_data)
        # These `populate()` methods are only defined in mock classes
        # noinspection PyUnresolvedReferences
        item.client.populate(data=test_geoserver_catalogue_data)
        # noinspection PyUnresolvedReferences
        item.wfs.populate(contents={
            'test-layer-1': {'geometry': 'invalid'},
            'test-namespace-1:test-layer-group-1': {'geometry': 'invalid'}
        })
        assert isinstance(item, GeoServer)

        with pytest.raises(ValueError) as e:
            item.get_layer(layer_reference='test-layer-1')
        assert f"Geometry type: [invalid] not mapped to LayerGeometry enum." in str(e.value)

        with pytest.raises(ValueError) as e:
            item.get_layer_group(
                layer_group_reference=test_geoserver_catalogue_data['layer_groups'][0]['name'],
                namespace_reference=test_geoserver_catalogue_data['layer_groups'][0]['workspace_name']
            )
        assert f"Geometry type: [invalid] not mapped to LayerGeometry enum." in str(e.value)


@pytest.mark.usefixtures('geoserver_catalogue', 'wms_client', 'wfs_client')
def test_geoserver_component_layer_group_namespaced_labels(geoserver_catalogue, wms_client, wfs_client):
    with patch('bas_web_map_inventory.components.geoserver.Catalogue') as mock_geoserver_catalogue, \
            patch('bas_web_map_inventory.components.geoserver.WebMapService') as mock_wms_client, \
            patch('bas_web_map_inventory.components.geoserver.WebFeatureService') as mock_wfs_client:
        mock_geoserver_catalogue.return_value = geoserver_catalogue
        mock_wms_client.return_value = wms_client
        mock_wfs_client.return_value = wfs_client

        item = GeoServer(**test_geoserver_data)
        # These `populate()` methods are only defined in mock classes
        # noinspection PyUnresolvedReferences
        data = deepcopy(test_geoserver_catalogue_data)
        data['layer_groups'][0]['layer_names'] = ['test-namespace-1:test-layer-1']
        data['layer_groups'][0]['style_names'] = ['test-namespace-1:test-style-1']
        item.client.populate(data=data)
        # noinspection PyUnresolvedReferences
        item.wfs.populate(contents={'test-layer-1': {'geometry': 'point'}})
        assert isinstance(item, GeoServer)

        result = item.get_layer_group(
            layer_group_reference=data['layer_groups'][0]['name'],
            namespace_reference=data['layer_groups'][0]['workspace_name']
        )
        assert result is not None
        assert result['layer_labels'][0] == ('test-layer-1', 'test-namespace-1')
