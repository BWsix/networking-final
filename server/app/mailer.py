import socket
import base64

from app import logger
from app.config import settings

def send(from_email: str, to_email: str, subject: str = "(no subject)", message_body: str = "(no body)"):
    email_message = f"""\
From: {from_email}
To: {to_email}
Subject: {subject}

{message_body}
"""
    logger.mailer.info(f"Sending email from {from_email} to {to_email} with subject {subject}")

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((settings.MAIL_SERVER, settings.MAIL_PORT))
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(b'EHLO ALICE\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(b'AUTH LOGIN\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(base64.b64encode(settings.MAIL_USERNAME.encode()) + b'\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(base64.b64encode(settings.MAIL_PASSWORD.encode()) + b'\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(f"MAIL FROM:<{from_email}>\r\n".encode())
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(f"RCPT TO:<{to_email}>\r\n".encode())
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(b'DATA\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(email_message.encode() + b'\r\n.\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.send(b'QUIT\r\n')
    response = server.recv(1024).decode()
    logger.mailer.info(response)

    server.close()
