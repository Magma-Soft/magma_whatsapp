from __future__ import annotations

import requests
from requests import Response

from typing import Any, Literal

from magma_whatsapp.exceptions import WhatsAppHTTPError, WhatsAppResponseError


AllowedMethod = Literal["GET", "POST"]


class WhatsAppAPIRequest:

    def request(
        self,
        method: AllowedMethod,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        files: dict[str, Any] | None = None,
        response_type: Literal["json", "content", "text", "raw"] = "json",
    ):
        normalized_method = method.upper()

        if normalized_method not in AllowedMethod.__args__:
            raise ValueError(f"HTTP method not allowed: {method}")

        if endpoint.startswith("http"):
            url = endpoint
        else:
            cleaned_endpoint = endpoint.lstrip("/")
            url = f"{self.config.base_url}/{cleaned_endpoint}"

        try:
            request_kwargs = {
                "method": method,
                "url": url,
                "params": params,
                "timeout": self.config.timeout,
            }

            if files:
                headers = self.session.headers.copy()
                headers.pop("Content-Type", None)

                request_kwargs["headers"] = headers
                request_kwargs["data"] = payload
                request_kwargs["files"] = files
            else:
                request_kwargs["json"] = payload

            response: Response = self.session.request(**request_kwargs)

        except requests.RequestException as exc:
            raise WhatsAppHTTPError(
                f"Network error when calling WhatsApp API: {exc}",
                status_code=0,
                endpoint=endpoint,
                response_body=None,
            ) from exc

        if not response.ok:
            try:
                response_body = response.json()
            except ValueError:
                response_body = response.text

            raise WhatsAppHTTPError(
                (
                    f"WhatsApp API returned an HTTP error "
                    f"{response.status_code}: {response_body}"
                ),
                status_code=response.status_code,
                endpoint=endpoint,
                response_body=response_body,
            )

        if response_type == "json":
            return response.json()

        if response_type == "content":
            return response.content

        if response_type == "text":
            return response.text

        if response_type == "raw":
            return response

        raise ValueError(f"Unsupported response_type: {response_type}")