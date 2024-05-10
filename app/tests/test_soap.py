from urllib import response
from xml.etree import ElementTree

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_iti47():
    with open("xml/pdqRequest.xml") as iti47:
        dom = ElementTree.parse(iti47)
        root = dom.getroot()
        body = ElementTree.tostring(root)
        response = client.post(
            "/SOAP/iti47", headers={"Content-Type": "application/xml"}, data=body
        )
        assert response.status_code == 200


def test_iti47():
    headers = {
    "Content-Type": "application/soap+xml",
    "SOAPAction": "urn:ihe:iti:2007:CrossGatewayQuery"  # Adjust this according to the specific SOAP action required for ITI-47
    }

    # ITI-47 request XML
    body = """
        <soapenv:envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                        xmlns:urn="urn:ihe:iti:xds-b:2007"
                        xmlns:urn1="urn:ihe:iti:xcpd:2009">
        <soapenv:Body>
            <urn:AdhocQueryRequest>
                <urn1:AdhocQuery>
                    <urn1:Slot name="$XDSDocumentEntryPatientId">
                    <urn1:ValueList>
                        <urn1:Value>'123456^^^&amp;1.2.840.113619.6.197&amp;ISO'</urn1:Value>
                    </urn1:ValueList>
                    </urn1:Slot>
                    <urn1:Slot name="$XDSDocumentEntryClassCode">
                    <urn1:ValueList>
                        <urn1:Value>('34133-9')</urn1:Value>
                    </urn1:ValueList>
                    </urn1:Slot>
                </urn1:AdhocQuery>
            </urn:AdhocQueryRequest>
        </soapenv:Body>
        </soapenv:Envelope>
        """

    response = client.post("/SOAP/iti47", headers=headers, data=body)

    # Check if the request was successful
    if response.status_code == 200:
        print("Request successful!")
        # Process the response as needed
        print(response.text)
    else:
        print(f"Request failed with status code: {response.status_code}")
        print(response.text)

    assert response.status_code == 200


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
