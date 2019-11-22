import json
import os

# noinspection PyPackageRequirements
import ulid

from enum import Enum
from pathlib import Path
from typing import List, Union, Dict, Optional, Tuple

from flask import Flask
from flask.cli import AppGroup
# noinspection PyPackageRequirements
from click import echo, confirm, style as click_style, option, Path as ClickPath
# noinspection PyPackageRequirements
from airtable import Airtable as _Airtable
# noinspection PyPackageRequirements
from geoserver.catalog import Catalog as Catalogue
from owslib.wfs import WebFeatureService
from owslib.wms import WebMapService

from map_layer_index.config import config


# Generic objects
#


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
        isolated: bool,
        server: Server = None
    ):
        self.id = namespace_id
        self.label = label
        self.title = title
        self.namespace = namespace
        self.isolated = isolated
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
            'isolated': self.isolated,
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
        return f"Namespace <id={self.id}, label={self.label}, type={self.type}>"


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
            'services': [],
            'relationships': {
                'namespaces': None,
                'layers': [],
                'styles': []
            }
        }

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

    def to_list(self) -> List[Dict]:
        _layer_groups = []
        for layer_group in self.values():
            _layer_groups.append(layer_group.to_dict())
        return _layer_groups


# GeoServer specific objects
#


class GeoServer(Server):
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
            password: str
    ):
        protocol = 'http'
        if port == '443':
            protocol = 'https'

        self.client = Catalogue(
            service_url=f"{protocol}://{hostname}:{port}{api_path}",
            username=username,
            password=password
        )
        self.wms = WebMapService(
            url=f"{protocol}://{hostname}:{port}{wms_path}",
            version='1.3.0',
            username=username,
            password=password
        )
        self.wfs = WebFeatureService(
            url=f"{protocol}://{hostname}:{port}{wfs_path}",
            version='2.0.0',
            username=username,
            password=password
        )

        super().__init__(
            server_id=server_id,
            label=label,
            hostname=hostname,
            server_type=ServerType.GEOSERVER.value,
            version=self._get_geoserver_version()
        )

    def get_namespaces(self) -> List[str]:
        workspaces = []
        for workspace in self.client.get_workspaces():
            workspaces.append(workspace.name)
        return workspaces

    def get_namespace(self, namespace_reference: str) -> Dict[str, str]:
        workspace = self.client.get_workspace(name=namespace_reference)
        if workspace is None:
            raise KeyError(f"Namespace [{namespace_reference}] not found in server [{self.label}]")

        return {
            'label': workspace.name,
            'title': '-',
            'namespace': '-'
        }

    def get_repositories(self) -> List[Tuple[str, str]]:
        stores = []
        # Passing workspaces here is a workaround for a bug in the get stores method where workspaces aren't specified.
        # The method says all workspaces should be checked but the logic to do this is in the wrong place so none are.
        for store in self.client.get_stores(workspaces=self.client.get_workspaces()):
            stores.append((store.name, store.workspace.name))
        return stores

    def get_repository(self, repository_reference: str, namespace_reference: str) -> Dict[str, str]:
        _store = self.client.get_store(name=repository_reference, workspace=namespace_reference)
        if _store is None:
            raise KeyError(f"Repository [{repository_reference}] not found in server [{self.label}]")

        store = {
            'label': _store.name,
            'title': '-',
            'repository_type': str(_store.type).lower(),
            'namespace_label': _store.workspace.name
        }
        if hasattr(store, 'description'):
            store['title'] = _store.description
        if store['repository_type'] == 'postgis':
            store['hostname'] = _store.connection_parameters['host']
            store['database'] = _store.connection_parameters['database']
            store['schema'] = _store.connection_parameters['schema']
        return store

    def get_styles(self) -> List[Tuple[str, Optional[str]]]:
        styles = []

        for _style in self.client.get_styles():
            styles.append((_style.name, _style.workspace))

        return styles

    def get_style(self, style_reference: str, namespace_reference: str = None) -> Dict[str, str]:
        _style = self.client.get_style(name=style_reference, workspace=namespace_reference)

        _type = str(_style.style_format).lower()
        if _type == 'sld10':
            _type = 'sld'

        style = {
            'label': _style.name,
            'title': '-',
            'style_type': _type,
        }
        if hasattr(_style, 'workspace') and _style.workspace is not None:
            style['namespace_label'] = _style.workspace

        return style

    def get_layers(self) -> List[str]:
        layers = []

        for _layer in self.client.get_layers():
            layers.append(_layer.name)

        return layers

    def get_layer(self, layer_reference: str) -> Dict[
            str, Union[Optional[str], List[str], List[Tuple[str, Optional[str]]]]]:
        _layer = self.client.get_layer(name=layer_reference)

        layer = {
            'label': _layer.resource.name,
            'title': _layer.resource.title,
            'layer_type': str(_layer.type).lower(),
            'geometry_type': None,
            'services': [],
            'table_view': None,
            'namespace_label': _layer.resource.workspace.name,
            'repository_label': _layer.resource.store.name,
            'style_labels': [(_layer.default_style.name, _layer.default_style.workspace)]
        }

        if layer_reference in list(self.wms.contents):
            # noinspection PyTypeChecker
            layer['services'].append(LayerService.WMS.value)
        if layer_reference in list(self.wfs.contents):
            # noinspection PyTypeChecker
            layer['services'].append(LayerService.WFS.value)
            _properties = self.wfs.get_schema(layer_reference)
            if _properties['geometry'].lower() == 'point':
                layer['geometry_type'] = LayerGeometry.POINT.value
            else:
                raise ValueError(f"Geometry type: [{_properties['geometry']}] not mapped to LayerGeometry enum.")

        if str(_layer.resource.store.type).lower() == 'postgis':
            layer['table_view'] = _layer.resource.native_name

        for style in _layer.styles:
            layer['style_labels'].append((style.name, style.workspace))

        return layer

    def get_layer_groups(self) -> List[Tuple[str, Optional[str]]]:
        layer_groups = []

        for _layer_group in self.client.get_layergroups(workspaces=self.client.get_workspaces()):
            layer_groups.append((_layer_group.name, _layer_group.workspace))

        return layer_groups

    def get_layer_group(self, layer_group_reference: str, namespace_reference: str) -> Dict[
            str, Union[Optional[str], List[str], List[Tuple[str, Optional[str]]]]]:
        _layer_group = self.client.get_layergroup(name=layer_group_reference, workspace=namespace_reference)

        layer_group = {
            'label': _layer_group.name,
            'title': _layer_group.title,
            "services": [],
            'namespace_label': _layer_group.workspace,
            'layer_labels': [],
            'style_labels': []
        }
        for layer_label in _layer_group.layers:
            layer_label = layer_label.split(':')
            if len(layer_label) == 2:
                layer_group['layer_labels'].append((layer_label[1], layer_label[0]))
            elif len(layer_label) == 1:
                layer_group['layer_labels'].append((layer_label[0], None))

        if f"{namespace_reference}:{layer_group_reference}" in list(self.wms.contents):
            # noinspection PyTypeChecker
            layer_group['services'].append(LayerService.WMS.value)
        if f"{namespace_reference}:{layer_group_reference}" in list(self.wfs.contents):
            # noinspection PyTypeChecker
            layer_group['services'].append(LayerService.WFS.value)
            _properties = self.wfs.get_schema(layer_group_reference)
            if _properties['geometry'].lower() == 'point':
                layer_group['geometry_type'] = LayerGeometry.POINT.value
            else:
                raise ValueError(f"Geometry type: [{_properties['geometry']}] not mapped to LayerGeometry enum.")

        for style_label in _layer_group.styles:
            style_label = style_label.split(':')
            if len(style_label) == 2:
                layer_group['style_labels'].append((style_label[1], style_label[0]))
            if len(style_label) == 1:
                layer_group['style_labels'].append((style_label[0], None))

        return layer_group

    def _get_geoserver_version(self) -> str:
        return self.client.get_version()


