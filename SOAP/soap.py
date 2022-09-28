import json
from urllib.request import Request

import xmltodict
from fastapi import APIRouter, HTTPException, Request, Response

from ccda.helpers import clean_soap
from redis_connect import redis_connect

router = APIRouter(prefix="/SOAP")
client = redis_connect()

NAMESPACES = (
    {
        "http://www.w3.org/2003/05/soap-envelope": None,
        "http://www.w3.org/2005/08/addressing": None,
        "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
        "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
        "urn:ihe:iti:xds-b:2007": None,
    },
)


@router.post("/iti41")
async def iti41(equest: Request):
    # Response(content=data, media_type="application/xml")
    pass


@router.post("/iti39")
async def iti39(request: Request):
    content_type = request.headers["Content-Type"]
    if content_type == "application/xml":
        body = await request.body()
        envelope = clean_soap(body)
        try:
            document_id = envelope["Body"]["RetrieveDocumentSetRequest"][
                "DocumentRequest"
            ]["DocumentUniqueId"]
            document = client.get(document_id)
            return document
        except:
            raise HTTPException(status_code=404, detail=f"Document not found")
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )

from fhirclient.models import bundle

@router.post("/iti38")
async def iti38(request: Request):
    content_type = request.headers["Content-Type"]
    # Response(content=data, media_type="application/xml")
    if content_type == "application/xml":
        body = await request.body()
        dict = xmltodict.parse(
            body,
            process_namespaces=True,
            namespaces={
                "http://www.w3.org/2003/05/soap-envelope": None,
                "http://www.w3.org/2005/08/addressing": None,
                "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
                "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
                "urn:ihe:iti:xds-b:2007": None,
            },
        )
        return dict
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )
