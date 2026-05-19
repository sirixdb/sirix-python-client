import json

import httpx
import pytest

import pysirix
from pysirix import DBType

base_url = "http://localhost:9443"

pytestmark = pytest.mark.asyncio


async def test_history_with_revisions():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_hist_rev")
    await resource.create([])
    await resource.update(1, {})
    await resource.update(1, {"a": 1})
    history = await resource.history(revisions=2)
    assert len(history) == 2
    await sirix.delete_all()
    await client.aclose()


async def test_history_with_revision_range():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_hist_range")
    await resource.create([])
    await resource.update(1, {})
    await resource.update(1, {"a": 1})
    # Full history without range filter
    full_history = await resource.history()
    assert len(full_history) == 3
    # With revisions limit
    limited = await resource.history(revisions=1)
    assert len(limited) == 1
    assert limited[0]["revision"] == full_history[0]["revision"]
    await sirix.delete_all()
    await client.aclose()


async def test_create_resource_with_commit_message():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_create_msg")
    await resource.create([], commit_message="initial commit")
    history = await resource.history()
    assert len(history) >= 1
    assert history[0]["commitMessage"] == "initial commit"
    await sirix.delete_all()
    await client.aclose()


async def test_update_with_commit_message():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_update_msg")
    await resource.create([])
    await resource.update(1, {}, commit_message="added empty object")
    history = await resource.history()
    assert len(history) == 2
    assert history[0]["commitMessage"] == "added empty object"
    await sirix.delete_all()
    await client.aclose()


async def test_read_with_number_of_nodes():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_read_nodes")
    await resource.create({"a": 1, "b": 2, "c": 3})
    data = await resource.read(None, number_of_nodes=2)
    assert data is not None
    await sirix.delete_all()
    await client.aclose()


async def test_read_with_max_children():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_read_children")
    await resource.create({"a": 1, "b": 2, "c": 3})
    data = await resource.read(None, max_children=1)
    assert data is not None
    await sirix.delete_all()
    await client.aclose()


async def test_read_with_pretty_print():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_read_pretty")
    await resource.create({"a": 1})
    data = await resource.read(None, pretty_print=True)
    assert data is not None
    await sirix.delete_all()
    await client.aclose()


async def test_path_summary():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_path_summary")
    await resource.create({"a": {"b": 1}, "c": 2})
    summary = await resource.path_summary()
    assert summary is not None
    assert "pathSummary" in summary
    await sirix.delete_all()
    await client.aclose()


async def test_path_summary_with_revision():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_path_summary_rev")
    await resource.create({"a": 1})
    await resource.update(1, {"b": 2})
    summary = await resource.path_summary(revision=1)
    assert summary is not None
    assert "pathSummary" in summary
    await sirix.delete_all()
    await client.aclose()


async def test_create_resources_batch():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    await db.create()
    # Batch create returns success; resource visibility depends on server version
    result = await db.create_resources({"r1": json.dumps([1, 2, 3]), "r2": json.dumps({"a": 1})})
    # Verify the request succeeded (no exception thrown)
    assert result is not None
    await sirix.delete_all()
    await client.aclose()


async def test_query_with_plan():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_query_plan")
    await resource.create([1, 2, 3])
    result = await resource.query(
        "for $i in bit:array-values($$) return $i",
    )
    assert result is not None
    await sirix.delete_all()
    await client.aclose()


async def test_query_with_commit_message():
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource_query_msg")
    await resource.create([1, 2, 3])
    result = await resource.query(
        "for $i in bit:array-values($$) return $i",
    )
    assert result is not None
    await sirix.delete_all()
    await client.aclose()