# Airtable specific objects
#


class Airtable:
    """
    Base class for interacting with Airtable representations of inventory components.

    The goal of this class is to enable a one-way sync of items of a given type (e.g. Layers) with an Airtable table.

    This class uses Airtable versions of inventory classes (i.e. he Airtable Layer class wraps around the Layer class).
    These sub-classes add Airtable specific properties (such as the Airtable ID) and methods for coercing Airtable's
    representation of a component into the inventory classes (e.g. converting a dict representing a layer into a
    structured Layer class).

    Crucially the ID property (our ID, not the Airtable ID) is used to link local and remote instances of an item.

    This class uses collections of these classes (local, built from generic classes and remote taken from Airtable's
    API) to enable syncing. Methods are provided to read/create/update/delete items in Airtable as needed as well as to
    determine:
    * which items are out of date or missing in Airtable
    * which items are now orphaned as they've been removed locally
    """
    ItemClass = None
    ItemClassAirtable = None

    def __init__(self, airtable: _Airtable, items, **kwargs):
        self.airtable = airtable
        self.kwargs = kwargs

        self.items_local = {}
        self.items_airtable = {}

        self.airtable_ids_to_ids = {}

        self.missing = []
        self.current = []
        self.outdated = []
        self.orphaned = []

        if items is not None:
            for item in items.values():
                self.items_local[item.id] = self.ItemClassAirtable(item=item, **self.kwargs)

        self.stat()

    def stat(self) -> None:
        self.items_airtable = {}

        self.missing = []
        self.current = []
        self.outdated = []
        self.orphaned = []

        for airtable_item in self.airtable.get_all():
            item_id = airtable_item['fields']['ID']
            try:
                item = self.ItemClassAirtable(item=airtable_item, **self.kwargs)
                self.items_airtable[item.id] = item

                # try to add Airtable ID to corresponding local item
                self.items_local[item.id].airtable_id = item.airtable_id
                self.airtable_ids_to_ids[item.airtable_id] = item.id
            except KeyError:
                self.orphaned.append(item_id)
                continue

        for item in self.items_local.values():
            try:
                if item != self.items_airtable[item.id]:
                    self.outdated.append(item.id)
                    continue

                self.current.append(item.id)
            except KeyError:
                self.missing.append(item.id)
                continue

    def get_by_id(self, item_id: str):
        return self.items_local[item_id]

    def get_by_airtable_id(self, item_airtable_id: str):
        return self.items_local[self.airtable_ids_to_ids[item_airtable_id]]

    def load(self) -> None:
        """
        """
        _items = []
        for missing_id in self.missing:
            _items.append(self.items_local[missing_id].airtable_fields())
        self.airtable.batch_insert(records=_items)

    def sync(self) -> None:
        """
        """
        self.load()

        for outdated_id in self.outdated:
            item = self.items_local[outdated_id]
            self.airtable.update(record_id=item.airtable_id, fields=item.airtable_fields())

        _ids = []
        for orphaned_id in self.orphaned:
            _ids.append(self.items_airtable[orphaned_id].airtable_id)
        self.airtable.batch_delete(record_ids=_ids)

    def reset(self) -> None:
        """
        """
        _ids = []
        for item in self.items_airtable.values():
            _ids.append(item.airtable_id)
        self.airtable.batch_delete(record_ids=_ids)

    def status(self) -> Dict[str, List[str]]:
        self.stat()

        return {
            'current': self.current,
            'outdated': self.outdated,
            'missing': self.missing,
            'orphaned': self.orphaned
        }


class ServerTypeAirtable(Enum):
    """
    Represents the technology/product a server uses in Airtable.
    """
    GEOSERVER = 'GeoServer'


