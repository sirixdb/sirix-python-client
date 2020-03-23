from asyncio import ensure_future, sleep
from threading import Timer

import httpx

from typing import Union, Coroutine

from pysirix.info import TokenData


class Auth:
    def __init__(
        self,
        username: str,
        password: str,
        client: Union[httpx.Client, httpx.AsyncClient],
        asynchronous: bool,
    ):
        self._username = username
        self._password = password
        self._asynchronous = asynchronous
        self._client = client

    def authenticate(self) -> Union[None, Coroutine]:
        if self._asynchronous:
            return self._async_authenticate()
        else:
            self._authenticate()

    def _authenticate(self):
        resp = self._client.post(
            "/token",
            json={
                "username": self._username,
                "password": self._password,
                "grant_type": "password",
            },
        )
        resp.raise_for_status()
        self._handle_data(resp)

    async def _async_authenticate(self):
        resp = await self._client.post(
            "/token",
            json={
                "username": self._username,
                "password": self._password,
                "grant_type": "password",
            },
        )
        resp.raise_for_status()
        await self._async_handle_data(resp)

    def _refresh(self):
        resp = self._client.post(
            "/token", json={"refresh_token": self._token_data.refresh_token}
        )
        self._handle_data(resp)

    async def _async_refresh(self):
        resp = await self._client.post(
            "/token", json={"refresh_token": self._token_data.refresh_token}
        )
        await self._async_handle_data(resp)

    def _handle_data(self, resp):
        data = {k.replace("-", "_"): v for k, v in resp.json().items()}
        self._token_data = TokenData(**data)
        self._client.headers[
            "Authorization"
        ] = f"{self._token_data.token_type} {self._token_data.access_token}"
        self._timer = Timer(self._token_data.expires_in - 5, self._refresh)

    async def _async_handle_data(self, resp):
        data = {k.replace("-", "_"): v for k, v in resp.json().items()}
        self._token_data = TokenData(**data)
        self._client.headers[
            "Authorization"
        ] = f"{self._token_data.token_type} {self._token_data.access_token}"
        self._timer = ensure_future(self._sleep_then_refresh())

    async def _sleep_then_refresh(self):
        await sleep(self._token_data.expires_in - 5)
