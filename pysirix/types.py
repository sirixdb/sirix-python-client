try:
    from typing import TypedDict, Dict, Union


    class QueryResult(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """
        revisionNumber: int
        revisionTimestamp: str
        revision: Dict

    class Commit(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """
        revisionTimestamp: str
        revision: int
        author: str
        commitMessage: str

    class InsertDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """
        nodeKey: int
        insertPositionNodeKey: int
        insertPosition: str
        deweyID: str
        depth: int

    class ReplaceDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """
        nodeKey: int
        type: str
        data: str

    class UpdateDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """
        nodeKey: int
        type: str
        value: Union[str, int, float, bool, None]


except ImportError:
    from typing import Dict
    QueryResult = Dict
    Commit = Dict
    InsertDiff = Dict
    ReplaceDiff = Dict
    UpdateDiff = Dict
