from typing import Union, Dict, List, Tuple
from datetime import datetime

import xml.etree.ElementTree as ET

from ..constants import Revision


def get_info(self, ret: bool):
    response = self._session.get(
        f"{self._instance_data.sirix_uri}/?withResources=true",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json",
        },
    )
    if response.status_code == 200:
        self._instance_data.database_info = response.json()["databases"]
    else:
        print(response)
    if ret:
        return self._instance_data.database_info


def create_database(self, db_name, db_type):
    response = self._session.put(
        f"{self._instance_data.sirix_uri}/{db_name}",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": "application/json" if db_type == "json" else "application/xml",
        },
    )
    if response.status_code == 201:
        # refresh database_info
        get_info(self, False)
        return True
    else:
        print(response, response.content)
        return False


def create_resource(self, data: str):
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    response = self._session.put(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        data=data,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
            "Accept": data_type,
        },
    )
    if response.status_code == 200:
        # refresh database_info
        get_info(self, False)
        return True
    else:
        print(response, response.content)
        return False



def read_resource(
    self,
    revision: Union[Revision, Tuple[Revision, Revision], None],
    node_id: Union[int, None],
    max_level: Union[int, None],
) -> Union[ET.Element, Dict, List]:
    params = {}
    if node_id:
        params.update({"nodeId": node_id})
    if max_level:
        params.update({"maxLevel": max_level})
    if revision:
        if isinstance(revision, int):
            params.update({"revision": revision})
        elif isinstance(revision, datetime):
            params.update({"revision-timestamp": revision.isoformat()})
        elif isinstance(revision[0], int):
            params.update({"start-revision": revision[0], "end-revision": revision[1]})
        else:
            params.update(
                {
                    "start-revision-timestamp": revision[0].isoformat(),
                    "end-revision-timestamp": revision[1].isoformat(),
                }
            )

    res = self._session.get(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
    )
    if self.database_type == "json":
        return res.json()
    else:
        return ET.fromstring(res.content)


def update_resource(self, node_id: int, data: str, insert: str) -> bool:
    # prepare to get ETag
    params = {"nodeId": node_id}
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    # get ETag
    response = self._session.head(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={"Authorization": f"Bearer {self._auth_data.access_token}"},
    )
    etag = response.headers.get("ETag")
    # prepare to update
    params.update({"insert": insert})
    # update
    response = self._session.post(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
        },
        data=data,
    )
    if response.status_code == 201:
        return True
    return False


def delete(self, node_id: Union[int, None]):
    params = {}
    headers = {"Authorization": f"Bearer {self._auth_data.access_token}"}
    if node_id is not None:
        URL_string = (
            f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}"
        )
        params.update({"nodeId": node_id})
    if hasattr(self, "database_name"):
        headers.update(
            {
                "Content-Type": "application/json"
                if self.database_type == "json"
                else "application/xml",
            }
        )
    if hasattr(self, "resource_name"):
        URL_string = (
            f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}"
        )
    elif hasattr(self, "database_name"):
        URL_string = f"{self._instance_data.sirix_uri}/{self.database_name}"
    response = self._session.delete(URL_string, params=params, headers=headers)
    if response.status_code == 204:
        # refresh database_info
        get_info(self, False)
        return True
    else:
        return False
