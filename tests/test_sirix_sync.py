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


class TestDatabaseClass:
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)

    def test_create(self):
        db = self.sirix.database("First", DBType.JSON)
        db.create()
        info = db.get_database_info()
        assert info["resources"] == []

    def test_delete(self):
        db = self.sirix.database("First", DBType.JSON)
        db.delete()
        with pytest.raises(HTTPError):
            db.get_database_info()

    @classmethod
    def teardown_class(cls):
        cls.client.close()
