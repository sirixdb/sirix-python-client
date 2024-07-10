data_for_query = {
    "foo": ["bar", None, 2.33],
    "bar": {"hello": "world", "helloo": True},
    "baz": "hello",
    "tada": [{"foo": "bar"}, {"baz": False}, "boo", {}, []],
}
post_query = """let $nodeKey := sdb:nodekey(jn:doc('Query','query_resource1').foo[2])
return $nodeKey"""

resource_query = """let $nodeKey := sdb:nodekey($$.foo[2])
return $nodeKey"""
