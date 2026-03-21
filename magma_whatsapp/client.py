from __future__ import annotations

import requests

from .config import WhatsAppAPIConfig
from .modules import (
    WhatsAppMessages,
    WhatsAppMedia,
    WhatsAppAPIRequest,
    WhatsAppWebhookProcessor
)


class WhatsAppAPIClient(
    WhatsAppAPIRequest,
    WhatsAppMessages,
    WhatsAppMedia,
    WhatsAppWebhookProcessor
):

    def __init__(
            self, 
            config: WhatsAppAPIConfig,
            session: requests.Session | None = None,
        ):
        self.config = config
        self.session = session or requests.Session()

        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.config.access_token}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )