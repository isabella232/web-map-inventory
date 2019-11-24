import pytest

from bas_web_map_inventory.components.airtable import ServerAirtable, ServersAirtable, NamespaceAirtable, \
    NamespacesAirtable, RepositoryAirtable, RepositoriesAirtable, StyleAirtable, StylesAirtable, LayerAirtable, \
    LayersAirtable, LayerGroupAirtable, LayerGroupsAirtable

from tests.bas_web_map_inventory.conftest.components import test_server, test_servers, test_namespace, \
    test_namespaces, test_repository, test_repositories, test_style, test_styles, test_layer, test_layers, \
    test_layer_group, test_layer_groups
from tests.bas_web_map_inventory.conftest.airtable import MockAirtable, test_servers_airtable, \
    test_namespaces_airtable, test_repositories_airtable, test_styles_airtable, test_layers_airtable, \
    test_layer_groups_airtable


@pytest.mark.parametrize(
    argnames=['airtable_component', 'component_item', 'airtable_component_kwargs'],
    argvalues=[
        (ServerAirtable, test_server, {}),
        (NamespaceAirtable, test_namespace, {'servers_airtable': test_servers_airtable}),
        (RepositoryAirtable, test_repository, {'namespaces_airtable': test_namespaces_airtable}),
        (StyleAirtable, test_style, {'namespaces_airtable': test_namespaces_airtable}),
        (LayerAirtable, test_layer, {
            'namespaces_airtable': test_namespaces_airtable,
            'repositories_airtable': test_repositories_airtable,
            'styles_airtable': test_styles_airtable
        }),
        (LayerGroupAirtable, test_layer_group, {
            'namespaces_airtable': test_namespaces_airtable,
            'repositories_airtable': test_repositories_airtable,
            'styles_airtable': test_styles_airtable,
            'layers_airtable': test_layers_airtable
        })
    ]
)
def test_single_airtable_component(airtable_component, component_item, airtable_component_kwargs):
    parameters = {'item': component_item, **airtable_component_kwargs}
    item = airtable_component(**parameters)
    assert isinstance(item, airtable_component)


@pytest.mark.parametrize(
    argnames=['airtable_component', 'airtable_component_kwargs', 'airtable_table'],
    argvalues=[
        (ServersAirtable, {
            'servers': test_servers
        }, 'Servers'),
        (NamespacesAirtable, {
            'namespaces': test_namespaces,
            'servers_airtable': test_servers_airtable
        }, 'Workspaces'),
        (RepositoriesAirtable, {
            'repositories': test_repositories,
            'namespaces_airtable': test_namespaces_airtable
        }, 'Stores'),
        (StylesAirtable, {
            'styles': test_styles,
            'namespaces_airtable': test_namespaces_airtable
        }, 'Styles'),
        (LayersAirtable, {
            'layers': test_layers,
            'namespaces_airtable': test_namespaces_airtable,
            'repositories_airtable': test_repositories_airtable,
            'styles_airtable': test_styles_airtable
        }, 'Layers'),
        (LayerGroupsAirtable, {
            'layer_groups': test_layer_groups,
            'namespaces_airtable': test_namespaces_airtable,
            'repositories_airtable': test_repositories_airtable,
            'styles_airtable': test_styles_airtable,
            'layers_airtable': test_layers_airtable
        }, 'Layer Groups')
    ]
)
def test_multiple_airtable_component(airtable_component, airtable_component_kwargs, airtable_table):
    mock_airtable = MockAirtable(base_key='test', api_key='test', table_name=airtable_table)
    parameters = {'airtable': mock_airtable, **airtable_component_kwargs}
    # noinspection PyTypeChecker
    collection = airtable_component(**parameters)
    assert isinstance(collection, airtable_component)
    assert len(collection.items_local) == len(collection.items_airtable)


@pytest.mark.parametrize(
    argnames=['airtable_component'],
    argvalues=[
        (test_servers_airtable,),
        (test_namespaces_airtable,),
        (test_repositories_airtable,),
        (test_styles_airtable,),
        (test_layers_airtable,),
        (test_layer_groups_airtable,)
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
