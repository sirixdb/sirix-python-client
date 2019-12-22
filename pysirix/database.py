import json
import xml.etree.ElementTree as ET

from typing import Union, Dict

from requests import Session  # for type support

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
        self._session: Session = parent._session
        self._instance_data: InstanceData = parent._instance_data
        self._auth_data: AuthData = parent._auth_data

        self.database_name = database_name
        
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
        if self._asynchronous:
            return handle_async(async_create_database, self, self.database_name, self.database_type)
        else:
            return create_database(self, self.database_type, self.database_type)

    def update(self, resource: str, data: Union[str, ET.Element, Dict]):
        """Update a resource

        :param resource: the name of the resource to update
        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        :param data_type: the type of database being accessed
        """
        if self.exists:
            if self.database_type == "json":
                data_type = "application/json"
            else:
                data_type = ("application/xml",)
            return self._session.put(
                f"{self._instance_data.sirix_uri}/{self.database_name}/{resource}",
                data=data
                if type(data) is str
                else json.dumps(data)
                if self.database_type == "json"
                else ET.tostring(data),
                headers={
                    "Authorization": f"Bearer {self._auth_data.access_token}",
                    "Content-Type": data_type,
                    "Accept": data_type,
                },
            )
