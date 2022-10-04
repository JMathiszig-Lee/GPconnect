import logging

import xmltodict
from httpx import AsyncClient

from redis_connect import redis_client


async def iti_39_response(message_id, document_id, document):
    registry_id = redis_client.get("registry")
    soap_response = {}
    soap_response["Header"] = {
        "Action": {
            "@mustUnderstand": 1,
            "#text": "urn:ihe:iti:2007:CrossGatewayRetrieveResponse",
        },
        "RelatesTo": {"#text": message_id},
    }
    soap_response["Body"] = {
        "RetrieveDocumentSetResponse": {
            "@xmlns": "urn:ihe:iti:xds-b:2007",
            "RegistryResponse": {
                "@status": "urn:oasis:names:tc:ebxml-regrep:ResponseStatusType:Success",
                "@xmlns": "urn:oasis:names:tc:ebxml-regrep:xsd:rs:3.0",
                "DocumentResponse": {
                    "HomeCommunityId": {"#text": f"urn:oid:{registry_id}"},
                    "RepositoryUniqueId": {"#text": registry_id},
                    "DocumentUniqueId": {"#text": document_id},
                    "mimeType": {"#text": "text/xml"},
                    "Document": document,
                },
            },
        }
    }

    return xmltodict.unparse(soap_response, pretty=True)


async def iti_38_response(nhsno: int, queryid: str):
    soap_response = {}
    header = {
        "Action": {
            "@mustUnderstand": 1,
            "#text": "urn:ihe:iti:2007:CrossGatewayQueryResponse",
        },
        "RelatesTo": {"#text": queryid},
    }
    body = {}
    body["AdhocQueryResponse"] = {"@status": "ResponseStatusType:Success"}

    # check the redis cash if there's an existing ccda
    docid = redis_client.get(nhsno)

    if docid is None:
        # no cached ccda
        async with AsyncClient() as client:
            r = await client.get(f"http://127.0.0.1:8000/gpconnect/{nhsno}")
            if r.status_code == 200:
                logging.info(f"used internal call for {nhsno}")
                docid = r.json()
                docid = docid["document_id"]
            else:
                body["AdhocQueryResponse"]["@status"] = "ResponseStatusType:Failure"
                body["AdhocQueryResponse"]["RegistryErrorList"] = {
                    "@highestSeverity": "urn:oasis:names:tc:ebxml-regrep:ErrorSeverityType:Error",
                    "RegistryError": {
                        "@errorCode": "XDSRegistryError",
                        "@codeContext": f"Unable to locate SCR with NHS number {nhsno}",
                        "@location": "",
                        "@severity": "urn:oasis:names:tc:ebxml-regrep:ErrorSeverityType:Error",
                    },
                }

    if docid is not None:
        # add the ccda as registry object list

        # create list of slots
        slots = []
        classifications = []

        def create_slot(name: str, value) -> dict:
            slot_dict = {"@name": name, "ValueList": {"Value": {"#text": value}}}
            return slot_dict

        slots.append(create_slot("sourcePatientId", nhsno))
        slots.append(create_slot("languageCode", "en-GB"))
        slots.append(create_slot("hash", -1))
        slots.append(create_slot("size", -1))
        slots.append(create_slot("repositoryUniqueId", redis_client.get("registry")))

        body["RegistryObjectList"] = {
            "@xmlns": "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0",
            "ExtrinsicObject": {
                "@id": f"urn:uuid:{docid}",
                "@status": "urn:oasis:names:tc:ebxmlregrep:StatusType:Approved",
                "@objectType": "urn:uuid:34268e47-fdf5-41a6-ba33-82133c465248",
                "mimeType": "text/xml",
                "Slot": slots,
            },
        }

    else:
        body["AdhocQueryResponse"]["RegistryObjectList"] = {}

    soap_response["Envelope"] = {}
    soap_response["Envelope"]["Header"] = header
    soap_response["Envelope"]["Body"] = body
    print(xmltodict.unparse(soap_response, pretty=True))
    return xmltodict.unparse(soap_response, pretty=True)
