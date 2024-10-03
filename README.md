# MailerAPI

API to send email using brevo, build using FastAPI

# FastAPI Email Sender with Brevo (Sendinblue)

This project is a simple FastAPI application that provides an API endpoint to send emails using the Brevo (Sendinblue) transactional email service. It follows best practices by utilizing background tasks and asynchronous requests to ensure the API is responsive and scalable.

## Features

- Send emails using Brevo (Sendinblue) API.
- Asynchronous email sending for better performance.
- Background task support using FastAPI’s `BackgroundTasks`.
- Environment-based configuration using Pydantic and `.env` files.
- Modular project structure for scalability and maintainability.

## Getting Started

### Prerequisites

- **Python 3.8+**
- **FastAPI** and **Uvicorn** for running the API.
- A **Brevo (Sendinblue) account** to obtain an API key for sending emails.

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-username/fastapi-brevo-email-sender.git
   cd fastapi-brevo-email-sender
   ```
2. **Create a virtual environment**:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```
3. **Install the dependencies**:

   ```bash
   pip install -r requirements.txt
   ```
4. **Configure environment variables**:

   Create a `.env` file in the root of the project with the following content:

   ```
   API_KEY=your_brevo_api_key
   SENDER_EMAIL=your_verified_sender_email@example.com
   ```

   Replace:

   - `your_brevo_api_key` with your actual Brevo (Sendinblue) API key.
   - `your_verified_sender_email@example.com` with the email you’ve verified in Brevo as the sender.

### Running the Application

To run the FastAPI application locally:

```bash
uvicorn app.main:app --reload
```

The API will be available at: `http://127.0.0.1:8000`

### API Endpoints

#### POST `/send-email/`

Send an email using Brevo's transactional email API.

- **URL**: `/send-email/`
- **Method**: `POST`
- **Content-Type**: `application/json`

#### Request Body

```json
{
  "to_email": "recipient@example.com",
  "subject": "Test Email",
  "body": "<h1>Hello from FastAPI and Brevo!</h1>"
}
```

- `to_email`: The recipient’s email address.
- `subject`: The email subject.
- `body`: The HTML content of the email.

#### Example `curl` Command

```bash
curl -X 'POST' \
  'http://127.0.0.1:8000/send-email/' \
  -H 'Content-Type: application/json' \
  -d '{
  "to_email": "recipient@example.com",
  "subject": "Test Email",
  "body": "<h1>Hello from FastAPI and Brevo!</h1>"
}'
```

#### Response

On success:

```json
{
  "message": "Email is being sent in the background!"
}
```

On error:

```json
{
  "detail": "Failed to send email: [Error details]"
}
```

### Dependencies

- **FastAPI**: High-performance web framework for building APIs with Python.
- **Uvicorn**: ASGI server for serving FastAPI apps.
- **httpx**: Async HTTP client for making API requests.
- **python-dotenv**: For loading environment variables from `.env` files.
- **pydantic**: For data validation and settings management.

### Best Practices Followed

- **Environment Variables**: Sensitive information such as API keys and email addresses are managed using `.env` files and loaded via Pydantic’s `BaseSettings`.
- **Asynchronous Code**: Email sending is done asynchronously using `httpx` to avoid blocking the main request handler.
- **Background Tasks**: Emails are sent in the background using FastAPI's `BackgroundTasks`, ensuring the API is non-blocking and responsive.

### Future Improvements

- Add more robust error handling and logging.
- Implement email queuing for higher email volumes.
- Support for multiple email providers by extending the service layer.

---

### License

This project is licensed under the MIT License. Feel free to use, modify, and distribute it as needed.

---

### Acknowledgements

- FastAPI documentation
- Brevo (Sendinblue) API documentation
