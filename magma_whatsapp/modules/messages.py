from __future__ import annotations

from typing import Literal


class WhatsAppMessages:

    def send_message_text(self, recipient_id: str, message_content: str):
        """
        Send a plain text WhatsApp message to a recipient.

        :param recipient_id: The WhatsApp ID of the recipient (e.g., phone number in international format).
        :param message_content: The text body to send in the message.
        :return: The response returned by the WhatsApp API.
        """
        return self.request(
            method="POST",
            endpoint="/%s/messages" % self.config.phone_number_id,
            payload={
                "messaging_product": "whatsapp",
                "to": recipient_id,
                "type": "text",
                "text": {"body": message_content}
            })

    def send_message_media(self, recipient_id: str, media_id: str, media_type: Literal["image", "audio", "document"], caption: str = None, filename: str = None):
        """
        Send a media message (image, audio, document) to a recipient.

        :param recipient_id: The WhatsApp ID of the recipient (e.g., phone number in international format).
        :param media_id: The ID of the media object uploaded to WhatsApp.
        :param media_type: The type of media ("image", "audio", or "document").
        :param caption: Optional caption for the media message.
        :param filename: Optional filename for the media message (only for documents).
        :return: The response returned by the WhatsApp API.
        """
        if media_type not in ["image", "audio", "document"]:
            raise ValueError("Invalid media type: %s" % media_type)

        return self.request(
            method="POST",
            endpoint="/%s/messages" % self.config.phone_number_id,
            payload={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": recipient_id,
                "type": media_type,
                media_type: {
                    "id": media_id,
                    **({"caption": caption} if caption else {}),
                    **({"filename": filename} if filename and media_type == "document" else {}),
                },
            })
