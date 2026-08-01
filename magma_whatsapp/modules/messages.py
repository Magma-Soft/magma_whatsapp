from __future__ import annotations

import mimetypes
from typing import Literal


class WhatsAppMessages:

    def send_message_text(self, phone_number_id: str = None, to_phone: str = None, recipient_id: str = None, message_content: str = None, reply_to_message_id: str = None):
        """
        Send a plain text WhatsApp message to a recipient.

        :param phone_number_id: The phone number ID associated with the WhatsApp Business Account.
        :param to_phone: The phone number of the recipient in international format.
        :param recipient_id: The BSUID of the recipient.
        :param message_content: The text body to send in the message.
        :param reply_to_message_id: Optional ID of the message to which this message is a reply.
        :return: The response returned by the WhatsApp API.
        """
        if reply_to_message_id:
            context = {"message_id": reply_to_message_id}
        else:
            context = None

        response = self.request(
            method="POST",
            endpoint="/%s/messages" % phone_number_id,
            payload={
                "messaging_product": "whatsapp",
                **({"to": to_phone} if to_phone else {"recipient": recipient_id}),
                "type": "text",
                "text": {"body": message_content},
                **({"context": context} if context else {})
            })
        data = {
            "phone_number_id": "%s" % phone_number_id,
            "to": response.get("contacts", [{}])[0].get("wa_id"),
            "recipient_id": response.get("contacts", [{}])[0].get("user_id"),
            "type": "text",
            "data": {
                "wa_id": response.get("messages", [{}])[0].get("id"),
                "caption": message_content,
                "reply_to": reply_to_message_id
            }
        }
        return data

    def send_message_media(
            self,
            phone_number_id: str,
            media_id: str,
            media_type: Literal["image", "audio", "document", "video"],
            to_phone: str = None,
            recipient_id: str = None,
            caption: str = None,
            filename: str = None,
            reply_to_message_id: str = None):
        """
        Send a media message (image, audio, document, video) to a recipient.

        :param phone_number_id: The phone number ID associated with the WhatsApp Business Account.
        :param to_phone: The phone number of the recipient in international format.
        :param recipient_id: The BSUID of the recipient.
        :param media_id: The ID of the media object uploaded to WhatsApp.
        :param media_type: The type of media ("image", "audio", "document", "video").
        :param caption: Optional caption for the media message.
        :param filename: Optional filename for the media message (only for documents).
        :param reply_to_message_id: Optional ID of the message to which this message is a reply.
        :return: The response returned by the WhatsApp API.
        """
        if media_type not in ["image", "audio", "document", "video"]:
            raise ValueError("Invalid media type: %s" % media_type)

        if reply_to_message_id:
            context = {"message_id": reply_to_message_id}
        else:
            context = None

        response = self.request(
            method="POST",
            endpoint="/%s/messages" % phone_number_id,
            payload={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                **({"to": to_phone} if to_phone else {"recipient": recipient_id}),
                "type": media_type,
                media_type: {
                    "id": media_id,
                    **({"caption": caption} if caption else {}),
                    **({"filename": filename} if filename and media_type == "document" else {}),
                },
                **({"context": context} if context else {})
            })
        data = {
            "phone_number_id": "%s" % phone_number_id,
            "to": response.get("contacts", [{}])[0].get("wa_id"),
            "recipient_id": response.get("contacts", [{}])[0].get("user_id"),
            "type": media_type,
            "data": {
                "wa_id": response.get("messages", [{}])[0].get("id"),
                "caption": caption,
                "filename": filename,
                "reply_to": reply_to_message_id
            }
        }
        return data

    def send_message_file(self, phone_number_id: str = None, to_phone: str = None, recipient_id: str = None, file=None, caption=None, reply_to_message_id: str = None):
        """
        Send a file message to a recipient. This method handles the upload of the file and then sends it as a media message.

        :param phone_number_id: The phone number ID associated with the WhatsApp Business Account.
        :param to_phone: The phone number of the recipient in international format.
        :param recipient_id: The BSUID of the recipient.
        :param file: A file-like object containing the binary content of the file.
        :param caption: Optional caption for the file message.
        :param reply_to_message_id: Optional ID of the message to which this message is a reply.
        :return: The response returned by the WhatsApp API.
        """
        file.seek(0)
        file_binary = file.read()

        mime_type = file.content_type
        media_type = self._resolve_media_type(mime_type)

        upload = self.upload_media(
            phone_number_id=phone_number_id,
            file_binary=file_binary,
            mime_type=mime_type,
            filename=file.name
        )

        media_id = upload.get("id")

        if not media_id:
            raise ValueError("Failed to upload media")

        return self.send_message_media(
            phone_number_id=phone_number_id,
            to_phone=to_phone,
            recipient_id=recipient_id,
            media_id=media_id,
            media_type=media_type,
            caption=caption,
            filename=file.name,
            reply_to_message_id=reply_to_message_id
        )

    def send_message_reaction(self, phone_number_id: str, to_phone: str = None, recipient_id: str = None, message_id: str = None, reaction: str = None):
        """
        Send a reaction message in reply to a specific message.

        :param phone_number_id: The phone number ID associated with the WhatsApp Business Account.
        :param to_phone: The phone number of the recipient in international format.
        :param recipient_id: The BSUID of the recipient.
        :param message_id: The ID of the message to which the reaction is being sent.
        :param reaction: The emoji reaction to send (e.g., "👍", "❤️").
        :return: The response returned by the WhatsApp API.
        """
        response = self.request(
            method="POST",
            endpoint="/%s/messages" % phone_number_id,
            payload={
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                **({"to": to_phone} if to_phone else {"recipient": recipient_id}),
                "type": "reaction",
                "reaction": {"message_id": message_id, "emoji": reaction}
            })
        data = {
            "phone_number_id": "%s" % phone_number_id,
            "to": response.get("contacts", [{}])[0].get("wa_id"),
            "recipient_id": response.get("contacts", [{}])[0].get("user_id"),
            "type": "reaction",
            "data": {
                "wa_id": response.get("messages", [{}])[0].get("id"),
                "emoji": reaction
            }
        }
        return data
