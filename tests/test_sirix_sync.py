import pytest
import httpx
from httpx import HTTPError

import pysirix
from pysirix import DBType

from .data import data_for_query, query

base_url = "https://localhost:9443"
verify = "tests/resources/cert.pem"


def test_sirix_sync_init():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    data = sirix._auth._token_data
    assert type(data.access_token) == str
    assert type(data.refresh_token) == str
    assert type(data.expires_in) == int
    client.close()


def test_auth_refresh():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    data = sirix._auth._token_data
    sirix._auth._refresh()
    new_data = sirix._auth._token_data
    assert new_data != data
    client.close()


def test_get_info():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    data = sirix.get_info()
    assert data == []
    client.close()


def test_create():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    db.create()
    info = db.get_database_info()
    assert info["resources"] == []
    sirix.delete_all()
    client.close()


def test_delete():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    db.create()
    db.delete()
    with pytest.raises(HTTPError):
        db.get_database_info()
    client.close()


def test_exists():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    assert resource.exists() is False
    client.close()


def test_create_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    assert resource.create([]) == "[]"
    assert resource.exists() is True
    sirix.delete_all()
    client.close()


def test_delete_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    resource.delete(None, None)
    assert resource.exists() is False
    sirix.delete_all()
    client.close()


def test_delete_nonexistent_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("blah", DBType.JSON)
    resource = db.resource("blah")
    assert resource.exists() is False
    with pytest.raises(HTTPError):
        resource.delete(None, None)
    client.close()


def test_read_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    data = resource.read(None)
    assert data == []
    sirix.delete_all()
    client.close()


def test_get_etag():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    etag = resource.get_etag(1)
    assert type(etag) == str
    sirix.delete_all()
    client.close()


def test_get_etag_nonexistent():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    with pytest.raises(HTTPError):
        resource.get_etag(2)
    sirix.delete_all()
    client.close()


def test_delete_by_node_id():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create({})
    resource.delete(1, None)
    with pytest.raises(HTTPError):
        resource.delete(1, None)
    sirix.delete_all()
    client.close()


def test_delete_by_etag():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create({})
    etag = resource.get_etag(1)
    resource.delete(1, etag)
    with pytest.raises(HTTPError):
        resource.delete(1, None)
    sirix.delete_all()
    client.close()


def test_update_by_etag():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    etag = resource.get_etag(1)
    resource.update(1, {}, etag=etag)
    assert resource.read(None) == [{}]
    sirix.delete_all()
    client.close()


def test_update_by_node_id():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    resource.update(1, {})
    assert resource.read(None) == [{}]
    sirix.delete_all()
    client.close()


def test_update_nonexistent_node():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.create([])
    with pytest.raises(HTTPError):
        resource.update(5, {})
    sirix.delete_all()
    client.close()


def test_sirix_query():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("Query1", DBType.JSON)
    resource = db.resource("query_resource")
    resource.create(data_for_query)
    assert sirix.query(query) == '{"rest": [6]}'
    sirix.delete_all()
    client.close()


def test_resource_query():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("Query2", DBType.JSON)
    resource = db.resource("query_resource")
    resource.create(data_for_query)
    assert resource.query(query) == {"rest": [6]}
    sirix.delete_all()
    client.close()
