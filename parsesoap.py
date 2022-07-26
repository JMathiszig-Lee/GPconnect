from xml.etree import ElementTree
import pprint
import xmltodict


with open("xml/iti38query.xml") as iti38:
    dom = ElementTree.parse(iti38)
    root = dom.getroot()

    print("adhocquery ID: " + root[1][0][1].get("id"))

    for slot in root[1][0][1]:
        print(slot.get("name"))
        for value in slot[0]:
            print(value.text)
    # for child in root[1]:
    #     print(child.tag, child.attrib)
    #     for i in child:
    #         print(i.tag, i.attrib)
    # print(root[1][0].text)

print("xcpd")
with open("xml/xcpd.xml") as xcpd:
    dom = ElementTree.parse(xcpd)
    root = dom.getroot()
    for child in root[0]:
        print(child.tag, child.attrib)
    for child in root[1][0]:
        print(child.tag, child.attrib)
    ElementTree.register_namespace("", "urn:hl7-org:v3")
    xmldict = xmltodict.parse(ElementTree.tostring(root[1][0]))
    pprint.pprint(xmldict["PRPA_IN201305UV02"]["controlActProcess"]["queryByParameter"])
    # for child in root[1][0][8].findall(".//"):
    #     print(child.tag, child.attrib)
