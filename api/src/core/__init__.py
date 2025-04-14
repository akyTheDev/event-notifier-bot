"""Shared core module."""

from .config import configuration
from .exceptions import (
    BadRequestException,
    ForbiddenException,
    NotFoundException,
    UnauthorizedException,
    UnprocessableEntityException,
)

__all__ = [
    "configuration",
    # Exceptions
    "BadRequestException",
    "UnauthorizedException",
    "ForbiddenException",
    "NotFoundException",
    "UnprocessableEntityException",
]
