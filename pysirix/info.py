from enum import Enum


class NodeType(Enum):
    OBJECT = "OBJECT"
    ARRAY = "ARRAY"
    OBJECT_KEY = "OBJECT_KEY"
    OBJECT_STRING_VALUE = "OBJECT_STRING_VALUE"
    STRING_VALUE = "STRING_VALUE"
    OBJECT_NUMBER_VALUE = "OBJECT_NUMBER_VALUE"
    NUMBER_VALUE = "NUMBER_VALUE"
    OBJECT_BOOLEAN_VALUE = "OBJECT_BOOLEAN_VALUE"
    BOOLEAN_VALUE = "BOOLEAN_VALUE"
    OBJECT_NULL_VALUE = "OBJECT_NULL_VALUE"
    NULL_VALUE = "NULL_VALUE"


class InsertPosition(Enum):
    asFirstChild = "asFirstChild"
    asLeftSibling = "asLeftSibling"
    asRightSibling = "asRightSibling"
    replace = "replace"


class DataType(Enum):
    string = "string"
    number = "number"
    boolean = "boolean"
    null = "null"
    jsonFragment = "jsonFragment"
