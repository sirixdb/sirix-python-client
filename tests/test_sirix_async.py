import pytest
import httpx
from httpx import HTTPError

import pysirix
from pysirix import DBType

base_url = "https://localhost:9444"
verify = "./resources/cert.pem"

pytestmark = pytest.mark.asyncio


async def test_sirix_async_init():
    client = httpx.AsyncClient(base_url=base_url, verify=verify)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = sirix._auth._token_data
    assert type(data.access_token) == str
    assert type(data.refresh_token) == str
    assert type(data.expires_in) == int
    await client.aclose()
    sirix._auth._timer.cancel()


async def test_auth_refresh():
    client = httpx.AsyncClient(base_url=base_url, verify=verify)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = sirix._auth._token_data
    await sirix._auth._async_refresh()
    new_data = sirix._auth._token_data
    assert new_data != data
    await client.aclose()
    sirix._auth._timer.cancel()


async def test_get_info():
    client = httpx.AsyncClient(base_url=base_url, verify=verify)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = await sirix.get_info()
    assert data == []
    await client.aclose()


async def test_database_create():
    client = httpx.AsyncClient(base_url=base_url, verify=verify)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.create()
    info = await db.get_database_info()
    assert info["resources"] == []
    await client.aclose()


async def test_database_delete():
    client = httpx.AsyncClient(base_url=base_url, verify=verify)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.delete()
    with pytest.raises(HTTPError):
        await db.get_database_info()
    await client.aclose()
