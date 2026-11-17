"""
Behavioral tests for the ``hashType`` sent when a resource is created.

Node hashes are off by default: omitting ``hash_type`` must send ``hashType=NONE``
through every entry point that creates a resource, and an explicit ``"ROLLING"`` /
``"POSTORDER"`` must reach the server unchanged.

These tests assert at the transport boundary (``httpx.MockTransport`` records the real
PUT request that the client builds), so they need no running SirixDB server.
"""
from contextlib import asynccontextmanager

import httpx
import pytest

import pysirix
from pysirix import DBType, SirixServerError

TOKEN = {
    "access_token": "token",
    "refresh_token": "refresh",
    "token_type": "Bearer",
    "expires_in": 3600,
}


class Recorder:
    """A mock SirixDB that answers the token call and records every other request."""

    def __init__(self, status_code: int = 200, body: str = "[]"):
        self.status_code = status_code
        self.body = body
        self.puts = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/token":
            return httpx.Response(200, json=TOKEN)
        if request.method == "PUT":
            self.puts.append(request)
        return httpx.Response(self.status_code, text=self.body)

    @property
    def only_put(self) -> httpx.Request:
        assert len(self.puts) == 1, f"expected exactly one PUT, got {len(self.puts)}"
        return self.puts[0]


def hash_type_params(request: httpx.Request):
    """All ``hashType`` values on the request (a list, so duplicates would be visible)."""
    return request.url.params.get_list("hashType")


# ---------------------------------------------------------------- synchronous


@pytest.fixture
def sync_env():
    rec = Recorder()
    client = httpx.Client(base_url="http://sirix.test", transport=httpx.MockTransport(rec))
    sirix = pysirix.sirix_sync("admin", "admin", client)
    yield rec, sirix
    sirix.dispose()
    client.close()


def test_sync_resource_create_defaults_to_hash_none(sync_env):
    rec, sirix = sync_env
    sirix.database("db", DBType.JSON).resource("res").create([])
    request = rec.only_put
    assert request.url.path == "/db/res"
    assert hash_type_params(request) == ["NONE"]


def test_sync_client_create_resource_defaults_to_hash_none(sync_env):
    rec, sirix = sync_env
    sirix._client.create_resource("db", DBType.JSON, "res", "[]")
    assert hash_type_params(rec.only_put) == ["NONE"]


def test_sync_json_store_create_defaults_to_hash_none(sync_env):
    rec, sirix = sync_env
    sirix.database("db", DBType.JSON).json_store("res").create()
    assert hash_type_params(rec.only_put) == ["NONE"]


def test_sync_xml_resource_create_defaults_to_hash_none():
    import xml.etree.ElementTree as ET

    rec = Recorder(body="<a/>")
    client = httpx.Client(base_url="http://sirix.test", transport=httpx.MockTransport(rec))
    sirix = pysirix.sirix_sync("admin", "admin", client)
    sirix.database("db", DBType.XML).resource("res").create(ET.fromstring("<a/>"))
    assert hash_type_params(rec.only_put) == ["NONE"]
    sirix.dispose()
    client.close()


@pytest.mark.parametrize("hash_type", ["ROLLING", "POSTORDER", "NONE"])
def test_sync_explicit_hash_type_reaches_server_unchanged(sync_env, hash_type):
    rec, sirix = sync_env
    sirix.database("db", DBType.JSON).resource("res").create([], hash_type=hash_type)
    assert hash_type_params(rec.only_put) == [hash_type]


@pytest.mark.parametrize("hash_type", ["ROLLING", "POSTORDER"])
def test_sync_explicit_hash_type_reaches_server_unchanged_via_client(sync_env, hash_type):
    rec, sirix = sync_env
    sirix._client.create_resource("db", DBType.JSON, "res", "[]", hash_type)
    assert hash_type_params(rec.only_put) == [hash_type]


