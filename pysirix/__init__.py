import httpx

from pysirix.sirix import Sirix
from pysirix.database import Database
from pysirix.resource import Resource
from pysirix.constants import Insert, DBType


def sirix_sync(
    username: str,
    password: str,
    client: httpx.Client,
    client_id: str = None,
    client_secret: str = None,
) -> Sirix:
    """
    :param username: the username registered with keycloak for this application.
    :param password: the password registered with keycloak for this application.
    :param client: an ``httpx.Client`` instance. You should instantiate the instance with
            the ``base_url`` param as the url for the sirix database.
    :param client_id: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param client_secret: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    """
    s = Sirix(
        username=username,
        password=password,
        client=client,
        client_id=client_id,
        client_secret=client_secret,
    )
    s.authenticate()
    return s


async def sirix_async(
    username: str,
    password: str,
    client: httpx.AsyncClient,
    client_id: str = None,
    client_secret: str = None,
) -> Sirix:
    """
    :param username: the username registered with keycloak for this application.
    :param password: the password registered with keycloak for this application.
    :param client: an ``httpx.AsyncClient`` instance. You should instantiate the instance with
            the ``base_url`` param as the url for the sirix database.
    :param client_id: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    :param client_secret: optional parameter, for authenticating directly with
            keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
            This option is not recommended.
    """
    s = Sirix(
        username=username,
        password=password,
        client=client,
        client_id=client_id,
        client_secret=client_secret,
    )
    await s.authenticate()
    return s


__all__ = [
    "sirix_sync",
    "sirix_async",
    "Sirix",
    "Database",
    "Resource",
    "Insert",
    "DBType",
]
