async def async_authenticate(self, fut):
    """Retrieve and store access_token and refresh_token
    This function calls either :ref:`keycloak_auth_call` or
    :ref:`sirix_auth_call` depending on whether or not enough
    information has been provided to access keycloak directly.

    :param self: an instance of :ref:`pysirix.auth.Auth`
    :param fut: an instance of an asynchronous Future
    """
    # if we were provided adequate credentials to authenticate
    # to keycloak directly, then let's do so
    if (
        self._auth_data.client_secret is not None
        and self._auth_data.client_id is not None
        and self._auth_data.keycloak_uri is not None
    ):
        response = await keycloak_auth_call(self)
    else:
        await sirix_auth_call(self)
    try:
        json_res = await response.json()
        self._auth_data.access_token = json_res["access_token"]
        self._auth_data.refresh_token = json_res["refresh_token"]
    except Exception as e:
        raise Exception(e)
    fut.set_result(None)


async def keycloak_auth_call(self):
    async with self._session.post(
        f"{self._auth_data.keycloak_uri}/auth/realms/sirixdb/protocol/openid-connect/token",
        data={
            "username": self._auth_data.username,
            "password": self._auth_data.password,
            "grant_type": "password",
            "client_id": self._auth_data.client_id,
            "client_secret": self._auth_data.client_secret,
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        return response


async def sirix_auth_call(self):
    async with self._session.post(
        f"{self._instance_data.sirix_uri}/token",
        data={
            "username": self._auth_data.username,
            "password": self._auth_data.password,
            "grant_type": "password",
        },
        ssl=False if self._allow_self_signed else True,
    ) as response:
        return response
