import pytest
import httpx

import pysirix

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
