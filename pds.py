import fastapi
import httpx
import asyncio
import uuid
import json
import os

from fhirclient.models import patient as p

BASE_PATH = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/"

router = fastapi.APIRouter()


@router.get("/lookup_patient/{nhsno}")
async def lookup_patient(nhsno: int) -> p.Patient:
    url = f"{BASE_PATH}/Patient/{nhsno}"
    headers = {"X-Request-ID": str(uuid.uuid4())}
    r = httpx.get(url, headers=headers)
    patient_dict = json.loads(r.text)
    print(patient_dict)
    print(patient_dict["generalPractitioner"])

    # nhs pds lookup returns superfluous values of type in resource which must be deleted
    del patient_dict["generalPractitioner"][0]["type"]
    del patient_dict["managingOrganization"]["type"]

    return p.Patient(patient_dict)


@router.get("/sds/{ods}")
def sds_trace(ods: str):
    url = "https://int.api.service.nhs.uk/spine-directory/FHIR/R4/Device"
    organisation = f"https://fhir.nhs.uk/Id/ods-organization-code|{ods}"
    identifier = ["https://fhir.nhs.uk/Id/nhsServiceInteractionId|urn:nhs:names:services:gpconnect:fhir:operation:gpc.getstructuredrecord-1"]
    api_key = os.environ.get("API_KEY")
    parameters = {
        "organization": organisation,
        "identifier": identifier,
    }
    print(parameters)
    headers = {"X-Request-ID": str(uuid.uuid4()), "accept": "application/fhir+json", "apikey": api_key}
    r = httpx.get(url, headers=headers, params=parameters)
    return r


if __name__ == "__main__":

    patient = asyncio.run(lookup_patient(9000000009))

    print(patient.gender)
    print(patient.name[0].family)
    print(patient.generalPractitioner[0].identifier.value)

    ods = sds_trace("T99999")
    print(ods.text)
