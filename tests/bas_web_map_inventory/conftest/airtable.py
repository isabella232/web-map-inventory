from typing import List, Dict

from bas_web_map_inventory.components.airtable import ServerAirtable, NamespaceAirtable, RepositoryAirtable, \
    StyleAirtable, LayerAirtable, LayerGroupAirtable
from bas_web_map_inventory.components.airtable import ServersAirtable, NamespacesAirtable, RepositoriesAirtable, \
    StylesAirtable, LayersAirtable, LayerGroupsAirtable

from tests.bas_web_map_inventory.conftest.components import test_server, test_servers, test_namespace, \
    test_namespaces, test_repository, test_repositories, test_style, test_styles, test_layer, test_layers, \
    test_layer_group, test_layer_groups


class MockAirtable:
    def __init__(self, base_key: str, api_key: str, table_name: str):
        self.base_key = base_key
        self.api_key = api_key
        self.table_name = table_name

    def get_all(self) -> List:
        if self.table_name == 'Servers':
            return [test_server_data_airtable]
        elif self.table_name == 'Workspaces':
            return [test_namespace_data_airtable]
        elif self.table_name == 'Stores':
            return [test_repository_data_airtable]
        elif self.table_name == 'Styles':
            return [test_style_data_airtable]
        elif self.table_name == 'Layers':
            return [test_layer_data_airtable]
        elif self.table_name == 'Layer Groups':
            return [test_layer_group_data_airtable]
        else:
            return []

    # noinspection PyUnusedLocal
    @staticmethod
    def batch_insert(records: List[Dict]):
        return NotImplementedError()

    # noinspection PyUnusedLocal
    @staticmethod
    def batch_delete(self, record_ids: List[str]):
        return NotImplementedError()

    # noinspection PyUnusedLocal
    @staticmethod
    def mock_update(self, record_id: str, fields: Dict):
        return NotImplementedError()


