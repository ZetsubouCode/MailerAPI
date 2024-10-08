from fastapi import FastAPI, UploadFile, File, Form
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = FastAPI()

def send_email(to_emails, subject, body, cc_emails=None, bcc_emails=None, attachment_file=None):
    # Your Gmail account details
    gmail_user = 'your_email@gmail.com'
    gmail_password = 'your_app_password'  # Use the app-specific password you generated

    # Create the MIME message
    msg = MIMEMultipart()
    msg['From'] = gmail_user
    msg['To'] = ', '.join(to_emails)  # Join the to_emails list as comma-separated string
    msg['Subject'] = subject

    # Handle CC recipients
    if cc_emails:
        msg['Cc'] = ', '.join(cc_emails)

    # Attach the body of the email to the MIME message
    msg.attach(MIMEText(body, 'html'))

    # Handle the file attachment from the request
    if attachment_file:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment_file.file.read())  # Read the file content from the UploadFile object
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename={attachment_file.filename}'  # Use the filename from the UploadFile object
        )
        msg.attach(part)

    # Combine all recipients (To, CC, BCC)
    all_recipients = to_emails
    if cc_emails:
        all_recipients += cc_emails
    if bcc_emails:
        all_recipients += bcc_emails

    try:
        # Set up the SMTP server
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(gmail_user, gmail_password)
        text = msg.as_string()

        # Send the email to all recipients
        server.sendmail(gmail_user, all_recipients, text)
        server.quit()

        print(f'Email sent to {", ".join(to_emails)}')
        if cc_emails:
            print(f'CC: {", ".join(cc_emails)}')
        if bcc_emails:
            print(f'BCC: {", ".join(bcc_emails)}')

    except Exception as e:
        print(f'Failed to send email. Error: {str(e)}')
