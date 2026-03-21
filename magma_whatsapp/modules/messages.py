from __future__ import annotations

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
