from __future__ import annotations

import requests

from .config import WhatsAppAPIConfig
from .modules import (
    WhatsAppMessages,
    WhatsAppMedia,
    WhatsAppAPIRequest,
    WhatsAppWebhookProcessor,
    WhatsAppTemplates
)


class WhatsAppAPIClient(
    WhatsAppAPIRequest,
    WhatsAppMessages,
    WhatsAppMedia,
    WhatsAppWebhookProcessor,
    WhatsAppTemplates
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
                "Accept": "application/json",
            }
        )