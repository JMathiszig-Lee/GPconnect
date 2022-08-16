import datetime

from fhirclient.models import list as fhirlist
from fhirclient.models import patient
from fhirclient.models import bundle

from entries import allergy, medication, problem


async def convert_bundle(bundle: bundle.Bundle, index: dict) -> dict:
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
    ccda["ClinicalDocument"] = {
        "realmCode": {"@code": "GB"},
        "title": {"#text": "Summary Care Record"},
    }
    ccda["ClinicalDocument"]["templateid"] = {
        "@root": "2.16.840.1.113883.10.20.22.1.2",
        "@extension": "2015-08-01",
    }

    # code
    ccda["ClinicalDocument"]["code"] = {
        "@code": "34133-9",
        "@codeSystem": "2.16.840.1.113883.6.1",
    }

    # patient
    # TODO refine address parsing as may have multiple

    patient_dict = {
        "patientRole": {
            "patient": {
                "id": {
                    "@extension": subject[0].identifier[0].value,
                    "@root": "2.16.840.1.113883.2.1.4.1",
                },
                "name": {
                    "@use": "L",
                    "given": {"#text": " ".join(subject[0].name[0].given)},
                    "family": {"#text": subject[0].name[0].family},
                },
                "birthTime": {"@value": subject[0].birthDate.isostring},
                "addr": {
                    "@use": "HP",
                    "streetAddressLine": [x for x in subject[0].address[0].line],
                    "city": {"#text": subject[0].address[0].city},
                    "postalCode": {"#text": subject[0].address[0].postalCode},
                },
            }
        }
    }

    ccda["ClinicalDocument"]["recordTarget"] = patient_dict

    # author
    ccda["ClinicalDocument"]["author"] = {
        "time": {"@value": datetime.datetime.today().isoformat()},
        "assignedAuthor": {
            "addr": {"@nullFlavor": "NA"},
            "telecom": {"@nullFlavor": "NA"},
            "assignedAuthoringDevice": {
                "manufacturerModelName": {"#text": "SCR Connector"},
                "softwareName": {"#text": "SCR Connector v0.1"},
            },
        },
    }

    # documentationOf
    ccda["ClinicalDocument"]["documentationOf"] = {
        "serviceEvent": {
            "@classCode": "PCPR",
            "effectiveTime": {
                "low": {
                    "@value": subject[0].birthDate.isostring,
                },
                "high": {"@value": datetime.date.today()},
            },
        }
    }


    #vital signs doesn't appear in the SCR therefore crate blank list to generate xml
    vital_signs = fhirlist.List()
    vital_signs.title = "Vital Signs"
    lists.append(vital_signs)

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
            "Vital Signs": {
                "displayName": "Vital Signs",
                "root": "2.16.840.1.113883.10.20.22.2.4.1",
                "Code": "8716-3",
            }
        }

        sections = [
            "Allergies and adverse reactions",
            "Immunisations",
            "Medications and medical devices",
            "Problems",
            "Vital Signs"
        ]

        # check if list is one of the desired ones
        if list.title in sections:
            print(list.title)
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
                    elif list.title == "Medications and medical devices":
                        comp["section"]["entry"].append(medication(referenced_item, index))

            return comp

    bundle_components = [create_section(list) for list in lists]
    bundle_components = [x for x in bundle_components if x is not None]
    ccda["ClinicalDocument"]["component"] = {}
    ccda["ClinicalDocument"]["component"]["structuredBody"] = {}
    ccda["ClinicalDocument"]["component"]["structuredBody"][
        "component"
    ] = bundle_components

    return ccda
