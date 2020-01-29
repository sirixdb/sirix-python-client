from typing import Union

from ..utils import handle_async


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
    async with self._session.post(
        f"{self._instance_data.sirix_uri}/{db_name}",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json" if db_type == "json" else "application/xml",
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        if response.status == 200:
            # refresh database_info
            await handle_async(async_get_info, False)
            fut.set_result(True)
        else:
            print(response)
            fut.set_result(False)


async def async_create_resource(self, fut, data) -> bool:
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
    ) as response:
        if response.status == 200:
            fut.set_result(True)
        else:
            fut.set_result(False)


async def async_update_resource(self, fut, nodeId: int, data: str, insert: str) -> bool:
    # prepare to get ETag
    params = {"nodeId": nodeId}
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
        },
        data=data,
    ) as response:
        if response.status == 201:
            fut.set_result(True)
        else:
            fut.set_result(False)


async def async_delete(self, fut, nodeId: Union[int, None]):
    if nodeId is not None:
        async with self._session.delete(
            f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}?nodeId={nodeId}",
            headers={
                "Authorization": f"Bearer {self._auth_data.access_token}",
                "Content-Type": self.database_type,
            },
        ) as response:
            if response.status == 204:
                fut.set_result(True)
            else:
                fut.set_result(False)
    if hasattr(self, "resource_name"):
        async with self._session.delete(
            f"{self._instance_data.sirix_uri}/{self.database_name}/{self.resource_name}",
            headers={
                "Authorization": f"Bearer {self._auth_data.access_token}",
                "Content-Type": self.database_type,
            },
        ) as response:
            if response.status == 204:
                fut.set_result(True)
            else:
                fut.set_result(False)
    elif hasattr(self, "database_name"):
        async with self._session.delete(
            f"{self._instance_data.sirix_uri}/{self.database_name}",
            headers={
                "Authorization": f"Bearer {self._auth_data.access_token}",
                "Content-Type": self.database_type,
            },
        ) as response:
            if response.status == 204:
                fut.set_result(True)
            else:
                fut.set_result(False)
    else:
        async with self._session.delete(
            self._instance_data.sirix_uri,
            headers={"Authorization": f"Bearer {self._auth_data.access_token}"},
        ) as response:
            if response.status == 204:
                fut.set_result(True)
            else:
                fut.set_result(False)

