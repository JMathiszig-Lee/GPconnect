import asyncio
import json
import os
import uuid
from datetime import timedelta

import fastapi
import httpx
from fhirclient.models import patient as p

from app.redis_connect import redis_client
from app.security import pds_jwt

BASE_PATH = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/"
DEV_BASE_PATH = "https://dev.api.service.nhs.uk/"
INT_BASE_PATH = "https://int.api.service.nhs.uk/"
API_KEY = os.getenv("API_KEY")

router = fastapi.APIRouter(prefix="/pds")


@router.get("/lookup_patient/{nhsno}")
async def lookup_patient(nhsno: int):
    full_path = f"{INT_BASE_PATH}oauth2/token"
    jwt_token = pds_jwt(API_KEY, API_KEY, full_path, "test-1")

    oauth_params = {
        "grant_type": "client_credentials",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
        "client_assertion": jwt_token,
    }
    r = httpx.post(full_path, data=oauth_params)

    response_dict = json.loads(r.text)
    nhs_token = response_dict["access_token"]
    redis_client.setex("access_token", response_dict["expires_in"], nhs_token)

    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "X-Correlation-ID": str(uuid.uuid4()),
        "NHSD-End-User-Organisation-ODS": "Y12345",
        "Authorization": f"Bearer {nhs_token}",
        "accept": "application/fhir+json",
    }

    url = f"{DEV_BASE_PATH}FHIR/R4/Patient/{nhsno}"
    print(url)

    r = httpx.get(url, headers=headers)
    patient_dict = json.loads(r.text)
    print(patient_dict)
    # print(patient_dict["generalPractitioner"])

    # nhs pds lookup returns superfluous values of type in resource which must be deleted
    # del patient_dict["generalPractitioner"][0]["type"]
    # del patient_dict["managingOrganization"]["type"]

    return p.Patient(patient_dict)


@router.get("/sds/{ods}")
def sds_trace(ods: str):
    url = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Device"
    organisation = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods}"
    identifier = [
        "https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1"
    ]
    api_key = os.environ.get("API_KEY")
    parameters = {
        "organization": organisation,
        "identifier": identifier,
    }
    print(parameters)
    headers = {
        "X-Request-ID": str(uuid.uuid4()),
        "accept": "application/fhir+json",
        "apikey": api_key,
    }
    r = httpx.get(url, headers=headers, params=parameters)
    return r


if __name__ == "__main__":

    patient = asyncio.run(lookup_patient(9000000009))

    print(patient.gender)
    print(patient.name[0].family)
    print(patient.generalPractitioner[0].identifier.value)

    ods = sds_trace("T99999")
    print(ods.text)
