from typing import Union, Optional, Coroutine, Dict, List

from pysirix.constants import DBType
from pysirix.sync_client import SyncClient
from pysirix.async_client import AsyncClient
from pysirix.resource import Resource


class Database:
    def __init__(
        self,
        database_name: str,
        database_type: DBType,
        client: Union[SyncClient, AsyncClient],
    ):
        """database access class
        this class allows for manipulation of a database 

        :param database_name: the name of the database to access, or create
                if it does not yet exist
        :param database_type: the type of the database being accessed, or to
                be created if the database does not yet exist
        :param client: the :py:class:`SyncClient` or :py:class:`AsyncClient`
                instance to use for network requests
        """
        self._client = client

        self.database_name = database_name
        self.database_type = database_type

    def create(self):
        return self._client.create_database(self.database_name, self.database_type)

    def get_database_info(self) -> Union[Coroutine, List[Dict]]:
        return self._client.get_database_info(self.database_name)

    def resource(self, resource_name: str):
        """Returns a resource instance

        If a resource with the given name and type does not exist,
        it is created.

        If the resource does not yet exist, it is created

        :param resource_name: the name of the resource to access
        """
        return Resource(
            self.database_name, self.database_type, resource_name, self._client
        )

    def delete(self) -> Optional[Coroutine]:
        """

        :return:
        :raises:
        """
        return self._client.delete_database(self.database_name)
