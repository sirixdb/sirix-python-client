import pytest
import httpx
from httpx import HTTPError

import pysirix
from pysirix import DBType

base_url = "https://localhost:9444"
verify = "./resources/cert.pem"


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
    client.close()


def test_delete():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
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
    client.close()


def test_delete_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    resource.delete(None, None)
    assert resource.exists() is False
    client.close()


"""
def test_delete_nonexistent_resource():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.JSON)
    resource = db.resource("test_resource")
    assert resource.exists() is False
    with pytest.raises(HTTPError):
        resource.delete(None, None)
    client.close()
"""
