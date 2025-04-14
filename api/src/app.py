"""Main application file."""

from fastapi import Depends, FastAPI
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.middleware import Middleware

from src.api import event_router
from src.core import UnauthorizedException, configuration
from src.middleware import GenericErrorHandlerMiddleware

security: HTTPBasic = HTTPBasic()
security_dependency = Depends(security)


def verify_credentials(credentials: HTTPBasicCredentials = security_dependency):
    """Verify the given credentials."""
    correct_credentials: dict[str, str] = {
        "username": configuration.AUTH.USER,
        "password": configuration.AUTH.PASS,
    }
    if dict(credentials) != correct_credentials:
        raise UnauthorizedException()


app: FastAPI = FastAPI(
    title="Calendar Bot API",
    description="Calendar Bot API.",
    version="0.0.1",
    middleware=[Middleware(GenericErrorHandlerMiddleware)],
    dependencies=[Depends(verify_credentials)],
)

app.include_router(event_router)
