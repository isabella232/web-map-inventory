import pytest

from typing import List, Dict

from map_layer_index import create_app, Server, Namespace, Repository, Style, Layer, LayerGroup, Servers, Namespaces, \
    Repositories, Styles, Layers, LayerGroups, ServerAirtable, NamespaceAirtable, RepositoryAirtable, \
    StyleAirtable, LayerAirtable, LayerGroupAirtable, ServersAirtable, NamespacesAirtable, RepositoriesAirtable, \
    StylesAirtable, LayersAirtable, LayerGroupsAirtable

# Generic objects

test_server_data = {
    'server_id': '01DRS53XAG5E85MJNYTA6WPTBM',
    'label': 'test-server-1',
    'hostname': 'test-server-1.example.com',
    'server_type': 'geoserver',
    'version': '0.0.0'
}
test_server = Server(**test_server_data)
test_servers = Servers()
test_servers['test'] = test_server

test_namespace_data = {
    'namespace_id': '01DRS53XAGHZ63VSWDV1M4WBFG',
    'label': 'test-namespace-1',
    'title': 'Test Namespace 1',
    'namespace': 'https://example.com/test-namespace-1',
    'isolated': False,
    'server': test_server
}
test_namespace = Namespace(**test_namespace_data)
test_namespaces = Namespaces()
test_namespaces['test'] = test_namespace

test_repository_data = {
    'repository_id': '01DRS53XAG2QEB6MYES5DZ8P7Q',
    'label': 'test-repository-1',
    'title': 'Test Repository 1',
    'repository_type': 'postgis',
    'hostname': 'test-postgis-1.example.com',
    'database': 'test',
    'schema': 'test',
    'namespace': test_namespace
}
test_repository = Repository(**test_repository_data)
test_repositories = Repositories()
test_repositories['test'] = test_repository

test_style_data = {
    'style_id': '01DRS53XAGEXJ0JWGB73FXQS04',
    'label': 'test-style-1',
    'title': 'Test Style 1',
    'style_type': 'sld',
    'namespace': test_namespace
}
test_style = Style(**test_style_data)
test_styles = Styles()
test_styles['test'] = test_style

test_layer_data = {
    'layer_id': '01DRS53XAHN84G0NE0YJJRWVKA',
    'label': 'test-layer-1',
    'title': 'Test Layer 1',
    'layer_type': 'vector',
    'geometry_type': 'point',
    'services': ['wfs'],
    'table_view': 'test',
    'namespace': test_namespace,
    'repository': test_repository,
    'styles': [test_style]
}
test_layer = Layer(**test_layer_data)
test_layers = Layers()
test_layers['test'] = test_layer

test_layer_group_data = {
    'layer_group_id': '01DRS53XAH7TB65G8BBQZGMHYB',
    'label': 'test-layer-group-1',
    'title': 'Test Layer Group 1',
    'namespace': test_namespace,
    'layers': [test_layer],
    'styles': [test_style]
}
test_layer_group = LayerGroup(**test_layer_group_data)
test_layer_groups = LayerGroups()
test_layer_groups['test'] = test_layer_group


# GeoServer specific objects


class MockGeoserverCatalogueWorkspace:
    def __init__(self, name):
        self.name = name


class MockGeoserverCatalogueStore:
    def __init__(self, name, workspace):
        self.name = name
        self.type = test_repository_data['repository_type']
        self.description = test_repository_data['title']
        self.connection_parameters = {
            'host': test_repository_data['hostname'],
            'database': test_repository_data['database'],
            'schema': test_repository_data['schema']
        }
        self.workspace = MockGeoserverCatalogueWorkspace(name=workspace)


class MockGeoserverCatalogueStyle:
    def __init__(self, name, workspace):
        self.name = name
        self.style_format = 'sld10'
        self.workspace = MockGeoserverCatalogueWorkspace(name=workspace).name


