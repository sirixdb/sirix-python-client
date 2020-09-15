from pysirix.info import NodeType, InsertPosition, DataType

try:
    from typing import TypedDict, Dict, Union, List, Iterable

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

    class InsertDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        nodeKey: int
        insertPositionNodeKey: int
        insertPosition: InsertPosition
        deweyID: str
        depth: int
        type: str
        data: DataType

    class ReplaceDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        nodeKey: int
        type: DataType
        data: str

    class UpdateDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        nodeKey: int
        type: DataType
        value: Union[str, int, float, bool, None]

    class DeleteDiff(TypedDict):
        """
        This type is available only in python 3.8+.
        Otherwise, defaults to ``dict``.
        """

        nodeKey: int
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
