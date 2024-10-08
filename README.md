
# Mailer API

This is a simple Mailer API built using FastAPI, which allows sending emails with attachments, CC, and BCC functionality using Gmail's SMTP server.

## Features

- Send emails to multiple recipients
- Support for CC and BCC
- Attachments support
- Uses Gmail SMTP for email sending

## Prerequisites

- Python 3.8+
- Gmail account with [App Password](https://support.google.com/accounts/answer/185833)

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
GMAIL_USER=your_email@gmail.com
GMAIL_PASSWORD=your_app_password
```

Replace `your_email@gmail.com` with your Gmail address and `your_app_password` with the app password you generated.

### 5. Run the API

Start the FastAPI server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`.

## API Endpoints

### Send Email

#### Endpoint: `/send-email/`

- **Method**: `POST`
- **Description**: Sends an email to one or more recipients with support for CC, BCC, and attachments.

#### Parameters:

| Name           | Type           | Required | Description                                  |
| -------------- | -------------- | -------- | -------------------------------------------- |
| `to_emails`  | `str`        | Yes      | Comma-separated list of recipient emails     |
| `cc_emails`  | `str`        | No       | Comma-separated list of CC recipient emails  |
| `bcc_emails` | `str`        | No       | Comma-separated list of BCC recipient emails |
| `subject`    | `str`        | Yes      | Subject of the email                         |
| `body`       | `str`        | Yes      | Body of the email                            |
| `attachment` | `UploadFile` | No       | Optional file attachment                     |

#### Example cURL Request:

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/send-email/' \
  -F 'to_emails=recipient1@example.com,recipient2@example.com' \
  -F 'cc_emails=cc1@example.com,cc2@example.com' \
  -F 'bcc_emails=bcc1@example.com' \
  -F 'subject=Test Email' \
  -F 'body=This is a test email.' \
  -F 'attachment=@/path/to/attachment.pdf'
```

This will send an email with the provided subject and body to the specified recipients, including CC and BCC recipients, and attach the specified file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
