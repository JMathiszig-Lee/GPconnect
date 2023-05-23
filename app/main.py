import json
import logging
import os
from datetime import timedelta
from uuid import uuid4

import httpx
import xmltodict
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fhirclient.models import bundle

from .ccda.convert_mime import convert_mime
from .ccda.fhir2ccda import convert_bundle
from .ccda.helpers import validateNHSnumber
from .pds import pds
from .redis_connect import redis_client
from .security import create_jwt
from .soap import soap

app = FastAPI()
app.include_router(soap.router)
app.include_router(pds.router)

REGISTRY_ID = os.getenv("REGISTRY_ID", str(uuid4()))


@app.on_event("startup")
async def startup_event():
    redis_client.set("registry", REGISTRY_ID)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def root():
    return """
    <html>
        <head>
            <title> Welcome </title
        </head>
        <body>
            <h3>Xhuma</h3>
            <p>This is the internet facing demo for Xhuma</p>
            <p>Interactive API documentation is available <a href="/docs#/">here</a>
            <h4>endpoints</h4>
            <p>/pds/lookuppatient/nhsno will perform a pds lookup and return the fhir response. <a href="pds/lookup_patient/9449306680">Example</a></p>
            <p>/gpconnect/nhsno will perform a gpconnect access record structured query, convert it to a CCDA and return the cached record uuid. <a href="gpconnect/9690937278">Example</a></p>
            <p>for the purposes of the internet facing demo /demo/nhsno will return the mime encoded ccda. <a href="/demo/9690937278">Example</a></p>
        </body>
    </html
    """

@app.get("/demo/{nhsno}")
async def demo(nhsno: int):
    """
    """
    bundle_id = await gpconnect(nhsno)

    return redis_client.get(bundle_id["document_id"])

@app.get("/gpconnect/{nhsno}")
async def gpconnect(nhsno: int):
    """accesses gp connect endpoint for nhs number"""

    # validate nhsnumber
    if validateNHSnumber(nhsno) == False:
        logging.error(f"{nhsno} is not a valid NHS number")
        raise HTTPException(status_code=400, detail="Invalid NHS number")

    # TODO pds search
    pds_search = await pds.lookup_patient(nhsno)
    print(pds_search)

    # TODO sds search

    token = create_jwt()

    headers = {
        "Ssp-TraceID": "09a01679-2564-0fb4-5129-aecc81ea2706",
        "Ssp-From": "200000000359",
        "Ssp-To": "918999198738",
        "Ssp-InteractionID": "urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1",
        "Authorization": f"Bearer {token}",
        "accept": "application/fhir+json",
        "Content-Type": "application/fhir+json",
    }

    body = {
        "resourceType": "Parameters",
        "parameter": [
            {
                "name": "patientNHSNumber",
                "valueIdentifier": {
                    "system": "https://fhir.nhs.uk/Id/nhs-number",
                    "value": f"{nhsno}",
                },
            },
            {
                "name": "includeAllergies",
                "part": [{"name": "includeResolvedAllergies", "valueBoolean": False}],
            },
            {
                "name": "includeMedication",
                "part": [{"name": "includePrescriptionIssues", "valueBoolean": False}],
            },
            {"name": "includeProblems"},
            {"name": "includeImmunisations"},
            {"name": "includeInvestigations"},
        ],
    }
    r = httpx.post(
        "https://orange.testlab.nhs.uk/B82617/STU3/1/gpconnect/structured/fhir/Patient/$gpc.getstructuredrecord",
        json=body,
        headers=headers,
    )

    scr_bundle = json.loads(r.text)

    # get rid of fhir_comments
    comment_index = None
    for j, i in enumerate(scr_bundle["entry"]):
        if "fhir_comments" in i.keys():
            comment_index = j
    if comment_index is not None:
        scr_bundle["entry"].pop(comment_index)

    fhir_bundle = bundle.Bundle(scr_bundle)

    # index resources to allow for resolution
    bundle_index = {}
    for entry in fhir_bundle.entry:
        try:
            address = f"{entry.resource.resource_type}/{entry.resource.id}"
            bundle_index[address] = entry.resource
        except:
            pass

    xml_ccda = await convert_bundle(fhir_bundle, bundle_index)
    xop = convert_mime(xml_ccda)
    doc_uuid = str(uuid4())

    # TODO set this as background task
    redis_client.setex(nhsno, timedelta(minutes=5), doc_uuid)
    redis_client.setex(doc_uuid, timedelta(minutes=5), xop)

    # pprint(xml_ccda)
    with open(f"{nhsno}.xml", "w") as output:
        output.write(xmltodict.unparse(xml_ccda, pretty=True))

    return {"document_id": doc_uuid}
