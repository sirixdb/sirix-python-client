from typing import Dict, List, Union, Coroutine

import httpx

from pysirix.async_client import AsyncClient
from pysirix.info import AuthData
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
        client_id: str = None,
        client_secret: str = None,
    ):
        """
        :param username: the username registered with keycloak for this application
        :param password: the password registered with keycloak for this application
        :param client_id: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        :param client_secret: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        """
        if isinstance(client, httpx.Client):
            self._asynchronous = False
        else:
            self._asynchronous = True
        if self._asynchronous:
            self._client = AsyncClient(client)
        else:
            self._client = SyncClient(client)
        self._auth = Auth(
            AuthData(username, password, client_id, client_secret),
            client,
            self._asynchronous,
        )

    def authenticate(self):
        """
        Call the authenticate endpoint. Must be called before any other calls are made.
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
        self, ret: bool = True
    ) -> Union[Coroutine[List[Dict[str, str]]], List[Dict[str, str]]]:
        """
        :param ret: whether or not to return the info from the function
        """
        if self._asynchronous:
            return handle_async(self._client.global_info, ret)
        else:
            return self._client.global_info(ret)

    def delete(self) -> None:
        if self._asynchronous:
            return handle_async(self._client.delete_all)
        else:
            return self._client.delete_all()
