"""
End-to-end check that the hash type a resource is *created with* is the one that is persisted.

Needs a running SirixDB server (see ``test.sh``), like the other end-to-end tests.
Each test creates a resource with one client session and then re-reads its metadata through a
second, independent client session ("independent reopen"). Metadata only carries ``hash`` and
``descendantCount`` when the resource stores node hashes, so their absence/presence is the
persisted setting: absent for ``NONE``, present for ``ROLLING`` and ``POSTORDER``.
"""
import uuid

import httpx
import pytest

import pysirix
from pysirix import DBType

base_url = "http://localhost:9443"
PAYLOAD = {"a": [1, 2]}


def unique_db_name() -> str:
    return "hashtype_" + uuid.uuid4().hex[:12]


def assert_hashes_stored(metadata: dict, expected: bool):
    if expected:
        assert isinstance(metadata["hash"], str) and len(metadata["hash"]) == 16
        assert metadata["descendantCount"] == 3
    else:
        assert "hash" not in metadata
        assert "descendantCount" not in metadata


def sync_session():
    client = httpx.Client(base_url=base_url)
    return client, pysirix.sirix_sync("admin", "admin", client)


def sync_create_and_reopen(db_name: str, **create_kwargs) -> dict:
    client, sirix = sync_session()
    try:
        db = sirix.database(db_name, DBType.JSON)
        db.create()
        db.resource("res").create(PAYLOAD, **create_kwargs)
    finally:
        client.close()
    reopen_client, reopen = sync_session()  # independent session, independent client
    try:
        return reopen.database(db_name, DBType.JSON).resource("res").read_with_metadata(1, 1)["metadata"]
    finally:
        reopen.database(db_name, DBType.JSON).delete()
        reopen_client.close()


@pytest.mark.parametrize(
    "create_kwargs, hashes_stored",
    [
        ({}, False),  # default: hashes are off
        ({"hash_type": "NONE"}, False),
        ({"hash_type": "ROLLING"}, True),
        ({"hash_type": "POSTORDER"}, True),
    ],
)
def test_sync_persisted_hash_type(create_kwargs, hashes_stored):
    metadata = sync_create_and_reopen(unique_db_name(), **create_kwargs)
    assert_hashes_stored(metadata, hashes_stored)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "create_kwargs, hashes_stored",
    [
        ({}, False),
        ({"hash_type": "NONE"}, False),
        ({"hash_type": "ROLLING"}, True),
        ({"hash_type": "POSTORDER"}, True),
    ],
)
async def test_async_persisted_hash_type(create_kwargs, hashes_stored):
    db_name = unique_db_name()
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database(db_name, DBType.JSON)
    await db.create()
    await db.resource("res").create(PAYLOAD, **create_kwargs)
    await client.aclose()

    reopen_client = httpx.AsyncClient(base_url=base_url)  # independent session
    reopen = await pysirix.sirix_async("admin", "admin", reopen_client)
    try:
        resp = await reopen.database(db_name, DBType.JSON).resource("res").read_with_metadata(1, 1)
        assert_hashes_stored(resp["metadata"], hashes_stored)
    finally:
        await reopen.database(db_name, DBType.JSON).delete()
        await reopen_client.aclose()


def test_sync_json_store_create_persists_no_hashes():
    db_name = unique_db_name()
    client, sirix = sync_session()
    try:
        db = sirix.database(db_name, DBType.JSON)
        db.create()
        db.json_store("res").create('{"a":[1,2]}')
    finally:
        client.close()
    reopen_client, reopen = sync_session()
    try:
        md = reopen.database(db_name, DBType.JSON).resource("res").read_with_metadata(1, 1)["metadata"]
        assert_hashes_stored(md, False)
    finally:
        reopen.database(db_name, DBType.JSON).delete()
        reopen_client.close()


@pytest.mark.asyncio
async def test_async_json_store_create_persists_no_hashes():
    db_name = unique_db_name()
    client = httpx.AsyncClient(base_url=base_url)
    sirix = await pysirix.sirix_async("admin", "admin", client)
    db = sirix.database(db_name, DBType.JSON)
    await db.create()
    await db.json_store("res").create('{"a":[1,2]}')
    await client.aclose()

    reopen_client = httpx.AsyncClient(base_url=base_url)
    reopen = await pysirix.sirix_async("admin", "admin", reopen_client)
    try:
        resp = await reopen.database(db_name, DBType.JSON).resource("res").read_with_metadata(1, 1)
        assert_hashes_stored(resp["metadata"], False)
    finally:
        await reopen.database(db_name, DBType.JSON).delete()
        await reopen_client.aclose()


def test_subtree_history_needs_explicit_hashes():
    """For the root object container, ``history(subtree=True)`` needs stored subtree hashes to detect
    descendant changes; with the default (off), its zero hash yields only the first revision."""
    client, sirix = sync_session()
    db_name = unique_db_name()
    try:
        db = sirix.database(db_name, DBType.JSON)
        db.create()
        revisions = {}
        for name, kwargs in (("off", {}), ("rolling", {"hash_type": "ROLLING"})):
            resource = db.resource(name)
            resource.create({"a": [1, 2]}, **kwargs)
            resource.update(3, 5, insert=pysirix.Insert.RIGHT)
            resource.update(3, 7, insert=pysirix.Insert.RIGHT)
            revisions[name] = [r["revisionNumber"] for r in db.json_store(name).history(1)]
        assert revisions == {"off": [1], "rolling": [1, 2, 3]}
    finally:
        sirix.database(db_name, DBType.JSON).delete()
        client.close()
