from datetime import datetime
from typing import Union, Dict, List, Awaitable, Optional
from pysirix.types import Commit, Revision as RevisionType, SubtreeRevision
from json import dumps, loads

from abc import ABC

from pysirix.constants import DBType, Revision
from pysirix.async_client import AsyncClient
from pysirix.auth import Auth
from pysirix.sync_client import SyncClient
from pysirix.types import QueryResult


def parse_revision(revision: Revision, params: Dict) -> None:
    if type(revision) == int:
        params["revision"] = revision
    elif isinstance(revision, datetime):
        params["revision-timestamp"] = revision.isoformat()


def stringify(v: Union[None, int, str, Dict, List]):
    return (
        f'"{v}"'
        if isinstance(v, str)
        else f"{v}"
        if isinstance(v, int)
        else "true()"
        if v is True
        else "false()"
        if v is False
        else "jn:null()"
        if v is None
        # not a primitive value
        else f"jn:parse('{dumps(v)}')"
    )


query_function_include = (
    "declare function local:q($i, $q) {"
    "let $m := for $k in jn:keys($q) return if (not(empty($i=>$k))) then deep-equal($i=>$k, $q=>$k) else false()"
    "return empty(index-of($m, false()))"
    "};"
)


class JsonStoreBase(ABC):
    def __init__(
        self,
        db_name: str,
        name: str,
        client: Union[SyncClient, AsyncClient],
        auth: Auth,
    ):
        self.db_name = db_name
        self.db_type = DBType.JSON
        self.name = name
        self._client = client
        self._auth = auth

    def insert_one(self, insert_dict: Union[str, Dict]) -> Union[str, Awaitable[str]]:
        """
        Inserts a single record into the store. New records are added at the tail of the store.

        :param insert_dict: either a JSON string of a ``dict``, or a ``dict`` that can be converted to JSON.
        :return: an emtpy ``str`` or an empty ``Awaitable[str]``.
        """
        insert_dict = dumps(insert_dict)
        query = f"append json jn:parse('{insert_dict}') into jn:doc('{self.db_name}','{self.name}')"
        return self._client.post_query({"query": query})

    def insert_many(
        self, insert_list: Union[str, List[Dict]]
    ) -> Union[str, Awaitable[str]]:
        """
        Inserts a list of records into the store. New records are added at the the tail of the store.

        :param insert_list: either a JSON string of ``list`` of ``dict``\s, or a ``list`` that can be converted to JSON
        :return: a ``str`` "{rest: []}" or an ``Awaitable[str]`` resolving to this string.
        """
        insert_list = dumps(insert_list)
        query = (
            f"let $doc := jn:doc('{self.db_name}','{self.name}')"
            f"for $i in jn:parse('{insert_list}') return append json $i into $doc"
        )
        return self._client.post_query({"query": query})

    def exists(self) -> Union[bool, Awaitable[bool]]:
        """
        Sends a ``head`` request to determine whether or not this store/resource already exists.

        :return: a ``bool`` corresponding to the existence of the store.
        """
        return self._client.resource_exists(self.db_name, self.db_type, self.name)

    def create(self) -> Union[str, Awaitable[str]]:
        """
        Creates the store, will overwrite the store if it already exists.

        :return: will return the string "[]". If in async mode, an awaitable that resolves this string.
        """
        return self._client.create_resource(
            self.db_name,
            self.db_type,
            self.name,
            "[]",
        )

    def resource_history(self) -> Union[List[Commit], Awaitable[List[Commit]]]:
        """
        This method returns the entire history of a resource.

        :return: a list of :py:class:`Commit`.
        """
        return self._client.history(self.db_name, self.db_type, self.name)

    def history_embed(self, node_key: int, revision: Optional[Revision] = None):
        query = (
            f"let $node := sdb:select-item(., {node_key}) let $result := for $rev in jn:all-times($node)"
            f" return if (not(exists(jn:previous($rev)))) then $rev"
            f" else if (sdb:hash($rev) ne sdb:hash(jn:previous($rev))) then $rev"
            " else () return $result"
        )
        params = {"query": query}
        if revision:
            parse_revision(revision, params)
        return self._client.read_resource(self.db_name, self.db_type, self.name, params)

    def history(
        self, node_key: int, subtree: bool = True, revision: Optional[Revision] = None
    ):
        """
        This method returns the history of a node in the resource.

        :param node_key: the root of the subtree whose history should be returned. Defaults to document root.
        :param subtree: whether to account for changes in the subtree of the given node. Defaults to ``True``.
        :param revision: the revision in which the node with the given ``node_key`` exists
                (if it does not exist currently). Defaults to the latest revision. May be an integer or a
                ``datetime`` instance
        :return: If ``subtree`` is ``True``, a list of :py:class:`pysirix.types.SubtreeRevision`. Else, a list of
                :py:class:`pysirix.types.RevisionType`.
        """
        if subtree:
            revision_data = '{"revisionNumber": sdb:revision($rev), "revisionTimestamp": xs:string(sdb:timestamp($rev))}'
            query = (
                f"let $node := sdb:select-item(., {node_key}) let $result := for $rev in jn:all-times($node)"
                f" return if (not(exists(jn:previous($rev)))) then {revision_data}"
                f" else if (sdb:hash($rev) ne sdb:hash(jn:previous($rev))) then {revision_data}"
                " else () return $result"
            )
        else:
            query = f"sdb:item-history(sdb:select-item(., {node_key}))"
        params = {"query": query}
        if revision:
            parse_revision(revision, params)
        return self._client.read_resource(self.db_name, self.db_type, self.name, params)

    def _prepare_find_all(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
        hash=False,
        start_result_index: Optional[int] = None,
        end_result_index: Optional[int] = None,
    ):
        if revision is None:
            query_list = [
                query_function_include,
                f"for $i in jn:doc('{self.db_name}','{self.name}')",
            ]
        elif isinstance(revision, datetime):
            query_list = [
                query_function_include,
                "for $i in bit:array-values(jn:open"
                f"('{self.db_name}','{self.name}',xs:dateTime('{revision.isoformat()}')))",
            ]
        else:
            query_list = [
                query_function_include,
                f"for $i in bit:array-values(jn:doc('{self.db_name}','{self.name}',{revision}))",
            ]
        query_list.append(f"where local:q($i, {stringify(query_dict)})")
        return_obj = "".join(
            [
                "return {$i",
                ",'nodeKey': sdb:nodekey($i)" if node_key else "",
                ",'hash': sdb:hash($i)}" if hash else "}",
            ]
        )
        query_string = " ".join([*query_list, return_obj])
        if projection is not None:
            if node_key:
                projection.append("nodeKey")
            if hash:
                projection.append("hash")
            projection_string = ",".join(projection)
            query_string = "".join([query_string, "{", projection_string, "}"])
        params = {"query": query_string}
        if start_result_index is not None:
            params["startResultSeqIndex"] = start_result_index
        if end_result_index is not None:
            params["endResultSeqIndex"] = end_result_index
        return params

    def find_all(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
        hash=False,
        start_result_index: Optional[int] = None,
        end_result_index: Optional[int] = None,
    ) -> List[QueryResult]:
        """
        Finds and returns all records where the values of ``query_dict`` match the
        corresponding values the record.

        ``projection`` can optionally be used to retrieve only certain fields of the
        matching records.

        By default, the node_key of of each record is returned as a ``nodeKey`` field in the record.
        The ``node_key`` parameter controls this behavior.

        :param query_dict: a ``dict`` with which to query the records.
        :param projection: a ``list`` of field names to return for the matching records.
        :param node_key: a ``bool`` determining whether or not to return a ``nodeKey`` field containing
                        the nodeKey of the record.
        :param hash: a ``bool`` determining whether or not to return a ``hash`` field containing the hash of the record.
        :param revision: the revision to search, defaults to latest. May be an integer or a ``datetime`` instance
        :param start_result_index: index of first result to return.
        :param end_result_index: index of last result to return.
        :return: a ``list`` of :py:class:`QueryResult` records matching the query.
        """
        raise NotImplementedError()

    def update_by_key(
        self,
        node_key: int,
        update_dict: Dict[str, Union[List, Dict, str, int, None]],
    ) -> Union[str, Awaitable[str]]:
        """

        :param node_key: the nodeKey of the record to update
        :param update_dict: a dict of keys and matching values to replace in the given record
        :return:
        """
        query = (
            f"let $rec := sdb:select-item(jn:doc('{self.db_name}','{self.name}'),{node_key}) "
            f" let $update := {stringify(update_dict)}"
            " for $key in bit:fields($update) return replace json value of $rec=>$key with $update=>$key"
        )
        return self._client.post_query({"query": query})

    def update_many(
        self,
        query_dict: Dict,
        update_dict: Dict[str, Union[List, Dict, str, int, None]],
    ) -> Union[str, Awaitable[str]]:
        """

        :param query_dict: a ``dict`` of field names and their values to match against
        :param update_dict: a dict of keys and matching values to replace in the selected record
        :return:
        """
        query = (
            f"{query_function_include}"
            f"for $i in jn:doc('{self.db_name}','{self.name}') where local:q($i, {stringify(query_dict)})"
            f" let $update := {stringify(update_dict)}"
            " for $key in bit:fields($update) return replace json value of $i=>$key with $update=>$key"
        )
        return self._client.post_query({"query": query})

    def delete_fields_by_key(
        self, node_key: int, fields: List[str]
    ) -> Union[str, Awaitable[str]]:
        """

        :param node_key: the nodeKey of the record to update
        :param fields: the keys of the fields of the record to delete
        :return:
        """
        query = (
            f"let $obj := sdb:select-item(jn:doc('{self.db_name}','{self.name}'),{node_key})"
            f" let $update := {stringify(fields)}"
            f" for $i in $fields return delete json $obj=>$i"
        )
        return self._client.post_query({"query": query})

    def delete_field(
        self, query_dict: Dict, fields: List[str]
    ) -> Union[str, Awaitable[str]]:
        """

        :param query_dict: a ``dict`` of field names and their values to match against
        :param fields: the keys of the fields of the records to delete
        :return:
        """
        query = (
            f"{query_function_include}"
            f"let $records := for $i in jn:doc('{self.db_name}','{self.name}')"
            f" where local:q($i, {stringify(query_dict)}) return $i"
            f" let $fields := {stringify(fields)}"
            f" for $i in $fields return delete json $records=>$i"
        )
        return self._client.post_query({"query": query})

    def delete_records(self, query_dict: Dict) -> Union[str, Awaitable[str]]:
        """

        :param query_dict: a ``dict`` of field names and their values to match against
        :return:
        """
        query = (
            f"{query_function_include}"
            f"let $doc := jn:doc('{self.db_name}','{self.name}')"
            f" let $m := for $i at $pos in $doc where local:q($i, {stringify(query_dict)}) return $pos - 1"
            " for $i in $m order by $i descending return delete json $doc[[$i]]"
        )
        return self._client.post_query({"query": query})

    def find_by_key(
        self,
        node_key: Union[int, None],
        revision: Union[Revision, None] = None,
    ):
        """

        :param node_key: the nodeKey of the record to read
        :param revision: the revision to search, defaults to latest. May be an integer or a ``datetime`` instance
        :return:
        """
        params = {"nodeId": node_key}
        if revision:
            parse_revision(revision, params)
        return self._client.read_resource(self.db_name, self.db_type, self.name, params)

    def find_one(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
        hash=False,
    ) -> List[QueryResult]:
        """
        This method is the same as :py:meth:`find_many`, except that this method will only return the first result,
                by way of passing ``0`` to that method's ``start_result_index``, and ``end_result_index`` parameters.

        :param query_dict:
        :param projection:
        :param revision:
        :param node_key:
        :param hash:
        :return:
        """
        return self.find_all(
            query_dict,
            projection,
            revision,
            node_key,
            hash,
            start_result_index=0,
            end_result_index=0,
        )


