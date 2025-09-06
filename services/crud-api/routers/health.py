from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/healthz")
def healthz(): 
    return {"ok": True}


@router.get("/readyz")
def readyz(): 
    return {"ready": True}
