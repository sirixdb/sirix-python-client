from typing import Union, Dict, List, Coroutine, cast
from json import dumps

from pysirix.constants import DBType, Insert
from pysirix.async_client import AsyncClient
from pysirix.auth import Auth
from pysirix.sync_client import SyncClient
from pysirix.types import QueryResult


class JsonStore:
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
        return self._client.create_resource(
            self.db_name, self.db_type, self.name, "[]",
        )

    def exists(self) -> Union[bool, Coroutine[None, None, bool]]:
        return self._client.resource_exists(self.db_name, self.db_type, self.name)

    def insert_one(
        self, insert_dict: Union[str, Dict]
    ) -> Union[str, Coroutine[None, None, str]]:
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
        self, query_dict: Dict, projection: List[str] = None, node_key=True
    ) -> Union[
        Dict[str, List[Dict]], Coroutine[None, None, Dict[str, List[Dict]]],
    ]:
        query_list = ["for $i in bit:array-values(.) where"]
        for k, v in query_dict.items():
            v = (
                "".join(['"', v, '"'])
                if isinstance(v, str)
                else dumps(v)
                if isinstance(v, (dict, list))
                else v
            )
            query_list.append(f"deep-equal($i=>{k}, {v}) and")
        query_string = " ".join(
            [
                " ".join(query_list)[:-4],
                "return {$i, 'nodeKey': sdb:nodekey($i)}"
                if node_key
                else "return {$i}",
            ]
        )
        if projection is not None:
            if node_key:
                projection.append("nodeKey")
            projection_string = ",".join(projection)
            query_string = "".join([query_string, "{", projection_string, "}"])
        params = {"query": query_string}
        print(query_string)
        return cast(
            Union[
                Dict[str, List[QueryResult]],
                Coroutine[None, None, Dict[str, List[QueryResult]]],
            ],
            self._client.read_resource(self.db_name, self.db_type, self.name, params),
        )
