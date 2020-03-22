from asyncio import Future, sleep
import httpx

from typing import Union

from pysirix.info import AuthData, TokenData
from pysirix.utils import handle_async


class Auth:
    def __init__(
        self,
        auth_data: AuthData,
        client: Union[httpx.Client, httpx.AsyncClient],
        asynchronous: bool,
    ):
        self._auth_data = auth_data
        self._asynchronous = asynchronous
        self._client = client

    def authenticate(self) -> Union[None, Future]:
        if self._asynchronous:
            return handle_async(self._async_authenticate)
        else:
            self._authenticate()

    def _authenticate(self):
        resp = self._client.post(
            "/token",
            json={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
            },
        )
        resp.raise_for_status()
        self._token_data = TokenData(**resp.json())

    async def _async_authenticate(self, fut: Future):
        resp = await self._client.post(
            "/token",
            json={
                "username": self._auth_data.username,
                "password": self._auth_data.password,
                "grant_type": "password",
            },
        )
        resp.raise_for_status()
        self._token_data = TokenData(**resp.json())
        fut.set_result(None)


"""
    async def _async_refresh(self):
        await sleep(self._token_data.expires_in - 5)
        resp = await self._client.post(
            "/token", json={"refresh_token": self._token_data.refresh_token}
        )
        self._token_data = TokenData(**resp.json())
"""
