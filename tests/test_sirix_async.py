import pytest
import httpx

import pysirix
from pysirix import DBType
from pysirix.errors import SirixServerError

from .data import data_for_query, post_query, resource_query

base_url = "http://localhost:9443"

pytestmark = pytest.mark.asyncio


async def test_sirix_async_init():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = sirix._auth._token_data
    assert type(data["access_token"]) == str
    assert type(data["refresh_token"]) == str
    assert type(data["expires_in"]) == int
    await client.aclose()


async def test_auth_refresh():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = sirix._auth._token_data
    await sirix._auth._async_refresh()
    new_data = sirix._auth._token_data
    assert new_data != data
    await client.aclose()


async def test_get_info():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    await sirix.delete_all()
    data = await sirix.get_info()
    assert data == []
    await sirix.delete_all()
    await client.aclose()


async def test_database_create():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.create()
    info = await db.get_database_info()
    assert info["resources"] == []
    await sirix.delete_all()
    await client.aclose()


async def test_database_delete():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.create()
    await db.delete()
    with pytest.raises(SirixServerError):
        await db.get_database_info()
    await sirix.delete_all()
    await client.aclose()


async def test_resource_exists():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource6")
    assert await resource.exists() is False
    await sirix.delete_all()
    await client.aclose()


async def test_create_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource8")
    assert await resource.create([]) == "[]"
    assert await resource.exists() is True
    await sirix.delete_all()
    await client.aclose()


async def test_delete_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource10")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    await client.aclose()


async def test_delete_nonexistent_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("blah", DBType.JSON)
    resource = db.resource("blah")
    assert await resource.exists() is False
    with pytest.raises(SirixServerError):
        await resource.delete(None, None)
    await client.aclose()


async def test_read_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource13")
    await resource.create([])
    data = await resource.read(None)
    assert data == []
    await sirix.delete_all()
    await client.aclose()


async def test_get_etag():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource15")
    await resource.create([])
    etag = await resource.get_etag(1)
    assert type(etag) == str
    await sirix.delete_all()
    await client.aclose()


async def test_get_etag_nonexistent():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource17")
    await resource.create([])
    with pytest.raises(SirixServerError):
        await resource.get_etag(2)
    await sirix.delete_all()
    await client.aclose()


async def test_delete_by_node_id():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource19")
    await resource.create({})
    await resource.delete(1, None)
    with pytest.raises(SirixServerError):
        await resource.delete(1, None)
    await sirix.delete_all()
    await client.aclose()


async def test_delete_by_etag():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource21")
    await resource.create({})
    etag = await resource.get_etag(1)
    await resource.delete(1, etag)
    with pytest.raises(SirixServerError):
        await resource.delete(1, None)
    await sirix.delete_all()
    await client.aclose()


async def test_update_by_etag():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource23")
    await resource.create([])
    etag = await resource.get_etag(1)
    await resource.update(1, {}, etag=etag)
    assert await resource.read(None) == [{}]
    await sirix.delete_all()
    await client.aclose()


async def test_update_by_node_id():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource25")
    await resource.create([])
    await resource.update(1, {})
    assert await resource.read(None) == [{}]
    await sirix.delete_all()
    await client.aclose()


async def test_update_nonexistent_node():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource27")
    await resource.create([])
    with pytest.raises(SirixServerError):
        await resource.update(5, {})
    await sirix.delete_all()
    await client.aclose()


async def test_read_metadata():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource29")
    await resource.create([])
    resp = await resource.read_with_metadata(1, 1)
    metadata = resp["metadata"]
    # Verify hash exists and is a 16-character hex string
    assert "hash" in metadata
    assert isinstance(metadata["hash"], str)
    assert len(metadata["hash"]) == 16
    assert all(c in "0123456789abcdef" for c in metadata["hash"])
    # Verify other metadata fields
    assert metadata["nodeKey"] == 1
    assert metadata["type"] == "ARRAY"
    assert metadata["descendantCount"] == 0
    assert metadata["childCount"] == 0
    assert resp["value"] == []
    await sirix.delete_all()
    await client.aclose()


async def test_history():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource31")
    await resource.create([])
    await resource.update(1, {})
    await resource.delete(2, None)
    assert len(await resource.history()) == 3
    await sirix.delete_all()
    await client.aclose()


async def test_diff():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource33")
    await resource.create([])
    await resource.update(1, {})
    assert await resource.diff(1, 2) == [
        {
            "insert": {
                "data": "{}",
                "depth": 2,
                "deweyID": "1.17.17",
                "insertPosition": "asFirstChild",
                "insertPositionNodeKey": 1,
                "nodeKey": 2,
                "type": "jsonFragment",
            }
        }
    ]
    await sirix.delete_all()
    await client.aclose()


async def test_sirix_query():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource1")
    await resource.create(data_for_query)
    assert await sirix.query(post_query) == '{"rest":[6]}'
    await sirix.delete_all()
    await client.aclose()


async def test_resource_query():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource2")
    await resource.create(data_for_query)
    assert await resource.query(resource_query) == {"rest": [6]}
    await sirix.delete_all()
    await client.aclose()
