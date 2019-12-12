async def async_authenticate(self, allow_self_signed: bool, fut):
    """Retrieve and store access_token and refresh_token"""
    # if we were provided adequate credentials to authenticate
    # to keycloak directly, then let's do so
    if (
        self._auth_data.client_secret is not None
        and self._auth_data.client_id is not None
        and self._auth_data.keycloak_uri is not None
    ):
        response = await self._session.post(
            f"{self._auth_data.keycloak_uri}/auth/realms/sirixdb/protocol/openid-connect/token",
            data={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
                "client_id": self._auth_data.client_id,
                "client_secret": self._auth_data.client_secret,
            },
            ssl=False if allow_self_signed else True,
        )
    else:
        response = await self._session.post(
            f"{self._instance_data.sirix_uri}/token",
            data={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
            },
            ssl=False if allow_self_signed else True,
        )
        self._session.close()
    try:
        json_res = await response.json()
        self._auth_data.access_token = json_res["access_token"]
        self._auth_data.refresh_token = json_res["refresh_token"]
    except Exception as e:
        raise Exception(e)    
    fut.set_result(None)
