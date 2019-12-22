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


async def async_update_resource(self, data):
    pass
