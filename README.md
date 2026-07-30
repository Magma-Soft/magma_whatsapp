# magma_whatsapp

A lightweight Python client for the [WhatsApp Business Cloud API](https://developers.facebook.com/docs/whatsapp/cloud-api) (Meta), built on top of `requests`.

## Requirements

- Python >= 3.10
- `requests` >= 2.31.0

## Installation

Install directly from the repository:

```bash
pip install git+https://github.com/your-org/whatsapp_provider.git
```

Or clone and install locally:

```bash
git clone https://github.com/your-org/whatsapp_provider.git
cd whatsapp_provider
pip install .
```

## Configuration

Create a `WhatsAppAPIConfig` instance with your credentials:

```python
from magma_whatsapp import WhatsAppAPIConfig

config = WhatsAppAPIConfig(
    api_version="v20.0",
    access_token="YOUR_ACCESS_TOKEN",
    waba_id="YOUR_WABA_ID",          # optional
    graph_api_base_url="https://graph.facebook.com",  # optional, this is the default
    timeout=30,                       # optional, default is 30 seconds
)
```

| Parameter | Type | Required | Description |
|---|---|---|---|
| `api_version` | `str` | Yes | Graph API version (e.g. `"v20.0"`) |
| `access_token` | `str` | Yes | Bearer token for authentication |
| `waba_id` | `str` | No | WhatsApp Business Account ID |
| `graph_api_base_url` | `str` | No | Base URL (default: `https://graph.facebook.com`) |
| `timeout` | `int` | No | HTTP timeout in seconds (default: `30`) |

## Usage

### Initialise the client

```python
from magma_whatsapp import WhatsAppAPIClient, WhatsAppAPIConfig

config = WhatsAppAPIConfig(
    api_version="v20.0",
    access_token="YOUR_ACCESS_TOKEN",
)

client = WhatsAppAPIClient(config)
```

An existing `requests.Session` can be passed as the second argument if you need custom transport adapters or shared session state.

---

### Send a text message

```python
response = client.send_message_text(
    recipient_id="521234567890",   # international format, no "+"
    message_content="Hello from the API!",
)
```

---

### Retrieve media metadata and download binary

```python
# Get the download URL and MIME type for a media object
metadata = client.get_media_metadata(media_id="MEDIA_ID")
# {"download_url": "https://...", "mime_type": "image/jpeg"}

# Download the raw bytes
binary = client.get_media_binary(metadata["download_url"])
```

The `MediaProcessor` helper (included in `WhatsAppMedia`) can build a filename from the message payload:

```python
from magma_whatsapp.modules.media import MediaProcessor

processor = MediaProcessor()
filename = processor.build_media_filename(message=msg_dict, mime_type="image/jpeg")
# e.g. "abc123.jpg"
```

---

### Process incoming webhooks

Pass the raw webhook payload (parsed JSON dict) to the client:

```python
client.receive_webhook(payload)
```

You can also extract structured data directly:

```python
# Inbound message
data = client.get_inbound_message_data(value)
# {
#   "message_id": "wamid.xxx",
#   "contact_info": {"name": "John", "wa_id": "521234567890"},
#   "message_type": "text",
#   "caption": "Hello!",
# }

# Outbound message status update
data = client.get_outbound_message_data(value)
# {"message_id": "wamid.xxx", "status": "delivered"}
```

Additional webhook helpers:

| Method | Returns | Description |
|---|---|---|
| `get_message_direction(value)` | `"inbound"` \| `"outbound"` | Direction of the message |
| `get_message_type(value)` | `str` | Type: `"text"`, `"image"`, `"document"`, etc. |
| `get_contact_info(value)` | `dict \| None` | Sender name and WhatsApp ID |
| `get_message_id(value)` | `str` | Message or status ID |
| `get_send_status(value)` | `str` | Delivery status (`"sent"`, `"delivered"`, `"read"`, …) |
| `get_caption(value)` | `str` | Text body or media caption |

---

## Error handling

All exceptions inherit from `WhatsAppAPIError`.

```python
from magma_whatsapp import WhatsAppHTTPError, WhatsAppResponseError, WhatsAppAPIError

try:
    client.send_message_text("521234567890", "Hello!")
except WhatsAppHTTPError as e:
    print(e.status_code)    # HTTP status code
    print(e.endpoint)       # endpoint that failed
    print(e.response_body)  # raw response
except WhatsAppResponseError as e:
    print(e.endpoint)       # endpoint that returned unexpected data
    print(e.response_body)
except WhatsAppAPIError:
    # catch-all for any client error
    ...
```

| Exception | Raised when |
|---|---|
| `WhatsAppHTTPError` | HTTP request fails or returns a non-2xx status |
| `WhatsAppResponseError` | Response body has an unexpected or invalid format |

## Package structure

```text
whatsapp/
├── __init__.py          # Public exports
├── client.py            # WhatsAppAPIClient (main entry point)
├── config.py            # WhatsAppAPIConfig
├── exceptions.py        # WhatsAppAPIError, WhatsAppHTTPError, WhatsAppResponseError
├── models.py            # TextMessagePayload, TemplateMessagePayload
└── modules/
    ├── requests.py      # HTTP layer mixin
    ├── messages.py      # Message sending mixin
    ├── media.py         # Media download mixin + MediaProcessor
    └── webhook.py       # Webhook processing mixin
```
