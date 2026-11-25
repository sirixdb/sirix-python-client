"""
Behavioral tests for a missing ETag.

Servers stop sending an ``ETag`` header when a resource has no node hashes, so
``get_etag`` must return ``None`` instead of raising, and update/delete must simply
omit the ``ETag`` request header. A present ETag keeps working unchanged.

Asserted at the transport boundary (``httpx.MockTransport``); no SirixDB needed.
"""
import asyncio

import httpx
import pytest

import pysirix
from pysirix import DBType, Insert

TOKEN = {
    "access_token": "token",
    "refresh_token": "refresh",
    "token_type": "Bearer",
    "expires_in": 3600,
}


class Server:
    def __init__(self, etag_headers):
        self.etag_headers = etag_headers
        self.requests = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.url.path == "/token":
            return httpx.Response(200, json=TOKEN)
        self.requests.append(request)
        headers = self.etag_headers if request.method == "HEAD" else {}
        return httpx.Response(200, headers=headers, text="ok")

    def sent(self, method):
        return [r for r in self.requests if r.method == method]


ABSENT = {}
EMPTY = {"ETag": ""}
PRESENT = {"ETag": '"abc"'}


@pytest.fixture
def make_sync():
    opened = []

    def make(etag_headers):
        server = Server(etag_headers)
        client = httpx.Client(
            base_url="http://sirix.test", transport=httpx.MockTransport(server)
        )
        opened.append(client)
        resource = pysirix.sirix_sync("admin", "admin", client).database(
            "db", DBType.JSON
        ).resource("res")
        return server, resource

    yield make
    for c in opened:
        c.close()


def run_async(etag_headers, action):
    async def go():
        server = Server(etag_headers)
        async with httpx.AsyncClient(
            base_url="http://sirix.test", transport=httpx.MockTransport(server)
        ) as client:
            sirix = await pysirix.sirix_async("admin", "admin", client)
            resource = sirix.database("db", DBType.JSON).resource("res")
            result = await action(resource)
        return server, result

    return asyncio.run(go())


@pytest.mark.parametrize("headers", [ABSENT, EMPTY])
def test_sync_get_etag_missing_is_none(make_sync, headers):
    _, resource = make_sync(headers)
    assert resource.get_etag(1) is None


def test_sync_get_etag_present_is_returned(make_sync):
    _, resource = make_sync(PRESENT)
    assert resource.get_etag(1) == '"abc"'


@pytest.mark.parametrize("headers", [ABSENT, EMPTY])
def test_sync_update_without_etag_omits_header(make_sync, headers):
    server, resource = make_sync(headers)
    resource.update(1, "[]", Insert.CHILD)
    assert "etag" not in server.sent("POST")[0].headers


@pytest.mark.parametrize("headers", [ABSENT, EMPTY])
def test_sync_delete_without_etag_omits_header(make_sync, headers):
    server, resource = make_sync(headers)
    resource.delete(1, None)
    assert "etag" not in server.sent("DELETE")[0].headers


def test_sync_update_and_delete_forward_present_etag(make_sync):
    server, resource = make_sync(PRESENT)
    resource.update(1, "[]", Insert.CHILD)
    resource.delete(1, None)
    assert server.sent("POST")[0].headers["etag"] == '"abc"'
    assert server.sent("DELETE")[0].headers["etag"] == '"abc"'


@pytest.mark.parametrize("headers", [ABSENT, EMPTY])
def test_async_get_etag_missing_is_none(headers):
    _, etag = run_async(headers, lambda r: r.get_etag(1))
    assert etag is None


def test_async_get_etag_present_is_returned():
    _, etag = run_async(PRESENT, lambda r: r.get_etag(1))
    assert etag == '"abc"'


@pytest.mark.parametrize("headers", [ABSENT, EMPTY])
def test_async_update_and_delete_without_etag_omit_header(headers):
    async def action(r):
        await r.update(1, "[]", Insert.CHILD)
        await r.delete(1, None)

    server, _ = run_async(headers, action)
    assert "etag" not in server.sent("POST")[0].headers
    assert "etag" not in server.sent("DELETE")[0].headers


def test_async_update_and_delete_forward_present_etag():
    async def action(r):
        await r.update(1, "[]", Insert.CHILD)
        await r.delete(1, None)

    server, _ = run_async(PRESENT, action)
    assert server.sent("POST")[0].headers["etag"] == '"abc"'
    assert server.sent("DELETE")[0].headers["etag"] == '"abc"'