def test_sync_default_does_not_disturb_other_parameters(sync_env):
    rec, sirix = sync_env
    sirix.database("db", DBType.JSON).resource("res").create(
        {"a": 1}, use_dewey_ids=True, hash_kind="SOME_KIND"
    )
    request = rec.only_put
    assert hash_type_params(request) == ["NONE"]
    assert request.url.params.get_list("useDeweyIDs") == ["true"]
    assert request.url.params.get_list("hashKind") == ["SOME_KIND"]
    assert request.content == b'{"a": 1}'
    assert request.headers["Content-Type"] == "application/json"


def test_sync_invalid_hash_type_is_sent_and_server_error_propagates():
    rec = Recorder(status_code=400, body="Unknown hash type: BOGUS")
    client = httpx.Client(base_url="http://sirix.test", transport=httpx.MockTransport(rec))
    sirix = pysirix.sirix_sync("admin", "admin", client)
    with pytest.raises(SirixServerError) as exc_info:
        sirix.database("db", DBType.JSON).resource("res").create([], hash_type="BOGUS")
    assert hash_type_params(rec.only_put) == ["BOGUS"]
    assert "Unknown hash type: BOGUS" in str(exc_info.value)
    sirix.dispose()
    client.close()


# --------------------------------------------------------------- asynchronous


@asynccontextmanager
async def async_session(rec=None):
    """Plain async context manager (not a fixture) so it works with any pytest-asyncio version."""
    rec = rec or Recorder()
    client = httpx.AsyncClient(
        base_url="http://sirix.test", transport=httpx.MockTransport(rec)
    )
    sirix = await pysirix.sirix_async("admin", "admin", client)
    try:
        yield rec, sirix
    finally:
        sirix.dispose()
        await client.aclose()


@pytest.mark.asyncio
async def test_async_resource_create_defaults_to_hash_none():
    async with async_session() as (rec, sirix):
        await sirix.database("db", DBType.JSON).resource("res").create([])
        request = rec.only_put
        assert request.url.path == "/db/res"
        assert hash_type_params(request) == ["NONE"]


@pytest.mark.asyncio
async def test_async_client_create_resource_defaults_to_hash_none():
    async with async_session() as (rec, sirix):
        await sirix._client.create_resource("db", DBType.JSON, "res", "[]")
        assert hash_type_params(rec.only_put) == ["NONE"]


@pytest.mark.asyncio
async def test_async_json_store_create_defaults_to_hash_none():
    async with async_session() as (rec, sirix):
        await sirix.database("db", DBType.JSON).json_store("res").create()
        assert hash_type_params(rec.only_put) == ["NONE"]


@pytest.mark.asyncio
@pytest.mark.parametrize("hash_type", ["ROLLING", "POSTORDER", "NONE"])
async def test_async_explicit_hash_type_reaches_server_unchanged(hash_type):
    async with async_session() as (rec, sirix):
        await sirix.database("db", DBType.JSON).resource("res").create([], hash_type=hash_type)
        assert hash_type_params(rec.only_put) == [hash_type]


@pytest.mark.asyncio
@pytest.mark.parametrize("hash_type", ["ROLLING", "POSTORDER"])
async def test_async_explicit_hash_type_reaches_server_unchanged_via_client(hash_type):
    async with async_session() as (rec, sirix):
        await sirix._client.create_resource("db", DBType.JSON, "res", "[]", hash_type)
        assert hash_type_params(rec.only_put) == [hash_type]


@pytest.mark.asyncio
async def test_async_invalid_hash_type_is_sent_and_server_error_propagates():
    rec = Recorder(status_code=400, body="Unknown hash type: BOGUS")
    client = httpx.AsyncClient(
        base_url="http://sirix.test", transport=httpx.MockTransport(rec)
    )
    sirix = await pysirix.sirix_async("admin", "admin", client)
    with pytest.raises(SirixServerError) as exc_info:
        await sirix.database("db", DBType.JSON).resource("res").create(
            [], hash_type="BOGUS"
        )
    assert hash_type_params(rec.only_put) == ["BOGUS"]
    assert "Unknown hash type: BOGUS" in str(exc_info.value)
    sirix.dispose()
    await client.aclose()
