from enum import Enum

try:
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


except ImportError:

    class TokenData(dict):
        def __getattr__(self, item):
            return self.get(item)


class NodeType(Enum):
    OBJECT = ("OBJECT",)
    ARRAY = ("ARRAY",)
    OBJECT_KEY = ("OBJECT_KEY",)
    OBJECT_STRING_VALUE = ("OBJECT_STRING_VALUE",)
    STRING_VALUE = ("STRING_VALUE",)
    OBJECT_NUMBER_VALUE = ("OBJECT_NUMBER_VALUE",)
    NUMBER_VALUE = ("NUMBER_VALUE",)
    OBJECT_BOOLEAN_VALUE = ("OBJECT_BOOLEAN_VALUE",)
    BOOLEAN_VALUE = ("BOOLEAN_VALUE",)
    OBJECT_NULL_VALUE = ("OBJECT_NULL_VALUE",)
    NULL_VALUE = "NULL_VALUE"
