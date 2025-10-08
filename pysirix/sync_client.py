from httpx import Client

import xml.etree.ElementTree as ET
from typing import Dict, Union, List

from pysirix.constants import DBType, Insert
from pysirix.errors import include_response_text_in_errors
from pysirix.types import Commit, InsertDiff, ReplaceDiff, UpdateDiff, BytesLike

ET.register_namespace("rest", "https://sirix.io/rest")


class SyncClient:
    def __init__(self, client: Client):
        """
        The methods of this class call all SirixDB endpoints, with minimal handling.
        This class is used for synchronous calls, the :py:class:`AsyncClient` handles asynchronous calls.

        :param client: an instance of ``httpx.Client``.
        """
        self.client = client

    def global_info(self, resources: bool = True) -> List[Dict]:
        """
        Call the ``/`` endpoint with a GET request. If ``resources`` is ``True``,
        the endpoint is called with the query ``withResources=true``

        :param resources: whether to query resources as well
        :return: a ``list`` of ``dict``\\s, where each ``dict`` has a ``name``
                        field, a ``type`` field, and (if ``resources`` is
                        ``True``) a ``resources`` field (containing a ``list`` of names).
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        params = {}
        if resources:
            params["withResources"] = True
        resp = self.client.get("/", params=params)
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()["databases"]

    def delete_all(self) -> None:
        """
        Call the ``/`` endpoint with DELETE request.
        Deletes all databases and their resources. Be careful!

        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.delete("/")
        with include_response_text_in_errors():
            resp.raise_for_status()

    def create_database(self, name: str, db_type: DBType) -> None:
        """
        Call the ``/{database}`` endpoint with a PUT request

        :param name: name of the database to create.
        :param db_type: type of the database to create.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.put(name, headers={"Content-Type": db_type.value})
        with include_response_text_in_errors():
            resp.raise_for_status()

    def get_database_info(self, name: str) -> Dict:
        """
        Call the ``/{database}`` endpoint with a GET request.

        :param name: name of the database.
        :return: a ``dict`` with a ``resources`` field containing a ``list`` of resources.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.get(name, headers={"Accept": "application/json"})
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()

    def delete_database(self, name: str) -> None:
        """
        call the ``/{database}`` endpoint with a DELETE request.

        :param name: the name of the database to delete.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.delete(name)
        with include_response_text_in_errors():
            resp.raise_for_status()

    def resource_exists(self, db_name: str, db_type: DBType, name: str) -> bool:
        """
        Call the ``/{database}/{resource}`` endpoint with a HEAD request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :return: a ``bool`` indicating the existence (or lack thereof) of the resource.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.head(f"{db_name}/{name}", headers={"Accept": db_type.value})
        if resp.status_code == 200:
            return True
        return False

    def create_resource(
        self,
        db_name: str,
        db_type: DBType,
        name: str,
        data: BytesLike,
        hash_type: str = "ROLLING",
    ) -> str:
        """
        Call the ``/{database}/{resource}`` endpoint with a PUT request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :param data: the data to initialize the database with.
        :return: a ``str`` of ``data``.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.put(
            f"{db_name}/{name}",
            headers={"Content-Type": db_type.value},
            params={"hashType": hash_type},
            content=data,
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
    ) -> Union[Dict, List, ET.Element]:
        """
        Call the ``/{database}/{resource}`` endpoint with a GET request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :param params: query parameters to call the endpoint with.
        :return: either a ``dict`` or a ``xml.etree.ElementTree.Element``, depending on the database type.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.get(
            f"{db_name}/{name}", params=params, headers={"Accept": db_type.value}
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        if db_type == DBType.JSON:
            return resp.json()
        else:
            return ET.fromstring(resp.text)

    def history(self, db_name: str, db_type: DBType, name: str) -> List[Commit]:
        """
        Call the ``/{database}/{resource}/history`` endpoint with a GET request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :return: a ``list`` of ``dict`` containing the history of the resource.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        resp = self.client.get(
            f"{db_name}/{name}/history", headers={"Accept": db_type.value}
        )
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()["history"]

    def diff(
        self, db_name: str, name: str, params: Dict[str, str]
    ) -> List[Dict[str, Union[InsertDiff, ReplaceDiff, UpdateDiff, int]]]:
        """
        Call the ``/{database}/{resource}/diff`` endpoint with a GET request.

        :param db_name: the name of the database.
        :param name: the name of the resource.
        :param params: the parameters required for this request.
        :return:
        """
        resp = self.client.get(f"{db_name}/{name}/diff", params=params)
        with include_response_text_in_errors():
            resp.raise_for_status()
        return resp.json()["diffs"]

    def post_query(self, query: Dict[str, Union[int, str]]) -> str:
        """
        Call the ``/`` endpoint with a POST request.

        :param query: the body of the request.
        :return: the query result as a ``str``.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
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
        """
        Call the ``/{database}/{resource}`` endpoint with a HEAD request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :param params: the query parameters to call the endpoint with.
        :return: the ETag of the node queried.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
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
        data: BytesLike,
        insert: Insert,
        etag: Union[str, None],
    ) -> str:
        """
        Call the ``/{database}/{resource}`` endpoint with a POST request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :param node_id: the nodeKey of the node in relation to which the update is performed.
        :param data: the data used in the update operation.
        :param insert: the position of the update in relation to the node referenced by node_id.
        :param etag: the ETag of the node referenced by node_id.
        :return: the resource as a ``str``.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
        if not etag:
            etag = self.get_etag(db_name, db_type, name, {"nodeId": node_id})
        resp = self.client.post(
            f"{db_name}/{name}",
            params={"nodeId": node_id, "insert": insert.value},
            headers={"ETag": etag, "Content-Type": db_type.value},
            content=data,
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
        """
        Call the ``/{database}/{resource}`` endpoint with a DELETE request.

        :param db_name: the name of the database.
        :param db_type: the type of the database.
        :param name: the name of the resource.
        :param node_id: the nodeKey of the node to delete. ``None`` to delete the entire resource.
        :param etag: the etag of the node to delete.
        :raises: :py:class:`pysirix.SirixServerError`.
        """
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
