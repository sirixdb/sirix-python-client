from dataclasses import dataclass


@dataclass
class AuthData:
    username: str
    password: str
    client_id: str = None
    client_secret: str = None


@dataclass
class TokenData:
    access_token: str
    expires_in: int
    expires_at: int
    refresh_expires_in: int
    refresh_token: str
    token_type: str
    not_before_policy: int
    session_state: str
    scope: str