class RepositoryTypeAirtable(Enum):
    """
    Represents the technology/product a repository uses in Airtable.
    """

    POSTGIS = 'PostGIS'
    GEOTIFF = 'GeoTiff'
    ECW = 'ECW'
    JPEG2000 = 'JPEG2000'
    IMAGEMOSAIC = 'Image Mosaic'
    WORLDIMAGE = 'World Image'


class StyleTypeAirtable(Enum):
    """
    Represents the format a style is written in, in Airtable.
    """
    SLD = 'SLD'


class LayerTypeAirtable(Enum):
    """
    Represents a layer's fundamental data type (raster or vector) in Airtable.
    """
    RASTER = 'Raster'
    VECTOR = 'Vector'


class LayerGeometryAirtable(Enum):
    """
    Represents a (vector) layer's geometry in Airtable.
    """
    POINT = 'Point'
    LINESTRING = 'Linestring'
    POLYGON = 'Polygon'
    MULTIPOINT = 'Multi-Point'
    MULTILINESTRING = 'Multi-Linestring'
    MULTIPOLYGON = 'Multi-Polygon'


class LayerServiceAirtable(Enum):
    """
    Represents which OGC services a layer can be accessed with in Airtable.
    """
    WMS = 'WMS'
    WMTS = 'WMTS'
    WCS = 'WCS'
    WFS = 'WFS'


class LayerGroupServiceAirtable(Enum):
    """
    Represents which OGC services a layer group can be accessed with in Airtable.
    """
    WMS = 'WMS'
    WMTS = 'WMTS'
    WCS = 'WCS'
    WFS = 'WFS'


