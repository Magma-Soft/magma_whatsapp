from __future__ import annotations


class WhatsAppWebhookProcessor:
    def _iter_values(self, payload):
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value")
                if isinstance(value, dict):
                    yield value

    def get_message_direction(self, payload: dict) -> str:
        if payload.get("statuses", None):
            return "outbound"
        return "inbound"

    def get_message_type(self, payload: dict) -> str:
        if payload.get("messages", None):
            return payload["messages"][0].get("type")
        elif payload.get("statuses", None):
            return payload["statuses"][0].get("type")
        return "unknown"

    def get_contact_info(self, payload: dict) -> dict | None:
        contacts = payload.get("contacts")
        if not contacts:
            return None
        contact = contacts[0]
        profile = contact.get("profile", {})
        return {
            "name": profile.get("name") or profile.get("username"),
            "wa_id": contact.get("wa_id"),
        }

    def get_message_id(self, payload: dict) -> str:
        if payload.get("messages", None):
            return payload["messages"][0].get("id")
        elif payload.get("statuses", None):
            return payload["statuses"][0].get("id")
        return None

    def get_send_status(self, payload: dict) -> str:
        if payload.get("statuses", None):
            return payload["statuses"][0].get("status")
        return "unknown"

    def get_content(self, payload: dict) -> str:
        if payload.get("messages", None):
            message = payload["messages"][0]
            if message.get("type") in ["image", "audio", "video", "document"]:
                return message.get(message["type"], {}).get("caption", "")
            elif message.get("type") == "text":
                return message.get("text", {}).get("body", "")
            elif message.get("type") == "reaction":
                return message.get("reaction", {}).get("emoji", "")

        return ""

    def get_media_info(self, payload: dict) -> dict:
        if payload.get("messages", None):
            message = payload["messages"][0]
            if message.get("type") in ["sticker", "image", "audio", "video", "document"]:
                return {
                    "id": message.get(message["type"], {}).get("id"),
                    "mime_type": message.get(message["type"], {}).get("mime_type"),
                }
        return {}

    def get_reaction_info(self, payload: dict) -> dict:
        if payload.get("messages", None):
            message = payload["messages"][0]
            if message.get("type") == "reaction":
                return {
                    "emoji": message.get("reaction", {}).get("emoji"),
                    "message_id": message.get("reaction", {}).get("message_id"),
                }
        return {}

    def get_reply_info(self, payload: dict) -> dict:
        if payload.get("messages", None):
            message = payload["messages"][0]
            if message.get("context", None):
                return {
                    "message_id": message["context"].get("id"),
                    "from": message["context"].get("from"),
                }
        return {}

    def get_message_info(self, payload: dict) -> dict:
        return {
            "id": self.get_message_id(payload),
            "type": self.get_message_type(payload),
            "content": self.get_content(payload),
            "media_info": self.get_media_info(payload),
            "reaction_info": self.get_reaction_info(payload),
            "reply_info": self.get_reply_info(payload),
        }

    def get_inbound_message_data(self, payload: dict) -> dict:
        return {
            "contact": self.get_contact_info(payload),
            "message": self.get_message_info(payload),
        }

    def get_outbound_message_data(self, payload: dict) -> dict:
        return {
            "message_id": self.get_message_id(payload),
            "status": self.get_send_status(payload),
        }

    def get_phone_number_id(self, payload: dict) -> str:
        """Returns the phone_number_id from the webhook metadata."""
        metadata = payload.get("metadata")
        if not isinstance(metadata, dict):
            return ""
        return metadata.get("phone_number_id", "")

    def receive_webhook(self, payload: dict):
        for value in self._iter_values(payload):
            direction = self.get_message_direction(value)
            data = {
                "phone_number_id": self.get_phone_number_id(value),
                "direction": direction,
                "inbound_data": self.get_inbound_message_data(value) if direction == "inbound" else None,
                "outbound_data": self.get_outbound_message_data(value) if direction == "outbound" else None
            }
            return data
