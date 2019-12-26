import pytest

from copy import deepcopy
from unittest.mock import patch

from bas_web_map_inventory.components import Server, Servers
from bas_web_map_inventory.components.airtable import ServerAirtable, ServersAirtable, NamespaceAirtable, \
    NamespacesAirtable, RepositoryAirtable, RepositoriesAirtable, StyleAirtable, StylesAirtable, LayerAirtable, \
    LayersAirtable, LayerGroupAirtable, LayerGroupsAirtable

from tests.bas_web_map_inventory.conftest.components import test_server_data, test_server, test_servers, test_namespace, \
    test_namespaces, test_repository, test_repositories, test_style, test_styles, test_layer, test_layers, \
    test_layer_group, test_layer_groups
from tests.bas_web_map_inventory.conftest.airtable import MockAirtable, test_server_data_airtable, \
    test_namespace_data_airtable, test_repository_data_airtable, test_style_data_airtable, test_layer_data_airtable, \
    test_layer_group_data_airtable, test_servers_airtable, test_namespaces_airtable, test_repositories_airtable, \
    test_styles_airtable, test_layers_airtable, test_layer_groups_airtable


class InvalidItem:
    pass


# noinspection PyTypeChecker,PyUnusedLocal
def setup_airtable(config: dict) -> dict:
    _servers_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Servers',
        data=[deepcopy(test_server_data_airtable)]
    )
    servers_airtable = ServersAirtable(
        airtable=_servers_airtable,
        servers=test_servers
    )

    _namespaces_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Workspaces',
        data=[deepcopy(test_namespace_data_airtable)]
    )
    namespaces_airtable = NamespacesAirtable(
        airtable=_namespaces_airtable,
        namespaces=test_namespaces,
        servers_airtable=servers_airtable
    )

    _repositories_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Stores',
        data=[deepcopy(test_repository_data_airtable)]
    )
    repositories_airtable = RepositoriesAirtable(
        airtable=_repositories_airtable,
        repositories=test_repositories,
        namespaces_airtable=namespaces_airtable
    )

    _styles_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Styles',
        data=[deepcopy(test_style_data_airtable)]
    )
    styles_airtable = StylesAirtable(
        airtable=_styles_airtable,
        styles=test_styles,
        namespaces_airtable=namespaces_airtable
    )

    _layers_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Layers',
        data=[deepcopy(test_layer_data_airtable)]
    )
    layers_airtable = LayersAirtable(
        airtable=_layers_airtable,
        layers=test_layers,
        namespaces_airtable=namespaces_airtable,
        repositories_airtable=repositories_airtable,
        styles_airtable=styles_airtable
    )

    _layer_groups_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Layer Groups',
        data=[deepcopy(test_layer_group_data_airtable)]
    )
    layer_groups_airtable = LayerGroupsAirtable(
        airtable=_layer_groups_airtable,
        layer_groups=test_layer_groups,
        namespaces_airtable=namespaces_airtable,
        styles_airtable=styles_airtable,
        layers_airtable=layers_airtable
    )

    return {
        'servers': servers_airtable,
        'namespaces': namespaces_airtable,
        'repositories': repositories_airtable,
        'styles': styles_airtable,
        'layers': layers_airtable,
        'layer_groups': layer_groups_airtable
    }


# noinspection PyTypeChecker,PyUnusedLocal
def setup_airtable_outdated(config: dict) -> dict:
    outdated_server_data = deepcopy(test_server_data)
    outdated_server_data['label'] = 'outdated-server-1'
    outdated_server = Server(**outdated_server_data)

    _test_servers = Servers()
    _test_servers['outdated'] = outdated_server
    _test_server_data_airtable = deepcopy(test_server_data_airtable)

    _servers_airtable = MockAirtable(
        base_key='test',
        api_key='test',
        table_name='Servers',
        data=[_test_server_data_airtable]
    )
    servers_airtable = ServersAirtable(
        airtable=_servers_airtable,
        servers=_test_servers
    )

    airtable = setup_airtable(config=config)
    airtable['servers'] = servers_airtable
    return airtable


