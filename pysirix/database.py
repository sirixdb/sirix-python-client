import json
import xml.etree.ElementTree as ET

from typing import Union, Dict, Tuple

from .resource import Resource

from .sync.rest import create_database
from .asynchronous.rest import async_create_database
from .utils import handle_async

from .info import AuthData, InstanceData  # for type support


class Database:
    def __init__(self, database_name: str, database_type: str, parent):
        """database access class
        this class allows for manipulation of a database 

        :param database_name: the name of the database to access, or create
                if it does not yet exist
        :param database_type: the type of the database being accessed, or to
                be created if the database does not yet exist
        :param parent: the ``SirixClient`` instance which created this instance
        """
        self._session = parent._session
        self._instance_data: InstanceData = parent._instance_data
        self._auth_data: AuthData = parent._auth_data
        self._asynchronous = parent._asynchronous

        self.database_name = database_name
        self.database_type = database_type

        self._allow_self_signed = parent._allow_self_signed

    def _init(self):
        database_list = [
            db
            for db in self._instance_data.database_info
            if db["name"] == database_name
        ]
        if len(database_list) != 0:
            self.database_type: str = database_list[0]["type"]
        elif self.database_type:
            self.database_type: str = self.database_type.lower()
            self._create()
        else:
            raise Exception(
                "No database type specified, and database does not already exist"
            )

    def _create(self):
        """Creates the database. Should be called if the database does not yet exist"""
        if self._asynchronous:
            return handle_async(
                async_create_database, self, self.database_name, self.database_type
            )
        else:
            return create_database(self, self.database_type, self.database_type)

    def __getitem__(self, key: str):
        """
        Returns a resource instance. See :meth:`_get_resource` for further information
        """
        return self._get_resource(key)

    def _get_resource(self, resource_name: str, data: Union[str, ET.Element, Dict] = None):
        """Returns a resource instance

        If a resource with the given name and type does not exist,
        it is created.

        If the resource does not yet exist, it is created

        :param database_name: the name of the database to access
        :param database_type: the type of the database to access
        :param resource_name: the name of the resource to aceess
        :param data: data to initialize resource with if it does
                yet exist

        You shouldn't use this method directly, rather, you should use index access, as follows:
            >>> sirix = Sirix(params)
            >>> sirix[(database_name, database_type)]
        """
        return Resource(resource_name, parent=self)
