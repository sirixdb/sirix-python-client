from typing import Dict, List, Union, Coroutine, Optional

import httpx

from pysirix.sync_client import SyncClient
from pysirix.async_client import AsyncClient
from pysirix.auth import Auth
from pysirix.database import Database

from pysirix.constants import DBType


class Sirix:
    def __init__(
        self,
        username: str,
        password: str,
        client: Union[httpx.Client, httpx.AsyncClient],
    ):
        """
        :param username: the username registered with keycloak for this application
        :param password: the password registered with keycloak for this application
        :param client: the ``httpx`` ``Client`` or ``AsyncClient`` to use
        """
        if isinstance(client, httpx.Client):
            self._client = SyncClient(client)
            self._auth = Auth(username, password, client, False)
        else:
            self._client = AsyncClient(client)
            self._auth = Auth(username, password, client, True)

    def authenticate(self):
        """
        Call the authenticate endpoint. Must be called before any other calls are made.
        This is done internally by :py:func:`sirix_sync` or by :py:func:`sirix_async`.
        """
        return self._auth.authenticate()

    def database(self, database_name: str, database_type: DBType):
        """Returns a database instance

        :param database_name: the name of the database to access
        :param database_type: the type of the database to access
        """
        return Database(database_name, database_type, self._client, self._auth)

    def get_info(
        self, resources: bool = True
    ) -> Union[Coroutine, List[Dict[str, str]]]:
        """returns a list of database names and types, and (optionally) a list their resources as well

        :param resources: whether or not to include resource information
        :return:
        :raises:
        """
        return self._client.global_info(resources)

    def query(
        self,
        query: str,
        start_result_seq_index: int = None,
        end_result_seq_index: int = None,
    ):
        query_obj = {
            "query": query,
            "startResultSeqIndex": start_result_seq_index,
            "endResultSeqIndex": end_result_seq_index,
        }
        query_obj = {k: v for k, v in query_obj.items() if v}
        return self._client.post_query(query_obj)

    def delete_all(self) -> Union[Coroutine, None]:
        """
        Deletes all databases and resources in the sirix database.

        :return: ``None``
        :raises:
        """
        return self._client.delete_all()
