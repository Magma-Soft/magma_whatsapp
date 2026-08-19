from __future__ import annotations

from typing import Any, Literal


class WhatsAppTemplates:
    def list_all_templates(self, waba_id: str | None = None) -> list[dict[str, Any]]:
        """
        Retrieve all message templates from the WhatsApp Business Account.

        Fetches the full list of templates (approved, pending, rejected)
        registered under the given WABA. If no waba_id is provided, falls
        back to the one configured in the client.

        :param waba_id: Optional WhatsApp Business Account ID.
        :return: A list of template dicts.
        """
        waba_id = waba_id or self.config.waba_id
        if not waba_id:
            raise ValueError("waba_id must be provided or configured in WhatsAppAPIConfig")

        response = self.request(
            method="GET",
            endpoint="/%s/message_templates" % waba_id,
        )
        return response.get("data", [])

    def send_template_message(
        self,
        phone_number_id: str,
        template_name: str,
        language_code: str,
        components: list[dict[str, Any]],
        to_phone: str | None = None,
        recipient_id: str | None = None,
        category: Literal["MARKETING", "UTILITY", "AUTHENTICATION"] = "MARKETING",
    ) -> dict[str, Any]:
        """
        Send a template message to an individual recipient via WhatsApp.

        :param phone_number_id: The WhatsApp phone number ID.
        :param template_name: Name of the approved template to send.
        :param language_code: Language code of the template (e.g. 'es').
        :param components: List of component dicts (header, body, buttons).
        :param to_phone: Recipient phone number in international format.
        :param recipient_id: BSUID of the recipient.
        :param category: Template category, defaults to 'MARKETING'.
        :return: The response returned by the WhatsApp API.
        """
        payload: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language_code},
            },
        }
        
        if components:
            payload["template"]["components"] = components

        if to_phone:
            payload["to"] = to_phone
        elif recipient_id:
            payload["recipient"] = recipient_id
        else:
            raise ValueError("Either to_phone or recipient_id must be provided")

        endpoint = (
            "/%s/marketing_messages" % phone_number_id
            if category == "MARKETING"
            else "/%s/messages" % phone_number_id
        )

        return self.request(method="POST", endpoint=endpoint, payload=payload)