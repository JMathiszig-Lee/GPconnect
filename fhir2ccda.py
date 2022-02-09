import xml.etree.cElementTree as ET


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
        #code
        entry.append(get_code(res["resource"]["code"]))
        
        #status
        ET.SubElement(entry, "statusCode", code =res["resource"]["verificationStatus"]["coding"][0]["code"] )
        #effective time
        onset = ET.SubElement(entry, "effectiveTime")
        ET.SubElement(onset, "low", value = res["resource"]["onsetDateTime"])


        
        return entry


    def convert_Observation(res):
        entry = ET.Element("observation")
        entry.append(get_code(res["resource"]["code"]))
        
        #status
        ET.SubElement(entry, "statusCode", code =res["resource"]["status"])

        #time
        onset = ET.SubElement(entry, "effectiveTime")
        ET.SubElement(onset, "low", value = res["resource"]["effectivePeriod"]["start"])

        
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
