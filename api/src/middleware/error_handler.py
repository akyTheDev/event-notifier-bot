"""Error handler middleware."""

from fastapi.responses import ORJSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from src.core.exceptions import HttpException


class GenericErrorHandlerMiddleware(BaseHTTPMiddleware):
    """Generic error handler middleware."""

    async def dispatch(self, request, call_next):
        """Dispatch the request."""
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            status_code: int = e.status if isinstance(e, HttpException) else 500
            return ORJSONResponse(
                status_code=status_code,
                content={"detail": str(e)},
            )
