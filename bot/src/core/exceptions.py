"""Shared exceptions module."""


class HttpException(ValueError):
    """Raised when there is any HTTP exception."""

    def __init__(self, message: str) -> None:
        """Initialize the class."""
        super().__init__(message)
