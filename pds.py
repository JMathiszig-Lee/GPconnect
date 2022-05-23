import fastapi
import httpx
import asyncio
import uuid
import json

from fhirclient.models import patient as p

BASE_PATH = "https://sandbox.api.service.nhs.uk/personal-demographics/FHIR/R4/"

router = fastapi.APIRouter()

@router.post("/lookup_patient/{nhsno}")
async def lookup_patient(nhsno : int) -> p.Patient:
    url = f"{BASE_PATH}/Patient/{nhsno}"
    headers = {"X-Request-ID":str(uuid.uuid4())}
    r = httpx.get(url, headers=headers)
    patient_dict = json.loads(r.text)
    print(patient_dict.keys())
    print(patient_dict["generalPractitioner"])

    #nhs pds lookup returns superfluous values of type in resource which must be deleted
    del patient_dict["generalPractitioner"][0]["type"]
    del patient_dict["managingOrganization"]["type"]

    return p.Patient(patient_dict)

if __name__ == "__main__":

    patient = asyncio.run(lookup_patient(9000000009))

    print(patient.gender)
    print(patient.name[0].family)
    print(patient.managingOrganization)
    print(patient.generalPractitioner[0].as_json())
    print(patient.generalPractitioner[0].identifier.value)