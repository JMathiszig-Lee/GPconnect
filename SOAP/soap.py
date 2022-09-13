from fastapi import APIRouter

router = APIRouter(prefix="/SOAP")


@router.post("/iti41")
async def iti41():
    pass


@router.post("/iti39")
async def iti39():
    pass


@router.post("/iti38")
async def iti38():
    pass
