from httpx import Client

import xml.etree.ElementTree as ET
from typing import Dict, Union, List

from pysirix.constants import DBType, Insert
from pysirix.utils import include_response_text_in_errors


class SyncClient:
    def __init__(self, client: Client):
        self.client = client

    def global_info(self, resources=True) -> List[Dict]:
        params = {}
        if resources:
            params["withResources"] = True
        resp = self.client.get("/", params=params)
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()["databases"]

    def delete_all(self) -> None:
        resp = self.client.delete("/")
        with include_response_text_in_errors():
            resp.raise_for_status()

    def create_database(self, name: str, db_type: DBType) -> None:
        resp = self.client.put(name, headers={"Content-Type": db_type.value})
        with include_response_text_in_errors():
            resp.raise_for_status()

    def get_database_info(self, name: str) -> Dict:
        resp = self.client.get(name, headers={"Accept": "application/json"})
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()

    def delete_database(self, name: str) -> None:
        resp = self.client.delete(name)
        with include_response_text_in_errors():
            resp.raise_for_status()

    def resource_exists(self, db_name: str, db_type: DBType, name: str) -> bool:
        resp = self.client.head(f"{db_name}/{name}", headers={"Accept": db_type.value})
        if resp.status_code == 200:
            return True
        return False

    def create_resource(
        self, db_name: str, db_type: DBType, name: str, data: str
    ) -> str:
        resp = self.client.put(
            f"{db_name}/{name}", headers={"Content-Type": db_type.value}, data=data,
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.text

    def read_resource(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ) -> Union[Dict, ET.Element]:
        resp = self.client.get(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        if db_type == DBType.JSON:
            return resp.json()
        else:
            return ET.fromstring(resp.text)

    def history(self, db_name: str, db_type: DBType, name: str):
        resp = self.client.get(
            f"{db_name}/{name}/history", headers={"Accept": db_type.value}
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()["history"]

    def post_query(self, query: Dict[str, Union[int, str]]) -> str:
        resp = self.client.post("/", json=query)
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.text

    def get_etag(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ) -> str:
        resp = self.client.head(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.headers["etag"]

    def update(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: int,
        data: str,
        insert: Insert,
        etag: Union[str, None],
    ) -> str:
        if not etag:
            etag = self.get_etag(db_name, db_type, name, {"nodeId": node_id})
        resp = self.client.post(
            f"{db_name}/{name}",
            params={"nodeId": node_id, "insert": insert.value},
            headers={"ETag": etag, "Content-Type": db_type.value},
            data=data,
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.text

    def resource_delete(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        node_id: Union[int, None],
        etag: Union[str, None],
    ) -> None:
        if node_id and not etag:
            etag = self.get_etag(db_name, db_type, name, {"nodeId": node_id})
        headers = {"Content-Type": db_type.value}
        if etag:
            headers.update({"ETag": etag})
        params = {}
        if node_id:
            params["nodeId"] = node_id
        resp = self.client.delete(f"{db_name}/{name}", params=params, headers=headers)
        with include_response_text_in_errors():
            resp.raise_for_status()
