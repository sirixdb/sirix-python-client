try:
    from typing import TypedDict, Dict

    class QueryResult(TypedDict):
        revisionNumber: int
        revisionTimestamp: str
        revision: Dict


except ImportError:
    QueryResult = Dict
