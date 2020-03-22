import pytest
import httpx
import os

import pysirix

base_url = "https://localhost:9444"
verify = "tests/resources/cert.pem"


def test_sirix_sync_init():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    data = sirix._auth._token_data
    assert type(data.access_token) == str
    assert type(data.refresh_token) == str
    assert type(data.expires_in) == int


def test_auth_refresh():
    client = httpx.Client(base_url=base_url, verify=verify)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    data = sirix._auth._token_data
    sirix._auth._refresh()
    new_data = sirix._auth._token_data
    assert new_data != data
