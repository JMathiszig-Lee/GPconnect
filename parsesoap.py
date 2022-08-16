from xml.etree import ElementTree
import pprint
import xmltodict


with open("xml/iti38query.xml") as iti38:
    dom = ElementTree.parse(iti38)
    root = dom.getroot()
    xmldict = xmltodict.parse(
        ElementTree.tostring(root),
        process_namespaces=True,
        namespaces={
            "http://www.w3.org/2003/05/soap-envelope": None,
            "http://www.w3.org/2005/08/addressing": None,
            "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
            "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
        },
    )
    # pprint.pprint(xmldict)
    query = xmldict["Envelope"]["Body"]["AdhocQueryRequest"]["AdhocQuery"]
    pprint.pprint(query)

# print("xcpd")
# with open("xml/xcpd.xml") as xcpd:
#     dom = ElementTree.parse(xcpd)
#     root = dom.getroot()
#     for child in root[0]:
#         print(child.tag, child.attrib)
#     for child in root[1][0]:
#         print(child.tag, child.attrib)
#     ElementTree.register_namespace("", "urn:hl7-org:v3")
#     xmldict = xmltodict.parse(ElementTree.tostring(root[1][0]))
#     pprint.pprint(xmldict["PRPA_IN201305UV02"]["controlActProcess"]["queryByParameter"])
#     # for child in root[1][0][8].findall(".//"):
#     #     print(child.tag, child.attrib)
