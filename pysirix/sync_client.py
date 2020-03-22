from httpx import Client

from typing import Dict, Union

from pysirix.constants import DBType, Insert


class SyncClient:
    def __init__(self, client: Client):
        self.client = client

    def global_info(self, resources=True) -> str:
        params = {}
        if resources:
            params["withResources"] = "true"
        resp = self.client.get("/", params=params)
        resp.raise_for_status()
        return resp.text

    def delete_all(self) -> None:
        resp = self.client.delete("/")
        resp.raise_for_status()

    def create_database(self, name: str, db_type: DBType) -> None:
        resp = self.client.put(name, headers={"Content-Type": db_type.value})
        resp.raise_for_status()

    def get_database_info(self, name: str) -> str:
        resp = self.client.get(name)
        resp.raise_for_status()
        return resp.text

    def delete_database(self, name: str) -> None:
        resp = self.client.delete(name)
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
        resp.raise_for_status()
        return resp.text

    def read_resource(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        params: Dict[str, Union[str, int]],
    ) -> str:
        resp = self.client.get(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        resp.raise_for_status()
        return resp.text

    def post_query(self, query: str) -> str:
        resp = self.client.post("/", data=query)
        resp.raise_for_status()
        return resp.text

    def get_etag(
        self, db_name: str, db_type: DBType, name: str, params: Dict[str, str]
    ) -> str:
        resp = self.client.head(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
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
        etag: str,
    ) -> str:
        resp = self.client.post(
            f"{db_name}/{name}",
            params={"nodeId": node_id, "insert": insert.value},
            headers={"ETag": etag, "Content-Type": db_type.value},
            data=data,
        )
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
        headers = {"Content-Type": db_type.value}
        if etag:
            headers.update({"ETag": etag})
        params = {}
        if node_id:
            params["nodeId"] = node_id
        resp = self.client.delete(f"{db_name}/{name}", params=params, headers=headers)
        resp.raise_for_status()
