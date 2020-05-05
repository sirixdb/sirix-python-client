import httpx

import pysirix
from pysirix import DBType

base_url = "https://localhost:9443"
verify = "tests/resources/cert.pem"


def setup_function():
    global client
    global sirix
    global store
    client = httpx.Client(base_url=base_url, verify=verify)
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


def test_insert_into_store():
    store.create()
    assert (
        store.insert_one({"city": "Brooklyn", "state": "NY"})
        == '[{"city":"Brooklyn","state":"NY"}]'
    )


def test_find_all_store():
    store.create()
    store.insert_one({"city": "New York", "state": "NY"})
    response = store.find_all({"city": "New York"}, node_key=False)
    assert type(response["rest"]) is list and len(response["rest"]) == 1
    assert response["rest"][0] == {"city": "New York", "state": "NY"}
    response = store.find_all({"city": "New York"})
    assert response["rest"][0] == {"city": "New York", "state": "NY", "nodeKey": 2}


def test_find_all_projection():
    store.create()
    store.insert_one({"key": 1, "location": {"state": "NY", "city": "New York"}})
    store.insert_one({"key": 2, "location": {"state": "CA", "city": "Los Angeles"}})
    response = store.find_all({"key": 2}, ["location"], node_key=False)
    assert response["rest"][0] == {
        "location": {"state": "CA", "city": "Los Angeles"},
    }
    response = store.find_all({"key": 2}, ["location"])
    assert response["rest"][0] == {
        "location": {"state": "CA", "city": "Los Angeles"},
        "nodeKey": 11,
    }