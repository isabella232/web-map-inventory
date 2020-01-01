from enum import Enum
from typing import Dict, List, Union, Any, Optional

# noinspection PyPackageRequirements
from airtable import Airtable as _Airtable

from bas_web_map_inventory.components import (
    Server,
    Namespace,
    Repository,
    Style,
    Layer,
    LayerGroup,
    Servers,
    Namespaces,
    Repositories,
    Styles,
    Layers,
    LayerGroups,
)


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

    ItemClass: Any = None
    ItemClassAirtable: Any = None

    def __init__(self, airtable: _Airtable, items, **kwargs):
        """
        :param airtable: upstream Airtable SDK class instance
        :param items: collection of items (layers, repositories, etc.)
        """
        self.airtable = airtable
        self.kwargs = kwargs

        self.items_local: Dict[str, Any] = {}
        self.items_airtable: Dict[str, Any] = {}

        self.airtable_ids_to_ids: Dict[str, str] = {}

        self.missing: List[str] = []
        self.current: List[str] = []
        self.outdated: List[str] = []
        self.orphaned: List[str] = []

        if items is not None:
            for item in items.values():
                self.items_local[item.id] = self.ItemClassAirtable(item=item, **self.kwargs)

        self.stat()

    def stat(self) -> None:
        """
        Calculates the state of a set of local items compared to items stored in an Airtable table

        Items can be in one of four states:
        1. missing - item exists locally but not in Airtable
        2. current - item exists both locally and in Airtable and are both the same
        3. outdated -  item exists both locally and in Airtable but the local version is different to Airtble
        4. orphaned - item does not exist locally but does in Airtable

        The identifier of each item (e.g. layer identifier) is added to a list per state.
        """
        self.items_airtable = {}

        self.missing = []
        self.current = []
        self.outdated = []
        self.orphaned = []

        for airtable_item in self.airtable.get_all():
            item_id = airtable_item["fields"]["ID"]
            try:
                item = self.ItemClassAirtable(item=airtable_item, **self.kwargs)
                self.items_airtable[item.id] = item

                # try to add Airtable ID to corresponding local item, if missing assume item is orphaned
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
        """
        Gets a local item by its identifier

        :param item_id: identifier for a local item

        :return: local item with identifier
        """
        return self.items_local[item_id]

    def get_by_airtable_id(self, item_airtable_id: str):
        """
        Gets an local item by its corresponding Airtable (i.e. foreign) identifier

        :param item_airtable_id: Airtable native identifier for a local item

        :return: local item with corresponding Airtable native identifier
        """
        return self.items_local[self.airtable_ids_to_ids[item_airtable_id]]

    def load(self) -> None:
        """
        Import any missing local items into Airtable

        The Airtable SDK's batch insert method is used to automatically comply with Airtable's rate limiting.
        """
        _items = []
        for missing_id in self.missing:
            _items.append(self.items_local[missing_id].airtable_fields())
        self.airtable.batch_insert(records=_items)

    def sync(self) -> None:
        """
        Updates Airtable items that are outdated (i.e. properties of local items have changed) or orphaned (i.e. local
        items that no longer exist)

        The Airtable SDK's batch delete method is used for orphaned items to automatically comply with Airtable's rate
        limiting.
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
        Removes all Airtable items

        This method is largely intended for testing purposes.

        The Airtable SDK's batch delete method is used for orphaned items to automatically comply with Airtable's rate
        limiting.
        """
        _ids = []
        for item in self.items_airtable.values():
            _ids.append(item.airtable_id)
        self.airtable.batch_delete(record_ids=_ids)

    def status(self) -> Dict[str, List[str]]:
        """
        Outputs the state of a set of local items compared to items stored in an Airtable table

        Item identifiers are organised by state (see the stat() method for possible states).

        :return: identifiers of items organised by state
        """
        self.stat()

        return {"current": self.current, "outdated": self.outdated, "missing": self.missing, "orphaned": self.orphaned}


class ServerTypeAirtable(Enum):
    """
    Represents the technology/product a server uses in Airtable.
    """

    GEOSERVER = "GeoServer"


