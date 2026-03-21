from __future__ import annotations

from typing import Any


class WhatsAppAPIError(Exception):
    """Error base del cliente de WhatsApp Cloud API."""


class WhatsAppHTTPError(WhatsAppAPIError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        endpoint: str,
        response_body: Any,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.endpoint = endpoint
        self.response_body = response_body


class WhatsAppResponseError(WhatsAppAPIError):
    def __init__(self, message: str, *, endpoint: str, response_body: Any) -> None:
        super().__init__(message)
        self.endpoint = endpoint
        self.response_body = response_body
