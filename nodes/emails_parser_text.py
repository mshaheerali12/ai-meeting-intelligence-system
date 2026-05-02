import asyncio
import aiosmtplib
from email.mime.text import MIMEText
from nodes.state2 import emailstr
import os

GMAIL_USER = "ashaheer1111@gmail.com"
GMAIL_PASS = "krfvstzseaqkhqwm"

async def send_single_email(to: str, subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to
    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        username=GMAIL_USER,
        password=GMAIL_PASS,
        start_tls=True
    )

async def send_email(state: emailstr):
    emails_payload = state.get("emails_payload", [])
    subject = state.get("subject", "Meeting Tasks")

    if not emails_payload:
        return state

    # Send all emails in parallel
    await asyncio.gather(*[
        send_single_email(
            to=email["to"],
            subject=subject,
            body=email["body"]
        )
        for email in emails_payload
    ])

    return state