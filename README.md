# Mailer API

This is a simple Mailer API built using FastAPI, which allows sending emails with attachments, CC, and BCC functionality using a configurable SMTP server (Gmail, Hostinger/Niagahoster, etc.).

## Features

- Send emails to multiple recipients
- Support for CC and BCC
- Attachments support
- Uses configurable SMTP for email sending

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
```

If you previously used `GMAIL_USER` and `GMAIL_PASSWORD`, the app can still read them, but `SMTP_*` is recommended.

### 5. Run the API

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload --no-server-header  --port 5556
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Send Email

#### Endpoint: `/api/send-email/`

- **Method**: `POST`
- **Description**: Sends an email to one or more recipients with support for CC, BCC, and attachments.

#### Parameters:

| Name           | Type           | Required | Description                                                                 |
| -------------- | -------------- | -------- | --------------------------------------------------------------------------- |
| `to_emails`    | `str`          | Yes      | Repeat this field for multiple recipients (add multiple `to_emails` keys).  |
| `cc_emails`    | `str`          | No       | Repeat this field for multiple CC recipients.                                |
| `bcc_emails`   | `str`          | No       | Repeat this field for multiple BCC recipients.                               |
| `subject`      | `str`          | Yes      | Subject of the email                                                         |
| `body`         | `str`          | Yes      | Body of the email (HTML supported)                                           |
| `attachment`   | `UploadFile`   | No       | Optional file attachment                                                     |

#### Example cURL Request:

```bash
curl -X 'POST'   'http://127.0.0.1:8000/api/send-email/'   -F 'to_emails=recipient1@example.com'   -F 'to_emails=recipient2@example.com'   -F 'cc_emails=cc1@example.com'   -F 'cc_emails=cc2@example.com'   -F 'bcc_emails=bcc1@example.com'   -F 'subject=Test Email'   -F 'body=This is a test email.'   -F 'attachment=@/path/to/attachment.pdf'
```

This will send an email with the provided subject and body to the specified recipients, including CC and BCC recipients, and attach the specified file.

## API Documentation

To test and check the functionality, you can access [FastAPI docs](http://localhost:8000/docs).

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
