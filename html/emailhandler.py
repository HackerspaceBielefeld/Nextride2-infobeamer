"""
Email Handling Module

This module provides functions for sending various types of emails, including standard emails,
approval requests for new uploads, and error messages.

Functions:
    - sent_mail(subject, body, filename=False): Sends an email.
    - sent_email_approval_request(file_name, file_password, uploaded_file): Sends an
        email approval request for a new upload.
    - sent_email_error_message(subject, message): Sends an email error message.

Dependencies:
    - smtplib: Provides functions for sending emails.
    - ssl: Provides support for secure socket layer (SSL) connections.
    - os: Provides functions for interacting with the operating system.
    - email: Provides functionality for constructing and formatting email messages.
    - dotenv: Provides support for loading environment variables from .env files.
"""

import smtplib
import ssl
import os

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


def sent_mail(subject, body, filename=False):
    """
    Sends an email.

    Args:
        subject (str): The subject of the email.
        body (str): The body of the email.
        filename (bool, optional): The filename to attach (default is False).

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    # Load environment variables from .env file
    load_dotenv()

    # Return if ACTIVATE_EMAIL_APPROVAL in .env isn't True
    send_mails = os.environ.get('ACTIVATE_EMAIL_APPROVAL')
    if send_mails != "True" or send_mails != "true": return True

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

    return True

def sent_email_approval_request(file_name:str, file_password:str, uploaded_file:str):
    """
    Sends an email approval request for a new upload.

    Args:
        file_name (str): The name of the uploaded file.
        file_password (str): The password associated with the file.
        uploaded_file (str): The path to the uploaded file.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    subject = "[N2i] Approve new upload"
    body = "A new file was uploaded. It's currently in the approval queue " \
        "and needs to be allowed by you"    
    body += f"\n\nFilename: {file_name}"
    body += f"\n\nApprove: {os.environ.get('BASE_URL')}/upload/approve?" \
        f"file_name={file_name}&file_password={file_password}"
    if not sent_mail(subject, body, uploaded_file):
        return False
    return True

def sent_email_error_message(subject:str, message:str):
    """
    Sends an email error message.

    Args:
        subject (str): The subject of the error message.
        message (str): The error message.

    Returns:
        bool: True if the email was sent successfully, False otherwise.
    """

    subject = "[N2i] Error: " + subject
    body = '''An error occured. This mail was sent because the error might
    be critical and need a fast review.\n\nError: ''' + message
    if not sent_mail(subject, body):
        return False
    return True