@pytest.mark.parametrize(
    argnames=['airtable_component', 'component_item', 'airtable_component_kwargs', 'airtable_component_str_repr'],
    argvalues=[
        (
            ServerAirtable,
            test_server,
            {},
            'Server(Airtable) <id=01DRS53XAG5E85MJNYTA6WPTBM, airtable_id=None, name=test-server-1, type=ServerTypeAirtable.GEOSERVER>'
        ),
        (
            NamespaceAirtable,
            test_namespace,
            {'servers_airtable': test_servers_airtable},
            'Namespace(Airtable) <id=01DRS53XAGHZ63VSWDV1M4WBFG, airtable_id=None, name=test-namespace-1>'
        ),
        (
            RepositoryAirtable,
            test_repository,
            {'namespaces_airtable': test_namespaces_airtable},
            'Repository(Airtable) <id=01DRS53XAG2QEB6MYES5DZ8P7Q, airtable_id=None, name=test-repository-1>'
        ),
        (
            StyleAirtable,
            test_style,
            {'namespaces_airtable': test_namespaces_airtable},
            'Style(Airtable) <id=01DRS53XAGEXJ0JWGB73FXQS04, airtable_id=None, name=test-style-1>'
        ),
        (
            LayerAirtable,
            test_layer,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Layer(Airtable) <id=01DRS53XAHN84G0NE0YJJRWVKA, airtable_id=None, name=test-layer-1>'
        ),
        (
            LayerGroupAirtable,
            test_layer_group,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'LayerGroup(Airtable) <id=01DRS53XAH7TB65G8BBQZGMHYB, airtable_id=None, name=test-layer-group-1>'
        )
    ]
)
def test_single_airtable_component(
    airtable_component,
    component_item,
    airtable_component_kwargs,
    airtable_component_str_repr
):
    parameters = {'item': component_item, **airtable_component_kwargs}
    item = airtable_component(**parameters)
    assert isinstance(item, airtable_component)
    assert str(item) == airtable_component_str_repr

    assert isinstance(item.airtable_fields(), dict)


@pytest.mark.parametrize(
    argnames=['airtable_component', 'airtable_component_kwargs', 'airtable_table', 'airtable_data'],
    argvalues=[
        (
            ServersAirtable,
            {'servers': test_servers},
            'Servers',
            [test_server_data_airtable]
        ),
        (
            NamespacesAirtable,
            {'namespaces': test_namespaces, 'servers_airtable': test_servers_airtable},
            'Workspaces',
            [test_namespace_data_airtable]
        ),
        (
            RepositoriesAirtable,
            {'repositories': test_repositories, 'namespaces_airtable': test_namespaces_airtable},
            'Stores',
            [test_repository_data_airtable]
        ),
        (
            StylesAirtable,
            {'styles': test_styles, 'namespaces_airtable': test_namespaces_airtable},
            'Styles',
            [test_style_data_airtable]
        ),
        (
            LayersAirtable,
            {
                'layers': test_layers,
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Layers',
            [test_layer_data_airtable]
        ),
        (
            LayerGroupsAirtable,
            {
                'layer_groups': test_layer_groups,
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'Layer Groups',
            [test_layer_group_data_airtable]
        )
    ]
)
def test_multiple_airtable_component(airtable_component, airtable_component_kwargs, airtable_table, airtable_data):
    mock_airtable = MockAirtable(base_key='test', api_key='test', table_name=airtable_table, data=airtable_data)
    parameters = {'airtable': mock_airtable, **airtable_component_kwargs}
    # noinspection PyTypeChecker
    collection = airtable_component(**parameters)
    assert isinstance(collection, airtable_component)
    assert len(collection.items_local) == len(collection.items_airtable)


@pytest.mark.parametrize(
    argnames=['airtable_component', 'component_item', 'airtable_component_kwargs', 'exception_str'],
    argvalues=[
        (
            ServerAirtable,
            InvalidItem(),
            {},
            'Item must be a dict or Server object'
        ),
        (
            NamespaceAirtable,
            InvalidItem(),
            {'servers_airtable': test_servers_airtable},
            'Item must be a dict or Namespace object'
        ),
        (
            RepositoryAirtable,
            InvalidItem(),
            {'namespaces_airtable': test_namespaces_airtable},
            'Item must be a dict or Repository object'
        ),
        (
            StyleAirtable,
            InvalidItem(),
            {'namespaces_airtable': test_namespaces_airtable},
            'Item must be a dict or Style object'
        ),
        (
            LayerAirtable,
            InvalidItem(),
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Item must be a dict or Layer object'
        ),
        (
            LayerGroupAirtable,
            InvalidItem(),
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'Item must be a dict or LayerGroup object'
        )
    ]
)
def test_single_airtable_component_invalid_item(
    airtable_component,
    component_item,
    airtable_component_kwargs,
    exception_str
):
    with pytest.raises(TypeError) as e:
        parameters = {'item': component_item, **airtable_component_kwargs}
        airtable_component(**parameters)
    assert exception_str in str(e.value)


@pytest.mark.parametrize(
    argnames=['airtable_component', 'component_item', 'airtable_component_kwargs', 'exception_str'],
    argvalues=[
        (
            NamespaceAirtable,
            test_namespace,
            {},
            'ServersAirtable collection not included as keyword argument.'
        ),
        (
            RepositoryAirtable,
            test_repository,
            {},
            'NamespacesAirtable collection not included as keyword argument.'
        ),
        (
            StyleAirtable,
            test_style,
            {},
            'NamespacesAirtable collection not included as keyword argument.'
        ),
        (
            LayerAirtable,
            test_layer,
            {},
            'NamespacesAirtable collection not included as keyword argument.'
        ),
        (
            LayerAirtable,
            test_layer,
            {'namespaces_airtable': test_namespaces_airtable},
            'RepositoriesAirtable collection not included as keyword argument.'
        ),
        (
            LayerAirtable,
            test_layer,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable
            },
            'StylesAirtable collection not included as keyword argument.'
        ),
        (
            LayerGroupAirtable,
            test_layer_group,
            {},
            'NamespacesAirtable collection not included as keyword argument.'
        ),
        (
            LayerGroupAirtable,
            test_layer_group,
            {'namespaces_airtable': test_namespaces_airtable},
            'LayersAirtable collection not included as keyword argument.'
        ),
        (
            LayerGroupAirtable,
            test_layer_group,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'layers_airtable': test_layers_airtable
            },
            'StylesAirtable collection not included as keyword argument.'
        )
    ]
)
def test_single_airtable_component_missing_collection(
    airtable_component,
    component_item,
    airtable_component_kwargs,
    exception_str
):
    with pytest.raises(RuntimeError) as e:
        parameters = {'item': component_item, **airtable_component_kwargs}
        airtable_component(**parameters)
    assert exception_str in str(e.value)


