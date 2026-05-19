import json
import xml.etree.ElementTree as ET
from collections.abc import Iterator
from datetime import datetime

from typing import Union, Dict, Tuple, Awaitable, Optional, List

from pysirix.auth import Auth
from pysirix.constants import Insert, Revision, DBType, MetadataType

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

    def create(
        self,
        data: Union[str, Dict, ET.Element],
        hash_type: str = "ROLLING",
        use_dewey_ids: bool = False,
        hash_kind: str = None,
        commit_message: str = None,
        commit_timestamp: str = None,
    ):
        """
        :param data: the data with which to initialize the resource.
                May be an instance of ``dict``, or an instance of
                ``xml.etree.ElementTree.Element`` (depending on the database type),
                or a ``str`` of properly formed json or xml.
        :param use_dewey_ids: whether to use DeweyIDs for node identification.
        :param hash_kind: the hash kind parameter (if needed for newer SirixDB versions).
        :param commit_message: optional commit message for this revision.
        :param commit_timestamp: optional commit timestamp for this revision.
        """
        data = (
            data
            if type(data) is str or isinstance(data, Iterator)
            else json.dumps(data)
            if self.db_type == DBType.JSON
            else ET.tostring(data)
        )
        return self._client.create_resource(
            self.db_name,
            self.db_type,
            self.resource_name,
            data,
            hash_type,
            use_dewey_ids,
            hash_kind,
            commit_message,
            commit_timestamp,
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
        top_level_limit: Optional[int] = None,
        top_level_skip_last_node: Optional[int] = None,
        number_of_nodes: Optional[int] = None,
        max_children: Optional[int] = None,
        pretty_print: Optional[bool] = None,
        start_node_key: Optional[int] = None,
    ) -> Union[Union[dict, ET.Element], Awaitable[Union[dict, ET.Element]]]:
        """
        Read the node (and its sub-nodes) corresponding to ``node_id``.

        :param node_id: the nodeKey corresponding to the node to read, if ``None``,
                        the entire resource is read.
        :param revision: the revision to read from, defaults to latest.
        :param max_level: the maximum depth for reading sub-nodes, defaults to latest.
        :param top_level_limit: the maximum number of top level nodes to return (used for paging).
        :param top_level_skip_last_node: the last nodeId to skip (used for paging).
        :param number_of_nodes: limit the number of nodes returned.
        :param max_children: limit the number of children per node.
        :param pretty_print: whether to pretty-print the output.
        :param start_node_key: the start node key for reading.
        :return: either a ``dict`` or an instance of ``xml.etree.ElementTree.Element``,
                        depending on the database type of this resource.
        """
        params = self._build_read_params(
            node_id, revision, max_level, top_level_limit, top_level_skip_last_node,
            number_of_nodes, max_children, pretty_print, start_node_key,
        )
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    def read_with_metadata(
        self,
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        meta_type: MetadataType = MetadataType.ALL,
        max_level: Optional[int] = None,
        top_level_limit: Optional[int] = None,
        top_level_skip_last_node: Optional[int] = None,
        number_of_nodes: Optional[int] = None,
        max_children: Optional[int] = None,
        pretty_print: Optional[bool] = None,
        start_node_key: Optional[int] = None,
    ):
        """
        Read the node (and its sub-nodes) corresponding to ``node_id``, with metadata for each node.

        :param node_id: the nodeKey corresponding to the node to read, if ``None``,
                        the entire resource is read.
        :param revision: the revision to read from, defaults to latest.
        :param meta_type: the type of metadata to return, defaults to all.
        :param max_level: the maximum depth for reading sub-nodes, defaults to latest.
        :param top_level_limit: the maximum number of top level nodes to return (used for paging).
        :param top_level_skip_last_node: the last nodeId to skip (used for paging).
        :param number_of_nodes: limit the number of nodes returned.
        :param max_children: limit the number of children per node.
        :param pretty_print: whether to pretty-print the output.
        :param start_node_key: the start node key for reading.
        :return:
        """
        params = self._build_read_params(
            node_id, revision, max_level, top_level_limit, top_level_skip_last_node,
            number_of_nodes, max_children, pretty_print, start_node_key,
        )
        params["withMetadata"] = meta_type.value
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    @staticmethod
    def _build_read_params(
        node_id: Union[int, None],
        revision: Union[Revision, Tuple[Revision, Revision], None] = None,
        max_level: Union[int, None] = None,
        top_level_limit: Optional[int] = None,
        top_level_skip_last_node: Optional[int] = None,
        number_of_nodes: Optional[int] = None,
        max_children: Optional[int] = None,
        pretty_print: Optional[bool] = None,
        start_node_key: Optional[int] = None,
    ) -> Dict[str, Union[str, int]]:
        """
        Helper method to build a parameters ``dict`` for reading a resource.
        """
        params = {}
        if node_id:
            params["nodeId"] = node_id
        if max_level:
            params["maxLevel"] = max_level
        if top_level_limit:
            params["nextTopLevelNodes"] = top_level_limit
        if top_level_skip_last_node:
            params["startNodeKey"] = top_level_skip_last_node
        if number_of_nodes is not None:
            params["numberOfNodes"] = number_of_nodes
        if max_children is not None:
            params["maxChildren"] = max_children
        if pretty_print is not None:
            params["prettyPrint"] = "true" if pretty_print else "false"
        if start_node_key is not None:
            params["startNodeKey"] = start_node_key
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

    def history(
        self,
        revisions: int = None,
        start_revision: int = None,
        end_revision: int = None,
    ) -> List[Commit]:
        """
        Get a ``list`` of all commits/revision of this resource.

        :param revisions: limit the number of revisions returned.
        :param start_revision: the start revision number for a range query.
        :param end_revision: the end revision number for a range query.
        :return: a ``list`` of ``dict`` of the form :py:class:`pysirix.Commit`.
        """
        return self._client.history(
            self.db_name, self.db_type, self.resource_name,
            revisions, start_revision, end_revision,
        )

    def path_summary(self, revision: int = None):
        """
        Get the path summary of this resource.

        :param revision: the revision number to get the path summary for.
        :return: a ``dict`` with path summary data.
        """
        return self._client.path_summary(
            self.db_name, self.db_type, self.resource_name, revision
        )

    def diff(
        self,
        first_revision: Revision,
        second_revision: Revision,
        node_id: int = None,
        max_depth: int = None,
        include_data: bool = True,
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
        if include_data:
            params["include-data"] = "true"
        return self._client.diff(self.db_name, self.resource_name, params)

    def get_etag(self, node_id: int) -> Union[str, Awaitable[str]]:
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
        commit_message: str = None,
        commit_timestamp: str = None,
    ) -> Union[str, Awaitable[str]]:
        """
        Update a resource.

        :param node_id: the nodekey in reference to which the update should be performed.
        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        :param insert: the position of the update in relation to the node referenced by node_id.
        :param etag: the ETag of the node referenced by node_id.
        :param commit_message: optional commit message for this revision.
        :param commit_timestamp: optional commit timestamp for this revision.
        """
        data = (
            data
            if type(data) is str
            else json.dumps(data)
            if self.db_type == DBType.JSON
            else ET.tostring(data)
        )
        return self._client.update(
            self.db_name, self.db_type, self.resource_name, node_id, data, insert, etag,
            commit_message, commit_timestamp,
        )

    def query(
        self,
        query: str,
        start_result_seq_index: int = None,
        end_result_seq_index: int = None,
        commit_message: str = None,
        commit_timestamp: str = None,
        plan: bool = None,
        plan_stage: str = None,
    ):
        """
        Execute a custom query on this resource.
        The ``start_result_seq_index`` and ``end_result_seq_index`` can be used for pagination.

        :param query: the query ``str`` to execute.
        :param start_result_seq_index: the first index of the results from which to return, defaults to first.
        :param end_result_seq_index: the last index of the results to return, defaults to last.
        :param commit_message: optional commit message for modifying queries.
        :param commit_timestamp: optional commit timestamp for modifying queries.
        :param plan: whether to return a query plan instead of executing.
        :param plan_stage: the plan stage to return.
        :return: the query result.
        """
        params = {
            "query": query,
            "startResultSeqIndex": start_result_seq_index,
            "endResultSeqIndex": end_result_seq_index,
        }
        if commit_message is not None:
            params["commitMessage"] = commit_message
        if commit_timestamp is not None:
            params["commitTimestamp"] = commit_timestamp
        if plan is not None:
            params["plan"] = "true" if plan else "false"
        if plan_stage is not None:
            params["planStage"] = plan_stage
        params = {k: v for k, v in params.items() if v}
        return self._client.read_resource(
            self.db_name, self.db_type, self.resource_name, params
        )

    def delete(
        self, node_id: Union[int, None], etag: Union[str, None]
    ) -> Union[None, Awaitable[None]]:
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
