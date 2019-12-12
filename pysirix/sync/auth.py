from requests import Request


def authenticate(self) -> None:
    """Retrieve and store access_token and refresh_token"""
    # if we were provided adequate credentials to authenticate
    # to keycloak directly, then let's do so
    if (
        self._auth_data.client_secret is not None
        and self._auth_data.client_id is not None
        and self._auth_data.keycloak_uri is not None
    ):
        request = Request(
            "POST",
            f"{self._auth_data.keycloak_uri}/auth/realms/sirixdb/protocol/openid-connect/token",
            data={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
                "client_id": self._auth_data.client_id,
                "client_secret": self._auth_data.client_secret,
            },
        )
    # let's authenticate the regular way
    else:
        request = Request(
            "POST",
            f"{self._instance_data.sirix_uri}/token",
            data={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
            },
        )
    request = self._session.prepare_request(request)
    response = self._session.send(request)
    try:
        json_res = response.json()
        self._auth_data.access_token = json_res["access_token"]
        self._auth_data.refresh_token = json_res["refresh_token"]
    except Exception as e:
        raise Exception(e)
