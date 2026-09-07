import os
import smtplib

from email.message import EmailMessage
from dotenv import load_dotenv


load_dotenv()


MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_FROM = os.getenv("MAIL_FROM")


def send_otp_email(
    recipient_email: str,
    otp: str
):

    message = EmailMessage()

    message["Subject"] = "Password Reset OTP"
    message["From"] = MAIL_FROM
    message["To"] = recipient_email

    message.set_content(
        f"""
Your password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this password reset,
please ignore this email.
"""
    )

    with smtplib.SMTP_SSL(
        "smtp.gmail.com",
        465
    ) as smtp:

        smtp.login(
            MAIL_USERNAME,
            MAIL_PASSWORD
        )

        smtp.send_message(message)