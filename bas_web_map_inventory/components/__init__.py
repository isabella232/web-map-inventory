from enum import Enum
from typing import Dict, List, Optional


class ServerType(Enum):
    """
    Represents the technology/product a server uses.
    """
    GEOSERVER = 'geoserver'


class RepositoryType(Enum):
    """
    Represents the technology/product a repository uses.
    """
    POSTGIS = 'postgis'
    GEOTIFF = 'geotiff'
    ECW = 'ecw'
    JPEG2000 = 'jp2ecw'
    IMAGEMOSAIC = 'imagemosaic'
    WORLDIMAGE = 'worldimage'


class StyleType(Enum):
    """
    Represents the format a style is written in.
    """
    SLD = 'sld'


class LayerType(Enum):
    """
    Represents a layer's fundamental data type (raster or vector).
    """
    RASTER = 'raster'
    VECTOR = 'vector'


class LayerGeometry(Enum):
    """
    Represents a (vector) layer's geometry.
    """
    POINT = 'point'
    LINESTRING = 'linestring'
    POLYGON = 'polygon'
    MULTIPOINT = 'multi-point'
    MULTILINESTRING = 'multi-linestring'
    MULTIPOLYGON = 'multi-polygon'


class LayerService(Enum):
    """
    Represents which OGC services a layer can be accessed with.
    """
    WMS = 'wms'
    WMTS = 'wmts'
    WCS = 'wcs'
    WFS = 'wfs'


class LayerGroupService(Enum):
    """
    Represents which OGC services a layer group can be accessed with.
    """
    WMS = 'wms'
    WMTS = 'wmts'
    WCS = 'wcs'
    WFS = 'wfs'


class Server:
    """
    Represents an application, service or platform that provides access to layers.

    Servers can represent literal hosts or an entire platform/service-provider, in which case the 'hosts' are unknown
    and the hostname becomes more like an 'endpoint'.

    Servers MUST be globally unique.
    """

    def __init__(
        self,
        server_id: str,
        label: str,
        hostname: str,
        server_type: str,
        version: str
    ):
        self.id = server_id
        self.label = label
        self.hostname = hostname
        self.type = ServerType(server_type)
        self.version = version

    def to_dict(self) -> Dict:
        _server = {
            'id': self.id,
            'label': self.label,
            'hostname': self.hostname,
            'type': self.type.value,
            'version': self.version
        }

        return _server

    def __repr__(self):
        return f"Server <id={self.id}, label={self.label}, type={self.type}>"


class Namespace:
    """
    Represents a logical grouping of resources within a server/endpoint.

    For example, namespaces could be:
    * theme/subject
    * regions
    * time periods
    * projects/activities
    * progress states (e.g. draft/published)
    * access/usage status (e.g. public, internal)
    * provider/source
    * end-user
    * data formats, etc.

    Namespaces are known as 'workspaces' in GeoServer.

    Namespaces belong to, and MUST be unique within, a single server. Namespaces SHOULD be globally unique across all
    servers to avoid confusion.
    """

    def __init__(
        self,
        namespace_id: str,
        label: str,
        title: str,
        namespace: str,
        server: Server = None
    ):
        self.id = namespace_id
        self.label = label
        self.title = title
        self.namespace = namespace
        self.relationships = {
            'servers': None
        }

        if server is not None:
            self.relationships['servers'] = server

    def to_dict(self) -> Dict:
        _namespace = {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'namespace': self.namespace,
            'relationships': {
                'servers': self.relationships['servers'].id
            }
        }

        return _namespace

    def __repr__(self):
        return f"Namespace <id={self.id}, label={self.label}, server={self.relationships['servers'].id}>"


class Repository:
    """
    Represents a data source that backs one or more layers.

    Data sources may have a 1:1 or 1:many relationship to layers. Typically, raster layers are 1:1 (to an image or
    image mosaic) but vector layers can be 1:many where databases have multiple tables/views for a different layers.

    Repositories are known as 'stores' in GeoServer.

    Repositories belong to, and MUST be unique within, a single namespace.
    """

    def __init__(
        self,
        repository_id: str,
        label: str,
        title: str,
        repository_type: str,
        hostname: str = None,
        database: str = None,
        schema: str = None,
        namespace: Namespace = None
    ):
        self.id = repository_id
        self.label = label
        self.title = title
        self.type = RepositoryType(repository_type)
        self.hostname = hostname
        self.database = database
        self.schema = schema
        self.relationships = {
            'namespaces': None
        }

        if namespace is not None:
            self.relationships['namespaces'] = namespace

    def to_dict(self) -> Dict:
        _repository = {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'type': self.type.value,
            'hostname': self.hostname,
            'database': self.database,
            'schema': self.schema,
            'relationships': {
                'namespaces': self.relationships['namespaces'].id
            }
        }

        return _repository

    def __repr__(self):
        return f"Repository <id={self.id}, label={self.label}, type={self.type}>"


