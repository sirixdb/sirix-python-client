from dataclasses import dataclass


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
