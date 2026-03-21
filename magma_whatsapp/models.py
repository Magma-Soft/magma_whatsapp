from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class TextMessagePayload:
    to: str
    message: str
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"
    preview_url: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "messaging_product": self.messaging_product,
            "recipient_type": self.recipient_type,
            "to": self.to,
            "type": "text",
            "text": {
                "preview_url": self.preview_url,
                "body": self.message,
            },
        }


@dataclass(slots=True)
class TemplateMessagePayload:
    to: str
    template_name: str
    language: str
    components: list[dict[str, Any]] = field(default_factory=list)
    messaging_product: str = "whatsapp"
    recipient_type: str = "individual"

    def to_dict(self) -> dict[str, Any]:
        template: dict[str, Any] = {
            "name": self.template_name,
            "language": {"code": self.language},
        }
        if self.components:
            template["components"] = self.components

        return {
            "messaging_product": self.messaging_product,
            "recipient_type": self.recipient_type,
            "to": self.to,
            "type": "template",
            "template": template,
        }
