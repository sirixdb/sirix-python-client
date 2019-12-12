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
from sirix_client import SirixClient, Database


client = SirixClient(
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
