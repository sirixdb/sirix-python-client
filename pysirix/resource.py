import json
import xml.etree.ElementTree as ET
from datetime import datetime

from typing import Union, Dict, Tuple, Coroutine, List

from pysirix.auth import Auth
from pysirix.constants import Insert, Revision, DBType

from pysirix.sync_client import SyncClient
from pysirix.async_client import AsyncClient
from pysirix.types import Commit


class Resource:
    def __init__(
        self,
        db_name: str,
        db_type: DBType,
        resource_name: str,
        client: Union[SyncClient, AsyncClient],
        auth: Auth,
    ):
        """
        Resource access class.

        This class allows for manipulation of a resource

        :param db_name: the name of the database this resource belongs to.
        :param db_type: the type of data the database can hold.
        :param resource_name: the name of the resource being accessed, or to
                be created if the resource does not yet exist
        :param client: the :py:class:`SyncClient` or :py:class:`AsyncClient`
                instance to use for network requests
        :param auth: the :py:class:`Auth` that keeps the client authenticated.
                It is referenced to ensure that it never goes out of scope
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
        """
        Sends a ``head`` request to determine whether or not this store/resource already exists.

        :return: a ``bool`` corresponding to the existence of the store.
        """
        return self._client.resource_exists(
            self.db_name, self.db_type, self.resource_name
        )

    def read(
        self,
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
    ) -> Union[Union[dict, ET.Element], Coroutine[None, None, Union[dict, ET.Element]]]:
        """
        Read the node (and its sub-nodes) corresponding to ``node_id``.

        :param node_id: the nodeKey corresponding to the node to read, if ``None``,
                        the entire resource is read.
        :param revision: the revision to read from, defaults to latest.
        :param max_level: the maximum depth for reading sub-nodes, defaults to latest.
        :return: either a ``dict`` or an instance of ``xml.etree.ElementTree.Element``,
                        depending on the database type of this resource.
        """
        params = self._build_read_params(node_id, revision, max_level)
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    def read_with_metadata(
        self,
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
    ):
        """
        Read the node (and its sub-nodes) corresponding to ``node_id``, with metadata for each node.

        :param node_id: the nodeKey corresponding to the node to read, if ``None``,
                        the entire resource is read.
        :param revision: the revision to read from, defaults to latest.
        :param max_level: the maximum depth for reading sub-nodes, defaults to latest.
        :return:
        """
        params = self._build_read_params(node_id, revision, max_level)
        params["withMetadata"] = True
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    @staticmethod
    def _build_read_params(
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Helper method to build a parameters ``dict`` for reading a resource.
        """
        params = {}
        if node_id:
            params["nodeId"] = node_id
        if max_level:
            params["maxLevel"] = max_level
        if revision:
            if type(revision) == int:
                params["revision"] = revision
            elif isinstance(revision, datetime):
                params["revision-timestamp"] = revision.isoformat()
            if type(revision) == tuple:
                if isinstance(revision[0], datetime):
                    params["start-revision-timestamp"] = revision[0].isoformat()
                    params["end-revision-timestamp"] = revision[1].isoformat()
                else:
                    params["start-revision"] = revision[0]
                    params["end-revision"] = revision[1]
        return params

    def history(self) -> List[Commit]:
        """
        Get a ``list`` of all commits/revision of this resource.

        :return: a ``list`` of ``dict``\s of the form :py:class:`Commit`.
        """
        return self._client.history(self.db_name, self.db_type, self.resource_name)

    def diff(
        self,
        first_revision: Revision,
        second_revision: Revision,
        node_id: int = None,
        max_depth: int = None,
    ):
        params = {}
        if isinstance(first_revision, datetime):
            params["first-revision"] = first_revision.isoformat()
        else:
            params["first-revision"] = first_revision
        if isinstance(second_revision, datetime):
            params["second-revision"] = second_revision.isoformat()
        else:
            params["second-revision"] = second_revision
        if node_id is not None:
            params["startNodeKey"] = node_id
        if max_depth is not None:
            params["maxDepth"] = max_depth
        return self._client.diff(self.db_name, self.resource_name, params)

    def get_etag(self, node_id: int):
        """
        Get the ETag of a given node.

        :param node_id: the nodeKey corresponding to which the ETag should be returned.
        :return: a ``str`` ETag.
        """
        params = {"nodeId": node_id}
        """
        if revision:
            if type(revision) == int:
                params["revision"] = revision
            else:
                params["revision-timestamp"] = revision.isoformat()
        """
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
        """
        Update a resource.

        :param node_id: the nodekey in reference to which the update should be performed.
        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        :param insert: the position of the update in relation to the node referenced by node_id.
        :param etag: the ETag of the node referenced by node_id.
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
        """
        Execute a custom query on this resource.
        The ``start_result_seq_index`` and ``end_result_seq_index`` can be used for pagination.

        :param query: the query ``str`` to execute.
        :param start_result_seq_index: the first index of the results from which to return, defaults to first.
        :param end_result_seq_index: the last index of the results to return, defaults to last.
        :return: the query result.
        """
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
    ) -> Union[None, Coroutine]:
        """
        Delete a node in a resource, or, if ``node_id`` is specified as ``None``,
        delete the entire resource.

        :param node_id: an ``int`` corresponding to the node to delete.
                        Should be specified as none to delete the entire resource.
        :param etag: the ``etag`` of the node to delete. This can be fetched using
                        the py:method`get_etag` method. If ``etag`` is specified as
                        ``None``, then the ``etag`` will be fetched and provided implicitly.
        """
        return self._client.resource_delete(
            self.db_name, self.db_type, self.resource_name, node_id, etag
        )
