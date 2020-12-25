from asyncio import ensure_future, sleep
from threading import Timer

import httpx

from typing import Union, Awaitable


class Auth:
    """
    This class handles authentication for server access.
    """

    def __init__(
        self,
        username: str,
        password: str,
        client: Union[httpx.Client, httpx.AsyncClient],
        asynchronous: bool,
    ):
        """
        :param username: the username for this application.
        :param password: the password for this application.
        :param client: the ``httpx.Client`` or ``httpx.AsyncClient``
                        instance used for connecting to the server.
        :param asynchronous: whether or not this application is asynchronous.
        """
        self._username = username
        self._password = password
        self._asynchronous = asynchronous
        self._client = client
        self._refresh_check = True

    def authenticate(self) -> Union[None, Awaitable[None]]:
        """
        Initial authentication for server access, using username and password.
        Access tokens are renewed in the background.
        """
        if self._asynchronous:
            return self._async_authenticate()
        else:
            self._authenticate()

    def dispose(self):
        """
        Remove the authentication timer.
        """
        self._timer.cancel()

    def _authenticate(self):
        """
        Initial authentication, for synchronous, threaded applications.
        """
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
        """
        Initial authentication, for asynchronous applications.
        """
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
        """
        Refresh the access token, using the refresh token. For synchronous, threaded applications.
        """
        resp = self._client.post(
            "/token", json={"refresh_token": self._token_data['refresh_token']}
        )
        self._handle_data(resp)

    async def _async_refresh(self):
        """
        Refresh the access token, using the refresh token. For asynchronous applications.
        """
        resp = await self._client.post(
            "/token", json={"refresh_token": self._token_data['refresh_token']}
        )
        await self._async_handle_data(resp)

    def _handle_data(self, resp):
        """
        Parse token data, and set a ``threading.Timer`` to refresh the access token again before it expires.

        :param resp: the ``httpx.Response`` object.
        """
        data = {k.replace("-", "_"): v for k, v in resp.json().items()}
        self._token_data = data
        self._client.headers[
            "Authorization"
        ] = f"{self._token_data['token_type']} {self._token_data['access_token']}"
        self._timer = Timer(self._token_data['expires_in'] - 10, self._refresh)
        self._timer.daemon = True
        self._timer.start()

    async def _async_handle_data(self, resp):
        """
        Parse token data, and create an asynchronous task to refresh the access token again before it expires.

        :param resp: the ``httpx.Response`` object.
        """
        data = {k.replace("-", "_"): v for k, v in resp.json().items()}
        self._token_data = data
        self._client.headers[
            "Authorization"
        ] = f"{self._token_data['token_type']} {self._token_data['access_token']}"
        self._timer = ensure_future(self._sleep_then_refresh())

    async def _sleep_then_refresh(self):
        """
        Helper function for :py:func:`_async_handle_data`.
        This method sleeps, then calls :py:func:`_async_refresh`
        10 seconds before the access token is set to expire.
        """
        await sleep(self._token_data['expires_in'] - 10)
        await self._async_refresh()