class Style:
    """
    Represents a definition for how data in a layer should be represented/presented.

    This can include symbology, labeling and other properties. Styles can be written in a variety of formats, provided
    it's supported by the server.

    Styles belong to a single namespace and can be general, applying to multiple layers, or specific to a single layer.
    """

    def __init__(
        self,
        style_id: str,
        label: str,
        title: str,
        style_type: str,
        namespace: Namespace = None
    ):
        self.id = style_id
        self.label = label
        self.title = title
        self.type = StyleType(style_type)
        self.relationships = {
            'namespaces': None
        }

        if namespace is not None:
            self.relationships['namespaces'] = namespace

    def to_dict(self) -> Dict:
        _style = {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'type': self.type.value,
            'relationships': {
                'namespaces': None
            }
        }
        if self.relationships['namespaces'] is not None:
            # noinspection PyTypeChecker
            _style['relationships']['namespaces'] = self.relationships['namespaces'].id

        return _style

    def __repr__(self):
        return f"Style <id={self.id}, label={self.label}, type={self.type}>"


class Layer:
    """
    Represents a logical unit of geospatial information.

    Broadly, layers can be divided into either vector or raster layers, based on their backing data. Typically this
    broad data type will dictate how the layer can be accessed (e.g. WFS for vector data, WMS for raster data).

    For example, layers could be:
    * points indicating locations for a particular activity/purpose (e.g. field camps for a project)
    * lines/polygons defining regions for a particular activity/purpose (e.g. data limits, features in a gazetteer)
    * topological base data (inc. DEMs or other model output)
    * bathymetric base data (inc. DEMs or other model output)
    * coastlines and other natural features (rock outcrops etc.)

    Layers belong to a single namespace, backed by a single data source (or part of a single data source) and
    represented by one or more styles.
    """

    def __init__(
        self,
        layer_id: str,
        label: str,
        title: str,
        layer_type: str,
        geometry_type: str = None,
        services: List[str] = None,
        table_view: str = None,
        namespace: Namespace = None,
        repository: Repository = None,
        styles: List[Style] = None
    ):
        self.id = layer_id
        self.label = label
        self.title = title
        self.type = LayerType(layer_type)
        self.services = []
        self.relationships = {
            'namespaces': None,
            "repositories": None,
            'styles': []
        }

        self.geometry_type = None
        if geometry_type is not None:
            self.geometry_type = LayerGeometry(geometry_type)

        self.table_view = None
        if table_view is not None:
            self.table_view = table_view

        if services is not None and isinstance(services, list):
            for service in services:
                self.services.append(LayerService(service))

        if namespace is not None:
            self.relationships['namespaces'] = namespace
        if repository is not None:
            self.relationships['repositories'] = repository
        if styles is not None and isinstance(styles, list):
            self.relationships['styles'] = styles

    def to_dict(self) -> Dict:
        _layer = {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'type': self.type.value,
            'geometry': None,
            'services': [],
            'table_view': self.table_view,
            'relationships': {
                'namespaces': self.relationships['namespaces'].id,
                'repositories': self.relationships['repositories'].id,
                'styles': []
            }
        }
        if self.geometry_type is not None:
            _layer['geometry'] = self.geometry_type.value
        for service in self.services:
            _layer['services'].append(service.value)
        for style in self.relationships['styles']:
            _layer['relationships']['styles'].append(style.id)

        return _layer

    def __repr__(self):
        return f"Layer <id={self.id}, label={self.label}, type={self.type}>"


