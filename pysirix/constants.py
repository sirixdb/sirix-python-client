import enum
from datetime import datetime
from typing import Union


class Insert(enum.Enum):
    """
    This Enum class defines the possible options for a resource update
    """

    CHILD = "asFirstChild"
    LEFT = "asLeftSibling"
    RIGHT = "asRightSibling"
    REPLACE = "replace"


class DBType(enum.Enum):
    """
    This Enum class defines the possible database (and resource) types
    """

    XML = "application/xml"
    JSON = "application/json"


Revision = Union[int, datetime]
