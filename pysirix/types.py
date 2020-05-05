try:
    from typing import TypedDict, Dict

    class QueryResult(TypedDict):
        revisionNumber: int
        revisionTimestamp: str
        revision: Dict


except ImportError:
    from typing import Dict
    QueryResult = Dict
