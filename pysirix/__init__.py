import httpx

from pysirix.sirix import Sirix
from pysirix.database import Database
from pysirix.resource import Resource
from pysirix.constants import Insert, DBType


def sirix_sync(
    username: str,
    password: str,
    client: httpx.Client,
) -> Sirix:
    """
    :param username: the username registered with keycloak for this application.
    :param password: the password registered with keycloak for this application.
    :param client: an ``httpx.Client`` instance. You should instantiate the instance with
            the ``base_url`` param as the url for the sirix database.
    """
    s = Sirix(
        username=username,
        password=password,
        client=client,
    )
    s.authenticate()
    return s


async def sirix_async(
    username: str,
    password: str,
    client: httpx.AsyncClient,
) -> Sirix:
    """
    :param username: the username registered with keycloak for this application.
    :param password: the password registered with keycloak for this application.
    :param client: an ``httpx.AsyncClient`` instance. You should instantiate the instance with
            the ``base_url`` param as the url for the sirix database.
    """
    s = Sirix(
        username=username,
        password=password,
        client=client,
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
