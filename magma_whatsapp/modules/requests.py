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
            response: Response = self.session.request(
                method=method,
                url=url,
                json=payload,
                params=params,
                timeout=self.config.timeout,
            )
        except requests.RequestException as exc:
            raise WhatsAppHTTPError(
                f"Network error when calling WhatsApp API: {exc}",
                status_code=0,
                endpoint=endpoint,
                response_body=None,
            ) from exc

        if not response.ok:
            response_body: Any
            try:
                response_body = response.json()
            except ValueError:
                response_body = response.text

            raise WhatsAppHTTPError(
                "WhatsApp API returned an HTTP error",
                status_code=response.status_code,
                endpoint=cleaned_endpoint,
                response_body=response_body,
            )

        if response_type == "json":
            try:
                parsed_response = response.json()
            except ValueError as exc:
                raise WhatsAppResponseError(
                    "Invalid response: expected JSON",
                    endpoint=cleaned_endpoint,
                    response_body=response.text,
                ) from exc

            if not isinstance(parsed_response, dict):
                raise WhatsAppResponseError(
                    "Invalid response: expected JSON object",
                    endpoint=cleaned_endpoint,
                    response_body=parsed_response,
                )

            return parsed_response

        elif response_type == "content":
            return response.content

        elif response_type == "text":
            return response.text

        elif response_type == "raw":
            return response

        else:
            raise ValueError(f"Unsupported response_type: {response_type}")
