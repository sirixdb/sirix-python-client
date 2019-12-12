from .client import SirixClient
from .database import Database


def Sirix(
    username: str,
    password: str,
    sirix_uri: str = "https://localhost:9443",
    client_id: str = None,
    client_secret: str = None,
    keycloak_uri: str = "http://localhost:8080",
    allow_self_signed: bool = False,
):
    sirix = SirixClient(
        username=username,
        password=password,
        sirix_uri=sirix_uri,
        client_id=client_id,
        client_secret=client_secret,
        keycloak_uri=keycloak_uri,
        asynchronous=False,
        allow_self_signed=allow_self_signed,
    )
    sirix._init()
    return sirix


async def SirixAsync(
    username: str,
    password: str,
    sirix_uri: str = "https://localhost:9443",
    client_id: str = None,
    client_secret: str = None,
    keycloak_uri: str = "http://localhost:8080",
    allow_self_signed: bool = False,
):
    sirix = SirixClient(
        username=username,
        password=password,
        sirix_uri=sirix_uri,
        client_id=client_id,
        client_secret=client_secret,
        keycloak_uri=keycloak_uri,
        asynchronous=True,
        allow_self_signed=allow_self_signed,
    )
    await sirix._async_init()
    return sirix


__all__ = ["Sirix", "SirixAsync", "SirixClient", "Database"]
