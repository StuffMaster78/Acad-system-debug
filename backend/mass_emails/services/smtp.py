from django.core.mail import EmailMultiAlternatives
from .base import register_provider, EmailProviderBase


@register_provider("smtp")
class SMTPProvider(EmailProviderBase):
    def send_email(self, subject, body_html, from_email, to):
        msg = EmailMultiAlternatives(subject, "", from_email, to)
        msg.attach_alternative(body_html, "text/html")
        msg.send()