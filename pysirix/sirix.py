from typing import Dict, List, Union, Coroutine

import httpx

from pysirix.async_client import AsyncClient
from pysirix.auth import Auth
from pysirix.database import Database

from pysirix.sync_client import SyncClient

from pysirix.utils import handle_async


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
            self._asynchronous = False
        else:
            self._asynchronous = True
        if self._asynchronous:
            self._client = AsyncClient(client)
        else:
            self._client = SyncClient(client)
        self._auth = Auth(username, password, client, self._asynchronous)

    def authenticate(self):
        """
        Call the authenticate endpoint. Must be called before any other calls are made.

        Should be called internally by the :py:func:`sirix_sync` function or by the
        :py:func:`sirix_async` function.
        """
        if self._asynchronous:
            return handle_async(self._auth.authenticate)
        else:
            self._auth.authenticate()

    def database(self, database_name: str, database_type: str = None):
        """Returns a database instance

        If a database with the given name and type does not exist,
        it is created.
        
        If ``database_type`` conflicts with the actual database type,
        the value of ``database_type`` is ignored.

        if ``database_type`` is not provided, and the database does not yet exist,
        an error is raised.

        :param database_name: the name of the database to access
        :param database_type: the type of the database to access
        """
        db = Database(database_name, database_type, parent=self)
        db._init()
        return db

    def get_info(
        self, resources: bool = True
    ) -> Union[Coroutine[List[Dict[str, str]], str, int], List[Dict[str, str]]]:
        """returns a list of database names and types, and (optionally) a list their resources as well
        :param resources: whether or not to include resource information
        """
        if self._asynchronous:
            return handle_async(self._client.global_info, resources)
        else:
            return self._client.global_info(resources)

    def delete(self) -> None:
        if self._asynchronous:
            return handle_async(self._client.delete_all)
        else:
            return self._client.delete_all()
