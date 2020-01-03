from enum import Enum
from typing import Dict, List, Optional, Union, Any


class ServerType(Enum):
    """
    Represents the technology/product a server uses.
    """

    GEOSERVER = "geoserver"


class RepositoryType(Enum):
    """
    Represents the technology/product a repository uses.
    """

    POSTGIS = "postgis"
    GEOTIFF = "geotiff"
    ECW = "ecw"
    JPEG2000 = "jp2ecw"
    IMAGEMOSAIC = "imagemosaic"
    WORLDIMAGE = "worldimage"


class StyleType(Enum):
    """
    Represents the format a style is written in.
    """

    SLD = "sld"


class LayerType(Enum):
    """
    Represents a layer's fundamental data type (raster or vector).
    """

    RASTER = "raster"
    VECTOR = "vector"


class LayerGeometry(Enum):
    """
    Represents a (vector) layer's geometry.
    """

    POINT = "point"
    LINESTRING = "linestring"
    POLYGON = "polygon"
    MULTIPOINT = "multi-point"
    MULTILINESTRING = "multi-linestring"
    MULTIPOLYGON = "multi-polygon"


class LayerService(Enum):
    """
    Represents which OGC services a layer can be accessed with.
    """

    WMS = "wms"
    WMTS = "wmts"
    WCS = "wcs"
    WFS = "wfs"


class LayerGroupService(Enum):
    """
    Represents which OGC services a layer group can be accessed with.
    """

    WMS = "wms"
    WMTS = "wmts"
    WCS = "wcs"
    WFS = "wfs"


class Server:
    """
    Represents an application, service or platform that provides access to layers.

    Servers can represent literal hosts or an entire platform/service-provider, in which case the 'hosts' are unknown
    and the hostname becomes more like an 'endpoint'.

    Servers MUST be globally unique.
    """

    def __init__(self, server_id: str, label: str, hostname: str, server_type: str, version: str):
        """
        Server_id should be defined independently from the server they are based on (i.e. they should be assigned by
        this project to servers, rather than read from them, to prevent clashes and loss of integrity)

        :param server_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable Identifier)
        :param label: a human readable, well-known, identifier for the server - typically based on the hostname
        :param hostname: servers fully qualified hostname
        :param server_type: a servers implementation, specified as a member of the ServerType enumeration
        :param version: the version of the server's implementation
        """
        self.id = server_id
        self.label = label
        self.hostname = hostname
        self.type = ServerType(server_type)
        self.version = version

    def to_dict(self) -> Dict[str, str]:
        """
        Represents a Server as a dictionary

        :return: a Server represented as a dictionary
        """
        _server = {
            "id": self.id,
            "label": self.label,
            "hostname": self.hostname,
            "type": self.type.value,
            "version": self.version,
        }

        return _server

    def __repr__(self) -> str:
        """
        :return: String representation of a Server
        """
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

    def __init__(self, namespace_id: str, label: str, title: str, namespace: str, server: Server = None):
        """
        Namespace_id should be defined independently from the namespace they are based on (i.e. they should be assigned
        by this project to namespaces, rather than read from them, to prevent clashes and loss of integrity)

        :param namespace_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable
        Identifier)
        :param label: a human readable, well-known, identifier for the namespace
        :param title: a descriptive, formal, name for the namespace
        :param namespace: a globally unique URI for the namespace
        :param server: the identifier of a Server (server_id) the namespace is defined within
        """
        self.id = namespace_id
        self.label = label
        self.title = title
        self.namespace = namespace
        self.relationships: Dict[str, Server] = {}

        if server is not None:
            self.relationships["servers"] = server

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Represents a Namespace as a dictionary

        :return: a Namespace represented as a dictionary
        """
        _namespace: Dict[str, Union[str, Dict[str, str]]] = {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "namespace": self.namespace,
            "relationships": {"servers": self.relationships["servers"].id},
        }

        return _namespace

    def __repr__(self) -> str:
        """
        :return: String representation of a Namespace
        """
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
        namespace: Namespace = None,
    ):
        """
        Repository_id should be defined independently from the repository they are based on (i.e. they should be
        assigned by this project to repositories, rather than read from them, to prevent clashes and loss of integrity)

        Repositories consist of a range of core and optional properties, depending on the technology that underpins it.
        For example data in a PostgreSQL/PostGIS repository sits within a schema of a database, itself within an
        instance (server). The properties, schema, database, server (hostname) are not used for other types of
        repository such as a GeoTiff image.

        Core properties are:
        * repository_id
        * label
        * title
        * repository_type
        * namespace (relation)

        Optional properties are:
        * hostname
        * database
        * schema

        Note: This class requires all properties to be defined (using None for unknown or not-applicable values).
        In future, only core properties will be required, with any relevant optional properties then checked [#29].

        :param repository_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable
        Identifier)
        :param label: a human readable, well-known, identifier for the repository
        :param title: a descriptive, formal, name for the repository
        :param repository_type: the repositories implementation, specified as a member of the RepositoryType enumeration
        :param hostname: the hostname of the remote resource, where the repository represents is a remote resource
        :param database: the name of a database containing repository data, where the repository is a database
        :param schema: the name of a schema containing repository data, where the repository database supports schemas
        :param namespace: the identifier of a Namespace (namespace_id) the repository is defined within
        """
        self.id = repository_id
        self.label = label
        self.title = title
        self.type = RepositoryType(repository_type)
        self.hostname = hostname
        self.database = database
        self.schema = schema
        self.relationships: Dict[str, Namespace] = {}

        if namespace is not None:
            self.relationships["namespaces"] = namespace

    def to_dict(self) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Represents a Repository as a dictionary

        :return: a Repository represented as a dictionary
        """
        _repository = {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "type": self.type.value,
            "hostname": self.hostname,
            "database": self.database,
            "schema": self.schema,
            "relationships": {"namespaces": self.relationships["namespaces"].id},
        }

        return _repository

    def __repr__(self) -> str:
        """
        :return: String representation of a Repository
        """
        return f"Repository <id={self.id}, label={self.label}, type={self.type}>"


