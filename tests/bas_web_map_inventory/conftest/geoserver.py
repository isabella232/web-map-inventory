from typing import Dict, Any, List, Union

from tests.bas_web_map_inventory.conftest.components import test_namespace_data, test_repository_data, \
    test_style_data, test_layer_data, test_layer_group_data


class MockGeoserverCatalogueWorkspace:
    def __init__(self, name):
        self.name = name


class MockGeoserverCatalogueStore:
    def __init__(self, name: str, workspace: str, description: str = None):
        self.name = name
        self.type = test_repository_data['repository_type']
        self.description = description
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
    def __init__(self, name: str, layers: List[str], styles: List[str], workspace):
        self.name = name
        self.title = test_layer_group_data['title']
        self.workspace = workspace
        self.styles = styles
        self.layers = layers


class MockGeoServerCatalogue:
    def __init__(self):
        self.workspaces = None
        self.stores = None
        self.layergroups = None

    def populate(self, data: Dict[str, Any]):
        self.workspaces = data['workspaces']
        self.stores = data['stores']
        self.layergroups = data['layer_groups']

    @staticmethod
    def get_version() -> str:
        return 'testing'

    def get_workspaces(self):
        workspaces = []
        for workspace in self.workspaces:
            workspaces.append(MockGeoserverCatalogueWorkspace(name=workspace['name']))

        return workspaces

    def get_workspace(self, name: str):
        for workspace in self.workspaces:
            if name == workspace['name']:
                return MockGeoserverCatalogueWorkspace(name=workspace['name'])

        return None

    # noinspection PyUnusedLocal
    def get_stores(self, workspaces: List[str]):
        """
        We need to accept workspaces as a parameter to accommodate the bug in the GeoServer client, it doesn't do
        anything however.
        """
        stores = []
        for store in self.stores:
            stores.append(MockGeoserverCatalogueStore(name=store['name'], workspace=store['workspace_name']))

        return stores

    def get_store(self, name: str, workspace: str):
        for store in self.stores:
            if name == store['name'] and workspace == store['workspace_name']:
                _store = {
                    'name': store['name'],
                    'workspace': store['workspace_name']
                }
                if 'description' in store:
                    _store['description'] = store['description']
                return MockGeoserverCatalogueStore(**_store)

        return None

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

    def get_layergroups(self, workspaces: List[Union[str, MockGeoserverCatalogueWorkspace]]):
        _workspaces = []
        for workspace in workspaces:
            if isinstance(workspace, str):
                _workspaces.append(workspace)
            elif isinstance(workspace, MockGeoserverCatalogueWorkspace):
                _workspaces.append(workspace.name)

        layergroups = []
        for layergroup in self.layergroups:
            if layergroup['workspace_name'] in _workspaces:
                layergroups.append(MockGeoserverCatalogueLayerGroup(
                    name=layergroup['name'],
                    layers=layergroup['layer_names'],
                    styles=layergroup['style_names'],
                    workspace=layergroup['workspace_name']
                ))

        return layergroups

    def get_layergroup(self, name: str, workspace: str):
        for layergroup in self.layergroups:
            if layergroup['name'] == name and layergroup['workspace_name'] == workspace:
                return MockGeoserverCatalogueLayerGroup(
                    name=layergroup['name'],
                    layers=layergroup['layer_names'],
                    styles=layergroup['style_names'],
                    workspace=layergroup['workspace_name']
                )

        return None


class MockWMSClient:
    def __init__(self):
        self.contents = {
            test_layer_data['label']: None,
            f"{test_layer_group_data['namespace'].label}:{test_layer_group_data['label']}": None
        }


class MockWFSClient:
    def __init__(self):
        self.contents = {}

    def populate(self, contents: Dict[str, Any]):
        self.contents = contents

    def get_schema(self, name: str):
        return {
            'geometry': self.contents[name]['geometry']
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

test_geoserver_catalogue_data = {
    'workspaces': [
        {
            'name': test_namespace_data['label']
        }
    ],
    'stores': [
        {
            'name': test_repository_data['label'],
            'description': test_repository_data['title'],
            'workspace_name': test_repository_data['namespace'].label
        }
    ],
    'layer_groups': [
        {
            'name': test_layer_group_data['label'],
            'layer_names': [test_layer_group_data['layers'][0].label],
            'style_names': [test_layer_group_data['styles'][0].label],
            'workspace_name': test_layer_data['namespace'].label,
        }
    ]
}
