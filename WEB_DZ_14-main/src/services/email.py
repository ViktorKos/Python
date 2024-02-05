from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.services.auth import auth_service
from src.config.config import config

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_USERNAME,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME="Phenix corporation",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates', )


async def send_email(email: EmailStr, username: str, host: str):
    """
    The send_email function sends an email to the user with a link to verify their email address.
        The function takes in three parameters:
            -email: the user's email address, which is used as a unique identifier for them.
            -username: the username of the user, which is displayed in the body of the message.
            -host: this parameter contains information about where your application is hosted (e.g., localhost).

    :param email: EmailStr: Specify the type of email that is being sent
    :param username: str: Get the username of the user that is being registered
    :param host: str: Pass the hostname of the server to be used in the email template
    :return: A coroutine object
    :doc-author: Trelent
    """

    try:
        token_verification = await auth_service.create_email_token({"sub": email})
        message = MessageSchema(
            subject="Confirm your email address",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html)

        fast_m = FastMail(conf)
        await fast_m.send_message(message, template_name="verify_email.html")
    except ConnectionErrors as err:
        print(err)
