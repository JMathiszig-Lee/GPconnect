import os
import ast
from fastapi import FastAPI, Request
from fastapi.params import Depends
from fastapi.security import APIKeyCookie, OAuth2PasswordBearer
from requests.sessions import session
from starlette.responses import Response, RedirectResponse, HTMLResponse
from requests_oauthlib import OAuth2Session
from fhir.resources.bundle import Bundle
from fhir.resources.documentreference import DocumentReference

app = FastAPI()

BASE_URL = "https://sandbox.api.service.nhs.uk"
AUTHORISE_URL = "https://sandbox.api.service.nhs.uk/oauth2/authorize"
ACCESS_TOKEN_URL = "https://sandbox.api.service.nhs.uk/oauth2/token"
SUMMARY_CARE_URL = "https://sandbox.api.service.nhs.uk/summary-care-record/FHIR/R4"

cookie_sec = APIKeyCookie(name="session")
# replace "redirect_uri" with callback url,
# which you registered during the app registration
redirect_uri = "http://5650-82-69-117-126.ngrok.io/callback"

# replace with your api key
client_id = os.environ.get("CLIENT_ID")
# replace with your secret
client_secret = os.environ.get("CLIENT_SECRET")

@app.get("/")
async def root():
    return {"message": "hello world"}

@app.get("/login")
def login(response: Response):
    nhsd = OAuth2Session(client_id=client_id, redirect_uri=redirect_uri)
    authorization_url, state = nhsd.authorization_url(AUTHORISE_URL)
  
    # State is used to prevent CSRF, keep this for later.
    #session["oauth_state"] = state
    # response.set_cookie("session", state)
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
       code = code,
    )
    response = RedirectResponse("/scr")
    response.set_cookie("session", token)
    return response

@app.get("/profile")
def profile(token = Depends(cookie_sec)):
    #need ast.literal eval as otherwise token is a string and we get errors
    nhsd = OAuth2Session(client_id, token=ast.literal_eval(token))

    user_restricted_endpoint = nhsd.get(f"{BASE_URL}/hello-world/hello/user").json()
    return user_restricted_endpoint
    return {"test"}

@app.get("/scr")
def summary_care_record(token = Depends(cookie_sec)):
    #need ast.literal eval as otherwise token is a string and we get errors
    nhsd = OAuth2Session(client_id, token=ast.literal_eval(token))

    NHS_no = 9995000180
    FHir_identifier = f"https://fhir.nhs.uk/Id/nhs-number|{NHS_no}"
    user_restricted_endpoint = nhsd.get(f"{SUMMARY_CARE_URL}/DocumentReference", params={"patient":FHir_identifier}).json()
    
    scr_address = user_restricted_endpoint["entry"][0]["resource"]["content"][0]["attachment"]["url"]
    scr = nhsd.get(scr_address).json()
    html = ""
    # for key, value in scr["entry"][0].items():
    #     print(key, value)
    for i in scr["entry"][0]["resource"]["section"]:
        print("--------")
        print(i)
        print("--------")
        html += i["text"]["div"]
        html += "<hr>"
        # for key, value in i:
        #     print(key, value)
    return HTMLResponse(content=html)