from urllib import response
from xml.etree import ElementTree

from fastapi.testclient import TestClient

from main import app

client = TestClient(app)


# def test_iti38():
#     with open("xml/2. Perform XCA ITI-38 query.xml") as iti38:
#         dom = ElementTree.parse(iti38)
#         root = dom.getroot()
#         body = ElementTree.tostring(root)

#         response = client.post(
#             "/SOAP/iti38", headers={"Content-Type": "application/xml"}, data=body
#         )

#         assert response.status_code == 200
#         assert response.text == 1


def test_iti39():
    with open("xml/4. Perform XCA ITI-39 document retrieve.xml") as iti39:
        dom = ElementTree.parse(iti39)
        root = dom.getroot()
        body = ElementTree.tostring(root)

        response = client.post(
            "/SOAP/iti39", headers={"Content-Type": "application/xml"}, data=body
        )

        assert response.status_code == 200
        assert response.content == 1
