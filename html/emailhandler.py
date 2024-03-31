import email, smtplib, ssl
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


def sent_mail(subject, body, filename=False):
    # Load environment variables from .env file
    load_dotenv()

    sender_email = os.environ.get('SENDER_EMAIL')
    password = os.environ.get('EMAIL_PASSWORD')
    smtp_server = os.environ.get('SMTP_SERVER')
    receiver_email = os.environ.get('RECEIVER_EMAIL')


    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if filename:
        # Open PDF file in binary mode
        with open(filename, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email    
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        filename = filename.rsplit("/",1)[1]
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {filename}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, text)


def sent_email_approval_request(file_name:str, file_password:str, uploaded_file:str):
    subject = "[N2i] Approve new upload"
    body = "A new file was uploaded. It's currently in the approval queue and need to be allowed by you"
    body += f"\n\nFilename: {file_name}"
    body += f"\n\nApprove: http://127.0.0.1:5000/upload/approve?file_name={file_name}&file_password={file_password}"
    sent_mail(subject, body, uploaded_file)
    return True

def sent_email_error_message(subject:str, message:str):
    subject = "[N2i] Error: " + subject
    body = '''An error occured. This mail was sent because the error might
    be critical and need a fast review.\n\nError: ''' + message
    sent_mail(subject, body)
    return True