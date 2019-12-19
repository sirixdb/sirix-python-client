import pytest
import re

from .sync import register

import pysirix


class TestSirixInit:
    def test_sirix_init(self, requests_mock):
        register(requests_mock)
        sirix = pysirix.Sirix("admin", "admin")
        assert sirix._auth_data.access_token == "Bearer asdlfiohae5r4"
        assert sirix._auth_data.refresh_token == "987432asdfa312e"
        assert sirix._instance_data.database_info == [
            {
                "name": "Create Database By Index!",
                "type": "json",
                "resources": ["{'amazingly': 'easy'}"],
            }
        ]
