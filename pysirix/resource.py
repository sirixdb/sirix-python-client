import json
import xml.etree.ElementTree as ET

from typing import Union, Dict
from .info import AuthData, InstanceData  # for type support

from .utils import handle_async
from .sync.rest import create_resource, update_resource
from .asynchronous.rest import async_create_resource, async_update_resource


class Resource:
    def __init__(self, resource_name: str, parent):
        """database access class
        this class allows for manipulation of a database 

        :param resource_name: the name of the resource being accessed, or to
                be created if the resource does not yet exist
        :param data: the data to initialize the resource with, if it does not
                yet exist
        :param parent: the ``SirixClient`` instance which created this instance
        """
        self._session = parent._session
        self._instance_data: InstanceData = parent._instance_data
        self._auth_data: AuthData = parent._auth_data
        self._asynchronous = parent._asynchronous

        self.database_name = database_name
        self.database_type = database_type
        self.resource_name = resource_name

        self._allow_self_signed = parent._allow_self_signed

    def _create(self, data: str):
        """Creates the resource. Should be called if the resource does not yet exist"""
        if self._asynchronous:
            return handle_async(
                async_create_resource,
                self,
                self.database_name,
                self.database_type,
                self.resource_name,
                data=data,
            )
        else:
            return create_resource(
                self, self.database_type, self.database_type, self.resource_name
            )

    def update(self, data: Union[str, ET.Element, Dict]):
        """Update a resource

        :param data: the updated data, can be of type ``str``, ``dict``, or
                ``xml.etree.ElementTree.Element``
        """
        data = data if type(data) is str else json.dumps(
            data
        ) if self.database_type == "json" else ET.tostring(data)
        if (
            self.resource_name
            not in self._instance_data.database_info[self.database_name]
        ):
            return self._create(data)
        else:
            if self._asynchronous:
                return async_update_resource(self, data)
            else:
                return update_resource(self, data)
