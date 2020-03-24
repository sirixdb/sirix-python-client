from httpx import AsyncClient as Client

import xml.etree.ElementTree as ET
from typing import Dict, Union, List

from pysirix.constants import DBType, Insert


class AsyncClient:
    def __init__(self, client: Client):
        self.client = client

    async def global_info(self, resources=True) -> List[Dict]:
        params = {}
        if resources:
            params["withResources"] = True
        resp = await self.client.get("/", params=params)
        resp.raise_for_status()
        return resp.json()["databases"]

    async def delete_all(self) -> None:
        resp = await self.client.delete("/")
        resp.raise_for_status()

    async def create_database(self, name: str, db_type: DBType) -> None:
        resp = await self.client.put(name, headers={"Content-Type": db_type.value})
        resp.raise_for_status()

    async def get_database_info(self, name: str) -> Dict:
        resp = await self.client.get(name)
        resp.raise_for_status()
        return resp.json()

    async def delete_database(self, name: str) -> None:
        resp = await self.client.delete(name)
        resp.raise_for_status()

    async def resource_exists(self, db_name: str, db_type: DBType, name: str) -> bool:
        resp = await self.client.head(
            f"{db_name}/{name}", headers={"Accept": db_type.value}
        )
        if resp.status_code == 200:
            return True
        return False

    async def create_resource(
        self, db_name: str, db_type: DBType, name: str, data: str
    ) -> str:
        resp = await self.client.put(
            f"{db_name}/{name}", headers={"Content-Type": db_type.value}, data=data,
        )
        resp.raise_for_status()
        return resp.text

    async def read_resource(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ) -> Union[Dict, ET.Element]:
        resp = await self.client.get(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        resp.raise_for_status()
        if db_type == DBType.JSON:
            return resp.json()
        else:
            return ET.fromstring(resp.text)

    async def post_query(self, query: Dict[str, Union[int, str]]):
        resp = await self.client.post("/", data=query)
        resp.raise_for_status()
        return resp.text

    async def get_etag(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ) -> str:
        resp = await self.client.head(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        resp.raise_for_status()
        return resp.headers["etag"]

    async def update(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: int,
        data: str,
        insert: Insert,
        etag: str,
    ) -> str:
        if not etag:
            etag = await self.get_etag(db_name, db_type, name, {"nodeId": node_id})
        resp = await self.client.post(
            f"{db_name}/{name}",
            params={"nodeId": node_id, "insert": insert.value},
            headers={"ETag": etag, "Content-Type": db_type.value},
            data=data,
        )
        resp.raise_for_status()
        return resp.text

    async def resource_delete(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: Union[int, None],
        etag: Union[str, None],
    ) -> None:
        if node_id and not etag:
            etag = await self.get_etag(db_name, db_type, name, {"nodeId": node_id})
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
