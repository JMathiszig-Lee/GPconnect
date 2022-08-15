import asyncio
from bdb import effective
import xml.etree.cElementTree as ET
from fhirclient.models.bundle import Bundle
from fhirclient.models import list as fhirlist
from fhirclient.models import patient

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

        
def create_section(list : fhirlist.List) -> dict:
    pass

async def convert_bundle(bundle: Bundle, index: dict) -> dict:
    # http://www.hl7.org/ccdasearch/templates/2.16.840.1.113883.10.20.22.1.15.html
    lists = [entry.resource.title for entry in bundle.entry if isinstance(entry.resource, fhirlist.List)]
    subject = [entry.resource for entry in bundle.entry if isinstance(entry.resource, patient.Patient)]
    ccda = {}
    ccda["ClinicalDocument"] = {}
    ccda["ClinicalDocument"]["templateid"] = {
        "@root": "2.16.840.1.113883.10.20.22.1.2",
        "@extension": "2015-08-01"
    }

    #code
    ccda["ClinicalDocument"]["code"] = {
        "@code": "34133-9",
        "@codeSystem": "2.16.840.1.113883.6.1"
    }

    #author

    #documentationOf
    ccda["ClinicalDocument"]["documentationOf"] = {
        "serviceEvent" : {
            "@classCode": "PCPR",
            "effectiveTime": {
                "low": subject[0].birthDate.isostring,
                "high": "20120915"
            }
        }
    }

    bundle_components = 

    ccda["ClinicalDocument"]["component"]["structuredBody"] = {}

    for list in lists:


    return ccda