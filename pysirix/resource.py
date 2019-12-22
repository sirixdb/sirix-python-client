from .info import AuthData, InstanceData  # for type support
from .utils import handle_async
from .sync.rest import create_resource
from .asynchronous.rest import async_create_resource


class Database:
    def __init__(
        self, database_name: str, database_type: str, resource_name: str, parent
    ):
        """database access class
        this class allows for manipulation of a database 

        :param database_name: the name of the database to access, or create
                if it does not yet exist
        :param database_type: the type of the database being accessed, or to
                be created if the database does not yet exist
        :param resource_name: the name of the resource being accessed, or to
                be created if the resource does not yet exist
        :param parent: the ``SirixClient`` instance which created this instance
        """
        self._session = parent._session
        self._instance_data: InstanceData = parent._instance_data
        self._auth_data: AuthData = parent._auth_data

        self.database_name = database_name
        self.database_type = database_type
        self.resource_name = resource_name

        self._allow_self_signed = parent._allow_self_signed

    def _init(self):
        if (
            self.resource_name
            not in self._instance_data.database_info[self.database_name]
        ):
            self._create()

    def _create(self):
        """Creates the resource. Should be called if the resource does not yet exist"""
        if self._asynchronous:
            return handle_async(
                async_create_resource,
                self,
                self.database_name,
                self.database_type,
                self.resource_name,
            )
        else:
            return create_resource(
                self, self.database_type, self.database_type, self.resource_name
            )
