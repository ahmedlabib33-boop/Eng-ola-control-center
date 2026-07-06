from __future__ import annotations

import os
import smtplib
from email.message import EmailMessage

import requests

from ola_360.repositories.app_repository import AppRepository


class ChannelService:
    def __init__(self, repo: AppRepository):
        self.repo = repo

    def send_email(self, recipient: str, subject: str, body: str) -> dict[str, str]:
        host = os.getenv("OLA_SMTP_HOST")
        user = os.getenv("OLA_SMTP_USER")
        password = os.getenv("OLA_SMTP_PASSWORD")
        sender = os.getenv("OLA_SMTP_FROM", user or "")
        if not host or not sender:
            return self._record("email", recipient, subject, body, "draft", "SMTP is not configured.")
        message = EmailMessage()
        message["From"] = sender
        message["To"] = recipient
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP(host, int(os.getenv("OLA_SMTP_PORT", "587")), timeout=30) as smtp:
            smtp.starttls()
            if user and password:
                smtp.login(user, password)
            smtp.send_message(message)
        return self._record("email", recipient, subject, body, "sent", "SMTP sent.")

    def send_teams(self, subject: str, body: str) -> dict[str, str]:
        webhook = os.getenv("OLA_TEAMS_WEBHOOK_URL")
        if not webhook:
            return self._record("teams", "", subject, body, "draft", "Teams webhook is not configured.")
        response = requests.post(webhook, json={"text": f"**{subject}**\n\n{body}"}, timeout=30)
        return self._record("teams", "", subject, body, "sent" if response.ok else "failed", response.text[:500])

    def send_whatsapp(self, recipient: str, subject: str, body: str) -> dict[str, str]:
        sid = os.getenv("TWILIO_ACCOUNT_SID")
        token = os.getenv("TWILIO_AUTH_TOKEN")
        sender = os.getenv("TWILIO_WHATSAPP_FROM")
        if not sid or not token or not sender:
            return self._record("whatsapp", recipient, subject, body, "draft", "Twilio WhatsApp is not configured.")
        response = requests.post(
            f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json",
            auth=(sid, token),
            data={"From": sender, "To": recipient, "Body": f"{subject}\n{body}"},
            timeout=30,
        )
        return self._record("whatsapp", recipient, subject, body, "sent" if response.ok else "failed", response.text[:500])

    def _record(self, channel: str, recipient: str, subject: str, body: str, status: str, provider_response: str) -> dict[str, str]:
        self.repo.create_notification_delivery(channel, recipient, subject, body, status, provider_response)
        return {"channel": channel, "status": status, "provider_response": provider_response}
