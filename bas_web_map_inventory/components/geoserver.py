from enum import Enum
from typing import List, Dict, Tuple, Optional, Union

# noinspection PyPackageRequirements
from geoserver.catalog import Catalog as Catalogue
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService

from bas_web_map_inventory.components import RepositoryType, LayerService, LayerGeometry, Server, ServerType
from bas_web_map_inventory.utils import build_base_data_source_endpoint


class GeoServerRepositoryType(Enum):
    """
    Represents the technology/product a GeoServer repository uses.
    """

    POSTGIS = "postgis"
    GEOTIFF = "geotiff"
    ECW = "ecw"
    JPEG2000 = "jp2ecw"
    IMAGEMOSAIC = "imagemosaic"
    WORLDIMAGE = "worldimage"
    SHAPEFILE = "shapefile"
    SHAPEFILESDIR = "directory of spatial files (shapefiles)"
    ORACLE = "oracle ng"
    GEOGIG = "geogig"


class GeoServerLayerGeometry(Enum):
    """
    Represents a (vector) layer's geometry in GeoServer.
    """

    POINT = "Point"
    LINESTRING = "Linestring"
    POLYGON = "Polygon"
    MULTIPOINT = "MultiPoint"
    MULTILINESTRING = "MultiLinestring"
    MULTIPOLYGON = "MultiPolygon"
    MULTIPOLYGON3D = "3D MultiPolygon"
    GEOMETRYCOLLECTION = "GeometryCollection"


class GeoPropertyGeoServerLayerGeom(Enum):
    """
    Represents a (vector) layer geometry type in GeoServer based on its underlying geometry column

    This enumeration is used where the standard geometry property is not available, see the geometry_property_names
    enumeration for more information.

    This enumeration is a subset of properties from, and mapped to, option in the LayerGeometry enumeration.
    """

    LINESTRING = "CurvePropertyType"
    MULTILINESTRING = "MultiCurvePropertyType"


class GeoServerGeometryColumnNames(Enum):
    """
    Represents common/conventional names for the column in a layers source table/view that holds the geometry.

    Usually this detected by GeoServer and exposed as a 'geometry' property in WFS responses, but in cases where it
    isn't, this list will be used to check the underlying table/view and use that instead. See the
    GeoPropertyGeoServerLayerGeom enum for how values from these conventional columns are mapped to geometry types.
    """

    GEOM = "geom"
    WKBGEOMETRY = "wkb_geometry"
    THEGEOM = "the_geom"


