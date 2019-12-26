import datetime

from typing import List, Dict, Any
from random import randint

from bas_web_map_inventory.components.airtable import ServerAirtable, NamespaceAirtable, RepositoryAirtable, \
    StyleAirtable, LayerAirtable, LayerGroupAirtable
from bas_web_map_inventory.components.airtable import ServersAirtable, NamespacesAirtable, RepositoriesAirtable, \
    StylesAirtable, LayersAirtable, LayerGroupsAirtable

from tests.bas_web_map_inventory.conftest.components import test_server, test_servers, test_namespace, \
    test_namespaces, test_repository, test_repositories, test_style, test_styles, test_layer, test_layers, \
    test_layer_group, test_layer_groups


class MockAirtable:
    def __init__(self, base_key: str, api_key: str, table_name: str, data: List[Any]):
        self.base_key = base_key
        self.api_key = api_key
        self.table_name = table_name

        self.data = data

    def get_all(self) -> List:
        return self.data

    def batch_insert(self, records: List[Dict]):
        for fields in records:
            self.data.append({
                'id': f"recTest{str(randint(0, 99999)).rjust(5, '0')}",
                'fields': fields,
                'createdTime': datetime.datetime.utcnow().isoformat()
            })

    def update(self, record_id: str, fields: Dict, typecast: bool = False) -> Dict:
        index = None
        for _index, _record in enumerate(self.data):
            if isinstance(_record, dict):
                if 'id' in _record and _record['id'] == record_id:
                    index = _index
        if index is None:
            raise RuntimeError(f"Record with ID [{record_id}] not found")

        self.data[index]['fields'] = fields
        return self.data[index]

    def batch_delete(self, record_ids: List[str]):
        record_indexes = []
        for _index, _record in enumerate(self.data):
            if isinstance(_record, dict):
                if 'id' in _record and _record['id'] in record_ids:
                    record_indexes.append(_index)

        for index in record_indexes:
            self.data.pop(index)


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
_test_servers_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Servers',
    data=[test_server_data_airtable]
)
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
_test_namespaces_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Workspaces',
    data=[test_namespace_data_airtable]
)
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
_test_repositories_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Stores',
    data=[test_repository_data_airtable]
)
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
_test_styles_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Styles',
    data=[test_style_data_airtable]
)
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
_test_layers_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Layers',
    data=[test_layer_data_airtable]
)
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
        "Services": [
            "WFS"
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
_test_layer_groups_airtable = MockAirtable(
    base_key='test',
    api_key='test',
    table_name='Layer Groups',
    data=[test_layer_group_data_airtable]
)
# noinspection PyTypeChecker
test_layer_groups_airtable = LayerGroupsAirtable(
    airtable=_test_layer_groups_airtable,
    layer_groups=test_layer_groups,
    namespaces_airtable=test_namespaces_airtable,
    repositories_airtable=test_repositories_airtable,
    styles_airtable=test_styles_airtable,
    layers_airtable=test_layers_airtable
)
