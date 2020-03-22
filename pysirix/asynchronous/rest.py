from typing import Union, Dict, List, Tuple
from datetime import datetime

import xml.etree.ElementTree as ET

from ..utils import handle_async
from ..constants import Revision


async def async_get_info(self, fut, ret: bool):
    async with self._session.get(
        f"{self._instance_data.sirix_uri}/?withResources=true",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json",
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        if response.status == 200:
            info = await response.json()
            self._instance_data.database_info = info["databases"]
        if ret:
            fut.set_result(self._instance_data.database_info)
        else:
            fut.set_result(None)


async def async_create_database(self, fut, db_name, db_type):
    async with self._session.put(
        f"{self._instance_data.sirix_uri}/{db_name}",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json" if db_type == "json" else "application/xml",
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        if response.status == 201:
            # refresh database_info
            await handle_async(async_get_info, False)
            fut.set_result(True)
        else:
            print(response)
            fut.set_result(False)


async def async_create_resource(self, fut, data: str) -> bool:
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    async with self._session.put(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        data=data,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
            "Accept": data_type,
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        if response.status == 200:
            handle_async(async_get_info, False)
            fut.set_result(True)
        else:
            fut.set_result(False)


async def async_read_resource(
    self,
    fut,
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
    async with self._session.get(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json"
            if self.database_type == "json"
            else "application/xml",
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        if self.database_type == "json":
            fut.set_result(await response.json())
        else:
            fut.set_result(ET.fromstring(response.text))


async def async_update_resource(
    self, fut, node_id: int, data: str, insert: str
) -> bool:
    # prepare to get ETag
    params = {"nodeId": node_id}
    data_type = (
        "application/json" if self.database_type == "json" else "application/xml"
    )
    # get ETag
    async with self._session.head(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={"Authorization": f"Bearer {self._auth_data.access_token}"},
    ) as response:
        etag = response.headers().getone("ETag")
    # prepare to update
    params.update({"insert": insert})
    # update
    async with self._session.post(
        f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
        params=params,
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Content-Type": data_type,
            "ETag": etag,
        },
        ssl=False if self._allow_self_signed else True,
        data=data,
    ) as response:
        if response.status == 201:
            fut.set_result(True)
        else:
            fut.set_result(False)


async def async_delete(self, fut, node_id: Union[int, None]):
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
    async with self._session.delete(
        URL_string, params=params, headers=headers
    ) as response:
        if response.status == 204:
            # refresh database_info
            await handle_async(async_get_info, False)
            fut.set_result(True)
        else:
            fut.set_result(False)
