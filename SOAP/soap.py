from urllib.request import Request

from fastapi import APIRouter, HTTPException, Request, Response

router = APIRouter(prefix="/SOAP")


@router.post("/iti41")
async def iti41():
    # Response(content=data, media_type="application/xml")
    pass


@router.post("/iti39")
async def iti39():
    # Response(content=data, media_type="application/xml")
    pass


@router.post("/iti38")
async def iti38(request: Request):
    content_type = request.headers["Content-Type"]
    # Response(content=data, media_type="application/xml")
    if content_type == "application/xml":
        body = await request.body()
        return Response(content=body, media_type="application/xml")
    else:
        raise HTTPException(
            status_code=400, detail=f"Content type {content_type} not supported"
        )
