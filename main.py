import os
import ast
from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.security import APIKeyCookie
from starlette.responses import Response, RedirectResponse
from requests_oauthlib import OAuth2Session
import parse_scr

app = FastAPI()

BASE_URL = "https://sandbox.api.service.nhs.uk"
AUTHORISE_URL = "https://sandbox.api.service.nhs.uk/oauth2/authorize"
ACCESS_TOKEN_URL = "https://sandbox.api.service.nhs.uk/oauth2/token"
SUMMARY_CARE_URL = "https://sandbox.api.service.nhs.uk/summary-care-record/FHIR/R4"

cookie_sec = APIKeyCookie(name="session")
# replace "redirect_uri" with callback url,
# which you registered during the app registration
# this needs to be your own url or ngrok tunnel
redirect_uri = "http://4aaf-208-127-198-204.ngrok.io/callback"

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


@app.get("/scr")
async def summary_care_record(token=Depends(cookie_sec)):
    # need ast.literal eval as otherwise token is a string and we get errors
    nhsd = OAuth2Session(client_id, token=ast.literal_eval(token))

    NHS_no = 9995000180
    FHir_identifier = f"https://fhir.nhs.uk/Id/nhs-number|{NHS_no}"
    user_restricted_endpoint = nhsd.get(
        f"{SUMMARY_CARE_URL}/DocumentReference", params={"patient": FHir_identifier}
    ).json()

    scr_address = user_restricted_endpoint["entry"][0]["resource"]["content"][0][
        "attachment"
    ]["url"]
    scr = nhsd.get(scr_address).json()

    parsed = await parse_scr.parse_scr(scr)

    return {"scr": parsed}
