import httpx
import pytest
from httpx import HTTPError

import pysirix
from pysirix import DBType
from pysirix.errors import SirixServerError

base_url = "https://localhost:9443"
verify = "tests/resources/cert.pem"


def setup_function():
    global client
    global sirix
    global resource
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")


def teardown_function():
    sirix.delete_all()
    client.close()


def test_delete_resource():
    resource.create([])
    resource.delete(None, None)
    assert resource.exists() is False


def test_delete_nonexistent_resource():
    assert resource.exists() is False
    with pytest.raises(SirixServerError):
        resource.delete(None, None)


def test_read_resource():
    resource.create([])
    data = resource.read(None)
    assert data == []


def test_get_etag():
    resource.create([])
    etag = resource.get_etag(1)
    assert type(etag) == str


def test_get_etag_nonexistent():
    resource.create([])
    with pytest.raises(SirixServerError):
        resource.get_etag(2)


def test_delete_by_node_id():
    resource.create([])
    resource.delete(1, None)
    with pytest.raises(SirixServerError):
        resource.delete(1, None)


def test_delete_by_etag():
    resource.create([])
    etag = resource.get_etag(1)
    resource.delete(1, etag)
    with pytest.raises(SirixServerError):
        resource.delete(1, None)


def test_update_by_etag():
    resource.create([])
    etag = resource.get_etag(1)
    resource.update(1, {}, etag=etag)
    assert resource.read(None) == [{}]


def test_update_by_node_id():
    resource.create([])
    resource.update(1, {})
    assert resource.read(None) == [{}]


def test_update_nonexistent_node():
    resource.create([])
    with pytest.raises(SirixServerError):
        resource.update(5, {})


def test_read_metadata():
    resource.create([])
    resp = resource.read_with_metadata(1, 1)
    assert resp == {
        "metadata": {
            "nodeKey": 1,
            "hash": 54776712958846245656800940890181827689,
            "type": "ARRAY",
            "descendantCount": 0,
            "childCount": 0,
        },
        "value": [],
    }


def test_history():
    resource.create([])
    resource.update(1, {})
    resource.delete(2, None)
    assert len(resource.history()) == 3


def test_diff():
    resource.create([])
    resource.update(1, {})
    assert resource.diff(1, 2) == [
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


def test_query():
    resource.create([])
    assert resource.query("for $i in bit:array-values(.) return $i") == {"rest": []}
