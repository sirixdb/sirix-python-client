from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class InstanceData:
    sirix_uri: str
    database_info: List[Dict[str, str]] = field(default_factory=lambda: [])


@dataclass
class AuthData:
    username: str
    password: str
    keycloak_uri: str = None
    client_id: str = None
    client_secret: str = None
    access_token: str = field(default_factory=lambda: "")
    refresh_token: str = field(default_factory=lambda: "")
