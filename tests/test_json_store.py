import json
from datetime import datetime

import httpx
import pysirix
from pysirix import DBType

base_url = "http://localhost:9443"


def setup_function():
    global client
    global sirix
    global store
    client = httpx.Client(base_url=base_url)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    store = db.json_store("test_resource")


def teardown_function():
    sirix.delete_all()
    client.close()


def test_create_store():
    assert store.create() == "[]"


def test_exists():
    assert store.exists() is False
    store.create()
    assert store.exists() is True


def test_insert_one():
    store.create()
    doc = {"city": "Brooklyn", "state": "NY"}
    assert store.insert_one(doc) == '{"rest":[]}'


def test_insert_many():
    store.create()
    doc = [
        {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}},
        {"generic": 1, "location": {"state": "NY", "city": "New York"}},
    ]
    store.insert_many(doc)
    assert len(store.find_all({"generic": 1})) == 2


def test_find_all_store():
    store.create()
    store.insert_one({"city": "New York", "state": "NY"})
    response = store.find_all({"city": "New York"}, node_key=False)
    assert type(response) is list and len(response) == 1
    assert response[0] == {"city": "New York", "state": "NY"}
    response = store.find_all({"city": "New York"})
    assert response[0] == {"city": "New York", "state": "NY", "nodeKey": 2}


def test_find_all_projection():
    store.create()
    store.insert_one({"key": 1, "location": {"state": "NY", "city": "New York"}})
    store.insert_one({"key": 2, "location": {"state": "CA", "city": "Los Angeles"}})
    response = store.find_all({"key": 2}, ["location"], node_key=False)
    assert response[0] == {
        "location": {"state": "CA", "city": "Los Angeles"},
    }
    response = store.find_all({"key": 2}, ["location"])
    assert response[0] == {
        "location": {"state": "CA", "city": "Los Angeles"},
        "nodeKey": 11,
    }


def test_find_all_old_revision_number():
    store.create()
    store.insert_one({"city": "New York", "state": "NY"})
    response = store.find_all({"city": "New York"}, revision=1)
    assert response == []
    response = store.find_all({"city": "New York"}, revision=2)
    assert response == [{"city": "New York", "state": "NY", "nodeKey": 2}]


def test_find_all_old_revision_date():
    store.create()
    timestamp = datetime.utcnow()
    store.insert_one({"city": "New York", "state": "NY"})
    response = store.find_all({"city": "New York"}, revision=timestamp)
    assert response == []


def test_find_one():
    store.create()
    store.insert_many(
        [
            {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}},
            {"generic": 1, "location": {"state": "NY", "city": "New York"}},
        ]
    )
    response = store.find_one({"generic": 1})
    assert response == [
        {
            "generic": 1,
            "location": {"state": "CA", "city": "Los Angeles"},
            "nodeKey": 2,
        }
    ]


def test_history():
    store.create()
    store.insert_one({"generic": 1, "location": {"state": "NY", "city": "New York"}})
    store.insert_one({"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}})
    assert len(store.resource_history()) == 3
    history = store.history(11)
    assert len(history) == 1
    history = history[0]
    assert type(history["revisionTimestamp"]) == str
    assert type(history["revisionNumber"]) == int
    assert len(history) == 2
    assert len(store.history(11, subtree=False)[0]) == 3


def test_update_by_key():
    store.create()
    store.insert_one({"generic": 1, "location": {"state": "NY", "city": "New York"}})
    store.update_by_key(2, {"location": {"state": "CA", "city": "Los Angeles"}})
    assert store.find_one({"generic": 1}, node_key=False) == [
        {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}}
    ]


def test_update_many():
    store.create()
    store.insert_many(
        [
            {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}},
            {"generic": 2, "location": {"state": "NY", "city": "New York"}},
        ]
    )
    store.update_many({"generic": 2}, "generic", 1)
    assert len(store.find_all({"generic": 1})) == 2


def test_delete_field():
    store.create()
    store.insert_one({"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}})
    store.delete_field({"generic": 1}, "location")
    assert store.find_one({"generic": 1}, node_key=False) == [{"generic": 1}]


def test_delete_record():
    store.create()
    store.insert_many(
        [
            {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}},
            {"generic": 2, "location": {"state": "NY", "city": "New York"}},
            {"generic": 1, "location": {"state": "CA", "city": "Los Angeles"}},
            {"generic": 2, "location": {"state": "NY", "city": "New York"}},
        ]
    )
    store.delete_records({"generic": 1})
    assert len(store.find_all({"generic": 1})) == 0
