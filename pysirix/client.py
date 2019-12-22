from typing import Tuple, Dict, List, Union
import asyncio

from requests import Session
from aiohttp import ClientSession

from .info import AuthData, InstanceData
from .auth import Auth
from .database import Database

from .sync.rest import get_info
from .asynchronous.rest import async_get_info

from .utils import handle_async


class SirixClient:
    def __init__(
        self,
        username: str,
        password: str,
        sirix_uri: str = "https://localhost:9443",
        client_id: str = None,
        client_secret: str = None,
        keycloak_uri: str = "http://localhost:8080",
        asynchronous: bool = False,
        allow_self_signed: bool = False,
    ):
        """
        :param username: the username registered with keycloak for this application
        :param password: the password registered with keycloak for this application
        :param sirix_uri: the uri of the sirix instance
        :param client_id: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        :param client_secret: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        :param keycloak_uri: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_id`` and optional ``client_secret`` params).
                This option is not recommended.
        :param allow_self_signed: whether to accept self signed certificates. Not recommended.
        """
        self._asynchronous = asynchronous
        self._auth_data = AuthData(
            username, password, keycloak_uri, client_id, client_secret
        )
        self._instance_data = InstanceData(sirix_uri)
        if asynchronous:
            self._session = ClientSession()
            # we can't pass a global allow_self_signed setting to the async
            # ClientSession, so we have to store it and handle it manually
            self._allow_self_signed = allow_self_signed
        else:
            self._session = Session()
            if allow_self_signed:
                self._session.verify = False
        self._auth = Auth(self._auth_data, self._instance_data, self._session, self._asynchronous, allow_self_signed)

    def _init(self):
        """
        Initialize the instance. We may need to make async function calls,
        so we can't put this code in ``__init__`` 
        """
        
        self._auth.authenticate()
        self.get_info(False)

    async def _async_init(self):
        await self._auth.authenticate()
        await self.get_info()

    def __getitem__(self, key: Tuple[str]):
        """
        Returns a database instance. See :meth:`get_database` for further information
        """
        return Database(*key, parent=self)

    def get_database(self, database_name: str, database_type: str):
        """Returns a database instance

        If a database with the given name and type does not exist,
        it is created.
        
        If ``database_type`` conflicts with the actual database type,
        the value of ``database_type`` is ignored.

        if ``database_type`` is not provided, and the database does not yet exist,
        an error is raised.

        :param database_name: the name of the database to access
        :param database_type: the type of the database to access

        Note that you get the same behavior with index access, as follows:
            >>> sirix = Sirix(params)
            >>> sirix[(database_name, database_type)]
        """
        return Database(database_name, database_type, parent=self)

    def get_info(self, ret: bool = True) -> Union[None, List[Dict[str, str]]]:
        """
        :param ret: whether or not to return the info from the function
        """
        if self._asynchronous:
            return handle_async(async_get_info, self, ret)
        else:
            return get_info(self, ret)
