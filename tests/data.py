data_for_query = {
    "foo": ["bar", None, 2.33],
    "bar": {"hello": "world", "helloo": True},
    "baz": "hello",
    "tada": [{"foo": "bar"}, {"baz": False}, "boo", {}, []],
}
query = """let $nodeKey := sdb:nodekey(sdb:doc('First','testJsonResource')=>foo[[2]])
return $nodeKey"""
