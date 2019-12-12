# sirix-python-client

### The home of the SirixDB python client

This is currently a work in progress.

The python client will support both sync and async programs,
by way of two distinct packages

The api docs can be built with the following:
```bash
cd docs
make html
```


Some example code:
```python
from PySirix import Sirix, SirixClient, Database


client: SirixClient = Sirix(
    "admin",
    "admin",
    "https://192.168.99.101:9443",
    # the below are optional
    client_id="sirix",
    client_secret="<secret>",
    keycloak_uri="http://192.168.99.101:8080",
    allow_self_signed=True,
)

db: Database = client[
    ("Create Database By Index!", "json")
]  # specify type in case the database doesn't already exist

res = db.update(
    {"amazingly": "easy"}, "sirix"
)  # specify resource name, since this is a database instance, not a resource instance

```

Or with Async Support (in progress):
```python
import asyncio

from PySirix import SirixAsync, SirixClient, Database

async def client():
    client: SirixClient = await SirixAsync(
        "admin",
        "admin",
        "https://192.168.99.101:9443",
        # the below are optional
        client_id="sirix",
        client_secret="661f7ebf-174f-4157-aa42-47920a0ec76a",
        keycloak_uri="http://192.168.99.101:8080",
        allow_self_signed=True,
    )
    print(client._instance_data.database_info)

loop = asyncio.get_event_loop()
loop.run_until_complete(client())
```