class Style:
    """
    Represents a definition for how data in a layer should be represented/presented.

    This can include symbology, labeling and other properties. Styles can be written in a variety of formats, provided
    it's supported by the server.

    Styles belong to a single namespace and can be general, applying to multiple layers, or specific to a single layer.
    """

    def __init__(self, style_id: str, label: str, title: str, style_type: str, namespace: Namespace = None):
        """
        Style_id should be defined independently from the style they are based on (i.e. they should be assigned by this
        project to styles, rather than read from them, to prevent clashes and loss of integrity)

        :param style_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable Identifier)
        :param label: a human readable, well-known, identifier for the style
        :param title: a descriptive, formal, name for the style
        :param style_type: the style implementation, specified as a member of the StyleType enumeration
        :param namespace: the identifier of a Namespace (namespace_id) the repository is defined within
        """
        self.id = style_id
        self.label = label
        self.title = title
        self.type = StyleType(style_type)
        self.relationships: Dict[str, Optional[Namespace]] = {}

        if namespace is not None:
            self.relationships["namespaces"] = namespace

    def to_dict(self) -> Dict[str, Union[str, Dict[str, Optional[str]]]]:
        """
        Represents a Style as a dictionary

        :return: a Repository represented as a dictionary
        """
        _style = {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "type": self.type.value,
            "relationships": {"namespaces": None},
        }
        if "namespaces" in self.relationships and self.relationships["namespaces"] is not None:
            # noinspection PyTypeChecker
            _style["relationships"]["namespaces"] = self.relationships["namespaces"].id

        return _style

    def __repr__(self) -> str:
        """
        :return: String representation of a Style
        """
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
        styles: List[Style] = None,
    ):
        """
        Layer_id should be defined independently from the Layer they are based on (i.e. they should be assigned by this
        project to layers, rather than read from them, to prevent clashes and loss of integrity)

        Layers consist of a range of core and optional properties, depending on the data they represent. For example
        vector data have a geometry type (point, line, etc.). whereas raster data does not.

        Core properties are:
        * layer_id
        * label
        * title
        * layer_type
        * services
        * namespace (relation)
        * repository (relation)
        * styles (relation)

        Optional properties are:
        * geometry_type
        * table_view

        Note: This class requires all properties to be defined (using None for unknown or not-applicable values).
        In future, only core properties will be required, with any relevant optional properties then checked [#29].

        :param layer_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable Identifier)
        :param label: a human readable, well-known, identifier for the layer
        :param title: a descriptive, formal, name for the layer
        :param layer_type: whether the layer represents raster or vector data, specified as a member of the LayerType
        enumeration
        :param geometry_type: the type of vector data, specified as a member of the LayerGeometry enumeration, where the
        layer is vector data
        :param services: OGC services the layer is accessible by, specified as members of the LayerService enumeration
        :param table_view: the name of the table containing layer data, where the layer is based on a database based
        repository
        :param namespace: the identifier of a Namespace the layer is defined within
        :param repository: the identifier of a Repository the layer's data is sourced from
        :param styles: identifiers of styles through which the layer can be presented/represented
        """
        self.id = layer_id
        self.label = label
        self.title = title
        self.type = LayerType(layer_type)
        self.services = []
        self.relationships: Dict[str, Any] = {}

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
            self.relationships["namespaces"] = namespace
        if repository is not None:
            self.relationships["repositories"] = repository
        if styles is not None and isinstance(styles, list):
            self.relationships["styles"] = styles

    def to_dict(self) -> Dict[str, Union[str, Dict[str, Union[str, List[str]]]]]:
        """
        Represents a Layer as a dictionary

        :return: a Layer represented as a dictionary
        """
        _layer = {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "type": self.type.value,
            "geometry": None,
            "services": [],
            "table_view": self.table_view,
            "relationships": {
                "namespaces": self.relationships["namespaces"].id,
                "repositories": self.relationships["repositories"].id,
                "styles": [],
            },
        }
        if self.geometry_type is not None:
            _layer["geometry"] = self.geometry_type.value
        for service in self.services:
            _layer["services"].append(service.value)
        if "styles" in self.relationships:
            for style in self.relationships["styles"]:
                _layer["relationships"]["styles"].append(style.id)

        return _layer

    def __repr__(self) -> str:
        """
        :return: String representation of a Layer
        """
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
        styles: List[Style] = None,
    ):
        """
        Layer_group_id should be defined independently from the LayerGroup they are based on (i.e. they should be
        assigned by this project to layer groups, rather than read from them, to prevent clashes and loss of integrity)

        :param layer_group_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable
        Identifier)
        :param label: a human readable, well-known, identifier for the layer group
        :param title: a descriptive, formal, name for the layer group
        :param geometry_type: the type of vector data, specified as a member of the LayerGeometry enumeration, where the
        layer group contains vector data
        :param services: OGC services the layer group is accessible by, specified as members of the LayerService
        enumeration
        :param namespace: the identifier of a Namespace the layer group is defined within
        :param layers: the identifiers of layers that make up the layer group
        :param styles: identifiers of styles through which the layer group can be presented/represented
        """
        self.id = layer_group_id
        self.label = label
        self.title = title
        self.services = []
        self.relationships: Dict[str, Any] = {}

        self.geometry_type = None
        if geometry_type is not None:
            self.geometry_type = LayerGeometry(geometry_type)

        if services is not None and isinstance(services, list):
            for service in services:
                self.services.append(LayerGroupService(service))

        if namespace is not None:
            self.relationships["namespaces"] = namespace
        if layers is not None and isinstance(layers, list):
            self.relationships["layers"] = layers
        if styles is not None and isinstance(styles, list):
            self.relationships["styles"] = styles

    def to_dict(self) -> Dict[str, Any]:
        """
        Represents a LayerGroup as a dictionary

        :return: a LayerGroup represented as a dictionary
        """
        _layer_group: Dict[str, Any] = {
            "id": self.id,
            "label": self.label,
            "title": self.title,
            "geometry": None,
            "services": [],
            "relationships": {"namespaces": None, "layers": [], "styles": []},
        }

        if self.geometry_type is not None:
            _layer_group["geometry"] = str(self.geometry_type.value)
        for service in self.services:
            _layer_group["services"].append(service.value)

        if "namespaces" in self.relationships and self.relationships["namespaces"] is not None:
            # noinspection PyTypeChecker
            _layer_group["relationships"]["namespaces"] = self.relationships["namespaces"].id
        if "layers" in self.relationships:
            for layer in self.relationships["layers"]:
                _layer_group["relationships"]["layers"].append(layer.id)
        if "styles" in self.relationships:
            for style in self.relationships["styles"]:
                _layer_group["relationships"]["styles"].append(style.id)

        return _layer_group

    def __repr__(self) -> str:
        """
        :return: String representation of a LayerGroup
        """
        return f"LayerGroup <id={self.id}, label={self.label}>"


