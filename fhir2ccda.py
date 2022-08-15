import asyncio
import datetime
import xml.etree.cElementTree as ET
from bdb import effective

from fhirclient.models import list as fhirlist
from fhirclient.models import patient
from fhirclient.models.bundle import Bundle

from entries import allergy, problem


async def convert_resource(res):
    def get_code(code: dict):
        code_xml = ET.Element(
            "code",
            code=code["coding"][0]["code"],
            codeSystemName=code["coding"][0]["system"],
            displayName=code["coding"][0]["display"],
        )
        return code_xml

    def convert_Condition(res):
        entry = ET.Element("entry")
        # code
        entry.append(get_code(res["resource"]["code"]))

        # status
        ET.SubElement(
            entry,
            "statusCode",
            code=res["resource"]["verificationStatus"]["coding"][0]["code"],
        )
        # effective time
        onset = ET.SubElement(entry, "effectiveTime")
        ET.SubElement(onset, "low", value=res["resource"]["onsetDateTime"])

        return entry

    def convert_Observation(res):
        entry = ET.Element("observation")
        entry.append(get_code(res["resource"]["code"]))

        # status
        ET.SubElement(entry, "statusCode", code=res["resource"]["status"])

        # time
        onset = ET.SubElement(entry, "effectiveTime")
        ET.SubElement(onset, "low", value=res["resource"]["effectivePeriod"]["start"])

        return entry

    def convert_Encounter():
        pass

    def convert_PractionerRole():
        pass

    def convert_Practioner():
        pass

    def convert_Problem():
        pass

    def convert_Allergy():
        pass

    if res:
        # res = Condition.parse_obj(res["resource"])
        resource_type = res["resource"]["resourceType"]
        first_word = resource_type.split()[0]
        thing = locals()[f"convert_{first_word}"](res)
        return thing


async def convert_bundle(bundle: Bundle, index: dict) -> dict:
    # http://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.1.15.html
    lists = [
        entry.resource
        for entry in bundle.entry
        if isinstance(entry.resource, fhirlist.List)
    ]
    subject = [
        entry.resource
        for entry in bundle.entry
        if isinstance(entry.resource, patient.Patient)
    ]
    ccda = {}
    ccda["ClinicalDocument"] = {}
    ccda["ClinicalDocument"]["templateid"] = {
        "@root": "2.16.840.1.113883.10.20.22.1.2",
        "@extension": "2015-08-01",
    }

    # code
    ccda["ClinicalDocument"]["code"] = {
        "@code": "34133-9",
        "@codeSystem": "2.16.840.1.113883.6.1",
    }

    # author

    # documentationOf
    ccda["ClinicalDocument"]["documentationOf"] = {
        "serviceEvent": {
            "@classCode": "PCPR",
            "effectiveTime": {
                "low": {
                    "@value": subject[0].birthDate.isostring,
                },
                "high": {"@value": datetime.datetime.today().isoformat()},
            },
        }
    }

    def create_section(list: fhirlist.List) -> dict:
        templates = {
            "Allergies and adverse reactions": {
                "displayName": "Allergies, adverse reactions, alerts",
                "root": "2.16.840.1.113883.10.20.22.2.6.1",
                "Code": "48765-2",
            },
            "Medications and medical devices": {
                "displayName": "Medications",
                "root": "2.16.840.1.113883.10.20.22.2.1",
                "Code": "10160-0",
            },
            "Problems": {
                "displayName": "Problems List",
                "root": "2.16.840.1.113883.10.20.22.2.5.1",
                "Code": "11450-4",
            },
            "Immunisations": {
                "displayName": "Immunisations",
                "root": "2.16.840.1.113883.10.20.22.2.5",
                "Code": "11450-4",
            },
        }

        sections = [
            "Allergies and adverse reactions",
            "Immunisations",
            "Medications and medical devices",
            "Problems",
        ]

        # check if list is one of the desired ones
        if list.title in sections:
            comp = {}
            comp["section"] = {
                "templateId": {
                    "@root": templates[list.title]["root"],
                    "@extension": "2015-08-01",
                },
                "code": {
                    "@code": templates[list.title]["Code"],
                    "@displayName": templates[list.title]["displayName"],
                    "@codeSystem": "2.16.840.1.113883.6.1",
                },
                "title": list.title,
                "text": "lorem ipsum",
            }
            # if there are no entries
            if not list.entry:
                comp["section"]["@nullFlavour"] = "NI"
                comp["section"]["text"] = "No Information"

            else:
                comp["section"]["entry"] = []
                for entry in list.entry:
                    referenced_item = index[entry.item.reference]

                    if list.title == "Allergies and adverse reactions":
                        comp["section"]["entry"].append(allergy(referenced_item))
                    elif list.title == "Problems":
                        comp["section"]["entry"].append(problem(referenced_item))

            return comp

    bundle_components = [create_section(list) for list in lists]
    bundle_components = [x for x in bundle_components if x is not None]
    ccda["ClinicalDocument"]["component"] = {}
    ccda["ClinicalDocument"]["component"]["structuredBody"] = {}
    ccda["ClinicalDocument"]["component"]["structuredBody"][
        "component"
    ] = bundle_components

    return ccda