class JsonStoreSync(JsonStoreBase):
    """
    This class is a convenient abstraction over the resource entities exposed by SirixDB.
    As such, there is no JsonStore on the SirixDB server, only the underlying resource is stored.

    This class is for storing many distinct, JSON objects in a single resource, where the objects/records
    store data of similar type. As such, it's usage parallels a that of a document store, and an object is
    an abstraction similar to a single document in such a store.
    """

    def find_all(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
        hash=False,
        start_result_index: Optional[int] = None,
        end_result_index: Optional[int] = None,
    ) -> List[QueryResult]:
        params = self._prepare_find_all(
            query_dict,
            projection,
            revision,
            node_key,
            hash,
            start_result_index,
            end_result_index,
        )
        result = self._client.post_query(params)
        return loads(result)["rest"]

    def history(
        self, node_key: int, subtree: bool = True, revision: Optional[Revision] = None
    ) -> Union[List[SubtreeRevision], List[RevisionType],]:
        return super().history(node_key, subtree, revision)["rest"]

    def resource_history(self) -> List[Commit]:
        return super().resource_history()

    def history_embed(
        self, node_key: int, revision: Optional[Revision] = None
    ) -> List[QueryResult]:
        return super().history_embed(node_key, revision)["rest"]

    def find_by_key(
        self,
        node_key: Union[int, None],
        revision: Union[Revision, None] = None,
    ):
        return super().find_by_key(node_key, revision)


