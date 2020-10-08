import pysirix
from httpx import Client


def read_file(path: str, bytes_to_read: int):
    with open(path, "rb") as f:
        while True:
            data = f.read(bytes_to_read)
            if data == b"":
                break
            yield data


sirix = pysirix.sirix_sync("admin", "admin", Client(base_url="http://localhost:9443"))
db = sirix.database("test-db", pysirix.DBType.JSON)
"""
store = db.json_store("demo-json-store")
store.create()
store.insert_one({"data": "nothing to show here", "delete later": True})
store.insert_one({"text": "this is a blob of text"})
store.delete_records({"delete later": True})
print(sirix.query("sdb:node-history(sdb:select-node(jn:doc('demo', 'demo-json-store'), 8))"))
"""
resource = db.resource("test-resource")
resource.create(read_file("./tests/resources/realm-export.json", 96))