class Servers(dict):
    """
    Represents a collection of Servers.
    """

    def __init__(self, *args, **kwargs):
        super(Servers, self).__init__(*args, **kwargs)

    def to_list(self) -> List[Dict]:
        """
        Represents a collection of Servers as a list of dictionaries

        :return: a collection of Servers represented as dictionaries
        """
        _servers = []
        for server in self.values():
            _servers.append(server.to_dict())
        return _servers


class Namespaces(dict):
    """
    Represents a collection of Namespaces.
    """

    def __init__(self, *args, **kwargs):
        super(Namespaces, self).__init__(*args, **kwargs)

    def get_by_label(self, label: str) -> Optional[Namespace]:
        """
        Gets a Namespace from a collection of Namespaces identified by a name/label

        Matches are exact and based on labels rather than identifiers.

        :param label: label for a Style

        :return: Matching namespace or None if no matching namespace found
        """
        for item in self.values():
            if item.label == label:
                return item
        return None

    def to_list(self) -> List[Dict]:
        """
        Represents a collection of Namespaces as a list of dictionaries

        :return: a collection of Namespaces represented as dictionaries
        """
        _namespaces = []
        for namespace in self.values():
            _namespaces.append(namespace.to_dict())
        return _namespaces


class Repositories(dict):
    """
    Represents a collection of Repositories.
    """

    def __init__(self, *args, **kwargs):
        super(Repositories, self).__init__(*args, **kwargs)

    def get_by_label(self, label: str) -> Optional[Repository]:
        """
        Gets a Repository from a collection of Repositories identified by a name/label

        Matches are exact and based on labels rather than identifiers.

        :param label: label for a Style

        :return: Matching style or None if no matching repositories found
        """
        for item in self.values():
            if item.label == label:
                return item
        return None

    def to_list(self) -> List[Dict]:
        """
        Represents a collection of Repositories as a list of dictionaries

        :return: a collection of Repositories represented as dictionaries
        """
        _repositories = []
        for repository in self.values():
            _repositories.append(repository.to_dict())
        return _repositories


