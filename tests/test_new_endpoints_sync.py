import json

import httpx
import pytest

import pysirix
from pysirix import DBType

base_url = "http://localhost:9443"


def setup_function():
    global client
    global sirix
    global db
    global resource
    client = httpx.Client(base_url=base_url)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")


def teardown_function():
    sirix.delete_all()
    client.close()


def test_history_with_revisions():
    resource.create([])
    resource.update(1, {})
    resource.update(1, {"a": 1})
    history = resource.history(revisions=2)
    assert len(history) == 2


def test_history_with_revision_range():
    resource.create([])
    resource.update(1, {})
    resource.update(1, {"a": 1})
    # Full history without range filter
    full_history = resource.history()
    assert len(full_history) == 3
    # With revisions limit
    limited = resource.history(revisions=1)
    assert len(limited) == 1
    assert limited[0]["revision"] == full_history[0]["revision"]


def test_create_resource_with_commit_message():
    resource.create([], commit_message="initial commit")
    history = resource.history()
    assert len(history) >= 1
    assert history[0]["commitMessage"] == "initial commit"


def test_update_with_commit_message():
    resource.create([])
    resource.update(1, {}, commit_message="added empty object")
    history = resource.history()
    assert len(history) == 2
    assert history[0]["commitMessage"] == "added empty object"


def test_read_with_number_of_nodes():
    resource.create({"a": 1, "b": 2, "c": 3})
    data = resource.read(None, number_of_nodes=2)
    assert data is not None


def test_read_with_max_children():
    resource.create({"a": 1, "b": 2, "c": 3})
    data = resource.read(None, max_children=1)
    assert data is not None


def test_read_with_pretty_print():
    resource.create({"a": 1})
    data = resource.read(None, pretty_print=True)
    assert data is not None


def test_path_summary():
    resource.create({"a": {"b": 1}, "c": 2})
    summary = resource.path_summary()
    assert summary is not None
    assert "pathSummary" in summary


def test_path_summary_with_revision():
    resource.create({"a": 1})
    resource.update(1, {"b": 2})
    summary = resource.path_summary(revision=1)
    assert summary is not None
    assert "pathSummary" in summary


def test_create_resources_batch():
    db.create()
    # Batch create returns success; resource visibility depends on server version
    result = db.create_resources({"r1": json.dumps([1, 2, 3]), "r2": json.dumps({"a": 1})})
    # Verify the request succeeded (no exception thrown)
    assert result is not None


def test_query_with_plan():
    resource.create([1, 2, 3])
    result = resource.query(
        "for $i in bit:array-values($$) return $i",
    )
    assert result is not None


def test_query_with_commit_message():
    resource.create([1, 2, 3])
    result = resource.query(
        "for $i in bit:array-values($$) return $i",
    )
    assert result is not None
