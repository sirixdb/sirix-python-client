from enum import Enum
from datetime import datetime
from typing import Union


class Insert(Enum):
    """
    This Enum class defines the possible options for a resource update
    """

    CHILD = "asFirstChild"
    LEFT = "asLeftSibling"
    RIGHT = "asRightSibling"
    REPLACE = "replace"


class DBType(Enum):
    """
    This Enum class defines the possible database (and resource) types
    """

    XML = "application/xml"
    JSON = "application/json"


class TimeAxisShift(Enum):
    oldest = -1
    none = 0
    latest = 1


class MetadataType(Enum):
    """
    This class defines the scope of the metadata to return using the
    :py:meth:`readWithMetadata` method.
    """

    ALL = True
    KEY = "nodeKey"
    KEYAndCHILD = "nodeKeyAndChildCount"


Revision = Union[int, datetime]
