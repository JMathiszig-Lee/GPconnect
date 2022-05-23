import json
import asyncio
from bs4 import BeautifulSoup
import xml.etree.cElementTree as ET
from fhir2ccda import convert_resource

SUMMARY_CARE_URL = "https://sandbox.api.service.nhs.uk/summary-care-record/FHIR/R4"


async def parse_scr(scr):
    """
    parses scr json and returns structured data
    """
    entry = scr["entry"][0]

    scr_dict = {}

    async def parse_scr_section(section):
        """
        parses each section of the scr and converts html to stuctured data
        """
        section_list = []

        section_html = section["text"]["div"]
        soup = BeautifulSoup(section_html, "html.parser")
        table = soup.find("table")
        if table:
            headings = table.find_all("th")
            headings = [ele.text.strip() for ele in headings]

            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                cols = [ele.text.strip() for ele in cols]
                row_entry = {}
                for ind, val in enumerate(cols):
                    row_entry[headings[ind]] = val
                section_list.append(row_entry)
        scr_dict[section["title"]] = section_list

    await asyncio.gather(
        *[parse_scr_section(section) for section in entry["resource"]["section"]]
    )

    return scr_dict


async def create_ccda(scr):
    entry = scr["entry"][0]
    references = scr["entry"][1:]

    def find_reference(reference: str) -> dict:
        found = [
            ref
            for ref in references
            if ref["fullUrl"] == SUMMARY_CARE_URL + "/" + reference
        ]
        return found[0]

    ccda = ET.Element("ClinicalDocument")
    ET.SubElement(ccda, "realmcode", code="GB")
    ET.SubElement(
        ccda, "templateId", root="2.16.840.1.11883.10.20.22.1.2", extension="2015-08-01"
    )

    # snomed code
    ET.SubElement(
        ccda,
        "code",
        code=entry["resource"]["type"]["coding"][0]["code"],
        codeSystem="2.16.840.1.113883.6.1",
        codeSystemName=entry["resource"]["type"]["coding"][0]["system"],
        displayName=entry["resource"]["type"]["coding"][0]["display"],
    )

    # loinc code
    ET.SubElement(
        ccda,
        "code",
        code="34133-9",
        codeSystem="2.16.840.1.113883.6.1",
        codeSystemName="LOINC",
    )

    # author section
    author = ET.SubElement(ccda, "author")
    practioner_role = find_reference(entry["resource"]["author"][0]["reference"])
    practioner = find_reference(
        practioner_role["resource"]["practitioner"]["reference"]
    )
    ET.SubElement(author, "assignedAuthor").text = practioner["resource"]["name"][0][
        "text"
    ]

    # documentation of section
    doc_of = ET.SubElement(ccda, "documentationOf")
    service_event = ET.SubElement(doc_of, "serviceEvent", classCode="PCPR")
    time_covered = ET.SubElement(service_event, "effectiveTime")

    # TODO vlue should be date of birth
    ET.SubElement(time_covered, "low", value="19750501")
    # TODO vlue should be date of scr genration
    ET.SubElement(time_covered, "high", value="20120915")

    templateids = {
        "Allergies and Adverse Reactions": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.6.1",
            "Code": "48765-2",
        },
        "Current Repeat Medications": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.1",
            "Code": "10160-0",
        },
        "Problems and Issues": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.5",
            "Code": "11450-4",
        },
        "General Practice Summary": {"TemplateID": "blank", "Code": "blank"},
        "Diagnoses": {"TemplateID": "blank", "Code": "blank"},
        "Investigation Results": {"TemplateID": "blank", "Code": "blank"},
        "General Practice Summary": {"TemplateID": "blank", "Code": "blank"},
    }

    async def generate_component(section):
        if section["title"] in templateids:
            component = ET.SubElement(ccda, "component")
            sec = ET.SubElement(component, "section")

            # coding system
            ET.SubElement(
                sec,
                "code",
                code=templateids[section["title"]]["Code"],
                codeSystem="2.16.840.1.113883.6.1",
                codeSystemName="LOINC",
                displayName=section["title"],
            )

            # root and extension
            ET.SubElement(
                sec, "templateId", root=templateids[section["title"]]["TemplateID"]
            )
            ET.SubElement(
                sec,
                "templateId",
                root=templateids[section["title"]]["TemplateID"],
                extension="2015-08-01",
            )

            # must contain title
            ET.SubElement(sec, "title").text = section["title"]
            section_html = section["text"]["div"]
            # must contain text
            text = ET.SubElement(sec, "text")
            text.append(ET.XML(section_html))

            if "entry" in section:
                for entry in section["entry"]:
                    codeable_entry = find_reference(entry["reference"])
                    ent = ET.SubElement(sec, "entry")
                    ent.append(await (convert_resource(codeable_entry)))

    await asyncio.gather(
        *[generate_component(section) for section in entry["resource"]["section"]]
    )

    tree = ET.ElementTree(ccda)
    ET.indent(tree, space="\t", level=0)
    # ET.dump(tree)
    xml = ET.tostring(tree.getroot())
    return xml


if __name__ == "__main__":
    with open("scr.json") as scr_json:
        scr = json.load(scr_json)
        asyncio.run(create_ccda(scr))

        # bundle = Bundle.parse_obj(scr_json)
        # print(bundle)
