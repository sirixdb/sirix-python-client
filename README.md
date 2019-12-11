# sirix-python-client

### The home of the SirixDB python client

This is currently a work in progress. Some example code:
```python
from sirix_client import SirixClient, Database
from xml.etree import ElementTree as ET


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
# it is simpler to access a database and resources through a Database instance,
# as later on in this file, but it is also possible to do this:
# not recommened:
client.update(ET.fromstring("<hello-world />"), "attempt", "newXML", "xml")

# recommended:
db: Database = client[
    ("Create Database By Index!", "json")
]  # specify type in case the database doesn't already exist

res = db.update(
    {"amazingly": "easy"}, "sirix"
)  # specify resource name, since this is a database instance, not a resource instance

```