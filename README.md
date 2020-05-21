# sirix-python-client

### The home of the SirixDB python client

This package is currently in alpha stage.

The python client supports both sync and async programs.

The api docs can be found [here](https://pysirix.readthedocs.io/).
The api docs can also be built locally with the following:
```bash
cd docs
make html
```


Some example code:
```python
from pysirix import sirix_sync, DBType, Insert
from httpx import Client

client = Client(base_url="http://localhost:9443")
sirix = sirix_sync("admin", "admin", client)

db = sirix.database("json-diff", DBType.JSON)
db.create()

resource = db.resource("json-resource")
resource.create(
    {
        "foo": ["bar", None, 2.33],
        "bar": {"hello": "world", "helloo": True},
        "baz": "hello",
        "tada": [{"foo": "bar"}, {"baz": False}, "boo", {}, []],
    }
)

resource.update(4, {"new": "stuff"}, insert=Insert.RIGHT)
```

Or with Async Support:
```python
from pysirix import sirix_async, DBType, Insert
from httpx import AsyncClient
import asyncio


async def main():
    client = AsyncClient(base_url="http://localhost:9443")
    sirix = await sirix_async("admin", "admin", client)
    
    db = sirix.database("json-diff", DBType.JSON)
    await db.create()
    
    resource = db.resource("json-resource")
    await resource.create(
        {
            "foo": ["bar", None, 2.33],
            "bar": {"hello": "world", "helloo": True},
            "baz": "hello",
            "tada": [{"foo": "bar"}, {"baz": False}, "boo", {}, []],
        }
    )
    
    await resource.update(4, {"new": "stuff"}, insert=Insert.RIGHT)

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.run(main()))
```
