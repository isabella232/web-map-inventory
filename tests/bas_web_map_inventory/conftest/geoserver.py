from tests.bas_web_map_inventory.conftest.components import test_namespace_data, test_repository_data, \
    test_style_data, test_layer_data, test_layer_group_data


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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
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

    # noinspection PyUnusedLocal
    @staticmethod
    def get_schema(name: str):
        return {
            'geometry': test_layer_data['geometry_type']
        }


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
