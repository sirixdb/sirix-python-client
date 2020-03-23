import json
import xml.etree.ElementTree as ET
from datetime import datetime

from typing import Union, Dict, Tuple

from pysirix.constants import Insert, Revision, DBType

from pysirix.sync_client import SyncClient
from pysirix.async_client import AsyncClient


class Resource:
    def __init__(
        self,
        db_name: str,
        db_type: DBType,
        resource_name: str,
        client: Union[SyncClient, AsyncClient],
    ):
        """database access class
        this class allows for manipulation of a database

        :param db_name: the name of the database this resource belongs to.
        :param db_type: the type of data the database can hold.
        :param resource_name: the name of the resource being accessed, or to
                be created if the resource does not yet exist
        :param client: the :py:class:`SyncClient` or :py:class:`AsyncClient`
                instance to use for network requests
        """
        self.db_name = db_name
        self.db_type = db_type
        self.resource_name = resource_name
        self._client = client

    def create(self, data: Union[str, Dict, ET.Element, None]):
        """
        :param data: the data to initialize the resource with
        """

    def read(
        self,
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
    ):
        params = {}
        if node_id:
            params["nodeId"] = node_id
        if max_level:
            params["maxLevel"] = max_level
        if revision:
            if type(revision) == int:
                params["revision"] = revision
            elif type(revision) == datetime:
                params["revision-timestamp"] = revision.isoformat()
            if type(revision) == tuple:
                if type(revision[0]) == datetime:
                    params["start-revision-timestamp"] = revision[0].isoformat()
                    params["end-revision-timestamp"] = revision[1].isoformat()
                else:
                    params["start-revision"] = revision[0]
                    params["end-revision"] = revision[1]

        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

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