class MockGeoServerCatalogueLayerResource:
    def __init__(self, name, workspace):
        self.name = name
        self.native_name = test_layer_data['table_view']
        self.title = test_layer_data['title']
        self.workspace = MockGeoserverCatalogueWorkspace(name=workspace)
        self.store = MockGeoserverCatalogueStore(
            name=test_layer_data['repository'].label,
            workspace=test_layer_data['repository'].relationships['namespaces'].label
        )


class MockGeoserverCatalogueLayer:
    def __init__(self, name, workspace):
        self.name = name
        self.type = test_layer_data['layer_type']
        self.resource = MockGeoServerCatalogueLayerResource(name=name, workspace=workspace)
        # noinspection PyUnresolvedReferences
        self.default_style = MockGeoserverCatalogueStyle(
            name=test_layer_data['styles'][0].label,
            workspace=test_layer_data['styles'][0].relationships['namespaces'].label
        )
        self.styles = []


class MockGeoserverCatalogueLayerGroup:
    def __init__(self, name, workspace):
        self.name = name
        self.title = test_layer_group_data['title']
        self.workspace = workspace
        self.styles = [test_layer_group_data['styles'][0].label]
        self.layers = [test_layer_data['label']]


class MockGeoServerCatalogue:
    @staticmethod
    def get_version() -> str:
        return 'testing'

    @staticmethod
    def get_workspaces():
        return [MockGeoserverCatalogueWorkspace(name=test_namespace_data['label'])]

    @staticmethod
    def get_workspace(name: str):
        return MockGeoserverCatalogueWorkspace(name=name)

    @staticmethod
    def get_stores(workspaces):
        return [MockGeoserverCatalogueStore(
            name=test_repository_data['label'],
            workspace=test_repository_data['namespace'].label
        )]

    @staticmethod
    def get_store(name: str, workspace: str):
        return MockGeoserverCatalogueStore(
            name=name,
            workspace=workspace
        )

    @staticmethod
    def get_styles(workspaces=None):
        return [MockGeoserverCatalogueStyle(
            name=test_style_data['label'],
            workspace=test_style_data['namespace'].label
        )]

    @staticmethod
    def get_style(name: str, workspace: str):
        return MockGeoserverCatalogueStyle(
            name=name,
            workspace=workspace
        )

    @staticmethod
    def get_layers():
        return [MockGeoserverCatalogueLayer(
            name=test_layer_data['label'],
            workspace=test_layer_data['namespace'].label
        )]

    @staticmethod
    def get_layer(name: str):
        return MockGeoserverCatalogueLayer(
            name=name,
            workspace=test_layer_data['namespace'].label
        )

    @staticmethod
    def get_layergroups(workspaces: list):
        return [MockGeoserverCatalogueLayerGroup(
            name=test_layer_group_data['label'],
            workspace=test_layer_data['namespace'].label
        )]

    @staticmethod
    def get_layergroup(name: str, workspace: str):
        return MockGeoserverCatalogueLayerGroup(
            name=name,
            workspace=workspace
        )


test_geoserver_data = {
    'server_id': '01DRS53XAG5E85MJNYTA6WPTBM',
    'label': 'test-server-1',
    'hostname': 'test-server-1.example.com',
    'port': '80',
    'api_path': '/geoserver/rest',
    'wms_path': '/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities',
    'wfs_path': '/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities',
    'username': 'admin',
    'password': 'password'
}


class MockWMSClient:
    def __init__(self):
        self.contents = {
            test_layer_data['label']: None,
            f"{test_layer_group_data['namespace'].label}:{test_layer_group_data['label']}": None
        }


class MockWFSClient:
    def __init__(self):
        self.contents = {
            test_layer_data['label']: None
        }

    @staticmethod
    def get_schema(name: str):
        return {
            'geometry': test_layer_data['geometry_type']
        }


# Airtable specific objects


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

    def batch_insert(self, records: List[Dict]):
        return NotImplementedError()

    def batch_delete(self, record_ids: List[str]):
        return NotImplementedError()

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
