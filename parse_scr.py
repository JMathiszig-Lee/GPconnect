import json
import asyncio
from bs4 import BeautifulSoup
from pprint import pprint
import xml.etree.cElementTree as ET

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
    
    ccda = ET.Element("ClinicalDocument")
    ET.SubElement(ccda, "realmcode", code="GB")

    templateids = {
        "Allergies and Adverse Reactions": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.6",
            "Code": "48765-2"
        },
        "Current Repeat Medications": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.1",
            "Code": "10160-0"
        },
        "Problems and Issues": {
            "TemplateID": "2.16.840.1.113883.10.20.22.2.5",
            "Code": "11450-4"
        },
        "General Practice Summary": {
            "TemplateID": "blank",
            "Code": "blank"
        },
        "General Practice Summary": {
            "TemplateID": "blank",
            "Code": "blank"
        },
        "General Practice Summary": {
            "TemplateID": "blank",
            "Code": "blank"
        },
        "General Practice Summary": {
            "TemplateID": "blank",
            "Code": "blank"
        }

    }
    async def generate_component(section):
        try:
            component = ET.SubElement(ccda, "component")
            sec = ET.SubElement(component, "section")
            ET.SubElement(sec, "code", code =templateids[section["title"]]["Code"], codeSystem="2.16.840.1.113883.6.1", codeSystemName="LOINC", displayName=section["title"])
            ET.SubElement(sec, "templateId", root=templateids[section["title"]]["TemplateID"])
            ET.SubElement(sec, "title").text=section["title"]
            # ET.SubElement(sec, "text").text = section["text"]["div"]
        except:
            pass

    entry = scr["entry"][0]

    await asyncio.gather(
        *[generate_component(section) for section in entry["resource"]["section"]]
    )


    tree = ET.ElementTree(ccda)
    tree.write("ccda.xml")

if __name__ == "__main__":
    with open("scr.json") as scr_json:
        scr = json.load(scr_json)
        asyncio.run(create_ccda(scr))