class ServerAirtable:
    """
    Wrapper around the generic Server class to represent Servers in Airtable.

    See 'Airtable' class for general information.
    """

    # noinspection PyUnusedLocal
    def __init__(self, item: Union[Server, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.hostname = None
        self.type = None
        self.version = None

        if isinstance(item, Server):
            self.id = item.id
            self.name = item.label
            self.hostname = item.hostname
            self.type = ServerTypeAirtable[item.type.name]
            self.version = item.version
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.hostname = item['fields']['Hostname']
            self.type = ServerTypeAirtable(item['fields']['Type'])
            self.version = item['fields']['Version']
        else:
            TypeError("Item must be a dict or Server object")

    def airtable_fields(self) -> dict:
        return {
            'ID': self.id,
            'Name': self.name,
            'Hostname': self.hostname,
            'Type': self.type.value,
            'Version': self.version
        }

    def _dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'hostname': self.hostname,
            'type': self.type,
            'version': self.version
        }

    def __repr__(self):
        return f"Server(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}, type={self.type}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class NamespaceAirtable:
    """
    Wrapper around the generic Namespace class to represent Namespaces in Airtable.

    See 'Airtable' class for general information.
    """
    def __init__(self, item: Union[Namespace, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.title = None
        self.isolated = None
        self.server = None

        if isinstance(item, Namespace):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.isolated = item.isolated
            self.server = kwargs['servers_airtable'].get_by_id(item.relationships['servers'].id)
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.title = item['fields']['Title']
            self.isolated = False

            if 'Isolated' in item['fields'] and item['fields']['Isolated'] is True:
                self.isolated = True

            if 'Server' in item['fields']:
                if 'servers_airtable' not in kwargs:
                    raise RuntimeError("ServersAirtable collection not included as keyword argument.")
                try:
                    self.server = kwargs['servers_airtable'].get_by_airtable_id(item['fields']['Server'][0])
                except KeyError:
                    raise KeyError(f"Server with Airtable ID [{item['fields']['Server'][0]}] not found.")
        else:
            TypeError("Item must be a dict or Namespace object")

    def airtable_fields(self) -> dict:
        return {
            'ID': self.id,
            'Name': self.name,
            'Title': self.title,
            'Isolated': self.isolated,
            'Server': [self.server.airtable_id]
        }

    def _dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'isolated': self.isolated,
            'server': self.server
        }

    def __repr__(self):
        return f"Namespace(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class RepositoryAirtable:
    """
    Wrapper around the generic Repository class to represent Repositories in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Repository, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.title = None
        self.type = None
        self.host = None
        self.database = None
        self.schema = None
        self.workspace = None

        if isinstance(item, Repository):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.type = RepositoryTypeAirtable[item.type.name]
            self.host = item.hostname
            self.database = item.database
            self.schema = item.schema
            self.workspace = kwargs['namespaces_airtable'].get_by_id(item.relationships['namespaces'].id)
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.title = item['fields']['Title']
            self.type = RepositoryTypeAirtable(item['fields']['Type'])

            if 'Host' in item['fields']:
                self.host = item['fields']['Host']
            if 'Database' in item['fields']:
                self.database = item['fields']['Database']
            if 'Schema' in item['fields']:
                self.schema = item['fields']['Schema']

            if 'Workspace' in item['fields']:
                if 'namespaces_airtable' not in kwargs:
                    raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
                try:
                    self.workspace = kwargs['namespaces_airtable'].get_by_airtable_id(item['fields']['Workspace'][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
        else:
            TypeError("Item must be a dict or Repository object")

    def airtable_fields(self) -> dict:
        return {
            'ID': self.id,
            'Name': self.name,
            'Title': self.title,
            'Type': self.type.value,
            'Host': self.host,
            'Database': self.database,
            'Schema': self.schema,
            'Workspace': [self.workspace.airtable_id]
        }

    def _dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'type': self.type.value,
            'host': self.host,
            'database': self.database,
            'schema': self.schema,
            'workspace': [self.workspace.airtable_id]
        }

    def __repr__(self):
        return f"Repository(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class StyleAirtable:
    """
    Wrapper around the generic Style class to represent Styles in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Style, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.title = None
        self.type = None
        self.workspace = None

        if isinstance(item, Style):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.type = StyleTypeAirtable[item.type.name]
            if item.relationships['namespaces'] is not None:
                self.workspace = kwargs['namespaces_airtable'].get_by_id(item.relationships['namespaces'].id)
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.title = item['fields']['Title']
            self.type = StyleTypeAirtable(item['fields']['Type'])

            if 'Workspace' in item['fields']:
                if 'namespaces_airtable' not in kwargs:
                    raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
                try:
                    self.workspace = kwargs['namespaces_airtable'].get_by_airtable_id(item['fields']['Workspace'][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
        else:
            TypeError("Item must be a dict or Style object")

    def airtable_fields(self) -> dict:
        _fields = {
            'ID': self.id,
            'Name': self.name,
            'Title': self.title,
            'Type': self.type.value,
        }
        if self.workspace is not None:
            _fields['Workspace'] = [self.workspace.airtable_id]

        return _fields

    def _dict(self) -> dict:
        _dict = {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'type': self.type.value,
        }
        if self.workspace is not None:
            _dict['namespace'] = [self.workspace.airtable_id]

        return _dict

    def __repr__(self):
        return f"Style(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class LayerAirtable:
    """
    Wrapper around the generic Layer class to represent Layers in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Layer, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.title = None
        self.type = None
        self.geometry = None
        self.services = []
        self.table_view = None
        self.workspace = None
        self.store = None
        self.styles = []

        if isinstance(item, Layer):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.type = LayerTypeAirtable[item.type.name]
            if item.geometry_type is not None:
                self.geometry = LayerGeometryAirtable[item.geometry_type.name]
            for service in item.services:
                self.services.append(LayerServiceAirtable[service.name])
            if item.table_view is not None:
                self.table_view = item.table_view
            self.workspace = kwargs['namespaces_airtable'].get_by_id(item.relationships['namespaces'].id)
            self.store = kwargs['repositories_airtable'].get_by_id(item.relationships['repositories'].id)
            for style_id in item.relationships['styles']:
                self.styles.append(kwargs['styles_airtable'].get_by_id(style_id.id))
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.title = item['fields']['Title']
            self.type = LayerTypeAirtable(item['fields']['Type'])

            if 'Geometry' in item['fields']:
                self.geometry = LayerGeometryAirtable(item['fields']['Geometry'])
            if 'Services' in item['fields']:
                for service in item['fields']['Services']:
                    self.services.append(LayerServiceAirtable(service))
            if 'Table/View' in item['fields']:
                self.table_view = item['fields']['Table/View']

            if 'Workspace' in item['fields']:
                if 'namespaces_airtable' not in kwargs:
                    raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
                try:
                    self.workspace = kwargs['namespaces_airtable'].get_by_airtable_id(item['fields']['Workspace'][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
            if 'Store' in item['fields']:
                if 'repositories_airtable' not in kwargs:
                    raise RuntimeError("RepositoriesAirtable collection not included as keyword argument.")
                try:
                    self.store = kwargs['repositories_airtable'].get_by_airtable_id(item['fields']['Store'][0])
                except KeyError:
                    raise KeyError(f"Repository with Airtable ID [{item['fields']['Store'][0]}] not found.")
            if 'Styles' in item['fields']:
                if 'styles_airtable' not in kwargs:
                    raise RuntimeError("StylesAirtable collection not included as keyword argument.")
                for style_id in item['fields']['Styles']:
                    try:
                        self.styles.append(kwargs['styles_airtable'].get_by_airtable_id(style_id))
                    except KeyError:
                        raise KeyError(f"Style with Airtable ID [{style_id}] not found.")
        else:
            TypeError("Item must be a dict or Layer object")

    def airtable_fields(self) -> dict:
        _services = []
        for service in self.services:
            _services.append(service.value)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        _fields = {
            'ID': self.id,
            'Name': self.name,
            'Title': self.title,
            'Type': self.type.value,
            'Geometry': None,
            'Services': _services,
            'Table/View': self.table_view,
            'Workspace': [self.workspace.airtable_id],
            'Store': [self.store.airtable_id],
            'Styles': _styles
        }
        if self.geometry is not None:
            _fields['Geometry'] = self.geometry.value

        return _fields

    def _dict(self) -> dict:
        _services = []
        for service in self.services:
            _services.append(service.value)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        _dict = {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'type': self.type.value,
            'geometry': None,
            'services': _services,
            'table-view': self.table_view,
            'workspace': [self.workspace.airtable_id],
            'store': [self.store.airtable_id],
            'styles': _styles
        }
        if self.geometry is not None:
            _dict['geometry'] = self.geometry.value

        return _dict

    def __repr__(self):
        return f"Layer(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class LayerGroupAirtable:
    """
    Wrapper around the generic LayerGroup class to represent LayerGroups in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[LayerGroup, dict], **kwargs):
        self.airtable_id = None
        self.id = None
        self.name = None
        self.title = None
        self.services = []
        self.workspace = None
        self.layers = []
        self.styles = []

        if isinstance(item, LayerGroup):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            for service in item.services:
                self.services.append(LayerGroupServiceAirtable[service.name])
            if item.relationships['namespaces'] is not None:
                self.workspace = kwargs['namespaces_airtable'].get_by_id(item.relationships['namespaces'].id)
            for layer in item.relationships['layers']:
                self.layers.append(kwargs['layers_airtable'].get_by_id(layer.id))
            for style in item.relationships['styles']:
                self.styles.append(kwargs['styles_airtable'].get_by_id(style.id))
        elif isinstance(item, dict):
            self.airtable_id = item['id']
            self.id = item['fields']['ID']
            self.name = item['fields']['Name']
            self.title = item['fields']['Title']

            if 'Services' in item['fields']:
                for service in item['fields']['Services']:
                    self.services.append(LayerGroupServiceAirtable(service))
            if 'Workspace' in item['fields']:
                if 'namespaces_airtable' not in kwargs:
                    raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
                try:
                    self.workspace = kwargs['namespaces_airtable'].get_by_airtable_id(item['fields']['Workspace'][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
            if 'Layers' in item['fields']:
                if 'layers_airtable' not in kwargs:
                    raise RuntimeError("LayersAirtable collection not included as keyword argument.")
                for layer in item['fields']['Layers']:
                    try:
                        self.layers.append(kwargs['layers_airtable'].get_by_airtable_id(layer))
                    except KeyError:
                        raise KeyError(f"Layer with Airtable ID [{layer}] not found.")
            if 'Styles' in item['fields']:
                if 'styles_airtable' not in kwargs:
                    raise RuntimeError("StylesAirtable collection not included as keyword argument.")
                for style_id in item['fields']['Styles']:
                    try:
                        self.styles.append(kwargs['styles_airtable'].get_by_airtable_id(style_id))
                    except KeyError:
                        raise KeyError(f"Style with Airtable ID [{style_id}] not found.")
        else:
            TypeError("Item must be a dict or LayerGroup object")

    def airtable_fields(self) -> dict:
        _services = []
        for service in self.services:
            _services.append(service.value)
        _layers = []
        for layer in self.layers:
            _layers.append(layer.airtable_id)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        return {
            'ID': self.id,
            'Name': self.name,
            'Title': self.title,
            'Services': _services,
            'Workspace': [self.workspace.airtable_id],
            'Layers': _layers,
            'Styles': _styles
        }

    def _dict(self) -> dict:
        _services = []
        for service in self.services:
            _services.append(service.value)
        _layers = []
        for layer in self.layers:
            _layers.append(layer.airtable_id)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        return {
            'id': self.id,
            'name': self.name,
            'title': self.title,
            'services': _services,
            'workspace': [self.workspace.airtable_id],
            'layers': _layers,
            'styles': _styles
        }

    def __repr__(self):
        return f"LayerGroup(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other):
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class ServersAirtable(Airtable):
    """
    Represents a collection of servers in Airtable.
    """
    ItemClass = Server
    ItemClassAirtable = ServerAirtable

    def __init__(self, airtable: _Airtable, servers: Servers, **kwargs):
        super().__init__(airtable=airtable, items=servers, **kwargs)


class NamespacesAirtable(Airtable):
    """
    Represents a collection of namespaces in Airtable.
    """
    ItemClass = Namespace
    ItemClassAirtable = NamespaceAirtable

    def __init__(
        self,
        airtable: _Airtable,
        namespaces: Namespaces,
        servers_airtable: ServersAirtable,
        **kwargs
    ):
        kwargs['servers_airtable'] = servers_airtable
        super().__init__(airtable=airtable, items=namespaces, **kwargs)


class RepositoriesAirtable(Airtable):
    """
    Represents a collection of repositories in Airtable.
    """
    ItemClass = Repository
    ItemClassAirtable = RepositoryAirtable

    def __init__(
        self,
        airtable: _Airtable,
        repositories: Repositories,
        namespaces_airtable: NamespacesAirtable,
        **kwargs
    ):
        kwargs['namespaces_airtable'] = namespaces_airtable
        super().__init__(airtable=airtable, items=repositories, **kwargs)


class StylesAirtable(Airtable):
    """
    Represents a collection of styles in Airtable.
    """
    ItemClass = Style
    ItemClassAirtable = StyleAirtable

    def __init__(
        self,
        airtable: _Airtable,
        styles: Styles,
        namespaces_airtable: NamespacesAirtable,
        **kwargs
    ):
        kwargs['namespaces_airtable'] = namespaces_airtable
        super().__init__(airtable=airtable, items=styles, **kwargs)


class LayersAirtable(Airtable):
    """
    Represents a collection of layers in Airtable.
    """
    ItemClass = Layer
    ItemClassAirtable = LayerAirtable

    def __init__(
        self,
        airtable: _Airtable,
        layers: Layers,
        namespaces_airtable: NamespacesAirtable,
        repositories_airtable: RepositoriesAirtable,
        styles_airtable: StylesAirtable,
        **kwargs
    ):
        kwargs['namespaces_airtable'] = namespaces_airtable
        kwargs['repositories_airtable'] = repositories_airtable
        kwargs['styles_airtable'] = styles_airtable
        super().__init__(airtable=airtable, items=layers, **kwargs)


class LayerGroupsAirtable(Airtable):
    """
    Represents a collection of layer groups in Airtable.
    """
    ItemClass = LayerGroup
    ItemClassAirtable = LayerGroupAirtable

    def __init__(
        self,
        airtable: _Airtable,
        layer_groups: LayerGroups,
        namespaces_airtable: NamespacesAirtable,
        styles_airtable: StylesAirtable,
        layers_airtable: LayersAirtable,
        **kwargs
    ):
        kwargs['namespaces_airtable'] = namespaces_airtable
        kwargs['styles_airtable'] = styles_airtable
        kwargs['layers_airtable'] = layers_airtable
        super().__init__(airtable=airtable, items=layer_groups, **kwargs)


# App
#


def create_app(env: str = None):
    app = Flask(__name__)

    if env is None:
        env = os.getenv('FLASK_ENV') or 'default'
    _config = config[env]
    app.config.from_object(_config)
    _config.init_app(app)

    if 'LOGGING_LEVEL' in app.config:
        app.logger.setLevel(app.config['LOGGING_LEVEL'])

    data_cli_group = AppGroup('data', help='Interact with data sources.')
    app.cli.add_command(data_cli_group)
    airtable_cli_group = AppGroup('airtable', help='Interact with Airtable service.')
    app.cli.add_command(airtable_cli_group)

    def _load_data() -> None:
        app.logger.info('Loading data...')

        with open(Path('resources/data.json'), 'r') as data_file:
            _data = data_file.read()
        data = json.loads(_data)

        servers = Servers()
        for server in data['servers']:
            server = Server(
                server_id=server['id'],
                label=server['label'],
                hostname=server['hostname'],
                server_type=server['type'],
                version=server['version']
            )
            servers[server.id] = server

        namespaces = Namespaces()
        for namespace in data['namespaces']:
            namespace = Namespace(
                namespace_id=namespace['id'],
                label=namespace['label'],
                title=namespace['title'],
                namespace=namespace['namespace'],
                isolated=namespace['isolated'],
                server=servers[namespace['relationships']['servers']]
            )
            namespaces[namespace.id] = namespace

        repositories = Repositories()
        for repository in data['repositories']:
            repository = Repository(
                repository_id=repository['id'],
                label=repository['label'],
                title=repository['title'],
                repository_type=repository['type'],
                hostname=repository['hostname'],
                database=repository['database'],
                schema=repository['schema'],
                namespace=namespaces[repository['relationships']['namespaces']]
            )
            repositories[repository.id] = repository

        styles = Styles()
        for style in data['styles']:
            _namespace = None
            if style['relationships']['namespaces'] is not None:
                _namespace = namespaces[style['relationships']['namespaces']]
            style = Style(
                style_id=style['id'],
                label=style['label'],
                title=style['title'],
                style_type=style['type'],
                namespace=_namespace
            )
            styles[style.id] = style

        layers = Layers()
        for layer in data['layers']:
            _styles = []
            for style_id in layer['relationships']['styles']:
                _styles.append(styles[style_id])
            layer = Layer(
                layer_id=layer['id'],
                label=layer['label'],
                title=layer['title'],
                layer_type=layer['type'],
                geometry_type=layer['geometry'],
                services=layer['services'],
                table_view=layer['table_view'],
                namespace=namespaces[layer['relationships']['namespaces']],
                repository=repositories[layer['relationships']['repositories']],
                styles=_styles
            )
            layers[layer.id] = layer

        layer_groups = LayerGroups()
        for layer_group in data['layer-groups']:
            _namespace = None
            if layer_group['relationships']['namespaces'] is not None:
                _namespace = namespaces[layer_group['relationships']['namespaces']]
            _layers = []
            for layer_id in layer_group['relationships']['layers']:
                _layers.append(layers[layer_id])
            _styles = []
            for style_id in layer_group['relationships']['styles']:
                _styles.append(styles[style_id])
            layer_group = LayerGroup(
                layer_group_id=layer_group['id'],
                label=layer_group['label'],
                title=layer_group['title'],
                services=layer_group['services'],
                namespace=_namespace,
                layers=_layers,
                styles=_styles
            )
            layer_groups[layer_group.id] = layer_group

        app.config['data'] = {
            'servers': servers,
            'namespaces': namespaces,
            'repositories': repositories,
            'styles': styles,
            'layers': layers,
            'layer_groups': layer_groups
        }

    def _setup_airtable() -> None:
        app.logger.info('Loading Airtable data...')

        _servers_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Servers'
        )
        servers_airtable = ServersAirtable(
            airtable=_servers_airtable,
            servers=app.config['data']['servers']
        )

        _namespaces_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Workspaces'
        )
        namespaces_airtable = NamespacesAirtable(
            airtable=_namespaces_airtable,
            namespaces=app.config['data']['namespaces'],
            servers_airtable=servers_airtable
        )

        _repositories_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Stores'
        )
        repositories_airtable = RepositoriesAirtable(
            airtable=_repositories_airtable,
            repositories=app.config['data']['repositories'],
            namespaces_airtable=namespaces_airtable
        )

        _styles_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Styles'
        )
        styles_airtable = StylesAirtable(
            airtable=_styles_airtable,
            styles=app.config['data']['styles'],
            namespaces_airtable=namespaces_airtable
        )

        _layers_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Layers'
        )
        layers_airtable = LayersAirtable(
            airtable=_layers_airtable,
            layers=app.config['data']['layers'],
            namespaces_airtable=namespaces_airtable,
            repositories_airtable=repositories_airtable,
            styles_airtable=styles_airtable
        )

        _layer_groups_airtable = _Airtable(
            base_key=app.config['AIRTABLE_BASE_ID'],
            api_key=app.config['AIRTABLE_API_KEY'],
            table_name='Layer Groups'
        )
        layer_groups_airtable = LayerGroupsAirtable(
            airtable=_layer_groups_airtable,
            layer_groups=app.config['data']['layer_groups'],
            namespaces_airtable=namespaces_airtable,
            styles_airtable=styles_airtable,
            layers_airtable=layers_airtable
        )

        app.config['airtable'] = {
            'servers': servers_airtable,
            'namespaces': namespaces_airtable,
            'repositories': repositories_airtable,
            'styles': styles_airtable,
            'layers': layers_airtable,
            'layer_groups': layer_groups_airtable
        }

    @data_cli_group.command('fetch')
    @option(
        '-s',
        '--data-sources-file-path',
        default='resources/sources.json',
        show_default=True,
        type=ClickPath(exists=True)
    )
    @option(
        '-d',
        '--data-output-file-path',
        default='resources/data.json',
        show_default=True,
        type=ClickPath()
    )
    def fetch(data_sources_file_path: str, data_output_file_path):
        """Fetch data from data sources into a data file"""
        app.config['data'] = {}

        echo(f"loading sources from {click_style(data_sources_file_path, fg='blue')}")
        echo("")
        with open(Path(data_sources_file_path), 'r') as data_sources_file:
            data_sources_data = data_sources_file.read()
        data_sources = json.loads(data_sources_data)

        echo(f"Fetching {click_style('Servers', fg='cyan')}:")
        servers = Servers()
        for server_config in data_sources['servers']:
            if server_config['type'] == 'geoserver':
                server = GeoServer(
                    server_id=server_config['id'],
                    label=server_config['label'],
                    hostname=server_config['hostname'],
                    port=server_config['port'],
                    api_path=server_config['api-path'],
                    wfs_path=server_config['wfs-path'],
                    wms_path=server_config['wms-path'],
                    username=server_config['username'],
                    password=server_config['password']
                )
                servers[server.id] = server
        app.config['data']['servers'] = servers
        echo(f"* fetched {click_style(str(len(servers)), fg='blue')} servers (total)")

        server_namespaces = {}
        for server in servers.values():
            server_namespaces[server.id] = []
            if isinstance(server, GeoServer):
                for namespace in server.get_namespaces():
                    server_namespaces[server.id].append(server.get_namespace(namespace_reference=namespace))

        namespaces = Namespaces()
        for server_id, _namespaces in server_namespaces.items():
            echo(f"Fetching {click_style('Namespaces', fg='cyan')} in "
                 f"{click_style(servers[server_id].label, fg='magenta')}:")
            for namespace in _namespaces:
                namespace = Namespace(
                    namespace_id=ulid.new().str,
                    label=namespace['label'],
                    title=namespace['title'],
                    namespace=namespace['namespace'],
                    isolated=False,
                    server=servers[server_id]
                )
                namespaces[namespace.id] = namespace
            echo(f"* fetched {click_style(str(len(_namespaces)), fg='blue')} namespaces for "
                 f"{click_style(servers[server_id].label, fg='magenta')}")
        app.config['data']['namespaces'] = namespaces
        echo(f"* fetched {click_style(str(len(namespaces)), fg='blue')} namespaces (total)")

        repositories = Repositories()
        for server in servers.values():
            _repositories_server_count = 0
            echo(f"Fetching {click_style('Repositories', fg='cyan')} in {click_style(server.label, fg='magenta')}:")
            for _repository in server.get_repositories():
                _repositories_server_count += 1
                _repository = server.get_repository(
                    repository_reference=_repository[0], namespace_reference=_repository[1])
                _repository['repository_id'] = ulid.new().str
                _repository['namespace'] = namespaces.get_by_label(label=_repository['namespace_label'])
                del(_repository['namespace_label'])
                repository = Repository(**_repository)
                repositories[repository.id] = repository
            echo(f"* fetched {click_style(str(_repositories_server_count), fg='blue')} repositories for "
                 f"{click_style(server.label, fg='magenta')}")
        app.config['data']['repositories'] = repositories
        echo(f"* fetched {click_style(str(len(repositories)), fg='blue')} repositories (total)")

        styles = Styles()
        for server in servers.values():
            _styles_server_count = 0
            echo(f"Fetching {click_style('Styles', fg='cyan')} in {click_style(server.label, fg='magenta')}:")
            for _style in server.get_styles():
                _styles_server_count += 1
                _style = server.get_style(style_reference=_style[0], namespace_reference=_style[1])
                _style['style_id'] = ulid.new().str
                if 'namespace_label' in _style:
                    _style['namespace'] = namespaces.get_by_label(label=_style['namespace_label'])
                    del(_style['namespace_label'])
                style = Style(**_style)
                styles[style.id] = style
            echo(f"* fetched {click_style(str(_styles_server_count), fg='blue')} styles for "
                 f"{click_style(server.label, fg='magenta')}")
        app.config['data']['styles'] = styles
        echo(f"* fetched {click_style(str(len(styles)), fg='blue')} styles (total)")

        layers = Layers()
        for server in servers.values():
            _layers_server_count = 0
            echo(f"Fetching {click_style('Layers', fg='cyan')} in {click_style(server.label, fg='magenta')}:")
            for _layer in server.get_layers():
                _layers_server_count += 1
                _layer = server.get_layer(layer_reference=_layer)
                _layer['layer_id'] = ulid.new().str
                _layer['namespace'] = namespaces.get_by_label(label=_layer['namespace_label'])
                _layer['repository'] = repositories.get_by_label(label=_layer['repository_label'])
                _layer['styles'] = []
                for _style_label in _layer['style_labels']:
                    _layer['styles'].append(styles.get_by_label(label=_style_label[0], namespace_label=_style_label[1]))
                del _layer['namespace_label']
                del _layer['repository_label']
                del _layer['style_labels']
                layer = Layer(**_layer)
                layers[layer.id] = layer
            echo(f"* fetched {click_style(str(_layers_server_count), fg='blue')} layers for "
                 f"{click_style(server.label, fg='magenta')}")
        app.config['data']['layers'] = layers
        echo(f"* fetched {click_style(str(len(layers)), fg='blue')} layers (total)")

        layer_groups = Layers()
        for server in servers.values():
            _layer_groups_server_count = 0
            echo(f"Fetching {click_style('Layer Groups', fg='cyan')} in {click_style(server.label, fg='magenta')}:")
            for _layer_group in server.get_layer_groups():
                _layer_groups_server_count += 1
                _layer_group = server.get_layer_group(
                    layer_group_reference=_layer_group[0],
                    namespace_reference=_layer_group[1]
                )
                _layer_group['layer_group_id'] = ulid.new().str
                _layer_group['namespace'] = namespaces.get_by_label(label=_layer_group['namespace_label'])
                _layer_group['layers'] = []
                for _layer_label in _layer_group['layer_labels']:
                    _layer_group['layers'].append(layers.get_by_label(
                        label=_layer_label[0], namespace_label=_layer_label[1]))
                _layer_group['styles'] = []
                for _style_label in _layer_group['style_labels']:
                    _layer_group['styles'].append(styles.get_by_label(
                        label=_style_label[0], namespace_label=_style_label[1]))
                del _layer_group['namespace_label']
                del _layer_group['layer_labels']
                del _layer_group['style_labels']
                layer_group = LayerGroup(**_layer_group)
                layer_groups[layer_group.id] = layer_group
            echo(f"* fetched {click_style(str(_layer_groups_server_count), fg='blue')} layer groups for "
                 f"{click_style(server.label, fg='magenta')}")
        app.config['data']['layer_groups'] = layer_groups
        echo(f"* fetched {click_style(str(len(layer_groups)), fg='blue')} layer groups (total)")

        echo(f"")
        echo(f"Saving fetched data to {click_style(data_output_file_path, fg='blue')}")
        _data = {
            'servers': servers.to_list(),
            'namespaces': namespaces.to_list(),
            'repositories': repositories.to_list(),
            'styles': styles.to_list(),
            'layers': layers.to_list(),
            'layer-groups': layer_groups.to_list()
        }
        with open(Path(data_output_file_path), 'w') as data_file:
            json.dump(_data, data_file, indent=4)
        echo(click_style('Fetch complete', fg='green'))

    @airtable_cli_group.command('status')
    def status():
        """Get status of all components in Airtable."""
        if 'data' not in app.config:
            _load_data()
        if 'airtable' not in app.config:
            _setup_airtable()

        _global_status = {
            'current': 0,
            'outdated': 0,
            'missing': 0,
            'orphaned': 0
        }

        echo(f"Getting status for {click_style('Servers', fg='cyan')}:")
        _status = app.config['airtable']['servers'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)
        echo(f"Getting status for {click_style('Namespaces (Workspaces)', fg='cyan')}:")
        _status = app.config['airtable']['namespaces'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)
        echo(f"Getting status for {click_style('Repositories (Stores)', fg='cyan')}:")
        _status = app.config['airtable']['repositories'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)
        echo(f"Getting status for {click_style('Styles', fg='cyan')}:")
        _status = app.config['airtable']['styles'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)
        echo(f"Getting status for {click_style('Layers', fg='cyan')}:")
        _status = app.config['airtable']['layers'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)
        echo(f"Getting status for {click_style('Layer Groups', fg='cyan')}:")
        _status = app.config['airtable']['layer_groups'].status()
        _global_status['current'] += len(_status['current'])
        _global_status['outdated'] += len(_status['outdated'])
        _global_status['missing'] += len(_status['missing'])
        _global_status['orphaned'] += len(_status['orphaned'])
        echo(f"* current: {click_style(str(len(_status['current'])), fg='blue')}")
        echo(f"* outdated: {click_style(str(len(_status['outdated'])), fg='blue')}")
        echo(f"* missing: {click_style(str(len(_status['missing'])), fg='blue')}")
        echo(f"* orphaned: {click_style(str(len(_status['orphaned'])), fg='blue')}")
        echo(_status)

        echo('')
        echo('Status summary:')
        echo(f"* current (total): {click_style(str(_global_status['current']), fg='blue')}")
        echo(f"* outdated (total): {click_style(str(_global_status['outdated']), fg='blue')}")
        echo(f"* missing (total): {click_style(str(_global_status['missing']), fg='blue')}")
        echo(f"* orphaned (total): {click_style(str(_global_status['orphaned']), fg='blue')}")
        echo(click_style('Status complete', fg='green'))

    @airtable_cli_group.command('sync')
    def sync():
        """Sync all components with Airtable."""
        if 'data' not in app.config:
            _load_data()
        if 'airtable' not in app.config:
            _setup_airtable()

        echo(f"Syncing {click_style('Servers', fg='yellow')}:")
        echo(app.config['airtable']['servers'].status())
        app.config['airtable']['servers'].sync()
        echo(app.config['airtable']['servers'].status())
        echo(f"Syncing {click_style('Namespaces (Workspaces)', fg='yellow')}:")
        echo(app.config['airtable']['namespaces'].status())
        app.config['airtable']['namespaces'].sync()
        echo(app.config['airtable']['namespaces'].status())
        echo(f"Syncing {click_style('Repositories (Stores)', fg='yellow')}:")
        echo(app.config['airtable']['repositories'].status())
        app.config['airtable']['repositories'].sync()
        echo(app.config['airtable']['repositories'].status())
        echo(f"Syncing {click_style('Styles', fg='yellow')}:")
        echo(app.config['airtable']['styles'].status())
        app.config['airtable']['styles'].sync()
        echo(app.config['airtable']['styles'].status())
        echo(f"Syncing {click_style('Layers', fg='yellow')}:")
        echo(app.config['airtable']['layers'].status())
        app.config['airtable']['layers'].sync()
        echo(app.config['airtable']['layers'].status())
        echo(f"Syncing {click_style('Layer Groups', fg='yellow')}:")
        echo(app.config['airtable']['layer_groups'].status())
        app.config['airtable']['layer_groups'].sync()
        echo(app.config['airtable']['layer_groups'].status())

    @airtable_cli_group.command('reset')
    def reset():
        """Reset all Airtable data."""
        confirm('Do you really want to continue? All Airtable data will be reset', abort=True)

        if 'data' not in app.config:
            _load_data()
        if 'airtable' not in app.config:
            _setup_airtable()

        echo(f"Resetting {click_style('Servers', fg='red')}:")
        app.config['airtable']['servers'].reset()
        echo(app.config['airtable']['servers_airtable'].status())
        echo(f"Resetting {click_style('Namespaces (Workspaces)', fg='red')}:")
        app.config['airtable']['namespaces'].reset()
        echo(app.config['airtable']['namespaces_airtable'].status())
        echo(f"Resetting {click_style('Repositories (Stores)', fg='red')}:")
        app.config['airtable']['repositories'].reset()
        echo(app.config['airtable']['repositories_airtable'].status())
        echo(f"Resetting {click_style('Styles', fg='red')}:")
        app.config['airtable']['styles'].reset()
        echo(app.config['airtable']['styles_airtable'].status())
        echo(f"Resetting {click_style('Layers', fg='red')}:")
        app.config['airtable']['layers'].reset()
        echo(app.config['airtable']['layers_airtable'].status())
        echo(f"Resetting {click_style('Layer Groups', fg='red')}:")
        app.config['airtable']['layer_groups'].reset()
        echo(app.config['airtable']['layer_groups_airtable'].status())

    return app