class JsonStoreAsync(JsonStoreBase):
    """
    This class is a convenient abstraction over the resource entities exposed by SirixDB.
    As such, there is no JsonStore on the SirixDB server, only the underlying resource is stored.

    This class is for storing many distinct, JSON objects in a single resource, where the objects/records
    store data of similar type. As such, it's usage parallels a that of a document store, and an object is
    an abstraction similar to a single document in such a store.
    """

    async def find_all(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
        hash=False,
        start_result_index: Optional[int] = None,
        end_result_index: Optional[int] = None,
    ) -> List[QueryResult]:
        params = self._prepare_find_all(
            query_dict,
            projection,
            revision,
            node_key,
            hash,
            start_result_index,
            end_result_index,
        )
        result = await self._client.post_query(params)
        return loads(result)["rest"]

    async def history(
        self, node_key: int, subtree: bool = True, revision: Optional[Revision] = None
    ) -> Union[List[SubtreeRevision], List[RevisionType]]:
        result = await super().history(node_key, subtree, revision)
        return result["rest"]

    async def resource_history(self) -> List[Commit]:
        return await super().resource_history()

    async def history_embed(
        self, node_key: int, revision: Optional[Revision] = None
    ) -> List[QueryResult]:
        result = await super().history_embed(node_key, revision)
        return result["rest"]

    async def find_by_key(
        self,
        node_key: Union[int, None],
        revision: Union[Revision, None] = None,
    ):
        return await super().find_by_key(node_key, revision)
