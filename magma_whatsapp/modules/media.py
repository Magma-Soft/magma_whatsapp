from __future__ import annotations

import mimetypes
from uuid import uuid4

class MediaProcessor:

    MIME_EXTENSION_MAP: dict[str, str] = {
        "image/jpeg": ".jpg",
        "image/jpg": ".jpg",
        "image/png": ".png",
        "image/webp": ".webp",
        "image/gif": ".gif",
        "video/mp4": ".mp4",
        "audio/mpeg": ".mp3",
        "audio/ogg": ".ogg",
        "application/pdf": ".pdf",
    }

    def extract_message_id(self, message):
        return message.get("id")

    def resolve_extension_from_mime_type(self, mime_type):
        if not mime_type:
            return ".bin"

        normalized = mime_type.split(";")[0].strip().lower()

        extension = type(self).MIME_EXTENSION_MAP.get(normalized)
        if extension:
            return extension

        guessed = mimetypes.guess_extension(normalized)
        return guessed or ".bin"

    def build_media_filename(self, message, mime_type):
        message_id = self.extract_message_id(message) or str(uuid4())
        extension = self.resolve_extension_from_mime_type(mime_type)
        return f"{message_id}{extension}"


class WhatsAppMedia(MediaProcessor):

    def get_media_metadata(self, media_id: str):
        """
        Retrieve metadata for a specific media item by its ID.

        :param media_id: The unique identifier of the media item.
        :return: The metadata information returned by the WhatsApp API.
        """
        metadata = self.request(
            method="GET",
            endpoint="/%s" % media_id
        )
        data = {
            "download_url": metadata.get("url"),
            "mime_type": metadata.get("mime_type"),
        }
        if not data["download_url"] or not data["mime_type"]:
            raise ValueError("Invalid media metadata response from WhatsApp")
        return data

    def get_media_binary(self, download_url: str):
        """
        Download the media content from a given download URL.

        :param download_url: The URL from which to download the media content.
        :return: The binary content of the media file.
        """
        content = self.request(
            method="GET",
            endpoint=download_url,
            response_type="content"
        )
        return content

    def upload_media(self, file_path: str, media_type: str):
        """
        Upload a media file to WhatsApp and obtain a media ID.

        :param file_path: The local path to the media file to be uploaded.
        :param media_type: The type of media ("image", "audio", "document").
        :return: The response containing the media ID returned by the WhatsApp API.
        """
        if media_type not in ["image", "audio", "document"]:
            raise ValueError("Invalid media type: %s" % media_type)

        with open(file_path, "rb") as f:
            files = {
                "file": (file_path, f, mimetypes.guess_type(file_path)[0] or "application/octet-stream")
            }
            response = self.request(
                method="POST",
                endpoint="/%s/media" % self.config.phone_number_id,
                files=files,
                payload={"type": media_type}
            )
        return response