class RepositoryTypeAirtable(Enum):
    """
    Represents the technology/product a repository uses in Airtable.
    """

    POSTGIS = "PostGIS"
    GEOTIFF = "GeoTiff"
    ECW = "ECW"
    JPEG2000 = "JPEG2000"
    IMAGEMOSAIC = "Image Mosaic"
    WORLDIMAGE = "World Image"


class StyleTypeAirtable(Enum):
    """
    Represents the format a style is written in, in Airtable.
    """

    SLD = "SLD"


class LayerTypeAirtable(Enum):
    """
    Represents a layer's fundamental data type (raster or vector) in Airtable.
    """

    RASTER = "Raster"
    VECTOR = "Vector"


class LayerGeometryAirtable(Enum):
    """
    Represents a (vector) layer's geometry in Airtable.
    """

    POINT = "Point"
    LINESTRING = "Linestring"
    POLYGON = "Polygon"
    MULTIPOINT = "Multi-Point"
    MULTILINESTRING = "Multi-Linestring"
    MULTIPOLYGON = "Multi-Polygon"


class LayerServiceAirtable(Enum):
    """
    Represents which OGC services a layer can be accessed with in Airtable.
    """

    WMS = "WMS"
    WMTS = "WMTS"
    WCS = "WCS"
    WFS = "WFS"


class LayerGroupServiceAirtable(Enum):
    """
    Represents which OGC services a layer group can be accessed with in Airtable.
    """

    WMS = "WMS"
    WMTS = "WMTS"
    WCS = "WCS"
    WFS = "WFS"


