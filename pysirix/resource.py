import json
import xml.etree.ElementTree as ET
from datetime import datetime

from typing import Union, Dict, Tuple, Coroutine

from pysirix.auth import Auth
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
        auth: Auth
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
        self._auth = auth

    def create(self, data: Union[str, Dict, ET.Element]):
        """
        :param data: the data with which to initialize the resource.
                May be an instance of ``dict``, or an instance of
                ``xml.etree.ElementTree.Element``, or a ``str`` of properly
                formed json or xml.
        """
        data = (
            data
            if type(data) is str
            else json.dumps(data)
            if self.db_type == DBType.JSON
            else ET.tostring(data)
        )
        return self._client.create_resource(
            self.db_name, self.db_type, self.resource_name, data
        )

    def exists(self):
        return self._client.resource_exists(
            self.db_name, self.db_type, self.resource_name
        )

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

    def history(self):
        return self._client.history(self.db_name, self.db_type, self.resource_name)

    def get_etag(self, node_id: int, revision: Revision = None):
        params = {"nodeId": node_id}
        if revision:
            if type(revision) == int:
                params["revision"] = revision
            else:
                params["revision-timestamp"] = revision.isoformat()
        return self._client.get_etag(
            self.db_name, self.db_type, self.resource_name, params
        )

    def update(
        self,
        node_id: int,
        data: Union[str, ET.Element, Dict],
        insert: Insert = Insert.CHILD,
        etag: str = None,
    ):
        """Update a resource

        :param node_id:
        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        :param insert:
        :param etag:
        """
        data = (
            data
            if type(data) is str
            else json.dumps(data)
            if self.db_type == DBType.JSON
            else ET.tostring(data)
        )
        return self._client.update(
            self.db_name, self.db_type, self.resource_name, node_id, data, insert, etag
        )

    def query(
        self,
        query: str,
        start_result_seq_index: int = None,
        end_result_seq_index: int = None,
    ):
        params = {
            "query": query,
            "startResultSeqIndex": start_result_seq_index,
            "endResultSeqIndex": end_result_seq_index,
        }
        params = {k: v for k, v in params.items() if v}
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    def delete(
        self, node_id: Union[int, None], etag: Union[str, None]
    ) -> Union[bool, Coroutine]:
        """delete a node in a resource, or the entire resource, if ``node_id``
                is specified as ``None``

        :param node_id:
        :param etag:
        :return:
        """
        return self._client.resource_delete(
            self.db_name, self.db_type, self.resource_name, node_id, etag
        )
