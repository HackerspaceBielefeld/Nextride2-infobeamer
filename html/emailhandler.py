"""
@file emailhandler.py
@brief This module handles sending emails, including those with attachments,
        using SMTP. It provides functionality for sending approval requests 
        and error notifications via email.

@details This module uses environment variables to configure the SMTP server, 
            sender email, and receiver email. It includes logging for error 
            handling and provides functions to send various types of emails.

@dependencies
- smtplib for sending emails
- ssl for secure connections
- Email modules for composing messages
- Environment variables for configuration

@author Inflac
@date 2024
"""

import os
import ssl
import smtplib
import logging

from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTPException, SMTPHeloError, SMTPAuthenticationError, SMTPNotSupportedError, SMTPRecipientsRefused, SMTPSenderRefused, SMTPDataError

logger = logging.getLogger()


def sent_mail(subject, body, file_path=False):
    """
    Send an email with the specified subject and body.

    This function composes an email and sends it using the SMTP server 
    configured in environment variables. Optionally, an attachment can be included.

    @param subject The subject of the email.
    @param body The body of the email.
    @param file_path The path to the file to attach (optional).

    @return True if the email was sent successfully, False otherwise.

    @exception SMTPException If there is an error during the email sending process.
    """
    sender_email = os.environ.get("SENDER_EMAIL")
    password = os.environ.get("EMAIL_PASSWORD")
    smtp_server = os.environ.get("SMTP_SERVER")
    receiver_email = os.environ.get("RECEIVER_EMAIL")

    # Create a multipart message and set headers
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message["Bcc"] = receiver_email  # Recommended for mass emails

    # Add body to email
    message.attach(MIMEText(body, "plain"))

    if file_path:
        try:
            with open(file_path, "rb") as attachment:
                # Add file as application/octet-stream
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            # Encode file in ASCII characters to send by email
            encoders.encode_base64(part)

            # Add header as key/value pair to attachment part
            filename = os.path.basename(file_path)
            part.add_header("Content-Disposition", f"attachment; filename={filename}")

            # Add attachment to message
            message.attach(part)
        except FileNotFoundError:
            logger.error(f"Attachment file '{file_path}' not found.")
            return False
        except Exception as e:
            logger.error(f"An error occurred while attaching the file: {e}")
            return False

    text = message.as_string()

    # Log in to server using secure context and send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, text)
            logger.info(f"Email sent successfully to {receiver_email}.")
    except SMTPHeloError:
        logger.error("The server didn't reply properly to the HELO greeting.")
        return False
    except SMTPAuthenticationError:
        logger.error("The server didn't accept the username/password combination.")
        return False
    except SMTPNotSupportedError:
        logger.error("The AUTH command is not supported by the server.")
        return False
    except SMTPRecipientsRefused:
        logger.error("The server rejected ALL recipients (no mail was sent).")
        return False
    except SMTPSenderRefused:
        logger.error("The server didn't accept the sender address.")
        return False
    except SMTPDataError:
        logger.error("The server replied with an unexpected error code.")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred while sending email: {e}")
        return False

    return True


def send_email_approval_request(file_name: str, file_password: str, uploaded_file: str) -> bool:
    """
    Send an approval request email for a new file upload.

    @param file_name The name of the file that needs approval.
    @param file_password The password associated with the file.
    @param uploaded_file The path to the uploaded file.

    @return True if the email was sent successfully, False otherwise.
    """
    subject = "[N2i] Approve new upload"
    body = (
        f"A new file was uploaded. It's currently in the approval queue "
        f"and needs to be allowed by you.\n\n"
        f"Filename: {file_name}\n\n"
        f"Approve: {os.environ.get('BASE_URL')}/upload/approve?file_name={file_name}&file_password={file_password}"
    )

    return send_mail(subject, body, uploaded_file)


def send_email_error_message(subject: str, message: str) -> bool:
    """
    Send an error message email.

    @param subject The subject of the error email.
    @param message The error message content.

    @return True if the email was sent successfully, False otherwise.
    """
    subject = "[N2i] Error: " + subject
    body = (
        f"An error occurred. This email was sent because the error might "
        f"be critical and need a fast review.\n\n"
        f"Error: {message}"
    )

    return send_mail(subject, body)
