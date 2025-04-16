"""Share core module."""

from .config import configuration
from .exceptions import HttpException

__all__ = [
    "configuration",
    # Exceptions
    "HttpException",
]
