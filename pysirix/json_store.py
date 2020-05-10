import json
from datetime import datetime
from typing import Union, Dict, List, Coroutine, cast
from json import dumps

from pysirix.constants import DBType, Insert, Revision
from pysirix.async_client import AsyncClient
from pysirix.auth import Auth
from pysirix.sync_client import SyncClient
from pysirix.types import QueryResult


class JsonStore:
    """
    This class is a convenient abstraction over the resource entities exposed by SirixDB.
    As such, there is no JsonStore on the SirixDB server, only the underlying resource is stored.

    This class is for storing many distinct, json objects in a single resource,
    where the objects storing data of similar type. As such, an object is an
    abstraction similar to a row in a relational database. The entirety of the
    store parallels a table in a relational database.
    """

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

    def create(self) -> Union[str, Coroutine[None, None, str]]:
        """
        Creates the store, will overwrite the store if it already exists.

        :return: will return the string "[]". If in async mode, an awaitable that resolves this string.
        """
        return self._client.create_resource(
            self.db_name, self.db_type, self.name, "[]",
        )

    def exists(self) -> Union[bool, Coroutine[None, None, bool]]:
        """
        Sends a ``head`` request to determine whether or not this store/resource already exists.

        :return: a ``bool`` corresponding to the existence of the store.
        """
        return self._client.resource_exists(self.db_name, self.db_type, self.name)

    def insert_one(
        self, insert_dict: Union[str, Dict]
    ) -> Union[str, Coroutine[None, None, str]]:
        """
        Inserts a single record into the store. New records are added at the head of the store.

        :param insert_dict: either a JSON string, or a ``dict`` that can be converted to JSON.
        :return: a JSON string of the database.
        """
        if not isinstance(insert_dict, str):
            insert_dict = dumps(insert_dict)
        return self._client.update(
            self.db_name,
            self.db_type,
            self.name,
            1,
            insert_dict,
            Insert.CHILD,
            etag=None,
        )

    def find_all(
        self,
        query_dict: Dict,
        projection: List[str] = None,
        revision: Revision = None,
        node_key=True,
    ) -> Union[
        Dict[str, List[QueryResult]],
        Coroutine[None, None, Dict[str, List[QueryResult]]],
    ]:
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
        :param revision: the revision to search, defaults to latest.
        :return: a ``dict`` with a field ``rest``, containing a ``list`` of ``dict`` records matching the query.
        """
        if revision is None:
            query_list = [f"for $i in jn:doc('{self.db_name}','{self.name}') where"]
        elif isinstance(revision, datetime):
            query_list = [
                "for $i in bit:array-values(jn:open"
                f"('{self.db_name}','{self.name}',xs:dateTime('{revision.isoformat()}'))) where"
            ]
        else:
            query_list = [
                f"for $i in bit:array-values(jn:doc('{self.db_name}','{self.name}',{revision})) where"
            ]
        for k, v in query_dict.items():
            v = (
                "".join(['"', v, '"'])
                if isinstance(v, str)
                else "true()"
                if v is True
                else "false()"
                if v is False
                else "jn:null()"
                if v is None
                else v
            )
            query_list.append(f"deep-equal($i=>{k}, {v}) and")
        query_string = " ".join(
            [
                " ".join(query_list)[:-4],
                "return {$i,'nodeKey': sdb:nodekey($i)}" if node_key else "return {$i}",
            ]
        )
        if projection is not None:
            if node_key:
                projection.append("nodeKey")
            projection_string = ",".join(projection)
            query_string = "".join([query_string, "{", projection_string, "}"])
        params = {"query": query_string}
        return json.loads(self._client.post_query(params))
