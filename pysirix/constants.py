import enum


class Insert(enum.Enum):
    """
    This Enum class defines the possible options for a resource update
    """
    CHILD = "asFirstChild"
    LEFT = "asLeftSibling"
    RIGHT = "asRightSibling"
    REPLACE = "replace"
