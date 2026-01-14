from pysirix.info import NodeType, InsertPosition, DataType
from typing import Union


try:
    from typing import TypedDict, Dict, List, Iterable

    class QueryResult(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        revisionNumber: int
        revisionTimestamp: str
        revision: Union[Dict, List]

    class Commit(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        revisionTimestamp: str
        revision: int
        author: str
        commitMessage: str

    class SubtreeRevision(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        revisionTimestamp: str
        revisionNumber: int

    class Revision(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        revisionTimestamp: str
        revisionNumber: int
        revision: Union[List, Dict, str, int, float, None]

    class InsertDiff(TypedDict, total=False):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.

        Fields ``path``, ``deweyID``, ``depth``, and ``data`` are optional depending
        on resource configuration (PathSummary and DeweyIDs).
        """

        nodeKey: int
        insertPositionNodeKey: int
        insertPosition: InsertPosition
        path: str
        deweyID: str
        depth: int
        type: str
        data: DataType

    class ReplaceDiff(TypedDict, total=False):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.

        Fields ``path``, ``deweyID``, ``depth``, and ``data`` are optional depending
        on resource configuration (PathSummary and DeweyIDs).
        """

        oldNodeKey: int
        newNodeKey: int
        path: str
        deweyID: str
        depth: int
        type: str
        data: str

    class UpdateDiff(TypedDict, total=False):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.

        Fields ``path``, ``deweyID``, ``depth``, ``name``, ``type``, and ``value``
        are optional depending on the update type and resource configuration.
        """

        nodeKey: int
        path: str
        deweyID: str
        depth: int
        name: str
        type: DataType
        value: Union[str, int, float, bool, None]

    class DeleteDiff(TypedDict, total=False):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.

        Fields ``path``, ``deweyID``, and ``depth`` are optional depending
        on resource configuration (PathSummary and DeweyIDs).
        """

        nodeKey: int
        path: str
        deweyID: str
        depth: int

    class Metadata(TypedDict):
        """
        ``descendantCount`` and ``childCount`` are provided only where ``type`` is :py:class:`pysirix.info.NodeType`
        OBJECT or ARRAY.
        """

        nodeKey: int
        hash: int
        type: NodeType
        descendantCount: int
        childCount: int

    class MetaNode(TypedDict):
        """
        ``key`` is provided only if ``type`` is :py:class:`pysirix.info.NodeType` ``OBJECT_KEY``.

        ``value`` is of type ``List[MetaNode]`` if ``metadata.type`` is ``OBJECT`` or ``ARRAY``,
        however, if ``metadata.childCount`` is 0, then ``value`` is an emtpy ``dict``, or an empty
        ``list``, depending on whether ``metadata.type`` is ``OBJECT`` or ``ARRAY``.

        ``value`` is of type :py:class:`MetaNode` if ``metadata.type`` is ``OBJECT_KEY``.

        ``value`` is a ``str`` if ``metadata.type`` is ``OBJECT_STRING_VALUE`` or ``STRING_VALUE``.

        ``value`` is an ``int`` or ``float`` if ``metadata.type`` == ``OBJECT_NUMBER_VALUE`` or ``NUMBER_VALUE``.

        ``value`` is a ``bool`` if ``metadata.type`` is ``OBJECT_BOOLEAN_VALUE`` or ``BOOLEAN_VALUE``.

        ``value`` is ``None`` if ``metadata.type`` is ``OBJECT_NULL_VALUE`` or ``NULL_VALUE``.
        """

        metadata: Metadata
        key: str
        value: Union[
            List[Iterable["MetaNode"]],
            Iterable["MetaNode"],
            str,
            int,
            float,
            bool,
            None,
        ]


except ImportError:
    from typing import Dict

    QueryResult = Dict
    Commit = Dict
    Revision = Dict
    SubtreeRevision = Dict
    InsertDiff = Dict
    ReplaceDiff = Dict
    UpdateDiff = Dict
    DeleteDiff = Dict
    Metadata = Dict
    MetaNode = Dict

import sys

if sys.version_info >= (3, 9):
    from collections.abc import Iterator, AsyncIterator
else:
    from typing import Iterator, AsyncIterator

BytesLike = Union[str, bytes, Iterator[bytes]]
BytesLikeAsync = Union[BytesLike, AsyncIterator[bytes]]
