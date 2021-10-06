# nhsAPIs
Test repo to connect up to NHS digital API's

basic demo of connection to summary care record via oauth2 and parsing

to run:
change callback to your url (ngrok is useful)
create .env file in repo and add nhs developer api keys
set up environment with pipenv
run fastapi with uvicorn main:app --reload