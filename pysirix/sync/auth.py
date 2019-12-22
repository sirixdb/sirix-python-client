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
        request = _keycloak_auth_prepare(self._auth_data)
    # let's authenticate the regular way
    else:
        request = _sirix_auth_prepare(self._auth_data, self._instance_data)
    request = self._session.prepare_request(request)
    response = self._session.send(request)
    try:
        json_res = response.json()
        self._auth_data.access_token = json_res["access_token"]
        self._auth_data.refresh_token = json_res["refresh_token"]
    except Exception as e:
        raise Exception(e)


def _keycloak_auth_prepare(auth_data):
    return Request(
        "POST",
        f"{auth_data.keycloak_uri}/auth/realms/sirixdb/protocol/openid-connect/token",
        data={
            "username": auth_data.username,
            "password": auth_data.password,
            "grant_type": "password",
            "client_id": auth_data.client_id,
            "client_secret": auth_data.client_secret,
        },
    )


def _sirix_auth_prepare(auth_data, instance_data):
    return Request(
        "POST",
        f"{instance_data.sirix_uri}/token",
        data={
            "username": auth_data.username,
            "password": auth_data.password,
            "grant_type": "password",
        },
    )
