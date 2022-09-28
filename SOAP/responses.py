import xmltodict


async def iti_39_response(request_header, document):

    soap_response = {}
    soap_response["Header"] = request_header
    soap_response["Body"] = {}

    return xmltodict.unparse(soap_response, pretty=True)
