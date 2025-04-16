"""Utils functions for service module."""

import urllib.parse
from base64 import b64encode
from enum import Enum
from json import dumps
from typing import Any

from aiohttp import ClientSession
from pydantic import validate_call

from src.core import HttpException, configuration


class HTTPMethods(str, Enum):
    """Enum of possible HTTP methods."""

    GET = "get"
    POST = "post"
    PUT = "put"
    PATCH = "patch"
    DELETE = "delete"


@validate_call
async def send_http_request(
    url: str,
    params: dict[str, Any] | None = None,
    method: HTTPMethods = HTTPMethods.GET,
    body: Any = None,
    headers: dict[str, str] | None = None,
) -> Any:
    """Send request to the specified url.

    Arguments:
        url: URL to send request.
        params: Query parameters of the request.
        method: HTTP Method to send request.
        body: Body parameters of the request.
        headers: Headers of the request.

    Returns:
        The json response of the request.
    """
    request_url: str = f"{url}?{urllib.parse.urlencode(params)}" if params else url
    print("Sending to ", request_url)

    token: str = f"{configuration.API.USER}:{configuration.API.PASS}"
    raw_headers: dict[str, str] = {
        "Content-Type": "application/json",
        "accept": "application/json",
        "Authorization": f"Basic {b64encode(token.encode('utf-8')).decode('utf-8')}",
    }
    headers = {**raw_headers, **headers} if headers else raw_headers

    raw_request_func_params: dict[str, str] = {
        "method": method,
        "url": request_url,
    }

    request_func_params: dict[str, Any] = (
        {**raw_request_func_params, "data": dumps(body)}
        if body
        else raw_request_func_params
    )

    async with (
        ClientSession(headers=headers) as session,
        session.request(**request_func_params) as response,
    ):
        if not response.ok:
            error_message: str = "Request is failed!"
            print(await response.json())
            raise HttpException(error_message)
        return await response.json()
