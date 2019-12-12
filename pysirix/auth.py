import asyncio

from typing import Union

from .sync.auth import authenticate
from .asynchronous.auth import async_authenticate

from .info import InstanceData, AuthData


class Auth:
    def __init__(
        self,
        auth_data: AuthData,
        instance_data: InstanceData,
        session,
        asynchronous: bool,
        allow_self_signed: bool,
    ):
        self._auth_data = auth_data
        self._instance_data = instance_data
        self._asynchronous = asynchronous
        self._session = session
        if asynchronous:
            self._allow_self_signed = allow_self_signed

    def authenticate(self) -> Union[None, asyncio.Future]:
        if self._asynchronous:
            loop = asyncio.get_running_loop()
            fut = loop.create_future()
            loop.create_task(async_authenticate(self, self._allow_self_signed, fut))
            return fut
        else:
            authenticate(self)
