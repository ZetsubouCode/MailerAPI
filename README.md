# Mailer API

This is a simple Mailer API built using FastAPI, which allows sending emails with attachments, CC, and BCC functionality using a configurable SMTP server (Gmail, Hostinger/Niagahoster, etc.).

## Features

- Send emails to multiple recipients
- Support for CC and BCC
- Attachments support
- Uses configurable SMTP for email sending
- Immediate send endpoints wait for SMTP acceptance before returning success
- Windows background launcher and Task Scheduler templates for unattended startup/watchdog recovery

## Prerequisites

- Python 3.8+
- SMTP account/credentials (for Gmail, use an [App Password](https://support.google.com/accounts/answer/185833))

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mailer-api.git
cd mailer-api
```

### 2. Create a virtual environment

```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

### 3. Install the dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Variables

Create a `.env` file in the root of your project and add the following content:

```env
# Generic SMTP settings (works for Gmail, Hostinger/Niagahoster, etc.)
SMTP_HOST=smtp.gmail.com          # e.g. smtp.gmail.com or smtp.hostinger.com
SMTP_PORT=465                     # 465 for SSL, 587 for STARTTLS
SMTP_SECURITY=ssl                 # ssl | starttls | none
SMTP_USER=your_email@gmail.com    # your mailbox/login
SMTP_PASSWORD=your_app_password   # provider password or Gmail App Password
SMTP_FROM=Your Name <your_email@gmail.com>
MAILER_API_HOST=127.0.0.1
MAILER_API_PORT=5556
```

If you previously used `GMAIL_USER` and `GMAIL_PASSWORD`, the app can still read them, but `SMTP_*` is recommended.

Optional:

```env
ATTACHMENT_MAX_MB=20
SMTP_MESSAGE_ID_DOMAIN=jig-cinema.local
MAILER_API_RELOAD=false
```

### 5. Run the API

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload --no-server-header --port 5556
```

The API will be available at `http://127.0.0.1:5556`.

Tip: Uvicorn defaults to port 8000 if you omit `--port`. If your client points to
`http://127.0.0.1:5556`, make sure you start Uvicorn with `--port 5556` or run
`python -m app` (uses `MAILER_API_PORT=5556` by default).

On Windows, manual background start:

```bat
start-mailerapi-background.bat
```

Logs are written to `%ProgramData%\JIGApp\logs\mailerapi.log`.

## API Endpoints

### Send Email

#### Endpoint: `/api/send-email/`

- **Method**: `POST`
- **Description**: Sends an email to one or more recipients with support for CC, BCC, inline attachments, and file attachments.
- **Important**: This endpoint is synchronous for immediate sends. It only returns success after SMTP accepts every required recipient. It does not use `asyncio.create_task()` for immediate delivery.

Compatibility routes are also available without the `/api` prefix:

- `/send-email/`
- `/send-email`

#### Parameters:

| Name           | Type           | Required | Description                                                                 |
| -------------- | -------------- | -------- | --------------------------------------------------------------------------- |
| `to_emails`    | `str`          | Yes      | Repeat this field for multiple recipients (add multiple `to_emails` keys).  |
| `cc_emails`    | `str`          | No       | Repeat this field for multiple CC recipients.                                |
| `bcc_emails`   | `str`          | No       | Repeat this field for multiple BCC recipients.                               |
| `subject`      | `str`          | Yes      | Subject of the email                                                         |
| `body`         | `str`          | Yes      | Body of the email (HTML supported)                                           |
| `attachment`   | `UploadFile`   | No       | Optional file attachment                                                     |
| `attachment_inline` | `str`     | No       | Repeat per attachment; `1`/`true` marks the corresponding attachment inline. |
| `attachment_cid` | `str`        | No       | Repeat per attachment; content ID for inline attachments.                    |

#### Example cURL Request:

```bash
curl -X 'POST'   'http://127.0.0.1:5556/api/send-email/'   -F 'to_emails=recipient1@example.com'   -F 'to_emails=recipient2@example.com'   -F 'cc_emails=cc1@example.com'   -F 'cc_emails=cc2@example.com'   -F 'bcc_emails=bcc1@example.com'   -F 'subject=Test Email'   -F 'body=This is a test email.'   -F 'attachment=@/path/to/attachment.pdf'
```

This will send an email with the provided subject and body to the specified recipients, including CC and BCC recipients, and attach the specified file.

#### Success response

HTTP 2xx is returned only after SMTP accepts the message for all recipients:

```json
{
  "status": true,
  "smtp_accepted": true,
  "message_id": "<generated-message-id@example>",
  "accepted_recipient_count": 2,
  "request_id": "a1b2c3d4"
}
```

Laravel receipt delivery treats success as valid only when all of these are true:

- HTTP status is 2xx
- `status` is `true`
- `smtp_accepted` is `true`
- `message_id` is non-empty

#### Failure response

Failures return non-2xx JSON:

```json
{
  "status": false,
  "smtp_accepted": false,
  "code": "SMTP_TIMEOUT",
  "message": "SMTP timed out or disconnected.",
  "request_id": "a1b2c3d4"
}
```

Stable failure codes:

- `SMTP_AUTH_FAILED`
- `SMTP_CONNECT_FAILED`
- `SMTP_TIMEOUT`
- `SMTP_SEND_FAILED`
- `RECIPIENT_REJECTED`
- `INVALID_REQUEST`
- `INTERNAL_ERROR`

Sensitive SMTP details, passwords, raw attachment data, and provider internals are not returned to clients.

### Health Check

```bash
curl http://127.0.0.1:5556/health
curl http://127.0.0.1:5556/api/health
```

Expected response:

```json
{"status": true, "service": "mailer-api"}
```

Use this for startup checks. Do not use `/send-email` as a health check because it sends a real email.

## Windows Operation

The Laravel admin panel depends on this service for online ticket receipt delivery. If MailerAPI is down, Laravel will mark receipt attempts `FAILED` and retry through its receipt outbox, but receipts will not send until MailerAPI is running.

### Manual start

```bat
start-mailerapi-background.bat
```

Behavior:

- Uses `PYTHON_BIN` when set, otherwise `python`.
- Uses `MAILER_API_PORT`, default `5556`.
- Prevents duplicate startup by checking a process marker and the listening port.
- Starts Uvicorn hidden/background.
- Logs to `%ProgramData%\JIGApp\logs\mailerapi.log`.

### Task Scheduler

Import these XML templates and adjust paths if the repo is installed elsewhere:

- `windows-scheduler-mailerapi-startup.xml`
- `windows-watchdog-mailerapi.xml`

Recommended Windows task names:

- `JIG MailerAPI Startup`
- `JIG MailerAPI Watchdog`

Configure the tasks to:

- Run whether user is logged on or not.
- Use a local/service account that can access this repo, Python, `.env`, network, and `%ProgramData%\JIGApp\logs`.
- Start at boot with a short delay.
- Run the watchdog every five minutes.
- Use no automatic execution timeout.

The XML uses `LogonType=Password`; Windows will ask for the account password when importing.

### Verify operation

```bat
curl http://127.0.0.1:5556/health
type "%ProgramData%\JIGApp\logs\mailerapi.log"
```

For Laravel integration, the admin panel should use:

```env
MAILER_SERVICE_URL=http://127.0.0.1:5556/send-email/
MAILER_HTTP_TIMEOUT=55
MAILER_HTTP_CONNECT_TIMEOUT=5
```

If `MAILER_SERVICE_URL` is unset, the current Laravel client can fall back to `MAILER_API_HOST` and append `/send-email/`.

## Online Ticket Receipt Contract

The JIG Cinema admin panel uses this API as the immediate delivery transport for receipt jobs. The intended flow is:

1. Laravel receipt job generates the PDF and POSTs to `/send-email/`.
2. MailerAPI runs blocking SMTP work in an executor thread.
3. MailerAPI returns success only after SMTP accepts every recipient.
4. Laravel marks `receipt_outbox.status=SENT` only after receiving the success contract.
5. On timeout, connection failure, SMTP rejection, or invalid response, Laravel records a failed attempt and retries later through its durable outbox.

Do not change `/send-email` back to fire-and-forget behavior for online ticket receipts. Keep `/schedule_email` separate for scheduled/background email use cases.

## API Documentation

To test and check the functionality, you can access [FastAPI docs](http://localhost:5556/docs).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
