from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Optional


@dataclass(slots=True, frozen=True)
class WhatsAppAPIConfig:
    api_version: str
    access_token: str
    waba_id: Optional[str] = None
    graph_api_base_url: str = "https://graph.facebook.com"
    timeout: int = 30
    base_url: Optional[str] = None

    def __post_init__(self) -> None:
        api_version = self.api_version.strip()
        access_token = self.access_token.strip()
        graph_api_base_url = self.graph_api_base_url.rstrip("/")

        if not api_version:
            raise ValueError("api_version no puede estar vacío")
        if not access_token:
            raise ValueError("access_token no puede estar vacío")

        base_url = self.base_url or f"{graph_api_base_url}/{api_version}"

        object.__setattr__(self, "api_version", api_version)
        object.__setattr__(self, "access_token", access_token)
        object.__setattr__(self, "graph_api_base_url", graph_api_base_url)
        object.__setattr__(self, "base_url", base_url)

    def __str__(self) -> str:
        return (
            f"WhatsAppAPIConfig(\n"
            f"  api_version={self.api_version},\n"
            f"  waba_id={self.waba_id},\n"
            f"  graph_api_base_url={self.graph_api_base_url},\n"
            f"  timeout={self.timeout},\n"
            f"  base_url={self.base_url},\n"
            f"  access_token=***hidden***\n"
            f")"
        )

    def print_config(self) -> None:
        print(self)

    def to_dict(self, hide_sensitive: bool = True) -> dict:
        data = asdict(self)

        if hide_sensitive:
            data["access_token"] = "***hidden***"

        return data