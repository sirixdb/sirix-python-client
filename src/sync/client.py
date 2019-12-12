from typing import Tuple, Dict, List, Union

from requests import Session

from .info import AuthData, InstanceData
from .auth import Auth
from .database import Database


class Sirix:
    def __init__(
        self,
        username: str,
        password: str,
        sirix_uri: str = "https://localhost:9443",
        client_id: str = None,
        client_secret: str = None,
        keycloak_uri: str = "http://localhost:8080",
        allow_self_signed: bool = False,
    ):
        """
        :param username: the username registered with keycloak for this application
        :param password: the password registered with keycloak for this application
        :param sirix_uri: the uri of the sirix instance
        :param client_id: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_secret`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        :param client_secret: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_id`` and optional ``keycloak_uri`` params).
                This option is not recommended.
        :param keycloak_uri: optional parameter, for authenticating directly with
                keycloak (also requires the ``client_id`` and optional ``client_secret`` params).
                This option is not recommended.
        :param allow_self_signed: whether to accept self signed certificates. Not recommended.
        """
        self._auth_data = AuthData(
            username, password, keycloak_uri, client_id, client_secret
        )
        self._instance_data = InstanceData(sirix_uri)
        self._session = Session()
        if allow_self_signed:
            self._session.verify = False
        self._auth = Auth(self._auth_data, self._instance_data, self._session)
        # initialize:
        self._auth.authenticate()
        self.get_info(False)

    def __getitem__(self, key: Tuple[str]):
        """
        Returns a database instance. See :meth:`get_database` for further information
        """
        return Database(*key, parent=self)

    def get_database(self, database_name: str, database_type: str):
        """Returns a database instance

        If a database with the given name and type does not exist,
        it is created.
        
        If ``database_type`` conflicts with the actual database type,
        the value of ``database_type`` is ignored.

        if ``database_type`` is not provided, and the database does not yet exist,
        an error is raised.

        :param database_name: the name of the database to access
        :param database_type: the type of the database to access

        Note that you can also use the following syntax:
        >>> sirix = Sirix(params)
        >>> sirix[(database_name, database_type)]
        """
        return Database(database_name, database_type, parent=self)

    def get_info(self, ret: bool = True) -> Union[None, List[Dict[str, str]]]:
        """
        :param ret: whether or not to return the info from the function
        """
        response = self._session.get(
            f"{self._instance_data.sirix_uri}/?withResources=true",
            headers={
                "Authorization": f"Bearer {self._auth_data.access_token}",
                "Accept": "application/json",
            },
        )
        if response.status_code == 200:
            self._instance_data.database_info += response.json()["databases"]
        if ret:
            return self._instance_data.database_info