class Styles(dict):
    """
    Represents a collection of Styles.
    """

    def __init__(self, *args, **kwargs):
        super(Styles, self).__init__(*args, **kwargs)

    def get_by_label(self, label: str, namespace_label: str = None) -> Optional[Style]:
        """
        Gets a Style from a collection of Styles identified by a name/label and, optionally, from within a namespace

        Matches are exact and based on labels rather than identifiers. If a namespace is specified any matching Styles
        must exist within this namespace or no match will be returned.

        :param label: label for a Style
        :param namespace_label: label for a namespace

        :return: Matching style or None if no matching style found
        """
        for item in self.values():
            if item.label == label:
                if namespace_label is None:
                    return item
                else:
                    if item.relationships["namespaces"].label == namespace_label:
                        return item
        return None

    def to_list(self) -> List[Dict]:
        """
        Represents a collection of Styles as a list of dictionaries

        :return: a collection of Styles represented as dictionaries
        """
        _styles = []
        for style in self.values():
            _styles.append(style.to_dict())
        return _styles


class Layers(dict):
    """
    Represents a collection of Layers.
    """

    def __init__(self, *args, **kwargs):
        super(Layers, self).__init__(*args, **kwargs)

    def get_by_label(self, label: str, namespace_label: str = None) -> Optional[Layer]:
        """
        Gets a Layer from a collection of Layers identified by a name/label and, optionally, from within a namespace

        Matches are exact and based on labels rather than identifiers. If a namespace is specified any matching Layers
        must exist within this namespace or no match will be returned.

        :param label: label for a Layer
        :param namespace_label: label for a namespace

        :return: Matching layer or None if no matching layer found
        """
        for item in self.values():
            if item.label == label:
                if namespace_label is None:
                    return item
                else:
                    if item.relationships["namespaces"].label == namespace_label:
                        return item
        return None

    def to_list(self) -> List[Dict]:
        """
        Represents a collection of Layers as a list of dictionaries

        :return: a collection of Layers represented as dictionaries
        """
        _layers = []
        for layer in self.values():
            _layers.append(layer.to_dict())
        return _layers


class LayerGroups(dict):
    """
    Represents a collection of LayerGroups.
    """

    def __init__(self, *args, **kwargs):
        super(LayerGroups, self).__init__(*args, **kwargs)
