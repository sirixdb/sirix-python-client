import json
import xml.etree.ElementTree as ET

from typing import Union, Dict, Tuple

from .resource import Resource

from .sync.rest import create_database, delete
from .asynchronous.rest import async_create_database, async_delete
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
            if db["name"] == self.database_name
        ]
        if len(database_list) != 0:
            self.database_type: str = database_list[0]["type"]
        elif self.database_type:
            self.database_type: str = self.database_type.lower()
            if self._asynchronous:
                return handle_async(
                    async_create_database, self, self.database_name, self.database_type
                )
            else:
                return create_database(self, self.database_name, self.database_type)
        else:
            raise Exception(
                "No database type specified, and database does not already exist"
            )

    def resource(self, resource_name: str, data: Union[str, ET.Element, Dict] = None):
        """Returns a resource instance

        If a resource with the given name and type does not exist,
        it is created.

        If the resource does not yet exist, it is created

        :param resource_name: the name of the resource to aceess
        :param data: data to initialize resource with if it does
                yet exist
        """
        resource = Resource(resource_name, parent=self)
        if self._asynchronous:
            return handle_async(resource._async_init(), data)
        else:
            resource._init(data)
        return resource

    def delete(self) -> bool:
        if self._asynchronous:
            return handle_async(async_delete, self, None)
        else:
            return delete(self, None)