class LayerGroup:
    """
    Represents a logical grouping of one or more layers that should be treated as a single, indivisible unit.

    Broadly speaking layer groups are useful for three reasons:
    1. to 'merge' distinct layers together but that form a more complete whole (e.g. a base map containing bathymetry
       and topological data)
    2. to show appropriate detail at different resolutions (e.g. a single logical layer switching between low, medium
       and high detail individual layers)
    3. to provide 'floating' or 'alias' layers for data that changes over time (e.g. a 'hillshade' layer that points to
       the most accurate provider/model at any given time)

    Layer groups belong to a single namespace, represented by one or more styles.
    """

    def __init__(
        self,
        layer_group_id: str,
        label: str,
        title: str,
        geometry_type: str = None,
        services: List[str] = None,
        namespace: Namespace = None,
        layers: List[Layer] = None,
        styles: List[Style] = None
    ):
        self.id = layer_group_id
        self.label = label
        self.title = title
        self.services = []
        self.relationships = {
            'namespaces': None,
            "layers": [],
            "styles": []
        }

        self.geometry_type = None
        if geometry_type is not None:
            self.geometry_type = LayerGeometry(geometry_type)

        if services is not None and isinstance(services, list):
            for service in services:
                self.services.append(LayerGroupService(service))

        if namespace is not None:
            self.relationships['namespaces'] = namespace
        if layers is not None and isinstance(layers, list):
            self.relationships['layers'] = layers
        if styles is not None and isinstance(styles, list):
            self.relationships['styles'] = styles

    def to_dict(self) -> Dict:
        _layer_group = {
            'id': self.id,
            'label': self.label,
            'title': self.title,
            'geometry': None,
            'services': [],
            'relationships': {
                'namespaces': None,
                'layers': [],
                'styles': []
            }
        }

        if self.geometry_type is not None:
            _layer_group['geometry'] = self.geometry_type.value
        for service in self.services:
            _layer_group['services'].append(service.value)

        if self.relationships['namespaces'] is not None:
            # noinspection PyTypeChecker
            _layer_group['relationships']['namespaces'] = self.relationships['namespaces'].id
        for layer in self.relationships['layers']:
            _layer_group['relationships']['layers'].append(layer.id)
        for style in self.relationships['styles']:
            _layer_group['relationships']['styles'].append(style.id)

        return _layer_group

    def __repr__(self):
        return f"LayerGroup <id={self.id}, label={self.label}>"


class Servers(dict):
    """
    Represents a collection of servers.
    """

    def __init__(self, *args, **kwargs):
        super(Servers, self).__init__(*args, **kwargs)

    def to_list(self) -> List[Dict]:
        _servers = []
        for server in self.values():
            _servers.append(server.to_dict())
        return _servers


class Namespaces(dict):
    """
    Represents a collection of namespaces.
    """

    def __init__(self, *args, **kwargs):
        super(Namespaces, self).__init__(*args, **kwargs)

    def get_by_label(self, label: str) -> Optional[Namespace]:
        for item in self.values():
            if item.label == label:
                return item
        return None

    def to_list(self) -> List[Dict]:
        _namespaces = []
        for namespace in self.values():
            _namespaces.append(namespace.to_dict())
        return _namespaces


class Repositories(dict):
    """
    Represents a collection of repositories.
    """

    def __init__(self, *args, **kwargs):
        super(Repositories, self).__init__(*args, **kwargs)

    def to_list(self) -> List[Dict]:
        _repositories = []
        for repository in self.values():
            _repositories.append(repository.to_dict())
        return _repositories

    def get_by_label(self, label: str) -> Optional[Repository]:
        for item in self.values():
            if item.label == label:
                return item
        return None


class Styles(dict):
    """
    Represents a collection of styles.
    """

    def __init__(self, *args, **kwargs):
        super(Styles, self).__init__(*args, **kwargs)

    def to_list(self) -> List[Dict]:
        _styles = []
        for style in self.values():
            _styles.append(style.to_dict())
        return _styles

    def get_by_label(self, label: str, namespace_label: str = None) -> Optional[Style]:
        for item in self.values():
            if item.label == label:
                if namespace_label is None:
                    return item
                else:
                    if item.relationships['namespaces'].label == namespace_label:
                        return item
        return None


class Layers(dict):
    """
    Represents a collection of layers.
    """

    def __init__(self, *args, **kwargs):
        super(Layers, self).__init__(*args, **kwargs)

    def to_list(self) -> List[Dict]:
        _layers = []
        for layer in self.values():
            _layers.append(layer.to_dict())
        return _layers

    def get_by_label(self, label: str, namespace_label: str = None) -> Optional[Layer]:
        for item in self.values():
            if item.label == label:
                if namespace_label is None:
                    return item
                else:
                    if item.relationships['namespaces'].label == namespace_label:
                        return item
        return None


class LayerGroups(dict):
    """
    Represents a collection of layer groups.
    """

    def __init__(self, *args, **kwargs):
        super(LayerGroups, self).__init__(*args, **kwargs)
