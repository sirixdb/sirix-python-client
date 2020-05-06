from typing import Union, Optional, Coroutine, Dict, List

from pysirix.auth import Auth
from pysirix.constants import DBType
from pysirix.json_store import JsonStore
from pysirix.sync_client import SyncClient
from pysirix.async_client import AsyncClient
from pysirix.resource import Resource


class Database:
    def __init__(
        self,
        database_name: str,
        database_type: DBType,
        client: Union[SyncClient, AsyncClient],
        auth: Auth,
    ):
        """
        Database access class

        This class allows for manipulation of a database

        :param database_name: the name of the database to access, or create
                if it does not yet exist
        :param database_type: the type of the database being accessed, or to
                be created if the database does not yet exist
        :param client: the :py:class:`SyncClient` or :py:class:`AsyncClient`
                instance to use for network requests
        :param auth: the :py:class:`Auth` that keeps the client authenticated.
                It is referenced to ensure that it never goes out of scope
        """
        self._client = client
        self._auth = auth

        self.database_name = database_name
        self.database_type = database_type

    def create(self) -> Union[None, Coroutine[None, None, None]]:
        """
        Create a database with the name and type of this :py:class:`Database` instance.
        """
        return self._client.create_database(self.database_name, self.database_type)

    def get_database_info(self) -> Union[Coroutine[None, None, Dict], Dict]:
        """
        Get information about this database and its resources.
        Raises a :py:class:`SirixServerError` error if the database does not exist.

        :return: a ``dict`` with the name, type, and resources (as a ``list`` of ``str``) of this database.
        :raises: :py:class:`SirixServerError`.
        """
        return self._client.get_database_info(self.database_name)

    def resource(self, resource_name: str):
        """
        Returns a :py:class:`resource` instance.

        :param resource_name: the name of the resource to access
        :return: an instance of :py:class:`Resource`.
        """
        return Resource(
            self.database_name,
            self.database_type,
            resource_name,
            self._client,
            self._auth,
        )

    def json_store(self, name: str):
        """
        Returns a :py:class:`store` instance.

        :param name: the resource name for the store.
        :return: an instance of :py:class:`JsonStore`.
        """
        return JsonStore(self.database_name, name, self._client, self._auth)

    def delete(self) -> Optional[Coroutine]:
        """
        Delete the database with the name of this :py:class:`Database` instance.
        """
        return self._client.delete_database(self.database_name)
