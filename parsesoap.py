import json
import pprint
from xml.etree import ElementTree

import requests
import xmltodict
from xmlschema import XMLSchema

from app.ccda.helpers import clean_soap

with open("xml/pdq10oct.xml") as iti47:
    response_schema = XMLSchema("xml/multicacheschemas/PRPA_IN201306UV02.xsd")

    print("ITI47 query")
    print("-" * 20)

    dom = ElementTree.parse(iti47)
    root = dom.getroot()
    body = ElementTree.tostring(root)

    headers = {"Content-Type": "application/soap+xml"}
    url = "http://127.0.0.1:8000/SOAP/iti47"

    r = requests.post(url, data=body, headers=headers)
    print(r.status_code)

    # save r.text as iti47.xml
    with open("iti47.xml", "w") as output:
        output.write(r.text)
    # print(r.text)
    # pprint.pprint(r.text)
    # response_schema.iter_decode(r.text, validation="lax")
    # response_schema.validate(r.text)
    print(response_schema.is_valid(r.text))

    print("-" * 20)

    # envelope = clean_soap(iti47)
    # print(envelope)


with open("xml/2. Perform XCA ITI-38 query.xml") as iti38:
    print("ITI38 query")
    print("-" * 20)
    dom = ElementTree.parse(iti38)
    root = dom.getroot()
    body = ElementTree.tostring(root)
    headers = {"Content-Type": "application/soap+xml"}
    url = "http://127.0.0.1:8000/SOAP/iti38"
    r = requests.post(url, data=body, headers=headers)
    with open("iti38.xml", "w") as output:
        output.write(r.text)
    print(r.status_code)
    print(r.text)

    # get the repository id
    xmldict = xmltodict.parse(r.text)
    # repository_id = xmldict["Envelope"]["Body"]["AdhocQueryResponse"]["RegistryObjectList"]["RegistryObject"]["Slot"]["ValueList"]["Value"]["#text"]
    repository_id = xmldict["Envelope"]["Body"]["AdhocQueryResponse"]
    slots = repository_id["RegistryObjectList"]["ExtrinsicObject"]["Slot"]
    for i, slot in enumerate(slots):
        print(i, slot)
        if slot["@name"] == "repositoryUniqueId":
            # print(slot["ValueList"]["Value"])
            repository_id = slot["ValueList"]["Value"]
    # pprint.pprint(repository_id)
    # if r.status_code == 200: perform iti39 request
    # if r.status_code == 200:
    #     with open("xml/4. Perform XCA ITI-39 document retrieve.xml") as iti39:
    #         dom = ElementTree.parse(iti39)
    #         root = dom.getroot()
    #         xmldict = xmltodict.parse(
    #             ElementTree.tostring(root),
    #             process_namespaces=True,
    #             namespaces={
    #                 "http://www.w3.org/2003/05/soap-envelope": None,
    #                 "http://www.w3.org/2005/08/addressing": None,
    #                 "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
    #                 "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
    #                 "urn:ihe:iti:xds-b:2007": None,
    #             },
    #         )
    #         query = xmldict["Envelope"]
    #         body = ElementTree.tostring(root)
    #         headers = {"Content-Type": "application/xml"}
    #         url = "http://

    print("-" * 20)

# with open("xml/3. Return XCA ITI-38 query response.xml") as iti38:
#     print("ITI38 response")
#     print("-" * 20)
#     dom = ElementTree.parse(iti38)
#     root = dom.getroot()
#     xmldict = xmltodict.parse(
#         ElementTree.tostring(root),
#         process_namespaces=True,
#         namespaces={
#             "http://www.w3.org/2003/05/soap-envelope": None,
#             "http://www.w3.org/2005/08/addressing": None,
#             "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
#             "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
#         },
#     )
#     # pprint.pprint(xmldict)
#     query = xmldict["Envelope"]
#     pprint.pprint(query)
#     print("-" * 20)


# with open("xml/4. Perform XCA ITI-39 document retrieve.xml") as iti38:
#     print("ITI39")
#     print("-" * 20)
#     dom = ElementTree.parse(iti38)
#     root = dom.getroot()
#     xmldict = xmltodict.parse(
#         ElementTree.tostring(root),
#         process_namespaces=True,
#         namespaces={
#             "http://www.w3.org/2003/05/soap-envelope": None,
#             "http://www.w3.org/2005/08/addressing": None,
#             "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
#             "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
#             "urn:ihe:iti:xds-b:2007": None,
#         },
#     )
#     # pprint.pprint(xmldict)
#     query = xmldict["Envelope"]
#     # pprint.pprint(query)
#     print("-" * 20)

#     body = ElementTree.tostring(root)
#     headers = {"Content-Type": "application/xml"}
#     url = "http://127.0.0.1:8000/SOAP/iti39"
#     r = requests.post(url, data=body, headers=headers)
#     print(r.status_code)
#     # print(r.text)
