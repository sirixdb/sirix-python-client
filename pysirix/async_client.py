from httpx import AsyncClient as Client

from typing import Dict, Union
from asyncio import Future

from pysirix.constants import DBType, Insert


class AsyncClient:
    def __init__(self, client: Client):
        self.client = client

    async def global_info(self, fut: Future, resources=True):
        params = {}
        if resources:
            params["withResources"] = "true"
        resp = await self.client.get("/", params=params)
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def delete_all(self, fut: Future):
        resp = await self.client.delete("/")
        resp.raise_for_status()
        fut.set_result(None)

    async def create_database(self, fut: Future, name: str, db_type: DBType):
        resp = await self.client.put(name, headers={"Content-Type": db_type.value})
        resp.raise_for_status()
        fut.set_result(None)

    async def get_database_info(self, fut: Future, name: str):
        resp = await self.client.get(name)
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def delete_database(self, fut: Future, name: str):
        resp = await self.client.delete(name)
        resp.raise_for_status()
        fut.set_result(None)

    async def resource_exists(
        self, fut: Future, db_name: str, db_type: DBType, name: str
    ):
        resp = await self.client.head(
            f"{db_name}/{name}", headers={"Accept": db_type.value}
        )
        if resp.status_code == 200:
            fut.set_result(True)
        fut.set_result(False)

    async def create_resource(
        self, fut: Future, db_name: str, db_type: DBType, name: str, data: str
    ):
        resp = await self.client.put(
            f"{db_name}/{name}", headers={"Content-Type": db_type.value}, data=data,
        )
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def read_resource(
        self,
        fut: Future,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ):
        resp = await self.client.get(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def post_query(self, fut: Future, query: str):
        resp = await self.client.post("/", data=query)
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def get_etag(
        self,
        fut: Future,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, str],
    ):
        resp = await self.client.head(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        resp.raise_for_status()
        fut.set_result(resp.headers["etag"])

    async def update(
        self,
        fut: Future,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: int,
        data: str,
        insert: Insert,
        etag: str,
    ):
        resp = await self.client.post(
            f"{db_name}/{name}",
            params={"nodeId": node_id, "insert": insert.value},
            headers={"ETag": etag, "Content-Type": db_type.value},
            data=data,
        )
        resp.raise_for_status()
        fut.set_result(resp.text)

    async def resource_delete(
        self,
        fut: Future,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: Union[int, None],
        etag: Union[str, None],
    ):
        headers = {"Content-Type": db_type.value}
        if etag:
            headers.update({"ETag": etag})
        params = {}
        if node_id:
            params["nodeId"] = node_id
        resp = await self.client.delete(
            f"{db_name}/{name}", params=params, headers=headers
        )
        resp.raise_for_status()
        fut.set_result(None)
