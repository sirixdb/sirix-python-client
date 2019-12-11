from typing import Tuple
from utils import partialized

from info import AuthData, InstanceData


class SirixClient:
    def __init__(
        self,
        username: str,
        password: str,
        sirix_uri: str = "https://localhost:9443",
        client_id: str = None,
        client_secret: str = None,
        keycloak_uri: str = "http://localhost:8080",
        allow_self_signed: bool = False,
        asynchronous: bool = False,
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
        :param asynchronous: whether the methods on this class should be asynchronous.
                The interface this class provides is the same regardless of the value of this param,
                however, all methods on this class must be ``await``\ ed if it is true.
        """
        self._auth_data = AuthData(
            username, password, keycloak_uri, client_id, client_secret
        )
        self._instance_data = InstanceData(sirix_uri)
        self.asynchronous = asynchronous
        if asynchronous:
            pass
        else:
            import network_sync
            self._network_module = network_sync
            self._network = network_sync.get_sync_session(allow_self_signed)
            # define all network methods
            self._authenticate = network_sync.get_token
            self.get_info = partialized(network_sync.get_sirix_info, self=self)
            self.update = partialized(network_sync.update, self=self)
            # initialize:
            self._authenticate(self)
            self.get_info(False)

    def __getitem__(self, key: Tuple[str]):
        return Database(*key, parent=self)


class Database:
    def __init__(self, database_name: str, database_type: str, parent: SirixClient):
        self._client = parent
        self._network = parent._network
        self._instance_data = parent._instance_data
        self._auth_data = parent._auth_data

        self.database_name = database_name
        data_list = [
            db
            for db in self._instance_data.database_info
            if db["name"] == database_name
        ]
        if len(data_list) != 0:
            self.database_type = data_list[0]["type"]
        elif database_type:
            self.database_type = database_type.lower()
        else:
            raise Exception(
                "No database type specified, and database does not already exist"
            )
        self.update = partialized(
            self._client._network_module.update, self=self, database=database_name, data_type=database_type
        )
