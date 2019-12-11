from requests import Request, Session
from xml.etree import ElementTree as ET
import json

from sirix_client import SirixClient

def update(
    data, resource: str, database: str = None, data_type: str = None, self: SirixClient = None
):
    """
    :param: `data` the updated data, can be of type `str`, `dict`, or
            `xml.etree.ElementTree.Element` 
    :param: `resource` the name of the resource to update
    :param: `database` the name of the database to update.
            On a database instance, this param is provided internally
    :param: `data_type` the type of database being accessed
            On a database instance, this param is provided internally
    :param: `self` THIS IS PROVIDED UNDER THE HOOD. PRETEND THIS PARAM DOES
            NOT EXIST.
    """
    
    if data_type:
        pass
    elif self.database_type == "json":
        data_type = "application/json"
    else:
        data_type = "application/xml",
    return self._network.put(
        f"{self._instance_data.sirix_uri}/{database if database else self.database_name}/{resource}",
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
