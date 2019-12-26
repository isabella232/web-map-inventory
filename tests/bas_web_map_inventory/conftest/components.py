from bas_web_map_inventory.components import Server, Servers, Namespace, Namespaces, Repository, Repositories, Style, \
    Styles, Layer, Layers, LayerGroup, LayerGroups


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
    'services': ['wfs'],
    'namespace': test_namespace,
    'layers': [test_layer],
    'styles': [test_style]
}
test_layer_group = LayerGroup(**test_layer_group_data)
test_layer_groups = LayerGroups()
test_layer_groups['test'] = test_layer_group
