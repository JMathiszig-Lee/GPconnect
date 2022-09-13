import json
import os
from uuid import uuid4

import httpx
import xmltodict
from fastapi import FastAPI, HTTPException
from fastapi.security import APIKeyCookie
from fhirclient.models import bundle

from fhir2ccda import convert_bundle
from helpers import validateNHSnumber
from redis_connect import redis_connect
from security import create_jwt

client = redis_connect()
app = FastAPI()
REGISTRY_ID = os.getenv("REGISTRY_ID", str(uuid4()))

BASE_URL = "https://sandbox.api.service.nhs.uk"
AUTHORISE_URL = "https://sandbox.api.service.nhs.uk/oauth2/authorize"
ACCESS_TOKEN_URL = "https://sandbox.api.service.nhs.uk/oauth2/token"
SUMMARY_CARE_URL = "https://sandbox.api.service.nhs.uk/summary-care-record/FHIR/R4"

cookie_sec = APIKeyCookie(name="session")
# replace "redirect_uri" with callback url,
# which you registered during the app registration
# this needs to be your own url or ngrok tunnel
redirect_uri = "http://520c-208-127-199-154.ngrok.io/callback"

# replace with your api key
client_id = os.environ.get("CLIENT_ID")
# replace with your secret
client_secret = os.environ.get("CLIENT_SECRET")


@app.on_event("startup")
async def startup_event():
    client.sadd("registry", REGISTRY_ID)


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/gpconnect/{nhsno}")
async def gpconnect(nhsno: int = 9690937286):
    # accesses gp connect endpoint for nhs number

    # validate nhsnumber
    if validateNHSnumber(nhsno) == False:
        raise HTTPException(status_code=400, detail="Invalid NHS number")

    FHir_identifier = f"https://fhir.nhs.uk/Id/nhs-number|{nhsno}"
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
    print(fhir_bundle)

    # index resources to allow for resolution
    bundle_index = {}
    for entry in fhir_bundle.entry:
        try:
            address = f"{entry.resource.resource_type}/{entry.resource.id}"
            bundle_index[address] = entry.resource
        except:
            pass

    for i in bundle_index:
        print(i)

    ##cache this response
    xml_ccda = await convert_bundle(fhir_bundle, bundle_index)
    # pprint(xml_ccda)
    with open(f"{nhsno}.xml", "w") as output:
        output.write(xmltodict.unparse(xml_ccda, pretty=True))

    return json.loads(r.text)