class ServerAirtable:
    """
    Wrapper around the generic Server class to represent Servers in Airtable.

    See 'Airtable' class for general information.
    """

    # noinspection PyUnusedLocal
    def __init__(self, item: Union[Server, dict], **kwargs):
        """
        :param item: a (local) Server object or a (remote) Airtable representation of a Server object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.hostname: str
        self.type: ServerTypeAirtable
        self.version: str

        if isinstance(item, Server):
            self.id = item.id
            self.name = item.label
            self.hostname = item.hostname
            self.type = ServerTypeAirtable[item.type.name]
            self.version = item.version
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.hostname = item["fields"]["Hostname"]
            self.type = ServerTypeAirtable(item["fields"]["Type"])
            self.version = item["fields"]["Version"]
        else:
            raise TypeError("Item must be a dict or Server object")

    def airtable_fields(self) -> Dict[str, str]:
        """
        Translates a Server's properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID').

        :return: a Server as Airtable fields
        """
        return {
            "ID": self.id,
            "Name": self.name,
            "Hostname": self.hostname,
            "Type": str(self.type.value),
            "Version": self.version,
        }

    def _dict(self) -> Dict[str, str]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a Server's internal properties
        """
        return {
            "id": self.id,
            "name": self.name,
            "hostname": self.hostname,
            "type": self.type.value,
            "version": self.version,
        }

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable Server
        """
        return f"Server(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}, type={self.type}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable Server is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class NamespaceAirtable:
    """
    Wrapper around the generic Namespace class to represent Namespaces in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Namespace, dict], **kwargs):
        """
        :param item: a (local) Namespace object or a (remote) Airtable representation of a Namespace object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.title: str
        self.server: ServerAirtable

        if "servers_airtable" not in kwargs:
            raise RuntimeError("ServersAirtable collection not included as keyword argument.")

        if isinstance(item, Namespace):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.server = kwargs["servers_airtable"].get_by_id(item.relationships["servers"].id)
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.title = item["fields"]["Title"]

            if "Server" in item["fields"]:
                try:
                    self.server = kwargs["servers_airtable"].get_by_airtable_id(item["fields"]["Server"][0])
                except KeyError:
                    raise KeyError(f"Server with Airtable ID [{item['fields']['Server'][0]}] not found.")
        else:
            raise TypeError("Item must be a dict or Namespace object")

    def airtable_fields(self) -> Dict[str, Union[str, List[Optional[str]]]]:
        """
        Translates a Namespace's properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID') and related objects linked by
        Airtable identifiers.

        :return: a Namespace as Airtable fields
        """
        return {"ID": self.id, "Name": self.name, "Title": self.title, "Server": [self.server.airtable_id]}

    def _dict(self) -> Dict[str, str]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a Namespace's internal properties
        """
        return {"id": self.id, "name": self.name, "title": self.title, "server": self.server.id}

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable Namespace
        """
        return f"Namespace(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable Namespace is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class RepositoryAirtable:
    """
    Wrapper around the generic Repository class to represent Repositories in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Repository, dict], **kwargs):
        """
        :param item: a (local) Repository object or a (remote) Airtable representation of a Repository object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.title: str
        self.type: RepositoryTypeAirtable
        self.host: Optional[str]
        self.database: Optional[str]
        self.schema: Optional[str]
        self.workspace: NamespaceAirtable

        if "namespaces_airtable" not in kwargs:
            raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")

        if isinstance(item, Repository):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.type = RepositoryTypeAirtable[item.type.name]
            self.host = item.hostname
            self.database = item.database
            self.schema = item.schema
            self.workspace = kwargs["namespaces_airtable"].get_by_id(item.relationships["namespaces"].id)
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.title = item["fields"]["Title"]
            self.type = RepositoryTypeAirtable(item["fields"]["Type"])

            if "Host" in item["fields"]:
                self.host = item["fields"]["Host"]
            if "Database" in item["fields"]:
                self.database = item["fields"]["Database"]
            if "Schema" in item["fields"]:
                self.schema = item["fields"]["Schema"]

            if "Workspace" in item["fields"]:
                try:
                    self.workspace = kwargs["namespaces_airtable"].get_by_airtable_id(item["fields"]["Workspace"][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
        else:
            raise TypeError("Item must be a dict or Repository object")

    def airtable_fields(self) -> Dict[str, Union[Optional[str], List[Optional[str]]]]:
        """
        Translates a Repositories properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID') and related objects linked by
        Airtable identifiers.

        :return: a Repository as Airtable fields
        """
        return {
            "ID": self.id,
            "Name": self.name,
            "Title": self.title,
            "Type": self.type.value,
            "Host": self.host,
            "Database": self.database,
            "Schema": self.schema,
            "Workspace": [self.workspace.airtable_id],
        }

    def _dict(self) -> Dict[str, Union[Optional[str], List[Optional[str]]]]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a Repositories internal properties
        """
        return {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "type": self.type.value,
            "host": self.host,
            "database": self.database,
            "schema": self.schema,
            "workspace": [self.workspace.airtable_id],
        }

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable Repository
        """
        return f"Repository(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable Repository is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class StyleAirtable:
    """
    Wrapper around the generic Style class to represent Styles in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Style, dict], **kwargs):
        """
        :param item: a (local) Style object or a (remote) Airtable representation of a Style object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.title: str
        self.type: StyleTypeAirtable
        self.workspace: NamespaceAirtable

        if "namespaces_airtable" not in kwargs:
            raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")

        if isinstance(item, Style):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            self.type = StyleTypeAirtable[item.type.name]
            if item.relationships["namespaces"] is not None:
                self.workspace = kwargs["namespaces_airtable"].get_by_id(item.relationships["namespaces"].id)
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.title = item["fields"]["Title"]
            self.type = StyleTypeAirtable(item["fields"]["Type"])

            if "Workspace" in item["fields"]:
                try:
                    self.workspace = kwargs["namespaces_airtable"].get_by_airtable_id(item["fields"]["Workspace"][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
        else:
            raise TypeError("Item must be a dict or Style object")

    def airtable_fields(self) -> Dict[str, Union[str, List[str]]]:
        """
        Translates a Style's properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID') and related objects linked by
        Airtable identifiers.

        :return: a Style as Airtable fields
        """
        _fields = {
            "ID": self.id,
            "Name": self.name,
            "Title": self.title,
            "Type": self.type.value,
        }
        if self.workspace is not None:
            _fields["Workspace"] = [self.workspace.airtable_id]

        return _fields

    def _dict(self) -> Dict[str, Union[str, List[str]]]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a Style's internal properties
        """
        _dict = {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "type": self.type.value,
        }
        if self.workspace is not None:
            _dict["namespace"] = [self.workspace.airtable_id]

        return _dict

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable Style
        """
        return f"Style(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable Style is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class LayerAirtable:
    """
    Wrapper around the generic Layer class to represent Layers in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[Layer, dict], **kwargs):
        """
        :param item: a (local) Layer object or a (remote) Airtable representation of a Layer object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.title: str
        self.type: LayerTypeAirtable
        self.geometry: LayerGeometryAirtable
        self.services: List[LayerServiceAirtable] = []
        self.table_view: str
        self.workspace: NamespaceAirtable
        self.store: RepositoryAirtable
        self.styles: List[StyleAirtable] = []

        if "namespaces_airtable" not in kwargs:
            raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
        if "repositories_airtable" not in kwargs:
            raise RuntimeError("RepositoriesAirtable collection not included as keyword argument.")
        if "styles_airtable" not in kwargs:
            raise RuntimeError("StylesAirtable collection not included as keyword argument.")

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
            self.workspace = kwargs["namespaces_airtable"].get_by_id(item.relationships["namespaces"].id)
            self.store = kwargs["repositories_airtable"].get_by_id(item.relationships["repositories"].id)
            for style_id in item.relationships["styles"]:
                self.styles.append(kwargs["styles_airtable"].get_by_id(style_id.id))
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.title = item["fields"]["Title"]
            self.type = LayerTypeAirtable(item["fields"]["Type"])

            if "Geometry" in item["fields"]:
                self.geometry = LayerGeometryAirtable(item["fields"]["Geometry"])
            if "Services" in item["fields"]:
                for service in item["fields"]["Services"]:
                    self.services.append(LayerServiceAirtable(service))
            if "Table/View" in item["fields"]:
                self.table_view = item["fields"]["Table/View"]

            if "Workspace" in item["fields"]:
                try:
                    self.workspace = kwargs["namespaces_airtable"].get_by_airtable_id(item["fields"]["Workspace"][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
            if "Store" in item["fields"]:
                try:
                    self.store = kwargs["repositories_airtable"].get_by_airtable_id(item["fields"]["Store"][0])
                except KeyError:
                    raise KeyError(f"Repository with Airtable ID [{item['fields']['Store'][0]}] not found.")
            if "Styles" in item["fields"]:
                for style_id in item["fields"]["Styles"]:
                    try:
                        self.styles.append(kwargs["styles_airtable"].get_by_airtable_id(style_id))
                    except KeyError:
                        raise KeyError(f"Style with Airtable ID [{style_id}] not found.")
        else:
            raise TypeError("Item must be a dict or Layer object")

    def airtable_fields(self) -> Dict[str, Union[str, List[str]]]:
        """
        Translates a Layer's properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID') and related objects linked by
        Airtable identifiers.

        :return: a Layer as Airtable fields
        """
        _services = []
        for service in self.services:
            _services.append(service.value)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        _fields = {
            "ID": self.id,
            "Name": self.name,
            "Title": self.title,
            "Type": self.type.value,
            "Geometry": None,
            "Services": _services,
            "Table/View": self.table_view,
            "Workspace": [self.workspace.airtable_id],
            "Store": [self.store.airtable_id],
            "Styles": _styles,
        }
        if self.geometry is not None:
            _fields["Geometry"] = self.geometry.value

        return _fields

    def _dict(self) -> Dict[str, Union[str, List[str]]]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a Layer's internal properties
        """
        _services = []
        for service in self.services:
            _services.append(service.value)
        _styles = []
        for style in self.styles:
            _styles.append(style.airtable_id)
        _dict = {
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "type": self.type.value,
            "geometry": None,
            "services": _services,
            "table-view": self.table_view,
            "workspace": [self.workspace.airtable_id],
            "store": [self.store.airtable_id],
            "styles": _styles,
        }
        if self.geometry is not None:
            _dict["geometry"] = self.geometry.value

        return _dict

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable Layer
        """
        return f"Layer(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable Layer is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class LayerGroupAirtable:
    """
    Wrapper around the generic LayerGroup class to represent LayerGroups in Airtable.

    See 'Airtable' class for general information.
    """

    def __init__(self, item: Union[LayerGroup, dict], **kwargs):
        """
        :param item: a (local) LayerGroup object or a (remote) Airtable representation of a LayerGroup object
        """
        self.airtable_id: Optional[str] = None
        self.id: str
        self.name: str
        self.title: str
        self.services: List[LayerGroupServiceAirtable] = []
        self.workspace: NamespaceAirtable
        self.layers: List[LayerAirtable] = []
        self.styles: List[StyleAirtable] = []

        if "namespaces_airtable" not in kwargs:
            raise RuntimeError("NamespacesAirtable collection not included as keyword argument.")
        if "layers_airtable" not in kwargs:
            raise RuntimeError("LayersAirtable collection not included as keyword argument.")
        if "styles_airtable" not in kwargs:
            raise RuntimeError("StylesAirtable collection not included as keyword argument.")

        if isinstance(item, LayerGroup):
            self.id = item.id
            self.name = item.label
            self.title = item.title
            for service in item.services:
                self.services.append(LayerGroupServiceAirtable[service.name])
            if item.relationships["namespaces"] is not None:
                self.workspace = kwargs["namespaces_airtable"].get_by_id(item.relationships["namespaces"].id)
            for layer in item.relationships["layers"]:
                self.layers.append(kwargs["layers_airtable"].get_by_id(layer.id))
            for style in item.relationships["styles"]:
                self.styles.append(kwargs["styles_airtable"].get_by_id(style.id))
        elif isinstance(item, dict):
            self.airtable_id = item["id"]
            self.id = item["fields"]["ID"]
            self.name = item["fields"]["Name"]
            self.title = item["fields"]["Title"]

            if "Services" in item["fields"]:
                for service in item["fields"]["Services"]:
                    self.services.append(LayerGroupServiceAirtable(service))
            if "Workspace" in item["fields"]:
                try:
                    self.workspace = kwargs["namespaces_airtable"].get_by_airtable_id(item["fields"]["Workspace"][0])
                except KeyError:
                    raise KeyError(f"Namespace with Airtable ID [{item['fields']['Workspace'][0]}] not found.")
            if "Layers" in item["fields"]:
                for layer in item["fields"]["Layers"]:
                    try:
                        self.layers.append(kwargs["layers_airtable"].get_by_airtable_id(layer))
                    except KeyError:
                        raise KeyError(f"Layer with Airtable ID [{layer}] not found.")
            if "Styles" in item["fields"]:
                for style_id in item["fields"]["Styles"]:
                    try:
                        self.styles.append(kwargs["styles_airtable"].get_by_airtable_id(style_id))
                    except KeyError:
                        raise KeyError(f"Style with Airtable ID [{style_id}] not found.")
        else:
            raise TypeError("Item must be a dict or LayerGroup object")

    def airtable_fields(self) -> Dict[str, Union[str, List[Optional[str]]]]:
        """
        Translates a LayerGroup's properties to Airtable fields

        This includes mapping property names to Airtable versions (e.g. 'id' to 'ID') and related objects linked by
        Airtable identifiers.

        :return: a LayerGroup as Airtable fields
        """
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
            "ID": self.id,
            "Name": self.name,
            "Title": self.title,
            "Services": _services,
            "Workspace": [self.workspace.airtable_id],
            "Layers": _layers,
            "Styles": _styles,
        }

    def _dict(self) -> Dict[str, Union[str, List[Optional[str]]]]:
        """
        Outputs an item's internal properties as a dictionary

        Internal properties are properties that relate directly to the resource, rather than properties assigned to
        the resource by external entities (such as an Airtable ID).

        This method is intended to prevent false positives when checking if an item has changed and needs updating.

        :return: a LayerGroup's internal properties
        """
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
            "id": self.id,
            "name": self.name,
            "title": self.title,
            "services": _services,
            "workspace": [self.workspace.airtable_id],
            "layers": _layers,
            "styles": _styles,
        }

    def __repr__(self) -> str:
        """
        :return: String representation of an Airtable LayerGroup
        """
        return f"LayerGroup(Airtable) <id={self.id}, airtable_id={self.airtable_id}, name={self.name}>"

    def __eq__(self, other) -> bool:
        """
        Used to determine if an item is materially different to another (in terms of properties specific to the resource
        rather than metadata). Typically used to determine if an item needs to be updated when comparing a local item
        against an Airtable counterpart.

        :return: Whether an Airtable LayerGroup is effectively equal to another
        """
        # noinspection PyProtectedMember
        return self._dict() == other._dict()


class ServersAirtable(Airtable):
    """
    Represents a collection of servers in Airtable.
    """

    ItemClass = Server
    ItemClassAirtable = ServerAirtable

    def __init__(self, airtable: _Airtable, servers: Servers, **kwargs):
        """
        :param airtable: upstream Airtable SDK class instance
        :param servers: collection of Server items
        """
        super().__init__(airtable=airtable, items=servers, **kwargs)


class NamespacesAirtable(Airtable):
    """
    Represents a collection of namespaces in Airtable.
    """

    ItemClass = Namespace
    ItemClassAirtable = NamespaceAirtable

    def __init__(self, airtable: _Airtable, namespaces: Namespaces, servers_airtable: ServersAirtable, **kwargs):
        """
        :param airtable: upstream Airtable SDK class instance
        :param servers: collection of Namespace items
        :param servers_airtable: collection of Airtable Server items for relating namespaces to servers
        """
        kwargs["servers_airtable"] = servers_airtable
        super().__init__(airtable=airtable, items=namespaces, **kwargs)


class RepositoriesAirtable(Airtable):
    """
    Represents a collection of repositories in Airtable.
    """

    ItemClass = Repository
    ItemClassAirtable = RepositoryAirtable

    def __init__(
        self, airtable: _Airtable, repositories: Repositories, namespaces_airtable: NamespacesAirtable, **kwargs
    ):
        """
        :param airtable: upstream Airtable SDK class instance
        :param repositories: collection of Repository items
        :param namespaces_airtable: collection of Airtable Namespace items for relating repositories to namespaces
        """
        kwargs["namespaces_airtable"] = namespaces_airtable
        super().__init__(airtable=airtable, items=repositories, **kwargs)


class StylesAirtable(Airtable):
    """
    Represents a collection of styles in Airtable.
    """

    ItemClass = Style
    ItemClassAirtable = StyleAirtable

    def __init__(self, airtable: _Airtable, styles: Styles, namespaces_airtable: NamespacesAirtable, **kwargs):
        """
        :param airtable: upstream Airtable SDK class instance
        :param styles: collection of Style items
        :param namespaces_airtable: collection of Airtable Namespace items for relating styles to namespaces
        """
        kwargs["namespaces_airtable"] = namespaces_airtable
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
        **kwargs,
    ):
        """
        :param airtable: upstream Airtable SDK class instance
        :param repositories: collection of Layer items
        :param namespaces_airtable: collection of Airtable Namespace items for relating layers to namespaces
        :param repositories_airtable: collection of Airtable Repository items for relating layers to repositories
        :param styles_airtable: collection of Airtable Style items for relating layers to styles
        """
        kwargs["namespaces_airtable"] = namespaces_airtable
        kwargs["repositories_airtable"] = repositories_airtable
        kwargs["styles_airtable"] = styles_airtable
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
        **kwargs,
    ):
        """
        :param airtable: upstream Airtable SDK class instance
        :param repositories: collection of LayerGroup items
        :param namespaces_airtable: collection of Airtable Namespace items for relating layer groups to namespaces
        :param styles_airtable: collection of Airtable Style items for relating layer groups to styles
        :param layers_airtable: collection of Airtable Layer items for relating layer groups to layers
        """
        kwargs["namespaces_airtable"] = namespaces_airtable
        kwargs["styles_airtable"] = styles_airtable
        kwargs["layers_airtable"] = layers_airtable
        super().__init__(airtable=airtable, items=layer_groups, **kwargs)
