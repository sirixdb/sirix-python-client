import httpx

import pysirix
from pysirix import DBType
from xml.etree import ElementTree as ET


base_url = "http://localhost:9443"


xml_string = """
<rest:sequence xmlns:rest="https://sirix.io/rest">
  <rest:item>
    <a rest:id="1">
      <b rest:id="2">
        <c rest:id="3"/>
      </b>
    </a>
  </rest:item>
</rest:sequence>
""".lstrip().rstrip()

xml_node = """
<rest:sequence xmlns:rest="https://sirix.io/rest">
  <rest:item>
    <b rest:id="2">
      <c rest:id="3" />
    </b>
  </rest:item>
</rest:sequence>
""".lstrip().rstrip()


def setup_function():
    global client
    global sirix
    global db
    global resource
    client = httpx.Client(base_url=base_url)
    sirix = pysirix.sirix_sync("admin", "admin", client)
    db = sirix.database("First", DBType.XML)
    resource = db.resource("test_resource")


def teardown_function():
    sirix.delete_all()
    client.close()


def test_create_xml_database():
    db.create()
    result = sirix.get_info(False)
    assert "First" in map(lambda x: x["name"], result)


def test_create_xml_resource():
    assert resource.create(ET.fromstring("<a><b><c/></b></a>")) == xml_string


def test_read():
    resource.create(ET.fromstring("<a><b><c/></b></a>"))
    assert (
        ET.tostring(resource.read(2), encoding="unicode").replace("\\n", "\n")
        == xml_node
    )
