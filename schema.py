from xmlschema import XMLSchema

response_schema = XMLSchema("xml/multicacheschemas/PRPA_IN201306UV02.xsd")

# response_schema.validate("iti47.xml")

response_schema.iter_decode("iti47.xml", validation="lax")
print(response_schema.is_valid("iti47.xml"))