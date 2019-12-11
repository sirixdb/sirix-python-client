from requests import Request, Session

from sirix_client import SirixClient

from typing import Union, List, Dict


def get_sync_session(allow_self_signed: bool = False) -> Session:
    session = Session()
    if allow_self_signed:
        session.verify = False
    return session


def get_token(self: SirixClient) -> None:
    """
    Retrieve and store access_token and refresh_token
    """
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
    request = self._network.prepare_request(request)
    response = self._network.send(request)
    try:
        json_res = response.json()
        self._auth_data.access_token = json_res["access_token"]
        self._auth_data.refresh_token = json_res["refresh_token"]
    except Exception as e:
        raise Exception(e)


def get_sirix_info(
    ret: bool = True, self: SirixClient = None
) -> Union[None, List[Dict[str, str]]]:
    """
    :param ret: whether or not to return the info from the function
    :param self: THIS IS PROVIDED UNDER THE HOOD. USE ONLY IF YOU ARE DEVELOPING
            THIS LIBRARY
    """
    response = self._network.get(
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
