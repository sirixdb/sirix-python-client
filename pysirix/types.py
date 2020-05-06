try:
    from typing import TypedDict, Dict, Union


    class QueryResult(TypedDict):
        revisionNumber: int
        revisionTimestamp: str
        revision: Dict

    class Commit(TypedDict):
        revisionTimestamp: str
        revision: int
        author: str
        commitMessage: str

    class InsertDiff(TypedDict):
        nodeKey: int
        insertPositionNodeKey: int
        insertPosition: str
        deweyID: str
        depth: int

    class ReplaceDiff(TypedDict):
        nodeKey: int
        type: str
        data: str

    class UpdateDiff(TypedDict):
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
