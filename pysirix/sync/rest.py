def get_info(self, ret: bool):
    response = self._session.get(
        f"{self._instance_data.sirix_uri}/?withResources=true",
        headers={
            "Authorization": f"Bearer {self._auth_data.access_token}",
            "Accept": "application/json",
        },
    )
    if response.status_code == 200:
        self._instance_data.database_info += response.json()["databases"]
    if ret:
        return self._instance_data.database_info