"""Core exceptions module."""


class HttpException(ValueError):
    """Base Http Exception class."""

    def __init__(self, message: str, status: int) -> None:
        """Construct the class."""
        super().__init__(message)
        self.status = status


class BadRequestException(HttpException):
    """Raised when the request is not acceptible."""

    def __init__(self, message: str = "Bad Request") -> None:
        """Construct the class."""
        super().__init__(message, 400)


class UnauthorizedException(HttpException):
    """Raised when the request is unauthorized."""

    def __init__(self, message: str = "Unauthorized") -> None:
        """Construct the class."""
        super().__init__(message, 401)


class ForbiddenException(HttpException):
    """Raised when the request is forbidden for the user."""

    def __init__(self, message: str = "Forbidden") -> None:
        """Construct the class."""
        super().__init__(message, 403)


class NotFoundException(HttpException):
    """Raised when the requested entity not found."""

    def __init__(self, message: str = "Not Found") -> None:
        """Construct the class."""
        super().__init__(message, 404)


class UnprocessableEntityException(HttpException):
    """Raised when the requested entity is not unprocessable."""

    def __init__(self, message: str = "Unprocessable Content") -> None:
        """Construct the class."""
        super().__init__(message, 422)
