import ast
import asyncio
import json
import os
import httpx
import parse_scr

from pprint import pprint
from fastapi import FastAPI, HTTPException, Request, Response, applications
from fastapi.params import Depends
from fastapi.security import APIKeyCookie
from fhirclient.models import bundle
from fhirclient.models import list as fhirlist
from fhirclient.models import medication, medicationstatement
from requests_oauthlib import OAuth2Session
from starlette.responses import RedirectResponse, Response

from fhir2ccda import convert_bundle
from security import create_jwt

app = FastAPI()

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


@app.get("/")
async def root():
    return {"message": "hello world"}


@app.get("/login")
def login():
    nhsd = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri)
    authorization_url, state = nhsd.authorization_url(AUTHORISE_URL)

    return RedirectResponse(authorization_url)


@app.get("/callback")
def callback(response: Response, request: Request, code, state):
    print("callback")
    nhsd = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri, state=state)

    token = nhsd.fetch_token(
        token_url=ACCESS_TOKEN_URL,
        client_secret=client_secret,
        include_client_id=client_id,
        authorization_response=request.url,
        code=code,
    )
    response = RedirectResponse("/scr")
    response.set_cookie("session", token)
    return response


@app.get("/gpconnect/{nhsno}")
async def gpconnect(nhsno: int = 9690937286):
    # accesses gp connect endpoint for nhs number
    def validateNHSnumber(number):
        numbers = [int(c) for c in str(number)]

        total = 0
        for idx in range(0, 9):
            multiplier = 10 - idx
            total += numbers[idx] * multiplier

        _, modtot = divmod(total, 11)
        checkdig = 11 - modtot

        if checkdig == 11:
            checkdig = 0

        return checkdig == numbers[9]

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
    print(r)

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

    for i in bundle_index:
        print(i)

    # pprint(bundle_index)
    xml_ccda = await convert_bundle(fhir_bundle, bundle_index)
    print(xml_ccda)

    for entry in fhir_bundle.entry:
        # print(entry.resource)
        if isinstance(entry.resource, medicationstatement.MedicationStatement):

            med_statement = entry.resource
            if med_statement.status == "active":
                pass
                # pprint(med_statement.as_json())
                # print(med_statement.dosage[0].text)
                # print(med_statement.dosage[0].patientInstruction)
                # print(bundle_index[entry.resource.medicationReference.reference].code.coding[0].display)

        elif isinstance(entry.resource, fhirlist.List):
            print("--------")

            scr_list = entry.resource
            print(scr_list.title)
            if scr_list.entry:
                for entry in scr_list.entry:

                    referenced_item = bundle_index[entry.item.reference]

                    if isinstance(
                        referenced_item, medicationstatement.MedicationStatement
                    ):

                        med_statement = referenced_item
                        # if med_statement.status == "active":
                        # pprint(med_statement.as_json())
                        print(
                            bundle_index[referenced_item.medicationReference.reference]
                            .code.coding[0]
                            .display
                        )
                        print("-" + med_statement.dosage[0].text)
                        print("-" + med_statement.dosage[0].patientInstruction)
                        print("STATUS: " + med_statement.status)
                    else:
                        try:
                            print(referenced_item.code.coding[0].display)
                        except:
                            try:
                                print(referenced_item.title)
                            except:
                                print(entry.item.reference)

                print("--------")

    return json.loads(r.text)


@app.get("/scr")
async def summary_care_record(token=Depends(cookie_sec)):
    # need ast.literal eval as otherwise token is a string and we get errors
    nhsd = OAuth2Session(client_id, token=ast.literal_eval(token))

    NHS_no = 9000000009
    FHir_identifier = f"https://fhir.nhs.uk/Id/nhs-number|{NHS_no}"
    user_restricted_endpoint = nhsd.get(
        f"{SUMMARY_CARE_URL}/DocumentReference", params={"patient": FHir_identifier}
    ).json()
    print(user_restricted_endpoint)
    scr_address = user_restricted_endpoint["entry"][0]["resource"]["content"][0][
        "attachment"
    ]["url"]
    scr = nhsd.get(scr_address).json()

    parsed = await parse_scr.parse_scr(scr)

    return {"scr": parsed}


@app.get("/ccda")
async def return_ccda():
    # returns a ccda from saved json for now to prevent auth headaches
    with open("scr.json") as scr_json:
        scr = json.load(scr_json)
        xml = await parse_scr.create_ccda(scr)
        # print(xml)
        return Response(content=xml, media_type="application/xml")
