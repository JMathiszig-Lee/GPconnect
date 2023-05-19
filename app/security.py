import uuid
from time import time

import jwt

"""
creation of JWT as per https://developer.nhs.uk/apis/gpconnect-1-5-0/integration_cross_organisation_audit_and_provenance.html
"""


def pds_jwt(issuer, subject, audience, key_id):
    headers = {"typ": "JWT", "kid": key_id}
    payload = {
        "sub": subject,
        "iss": issuer,
        "jti": str(uuid.uuid4()),
        "aud": audience,
        "exp": int(time()) + 300,
    }
    with open("keys/test-1.pem", "r") as f:
        private_key = f.read()
    return jwt.encode(payload, key=private_key, algorithm="RS512", headers=headers)


def create_jwt(
    audience: str = "https://orange.testlab.nhs.uk/B82617/STU3/1/gpconnect/documents/fhir",
):
    """
    creates JWT for access to GP connect

    TODO:
    - make requesting device dynamic
    - make requesting organisation dynamic
    - make requesting practioner dynamic
    - make audience dynamic
    """
    created_time = int(time.time())
    payload = {
        "iss": "https://orange.testlab.nhs.uk/",
        "sub": "1",
        "aud": audience,
        "iat": created_time,
        "exp": created_time + 300,
        "reason_for_request": "directcare",
        "requested_scope": "patient/*.read",
        "requesting_device": {
            "resourceType": "Device",
            "identifier": [
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-system-instance-id",
                    "value": "gpcdemonstrator-1-orange",
                }
            ],
            "model": "GP Connect Demonstrator",
            "version": "1.5.0",
        },
        "requesting_organization": {
            "resourceType": "Organization",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/ods-organization-code",
                    "value": "A11111",
                }
            ],
            "name": "Consumer organisation name",
        },
        "requesting_practitioner": {
            "resourceType": "Practitioner",
            "id": "1",
            "identifier": [
                {
                    "system": "https://fhir.nhs.uk/Id/sds-user-id",
                    "value": "111111111111",
                },
                {
                    "system": "https://fhir.nhs.uk/Id/sds-role-profile-id",
                    "value": "22222222222222",
                },
                {
                    "system": "https://orange.testlab.nhs.uk/gpconnect-demonstrator/Id/local-user-id",
                    "value": "1",
                },
            ],
            "name": [
                {"family": "Demonstrator", "given": ["GPConnect"], "prefix": ["Dr"]}
            ],
        },
    }
    return jwt.encode(payload, headers={"alg": "none", "typ": "JWT"}, key=None)


if __name__ == "__main__":
    token = create_jwt()
    print(token)
