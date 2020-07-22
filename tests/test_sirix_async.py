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
    assert type(data.access_token) == str
    assert type(data.refresh_token) == str
    assert type(data.expires_in) == int
    sirix.shutdown()
    await client.aclose()

"""
async def test_delete_resource1():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource1")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_auth_refresh():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    data = sirix._auth._token_data
    await sirix._auth._async_refresh()
    new_data = sirix._auth._token_data
    assert new_data != data
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource2():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource2")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_get_info():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    await sirix.delete_all()
    data = await sirix.get_info()
    assert data == []
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource3():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource3")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_database_create():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.create()
    info = await db.get_database_info()
    assert info["resources"] == []
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource4():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource4")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource5():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource5")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_resource_exists():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource6")
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource6():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource7")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_create_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource8")
    assert await resource.create([]) == "[]"
    assert await resource.exists() is True
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource7():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource9")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource8():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource11")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_nonexistent_resource():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("blah", DBType.JSON)
    resource = db.resource("blah")
    assert await resource.exists() is False
    with pytest.raises(SirixServerError):
        await resource.delete(None, None)
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource9():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource12")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource10():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource14")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource11():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource16")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource12():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource18")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource13():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource20")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource14():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource22")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource15():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource24")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource16():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource26")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource17():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource28")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_read_metadata():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource29")
    await resource.create([])
    resp = await resource.read_with_metadata(1, 1)
    assert resp == {
        "metadata": {
            "nodeKey": 1,
            "hash": "29359c75ea7bce76d9e352a23abf7c69",
            "type": "ARRAY",
            "descendantCount": 0,
            "childCount": 0,
        },
        "value": [],
    }
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource18():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource30")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource19():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource32")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
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
                "nodeKey": 2,
                "insertPositionNodeKey": 1,
                "insertPosition": "asFirstChild",
                "deweyID": "1.3.3",
                "depth": 2,
                "type": "jsonFragment",
                "data": "{}",
            }
        }
    ]
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource20():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource34")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_sirix_query():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource1")
    await resource.create(data_for_query)
    assert await sirix.query(post_query) == '{"rest":[6]}'
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_delete_resource21():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource35")
    await resource.create([])
    await resource.delete(None, None)
    assert await resource.exists() is False
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()


async def test_resource_query():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource2")
    await resource.create(data_for_query)
    assert await resource.query(resource_query) == {"rest": [6]}
    await sirix.delete_all()
    sirix.shutdown()
    await client.aclose()
"""