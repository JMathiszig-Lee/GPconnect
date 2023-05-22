# GPConnect to CCDA service
![Python versio](https://img.shields.io/github/pipenv/locked/python-version/JMathiszig-Lee/GPconnect)

---


This is a service to connect to GP Connect and return the structured SCR record as a CCDA document

---
## Overview

Current the service is designed to interact with a requesting EHR via ITI requests in order to lookup, request and convert a patients summary care record
```mermaid
  sequenceDiagram
  participant EHR
  participant Service
  participant NHS API's
  participant Redis Cache
  EHR->>Service: ITI 47 Request
  Service->>NHS API's: FHIR PDS lookup
  NHS API's->> Service: PDS response
  Service->>EHR: ITI 47 Response
  Service ->> Redis Cache: Check for cached SDS lookup
  Service -->> NHS API's: SDS lookup
  NHS API's -->> Service: SDS Response
  Redis Cache ->> Service: Return ADIS and Fhir root
  EHR->>Service: ITI 38 Request
  Service->>Redis Cache: Check for cached response
  Service-->>NHS API's:GPconnnect Structured SCR request
  NHS API's-->> Service: Return Structured SCR
  Service->>Service: convert SCR to CCDA
  Service->>Redis Cache: Cache CCDA
  Service->>EHR: ITI 38 Response
  EHR->>Service: ITI 39 Request
  Service->>EHR: ITI 39 Response
```
---
## Tasks
Currently on open test environment or int as able:
- [ ] ITI 47
- [x] Fhir PDS lookup
- [x] ITI 38 call and response
- [x] GP Connect call
- [x] Fhir Bundle -> CCDA conversion
- [x] ITI 39 call and response

## Todo
- [ ] Flesh out html section of CCDA
- [ ] Progress to NHS test environment
- [x] Sign up to PDS lookup

---
## Running

The project is built on fastAPI and pipenv for package management

to run locally
```
pipenv shell
pipenv install --dev
```
the project requires an active redis server running on port 6379
this should be activated first by running (for example)
```
redis-server /etc/redis/6379.conf
```
the server can then be started using
```
uvicorn app.main:app --reload
```

### Docker

The project can also be run using docker. Ensure you have a valid installation and simple run
```
docker-compose up
```
---
## Branches

Development will take place on <a href=https://github.com/UCLH-Foundry/Xhuma/tree/dev>Dev</a>, check there for latest progress. Feature development should be checked out onto their own branch.
`Demo` is the branch for the internet facing demo, currently on heroku.
`Integration` will be for final intergration testing and `Main` will host final production builds

```mermaid
flowchart TD
Feature --> Dev --> Feature
Dev --PR --> Integration
Integration --PR-->Main
Dev -.-> Demo
click Dev href "https://github.com/UCLH-Foundry/Xhuma/tree/dev"
```

