import pprint
from xml.etree import ElementTree
import json
import requests
import xmltodict
from app.ccda.helpers import clean_soap


with open("xml/pdqRequest.xml") as iti47:
    print("ITI47 query")
    print("-" * 20)

    dom = ElementTree.parse(iti47)
    root = dom.getroot()
    body = ElementTree.tostring(root)

    headers = {"Content-Type": "application/soap+xml"}
    url = "http://127.0.0.1:8000/SOAP/iti47"
    r = requests.post(url, data=body, headers=headers)
    print(r.status_code)
    # print(r.text)
    pprint.pprint(r.text)
    response_dict = json.loads(r.text)
    for key in response_dict["PRPA_IN201305UV02"] :
        print(key)
        pprint.pprint(response_dict["PRPA_IN201305UV02"][key])
    print("-" * 20)


    # envelope = clean_soap(iti47)
    # print(envelope)


# with open("xml/2. Perform XCA ITI-38 query.xml") as iti38:
#     print("ITI38 query")
#     print("-" * 20)
#     dom = ElementTree.parse(iti38)
#     root = dom.getroot()
#     body = ElementTree.tostring(root)
#     headers = {"Content-Type": "application/xml"}
#     url = "http://127.0.0.1:8000/SOAP/iti38"
#     r = requests.post(url, data=body, headers=headers)
#     print(r.status_code)
#     print(r.text)
#     print("-" * 20)

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
