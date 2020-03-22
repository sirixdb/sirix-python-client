import json
import xml.etree.ElementTree as ET

from typing import Union, Dict, Tuple
from .info import AuthData  # for type support

from .constants import Insert, Revision
from .utils import handle_async


class Resource:
    def __init__(self, resource_name: str, parent):
        """database access class
        this class allows for manipulation of a database 

        :param resource_name: the name of the resource being accessed, or to
                be created if the resource does not yet exist
        :param parent: the ``SirixClient`` instance which created this instance
        """
        self._session = parent._session
        self._instance_data = parent._instance_data
        self._auth_data: AuthData = parent._auth_data
        self._asynchronous = parent._asynchronous

        self.database_name = parent.database_name
        self.database_type = parent.database_type
        self.resource_name = resource_name

        self._allow_self_signed = parent._allow_self_signed

    def _init(self, data: Union[str, Dict, ET.Element, None]):
        """
        :param data: the data to initialize the resource with
        """
        database_info = next(
            (db
            for db in self._instance_data.database_info
            if db["name"] == self.database_name)
        )
        if self.resource_name not in database_info.get("resources"):
            if not isinstance(data, str):
                data = (
                    json.dumps(data)
                    if self.database_type == "json"
                    else ET.tostring(data)
                )
            # return create_resource(self, data)

    def _async_init(self, data: Union[str, Dict, ET.Element]):
        database_info = [
            db
            for db in self._instance_data.database_info
            if db["name"] == self.database_name
        ][0]
        # if self.resource_name not in database_info.get("resources"):
            # return handle_async(async_create_resource, self, data,)

    def read(
        self,
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
    ):
        pass
        # if self._asynchronous:
            # return handle_async(async_read_resource, self, revision, node_id, max_level)
        # else:
            # return read_resource(self, revision, node_id, max_level)

    def update(
        self,
        nodeId: int,
        data: Union[str, ET.Element, Dict],
        insert: Insert = Insert.CHILD,
    ):
        """Update a resource

        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        """
        data = (
            data
            if type(data) is str
            else json.dumps(data)
            if self.database_type == "json"
            else ET.tostring(data)
        )
        if (
            self.resource_name
            not in next(
                db
                for db in self._instance_data.database_info
                if db["name"] == self.database_name
            )["resources"]
        ):
            return self._create(data)
        else:
            print(insert.value)
            # if self._asynchronous:
                # return async_update_resource(self, nodeId, data, insert)
            # else:
                # return update_resource(self, nodeId, data, insert.value)

    def delete(self, nodeId: Union[int, None]) -> bool:
        pass
        # if self._asynchronous:
            # return handle_async(async_delete, self, nodeId)
        # else:
            # return delete(self, nodeId)