@pytest.mark.parametrize(
    argnames=['airtable_component', 'component_item', 'airtable_component_kwargs', 'collection', 'exception_str'],
    argvalues=[
        (
            NamespaceAirtable,
            test_namespace_data_airtable,
            {'servers_airtable': test_servers_airtable},
            'Server',
            'Server with Airtable ID [invalid] not found'
        ),
        (
            RepositoryAirtable,
            test_repository_data_airtable,
            {'namespaces_airtable': test_namespaces_airtable},
            'Workspace',
            'Namespace with Airtable ID [invalid] not found'
        ),
        (
            StyleAirtable,
            test_style_data_airtable,
            {'namespaces_airtable': test_namespaces_airtable},
            'Workspace',
            'Namespace with Airtable ID [invalid] not found'
        ),
        (
            LayerAirtable,
            test_layer_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Workspace',
            'Namespace with Airtable ID [invalid] not found'
        ),
        (
            LayerAirtable,
            test_layer_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Store',
            'Repository with Airtable ID [invalid] not found'
        ),
        (
            LayerAirtable,
            test_layer_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable
            },
            'Styles',
            'Style with Airtable ID [invalid] not found'
        ),
        (
            LayerGroupAirtable,
            test_layer_group_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'Workspace',
            'Namespace with Airtable ID [invalid] not found'
        ),
        (
            LayerGroupAirtable,
            test_layer_group_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'Styles',
            'Style with Airtable ID [invalid] not found'
        ),
        (
            LayerGroupAirtable,
            test_layer_group_data_airtable,
            {
                'namespaces_airtable': test_namespaces_airtable,
                'repositories_airtable': test_repositories_airtable,
                'styles_airtable': test_styles_airtable,
                'layers_airtable': test_layers_airtable
            },
            'Layers',
            'Layer with Airtable ID [invalid] not found'
        )
    ]
)
def test_single_airtable_component_missing_collection_item(
    airtable_component,
    component_item,
    airtable_component_kwargs,
    collection,
    exception_str
):
    with pytest.raises(KeyError) as e:
        item = deepcopy(component_item)
        item['fields'][collection][0] = 'invalid'
        parameters = {'item': item, **airtable_component_kwargs}
        airtable_component(**parameters)
    assert exception_str in str(e.value)


@pytest.mark.parametrize(
    argnames=['airtable_component'],
    argvalues=[
        (deepcopy(test_servers_airtable),),
        (deepcopy(test_namespaces_airtable),),
        (deepcopy(test_repositories_airtable),),
        (deepcopy(test_styles_airtable),),
        (deepcopy(test_layers_airtable),),
        (deepcopy(test_layer_groups_airtable),)
    ],
    ids=[
        'servers',
        'namespaces',
        'repositories',
        'styles',
        'layers',
        'layer_groups'
    ]
)
def test_airtable_status(airtable_component):
    status = airtable_component.status()
    assert isinstance(status, dict)
    assert len(status['current']) == 1
    assert len(status['outdated']) == 0
    assert len(status['missing']) == 0
    assert len(status['orphaned']) == 0