test_server_data_airtable = {
    "id": "recTest000000srv1",
    "fields": {
        "Hostname": "test-server-1.example.com",
        "Type": "GeoServer",
        "Version": "0.0.0",
        "Name": "test-server-1",
        "Workspaces": [
            "recTest00000wksp1"
        ],
        "ID": "01DRS53XAG5E85MJNYTA6WPTBM"
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_server_airtable = ServerAirtable(item=test_server)
_test_servers_airtable = MockAirtable(base_key='test', api_key='test', table_name='Servers')
# noinspection PyTypeChecker
test_servers_airtable = ServersAirtable(
    airtable=_test_servers_airtable,
    servers=test_servers
)

test_namespace_data_airtable = {
    "id": "recTest00000wksp1",
    "fields": {
        "Name": "test-namespace-1",
        "Styles": [
            "recTest00000styl1"
        ],
        "Layers": [
            "recTest000000lyr1"
        ],
        "Layer Groups": [
            "recTest00000lygp1"
        ],
        "Server": [
            "recTest000000srv1"
        ],
        "Title": "Test Namespace 1",
        "Stores": [
            "recTest0000000str1"
        ],
        "ID": "01DRS53XAGHZ63VSWDV1M4WBFG"
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_namespace_airtable = NamespaceAirtable(item=test_namespace, servers_airtable=test_servers_airtable)
_test_namespaces_airtable = MockAirtable(base_key='test', api_key='test', table_name='Workspaces')
# noinspection PyTypeChecker
test_namespaces_airtable = NamespacesAirtable(
    airtable=_test_namespaces_airtable,
    namespaces=test_namespaces,
    servers_airtable=test_servers_airtable
)

test_repository_data_airtable = {
    "id": "recTest0000000str1",
    "fields": {
        "Type": "PostGIS",
        "Title": "Test Repository 1",
        "Layers": [
            "recTest000000lyr1"
        ],
        "ID": "01DRS53XAG2QEB6MYES5DZ8P7Q",
        "Workspace": [
            "recTest00000wksp1"
        ],
        "Schema": "test",
        "Host": "test-postgis-1.example.com",
        "Database": "test",
        "Name": "test-repository-1"
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_repository_airtable = RepositoryAirtable(item=test_repository, namespaces_airtable=test_namespaces_airtable)
_test_repositories_airtable = MockAirtable(base_key='test', api_key='test', table_name='Stores')
# noinspection PyTypeChecker
test_repositories_airtable = RepositoriesAirtable(
    airtable=_test_repositories_airtable,
    repositories=test_repositories,
    namespaces_airtable=test_namespaces_airtable
)

test_style_data_airtable = {
    "id": "recTest00000styl1",
    "fields": {
        "Name": "test-style-1",
        "Layers": [
            "recTest000000lyr1"
        ],
        "Workspace": [
            "recTest00000wksp1"
        ],
        "Layer Groups": [
            "recTest00000lygp1"
        ],
        "Title": "Test Style 1",
        "Type": "SLD",
        "ID": "01DRS53XAGEXJ0JWGB73FXQS04"
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_style_airtable = StyleAirtable(item=test_style, namespaces_airtable=test_namespaces_airtable)
_test_styles_airtable = MockAirtable(base_key='test', api_key='test', table_name='Styles')
# noinspection PyTypeChecker
test_styles_airtable = StylesAirtable(
    airtable=_test_styles_airtable,
    styles=test_styles,
    namespaces_airtable=test_namespaces_airtable
)

test_layer_data_airtable = {
    "id": "recTest000000lyr1",
    "fields": {
        "Table/View": "test",
        "Styles": [
            "recTest00000styl1"
        ],
        "Services": [
            "WFS"
        ],
        "Geometry": "Point",
        "Layer Groups": [
            "recTest00000lygp1"
        ],
        "Store": [
            "recTest0000000str1"
        ],
        "Workspace": [
            "recTest00000wksp1"
        ],
        "Name": "test-layer-1",
        "Title": "Test Layer 1",
        "Type": "Vector",
        "ID": "01DRS53XAHN84G0NE0YJJRWVKA"
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_layer_airtable = LayerAirtable(
    item=test_layer,
    namespaces_airtable=test_namespaces_airtable,
    repositories_airtable=test_repositories_airtable,
    styles_airtable=test_styles_airtable
)
_test_layers_airtable = MockAirtable(base_key='test', api_key='test', table_name='Layers')
# noinspection PyTypeChecker
test_layers_airtable = LayersAirtable(
    airtable=_test_layers_airtable,
    layers=test_layers,
    namespaces_airtable=test_namespaces_airtable,
    repositories_airtable=test_repositories_airtable,
    styles_airtable=test_styles_airtable
)

test_layer_group_data_airtable = {
    "id": "recTest00000lygp1",
    "fields": {
        "Layers": [
            "recTest000000lyr1"
        ],
        "Title": "Test Layer Group 1",
        "ID": "01DRS53XAH7TB65G8BBQZGMHYB",
        "Styles": [
            "recTest00000styl1"
        ],
        "Name": "test-layer-group-1",
        "Workspace": [
            "recTest00000wksp1"
        ]
    },
    "createdTime": "2019-11-05T12:22:22.000Z"
}
test_layer_group_airtable = LayerGroupAirtable(
    item=test_layer_group,
    namespaces_airtable=test_namespaces_airtable,
    repositories_airtable=test_repositories_airtable,
    styles_airtable=test_styles_airtable,
    layers_airtable=test_layers_airtable
)
_test_layer_groups_airtable = MockAirtable(base_key='test', api_key='test', table_name='Layer Groups')
# noinspection PyTypeChecker
test_layer_groups_airtable = LayerGroupsAirtable(
    airtable=_test_layer_groups_airtable,
    layer_groups=test_layer_groups,
    namespaces_airtable=test_namespaces_airtable,
    repositories_airtable=test_repositories_airtable,
    styles_airtable=test_styles_airtable,
    layers_airtable=test_layers_airtable
)
