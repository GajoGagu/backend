from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

def install_error_handlers(app: FastAPI):
    @app.exception_handler(Exception)
    async def _any(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content={"error":"internal_error","detail":str(exc)})
