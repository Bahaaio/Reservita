from pathlib import Path
from typing import Annotated, Any

import emails
from app.core.config import settings
from app.db.models import Event, EventSeat, Review, Ticket, User
from app.util.qr import generate_qr_code_base64
from fastapi import Depends
from jinja2 import Template


class EmailService:
    def __init__(self):
        self.sender = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"

    def render_email_template(self, template_name: str, context: dict[str, Any]) -> str:
        template_path = (
            Path(__file__).parent.parent / "templates" / "emails" / template_name
        )
        template_content = template_path.read_text()
        return Template(template_content).render(context)

    def send_email(self, subject: str, email_to: str, html_content: str):
        assert settings.emails_enabled, "no provided configuration for email variables"

        message = emails.Message(
            subject=subject,
            html=html_content,
            mail_from=(settings.EMAILS_FROM_NAME, settings.EMAILS_FROM_EMAIL),
        )

        smtp_options = {
            "host": settings.SMTP_HOST,
            "port": settings.SMTP_PORT,
            "user": settings.SMTP_USER,
            "password": settings.SMTP_PASSWORD,
            "tls": True,
        }

        message.send(to=email_to, smtp=smtp_options)

    def send_welcome_email(self, user: User):
        subject = f"Welcome to {settings.PROJECT_NAME}!"
        html_content = self.render_email_template(
            "welcome.html",
            {
                "user_name": user.full_name,
                "project_name": settings.PROJECT_NAME,
                "link": settings.FRONTEND_URL,
            },
        )

        self.send_email(subject, self._get_email_to(user), html_content)

    def send_ticket_confirmation_email(
        self, user: User, ticket: Ticket, event: Event, seat: EventSeat
    ):
        subject = f"Ticket Confirmed: {event.title}"
        qr_code_base64 = generate_qr_code_base64(ticket.qr_code)

        html_content = self.render_email_template(
            "ticket_confirmation.html",
            {
                "user_name": user.full_name,
                "project_name": settings.PROJECT_NAME,
                "event_name": event.title,
                "event_date": event.starts_at.strftime("%B %d, %Y"),
                "event_time": event.starts_at.strftime("%I:%M %p"),
                "event_location": f"{event.venue}, {event.city}",
                "ticket_id": ticket.id,
                "seat_number": seat.seat_number,
                "seat_type": seat.seat_type.value,
                "price": f"{event.vip_ticket_price if seat.seat_type.value == 'vip' else event.ticket_price:.2f}",
                "link": f"{settings.FRONTEND_URL}/tickets/{ticket.id}",
                "qr_code_base64": qr_code_base64,
            },
        )

        self.send_email(subject, self._get_email_to(user), html_content)

    def send_ticket_cancellation_email(self, user: User, ticket: Ticket, event: Event):
        subject = f"Ticket Cancelled: {event.title}"
        html_content = self.render_email_template(
            "ticket_cancellation.html",
            {
                "user_name": user.full_name,
                "project_name": settings.PROJECT_NAME,
                "event_name": event.title,
                "event_date": event.starts_at.strftime("%B %d, %Y"),
                "ticket_id": ticket.id,
                "seat_number": ticket.seat_number,
                "cancelled_at": ticket.cancelled_at.strftime("%B %d, %Y at %I:%M %p")
                if ticket.cancelled_at
                else "N/A",
                "link": f"{settings.FRONTEND_URL}/events",
            },
        )

        self.send_email(subject, self._get_email_to(user), html_content)

    def send_review_notification_email(
        self, agency: User, review: Review, event: Event, reviewer: User
    ):
        subject = f"New Review: {event.title}"
        html_content = self.render_email_template(
            "review.html",
            {
                "agency_name": agency.full_name,
                "project_name": settings.PROJECT_NAME,
                "event_name": event.title,
                "rating": review.rating,
                "reviewer_name": reviewer.full_name,
                "review_comment": review.comment or "No comment provided.",
            },
        )

        self.send_email(subject, self._get_email_to(agency), html_content)

    def _get_email_to(self, user: User) -> str:
        return f"{user.full_name} <{user.email}>"


def get_email_service() -> EmailService:
    return EmailService()


EmailServiceDep = Annotated[EmailService, Depends(get_email_service)]
