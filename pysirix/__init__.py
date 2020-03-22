from .client import SirixClient
from .database import Database
from .resource import Resource
from .constants import Insert


def Sirix(
    username: str,
    password: str,
    sirix_uri: str = "https://localhost:9443",
    client_id: str = None,
    client_secret: str = None,
    keycloak_uri: str = "http://localhost:8080",
    allow_self_signed: bool = False,
) -> SirixClient:
    """
    :param username: the username registered with keycloak for this application
    :param password: the password registered with keycloak for this application
    :param sirix_uri: the uri of the sirix instance
    :param client_id: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param client_secret: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param keycloak_uri: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``client_secret`` params).
            This option is not recommended.
    :param allow_self_signed: whether to accept self signed certificates. Not recommended.
    """
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
) -> SirixClient:
    """
    :param username: the username registered with keycloak for this application
    :param password: the password registered with keycloak for this application
    :param sirix_uri: the uri of the sirix instance
    :param client_id: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param client_secret: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param keycloak_uri: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``client_secret`` params).
            This option is not recommended.
    :param allow_self_signed: whether to accept self signed certificates. Not recommended.
    """
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


__all__ = ["Sirix", "SirixAsync", "SirixClient", "Database", "Resource"]
