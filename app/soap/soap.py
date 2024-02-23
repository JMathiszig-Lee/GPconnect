import json
from urllib.request import Request

import xmltodict
from fastapi import APIRouter, HTTPException, Request, Response, APIRoute
from typing import Callable, Dict, Any
from starlette.background import BackgroundTask

from ..ccda.helpers import clean_soap
from ..redis_connect import redis_connect
from .responses import iti_38_response, iti_39_response

import logging

def log_info(req_body, res_body):
    logging.info(req_body)
    logging.info(res_body)

class LoggingRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def custom_route_handler(request: Request) -> Response:
                req_body = await request.body()
                response = await original_route_handler(request)
                tasks = response.background

                task = BackgroundTask(log_info, req_body, response.body)

                # check if the original response had background tasks already assigned to it
                if tasks:
                    tasks.add_task(task)  # add the new task to the tasks list
                    response.background = tasks
                else:
                    response.background = task

                return response
        
        return custom_route_handler




router = APIRouter(prefix="/SOAP", route_class=LoggingRoute)
logging.basicConfig(filename='info.log', level=logging.DEBUG)
client = redis_connect()

NAMESPACES = (
    {
        "http://www.w3.org/2003/05/soap-envelope": None,
        "http://www.w3.org/2005/08/addressing": None,
        "urn:oasis:names:tc:ebxml-regrep:xsd:query:3.0": None,
        "urn:oasis:names:tc:ebxml-regrep:xsd:rim:3.0": None,
        "urn:ihe:iti:xds-b:2007": None,
    },
)



@router.post("/iti47")
async def iti47(request: Request):
    content_type = request.headers["Content-Type"]
    if content_type == "application/soap+xml":
        body = await request.body()
        envelope = clean_soap(body)
        soap_body = envelope["Body"]
        slots = soap_body["AdhocQueryRequest"]["AdhocQuery"]["Slot"]
        query_id = soap_body["AdhocQueryRequest"]["AdhocQuery"]["@id"]
        patient_id = next(
            x["ValueList"]["Value"]
            for x in slots
            if x["@name"] == "$XDSDocumentEntryPatientId"
        )
        data = """"<?xml version="1.0"?>
            <Header>
                ping
            </Header>
            <Body>
            Pong
            </Body>
            """
        return Response(content=data, media_type="application/xml")
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )

    


@router.post("/iti39")
async def iti39(request: Request):
    content_type = request.headers["Content-Type"]
    if content_type == "application/soap+xml":
        body = await request.body()
        envelope = clean_soap(body)
        try:
            document_id = envelope["Body"]["RetrieveDocumentSetRequest"][
                "DocumentRequest"
            ]["DocumentUniqueId"]
        except:
            raise HTTPException(status_code=404, detail=f"DocumentUniqueId not found")

        document = client.get(document_id)
        if document is not None:
            # return ITI39 response
            message_id = envelope["Header"]["MessageID"]
            data = await iti_39_response(message_id, document_id, document)
            return Response(content=data, media_type="application/soap+xml")
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Document with Id {document_id} not found or is empty",
            )
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )


@router.post("/iti38")
async def iti38(request: Request):
    content_type = request.headers["Content-Type"]
    if content_type == "application/soap+xml":
        body = await request.body()
        envelope = clean_soap(body)
        soap_body = envelope["Body"]
        slots = soap_body["AdhocQueryRequest"]["AdhocQuery"]["Slot"]
        query_id = soap_body["AdhocQueryRequest"]["AdhocQuery"]["@id"]
        patient_id = next(
            x["ValueList"]["Value"]
            for x in slots
            if x["@name"] == "$XDSDocumentEntryPatientId"
        )
        data = await iti_38_response(patient_id, query_id)
        return Response(content=data, media_type="application/xml")
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )
