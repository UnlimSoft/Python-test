from fastapi import FastAPI, Request, responses

from utils import exceptions
from .v1 import router as v1

app = FastAPI()
app.include_router(v1)


@app.exception_handler(exceptions.BaseAPIException)
async def unicorn_exception_handler(request: Request, exc: exceptions.BaseAPIException):
    return responses.JSONResponse(
        status_code=400,
        content={'code': exc.code, 'error': exc.detail},
    )