class GeoServer(Server):
    """
    Represents a server running GeoServer [1], an application that provides access to layers.

    This class provides a concrete implementation of the more generic Server component (which is intentionally generic).
    Currently the Server class does not dictate an interface for accessing resources but this class aims to present
    GeoServer specific components (such as workspaces) as generic components (such as namespaces).

    GeoServer instances typically represent individual instances (i.e. hosts are servers) rather than a wider and more
    abstract platform offered by a service provider.

    Information on layers and other resources are fetched using a combination of the GeoServer specific administrative
    API [2] accessed through geoserver-restconfig [3] and OGC services accessed through OWSLib [4] (and currently
    limited to WMS and WFS).

    [1] https://geoserver.readthedocs.io/en/latest/
    [2] https://geoserver.readthedocs.io/en/latest/rest/index.html
    [3] https://pypi.org/project/geoserver-restconfig
    [4] https://pypi.org/project/OWSLib/
    """

    def __init__(
        self,
        server_id: str,
        label: str,
        hostname: str,
        port: str,
        api_path: str,
        wms_path: str,
        wfs_path: str,
        username: str,
        password: str,
    ):
        """
        :param server_id: unique identifier, typically a ULID (Universally Unique Lexicographically Sortable Identifier)
        :param label: a human readable, well-known, identifier for the server - typically based on the hostname
        :param hostname: servers fully qualified hostname
        :param port: port on which GeoServer is running (usually '80' or '8080')
        :param api_path: URL path, relative to the root of the server, to the GeoServer API (usually '/geoserver/rest')
        :param wms_path: URL path, relative to the root of the server, to the GeoServer WMS endpoint (usually
        '/geoserver/ows?service=wms&version=1.3.0&request=GetCapabilities')
        :param wfs_path: URL path, relative to the root of the server, to the GeoServer WFS endpoint (usually
        '/geoserver/ows?service=wfs&version=2.0.0&request=GetCapabilities')
        :param username: username for account to use for GeoServer API
        :param password: password for account to use for GeoServer API
        """
        endpoint = build_base_data_source_endpoint(data_source={"hostname": hostname, "port": port})

        self.client = Catalogue(service_url=f"{endpoint}{api_path}", username=username, password=password)
        self.wms = WebMapService(url=f"{endpoint}{wms_path}", version="1.3.0", username=username, password=password)
        self.wfs = WebFeatureService(url=f"{endpoint}{wfs_path}", version="2.0.0", username=username, password=password)

        super().__init__(
            server_id=server_id,
            label=label,
            hostname=hostname,
            server_type=ServerType.GEOSERVER.value,
            version=self._get_geoserver_version(),
        )

    def get_namespaces(self) -> List[str]:
        """
        Gets all GeoServer workspace names as Namespace labels

        :return: list of Namespace labels
        """
        workspaces = []
        for workspace in self.client.get_workspaces():
            workspaces.append(workspace.name)
        return workspaces

    def get_namespace(self, namespace_reference: str) -> Dict[str, str]:
        """
        Gets a specific workspace as a Namespace

        Note: GeoServer workspaces do not support the concept of a title, a static substitute value is therefore used
        Note: GeoServer workspaces do support the concept of a namespace, but it is not yet implemented [#28]

        :param namespace_reference: Namespace (workspace) label (name)

        :return: dictionary of Namespace information that can be made into a Namespace object
        """
        workspace = self.client.get_workspace(name=namespace_reference)
        if workspace is None:
            raise KeyError(f"Namespace [{namespace_reference}] not found in server [{self.label}]")

        return {"label": workspace.name, "title": "-", "namespace": "-"}

    def get_repositories(self) -> List[Tuple[str, str]]:
        """
        Gets all GeoServer store names as Repository labels

        :return: list of Repository:Namespace label tuples
        """
        stores = []
        # Passing workspaces here is a workaround for a bug in the get stores method where workspaces aren't specified.
        # The method says all workspaces should be checked but the logic to do this is in the wrong place so none are.
        for store in self.client.get_stores(workspaces=self.client.get_workspaces()):
            stores.append((store.name, store.workspace.name))
        return stores

    def get_repository(self, repository_reference: str, namespace_reference: str) -> Dict[str, str]:
        """
        Gets a specific store as a Repository

        If a Namespace (workspace) label is specified the Repository must exist within that Namespace.

        GeoServer store types are sometimes unsuitable or non-standard and so need to be mapped to a conventional value.
        in the RepositoryType enum using the GeoServerRepositoryType enum.

        Note: GeoServer stores do not support the concept of a title, a static substitute value is therefore used
        Note: Names (labels) will be returned for related components instead of identifiers or complete objects [#33]

        :param repository_reference: Repository (store) label (name)
        :param namespace_reference: Namespace (store) label (name)
        :return: dictionary of repository information that can be made into a Repository object
        """
        _store = self.client.get_store(name=repository_reference, workspace=namespace_reference)
        if _store is None:
            raise KeyError(f"Repository [{repository_reference}] not found in server [{self.label}]")

        store = {
            "label": _store.name,
            "title": "-",
            "repository_type": RepositoryType[GeoServerRepositoryType(str(_store.type).lower()).name].value,
            "namespace_label": _store.workspace.name,
        }
        if hasattr(_store, "description") and _store.description is not None:
            store["title"] = _store.description

        if (
            store["repository_type"] == RepositoryType.POSTGIS.value
            or store["repository_type"] == RepositoryType.ORACLE.value
        ):
            store["hostname"] = _store.connection_parameters["host"]
            store["database"] = _store.connection_parameters["database"]
            store["schema"] = _store.connection_parameters["schema"]
        return store

    def get_styles(self) -> List[Tuple[str, Optional[str]]]:
        """
        Gets all GeoServer style names as Style labels

        Python's None value will be used to represent the Namespace of global styles (i.e that don't have a Namespace
        (workspace)).

        :return: list of Style:Namespace label tuples
        """
        styles = []

        for _style in self.client.get_styles():
            styles.append((_style.name, _style.workspace))

        return styles

    def get_style(self, style_reference: str, namespace_reference: str = None) -> Dict[str, str]:
        """
        Gets a specific style as a Style

        If a Namespace (workspace) label is specified the Style must exist within that Namespace.

        Note: GeoServer styles do support the concept of a title, but it is not exposed through the admin API so a
        static substitute value is therefore used
        Note: Names (labels) will be returned for related components instead of identifiers or complete objects [#33]

        :param style_reference: Style (style) label (name)
        :param namespace_reference: Namespace (store) label (name)
        :return: dictionary of style information that can be made into a Style object
        """
        _style = self.client.get_style(name=style_reference, workspace=namespace_reference)

        _type = str(_style.style_format).lower()
        if _type == "sld10":
            _type = "sld"

        style = {
            "label": _style.name,
            "title": "-",
            "style_type": _type,
        }
        if hasattr(_style, "workspace") and _style.workspace is not None:
            style["namespace_label"] = _style.workspace

        return style

    def get_layers(self) -> List[str]:
        """
        Gets all GeoServer layer names as Layer labels

        :return: list of Layer labels
        """
        layers = []

        for _layer in self.client.get_layers():
            layers.append(_layer.name)

        return layers

    def get_layer(
        self, layer_reference: str
    ) -> Dict[str, Union[Optional[str], List[str], List[Tuple[str, Optional[str]]]]]:
        """
        Gets a specific layer as a Layer

        Note: Names (labels) will be returned for related components instead of identifiers or complete objects [#33]

        :param layer_reference: Layer (layer) label (name)
        :return: dictionary of layer information that can be made into a Layer object
        """
        _layer = self.client.get_layer(name=layer_reference)

        layer = {
            "label": _layer.resource.name,
            "title": _layer.resource.title,
            "layer_type": str(_layer.type).lower(),
            "geometry_type": None,
            "services": [],
            "table_view": None,
            "namespace_label": _layer.resource.workspace.name,
            "repository_label": _layer.resource.store.name,
            "style_labels": [(_layer.default_style.name, _layer.default_style.workspace)],
        }

        if layer_reference in list(self.wms.contents) or f"{_layer.resource.workspace.name}:{layer_reference}" in list(
            self.wms.contents
        ):
            layer["services"].append(LayerService.WMS.value)

        if layer_reference in list(self.wfs.contents) or f"{_layer.resource.workspace.name}:{layer_reference}" in list(
            self.wfs.contents
        ):
            layer["services"].append(LayerService.WFS.value)

            # WFS lookups don't seem to mind if the layer is namespaced or not
            _properties = self.wfs.get_schema(layer_reference)
            if "geometry" in _properties and isinstance(_properties["geometry"], str):
                try:
                    layer["geometry_type"] = LayerGeometry[
                        GeoServerLayerGeometry(str(_properties["geometry"])).name
                    ].value
                except ValueError:
                    raise ValueError(
                        f"Geometry [{_properties['geometry']}] for layer {layer_reference} not mapped to "
                        f"LayerGeometry enum."
                    )
            elif "properties" in _properties:
                for geometry_column_name in GeoServerGeometryColumnNames:
                    if geometry_column_name.value in _properties["properties"].keys():
                        try:
                            layer["geometry_type"] = LayerGeometry[
                                GeoPropertyGeoServerLayerGeom(
                                    str(_properties["properties"][geometry_column_name.value])
                                ).name
                            ].value
                        except ValueError:
                            raise ValueError(
                                f"Geometry [{_properties['properties'][geometry_column_name.value]}] for layer "
                                f"{layer_reference} in column '{geometry_column_name.value}' not mapped to "
                                f"LayerGeometry enum."
                            )

        if (
            str(_layer.resource.store.type).lower() == RepositoryType.POSTGIS.value
            or str(_layer.resource.store.type).lower() == RepositoryType.ORACLE.value
        ):
            layer["table_view"] = _layer.resource.native_name

        return layer

    def get_layer_groups(self) -> List[Tuple[str, Optional[str]]]:
        """
        Gets all GeoServer layer group names as LayerGroup labels

        Python's None value will be used to represent the Namespace of global layer groups (i.e that don't have a
        Namespace (workspace)).

        :return: list of LayerGroup:Namespace label tuples
        """
        layer_groups = []

        for _layer_group in self.client.get_layergroups(workspaces=self.client.get_workspaces()):
            layer_groups.append((_layer_group.name, _layer_group.workspace))

        return layer_groups

    def get_layer_group(
        self, layer_group_reference: str, namespace_reference: str
    ) -> Dict[str, Union[Optional[str], List[str], List[Tuple[str, Optional[str]]]]]:
        """
        Gets a specific layer group as a LayerGroup

        If a Namespace (workspace) label is specified the LayerGroup must exist within that Namespace.

        Note: Names (labels) will be returned for related components instead of identifiers or complete objects [#33]

        :param layer_group_reference: LayerGroup (layer group) label (name)
        :param namespace_reference: Namespace (store) label (name)
        :return: dictionary of layer group information that can be made into a LayerGroup object
        """
        _layer_group = self.client.get_layergroup(name=layer_group_reference, workspace=namespace_reference)

        layer_group = {
            "label": _layer_group.name,
            "title": _layer_group.title,
            "services": [],
            "namespace_label": _layer_group.workspace,
            "layer_labels": [],
            "style_labels": [],
        }
        for layer_label in _layer_group.layers:
            layer_label = layer_label.split(":")
            if len(layer_label) == 2:
                layer_group["layer_labels"].append((layer_label[1], layer_label[0]))
            elif len(layer_label) == 1:
                layer_group["layer_labels"].append((layer_label[0], None))

        if f"{namespace_reference}:{layer_group_reference}" in list(self.wms.contents):
            layer_group["services"].append(LayerService.WMS.value)
        if f"{namespace_reference}:{layer_group_reference}" in list(self.wfs.contents):
            layer_group["services"].append(LayerService.WFS.value)
            _properties = self.wfs.get_schema(f"{namespace_reference}:{layer_group_reference}")
            try:
                layer_group["geometry_type"] = LayerGeometry[
                    GeoServerLayerGeometry(str(_properties["geometry"])).name
                ].value
            except ValueError:
                raise ValueError(f"Geometry [{_properties['geometry']}] not mapped to LayerGeometry enum.")

        for style_label in _layer_group.styles:
            if style_label is not None:
                style_label = style_label.split(":")
                if len(style_label) == 2 and (style_label[1], style_label[0]) not in layer_group["style_labels"]:
                    layer_group["style_labels"].append((style_label[1], style_label[0]))
                if len(style_label) == 1 and (style_label[0], None) not in layer_group["style_labels"]:
                    layer_group["style_labels"].append((style_label[0], None))

        return layer_group

    def _get_geoserver_version(self) -> str:
        """
        Gets the GeoServer version

        :return: GeoServer version string
        """
        return self.client.get_version()
