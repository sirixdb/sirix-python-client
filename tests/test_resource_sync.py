import httpx
import pytest

import pysirix
from pysirix import DBType
from pysirix.constants import MetadataType
from pysirix.errors import SirixServerError

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
    metadata = resp["metadata"]
    # Verify hash if present (optional field depending on SirixDB configuration)
    if "hash" in metadata:
        assert isinstance(metadata["hash"], str)
        assert len(metadata["hash"]) == 16
        assert all(c in "0123456789abcdef" for c in metadata["hash"])
    # Verify other metadata fields
    assert metadata["nodeKey"] == 1
    assert metadata["type"] == "ARRAY"
    assert metadata["descendantCount"] == 0
    assert metadata["childCount"] == 0
    assert resp["value"] == []


def test_read_metadata_key_only():
    resource.create([{"test": "dict"}])
    resp = resource.read_with_metadata(1, 1, MetadataType.KEY)
    assert resp == {
        "metadata": {"nodeKey": 1},
        "value": [
            {
                "metadata": {"nodeKey": 2},
                "value": [
                    {
                        "key": "test",
                        "metadata": {"nodeKey": 3},
                        "value": {"metadata": {"nodeKey": 4}, "value": "dict"},
                    }
                ],
            }
        ],
    }


def test_read_metadata_key_and_child_count():
    resource.create([{}])
    resp = resource.read_with_metadata(1, 1, MetadataType.KEYAndCHILD)
    assert resp == {
        "metadata": {"childCount": 1, "nodeKey": 1},
        "value": [{"metadata": {"childCount": 0, "nodeKey": 2}, "value": {}}],
    }


def test_history():
    resource.create([])
    resource.update(1, {})
    resource.delete(2, None)
    assert len(resource.history()) == 3


def test_diff():
    resource.create([], use_dewey_ids=True)
    resource.update(1, {})
    assert resource.diff(1, 2) == [
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


def test_query():
    resource.create([])
    assert resource.query("for $i in bit:array-values($$) return $i") == {"rest": []}


def test_delete_resource16():
    resource = db.resource("test_resource16")
    resource.create([])
    resource.delete(None, None)
    assert resource.exists() is False