def test_airtable_sync():
    outdated_server = Server(**{
        'server_id': '01DRS53XAG5E85MJNYTA6WPTBM',
        'label': 'outdated-server-1',
        'hostname': 'outdated-server-1.example.com',
        'server_type': 'geoserver',
        'version': '0.0.0'
    })
    missing_server = Server(**{
        'server_id': 'missing',
        'label': 'missing-server',
        'hostname': 'missing-server.example.com',
        'server_type': 'geoserver',
        'version': '0.0.0'
    })
    servers = Servers()
    servers['outdated'] = outdated_server
    servers['missing'] = missing_server

    _test_server_data_airtable = deepcopy(test_server_data_airtable)
    airtable_servers = [
        _test_server_data_airtable,
        {
            "id": "recTest000001srv2",
            "fields": {
                "Hostname": "orphaned-server-1.example.com",
                "Type": "GeoServer",
                "Version": "0.0.0",
                "Name": "orphaned-server-1",
                "Workspaces": [
                    "recTest00000wksp1"
                ],
                "ID": "01DRS53XAJP6WYSDHS859CV30S"
            },
            "createdTime": "2019-11-05T12:22:22.000Z"
        }
    ]

    # noinspection PyTypeChecker
    airtable = ServersAirtable(
        airtable=MockAirtable(base_key='test', api_key='test', table_name='Servers', data=airtable_servers),
        servers=servers
    )

    status = airtable.status()
    assert isinstance(status, dict)
    assert len(status['current']) == 0
    assert len(status['outdated']) == 1
    assert len(status['missing']) == 1
    assert len(status['orphaned']) == 1

    airtable.sync()

    status = airtable.status()
    assert isinstance(status, dict)
    assert len(status['current']) == 2
    assert len(status['outdated']) == 0
    assert len(status['missing']) == 0
    assert len(status['orphaned']) == 0


def test_airtable_reset():
    airtable_data = [deepcopy(test_server_data_airtable)]
    # noinspection PyTypeChecker
    airtable = ServersAirtable(
        airtable=MockAirtable(base_key='test', api_key='test', table_name='Servers', data=airtable_data),
        servers=deepcopy(test_servers)
    )

    status = airtable.status()
    assert isinstance(status, dict)
    assert len(status['current']) == 1
    assert len(status['outdated']) == 0
    assert len(status['missing']) == 0
    assert len(status['orphaned']) == 0

    airtable.reset()

    status = airtable.status()
    assert isinstance(status, dict)
    assert len(status['current']) == 0
    assert len(status['outdated']) == 0
    assert len(status['missing']) == 1
    assert len(status['orphaned']) == 0


@pytest.mark.usefixtures('app', 'app_runner')
def test_airtable_status_command(app, app_runner):
    with patch('bas_web_map_inventory.cli._setup_airtable', side_effect=setup_airtable):
        result = app_runner.invoke(args=['airtable', 'status', '-d', 'tests/data/data.json'])
        assert result.exit_code == 0
        assert '* current (total): 6' in result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_airtable_sync_command(app, app_runner):
    with patch('bas_web_map_inventory.cli._setup_airtable', side_effect=setup_airtable_outdated):
        result = app_runner.invoke(args=['airtable', 'sync', '-d', 'tests/data/data.json'])
        assert result.exit_code == 0
        assert "{'current': [], 'outdated': ['01DRS53XAG5E85MJNYTA6WPTBM'], 'missing': [], 'orphaned': []}" in \
               result.output
        assert "{'current': ['01DRS53XAG5E85MJNYTA6WPTBM'], 'outdated': [], 'missing': [], 'orphaned': []}" in \
               result.output


@pytest.mark.usefixtures('app', 'app_runner')
def test_airtable_reset_command(app, app_runner):
    with patch('bas_web_map_inventory.cli._setup_airtable', side_effect=setup_airtable):
        result = app_runner.invoke(args=['airtable', 'reset', '-d', 'tests/data/data.json'], input='y\n')
        assert result.exit_code == 0
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAG5E85MJNYTA6WPTBM'], 'orphaned': []}" in\
               result.output
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAGHZ63VSWDV1M4WBFG'], 'orphaned': []}" in\
               result.output
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAG2QEB6MYES5DZ8P7Q'], 'orphaned': []}" in\
               result.output
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAGEXJ0JWGB73FXQS04'], 'orphaned': []}" in\
               result.output
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAHN84G0NE0YJJRWVKA'], 'orphaned': []}" in\
               result.output
        assert "{'current': [], 'outdated': [], 'missing': ['01DRS53XAH7TB65G8BBQZGMHYB'], 'orphaned': []}" in\
               result.output
