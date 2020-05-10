import pytest
import httpx

import pysirix
from pysirix import DBType
from pysirix.errors import SirixServerError

from .data import data_for_query, post_query, resource_query

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
    with pytest.raises(SirixServerError):
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


def test_sirix_query():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource")
    resource.create(data_for_query)
    assert sirix.query(post_query) == '{"rest":[6]}'
    sirix.delete_all()
    client.close()


def test_resource_query():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("Query", DBType.JSON)
    resource = db.resource("query_resource")
    resource.create(data_for_query)
    assert resource.query(resource_query) == {"rest": [6]}
    sirix.delete_all()
    client.close()
