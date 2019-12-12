async def async_get_info(self, ret: bool, fut):
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
