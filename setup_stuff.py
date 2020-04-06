from pysirix import sirix_sync, DBType, Insert
from httpx import Client


client = Client(base_url="https://localhost:9443", verify="tests/resources/cert.pem")
sirix = sirix_sync("admin", "admin", client)
db = sirix.database("json-diff", DBType.JSON)
sirix.delete_all()
db.create()
resource = db.resource("resource")
resource.create(
    {
        "foo": ["bar", None, 2.33],
        "bar": {"hello": "world", "helloo": True},
        "baz": "hello",
        "tada": [{"foo": "bar"}, {"baz": False}, "boo", {}, []],
    }
)

from pprint import pprint

resource.update(4, {"new": "stuff"}, insert=Insert.RIGHT)
# pprint(client.get("/json-diff/resource/diff?first-revision=1&second-revision=2").json())

resource.update(4, {"new": "stuff"}, insert=Insert.RIGHT)
# pprint(client.get("/json-diff/resource/diff?first-revision=1&second-revision=3").json())

resource.update(4, {"new": "stuff"}, insert=Insert.RIGHT)
# pprint(client.get("/json-diff/resource/diff?first-revision=1&second-revision=4").json())
