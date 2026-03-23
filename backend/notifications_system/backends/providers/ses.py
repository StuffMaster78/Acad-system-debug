# notifications_system/backends/providers/ses.py
"""
AWS SES email provider backend.

Uses boto3 — the official AWS SDK for Python.

Config:
    {
        'aws_access_key_id':     'AKIAxxxxxxxxxx',
        'aws_secret_access_key': 'xxxxxxxxxx',
        'region_name':           'us-east-1',
    }

Cheapest provider at scale:
    $0.10 per 1,000 emails
    62,000 emails/month free if sending from EC2

Requirements:
    - Verify your sending domain in AWS SES console
    - Request production access (sandbox mode blocks non-verified recipients)
    - pip install boto3
"""
from __future__ import annotations

import logging


from notifications_system.backends.providers.base import (
    BaseEmailBackend,
    EmailMessage,
    EmailSendResult,
)

logger = logging.getLogger(__name__)


class SESBackend(BaseEmailBackend):

    provider_name = 'AWS SES'

    def _validate_config(self) -> None:
        if not self.config.get('aws_access_key_id'):
            raise RuntimeError(
                "SESBackend requires 'aws_access_key_id' in config."
            )
        if not self.config.get('aws_secret_access_key'):
            raise RuntimeError(
                "SESBackend requires 'aws_secret_access_key' in config."
            )

    def _get_client(self):
        """Build and return a boto3 SES client."""
        try:
            import boto3
        except ImportError:
            raise RuntimeError(
                "boto3 is not installed. Run: pip install boto3"
            )

        return boto3.client(
            'ses',
            aws_access_key_id=self.config['aws_access_key_id'],
            aws_secret_access_key=self.config['aws_secret_access_key'],
            region_name=self.config.get('region_name', 'us-east-1'),
        )

    def send(self, message: EmailMessage) -> EmailSendResult:
        try:
            client = self._get_client()
        except RuntimeError as exc:
            return EmailSendResult(
                success=False,
                error_code='NO_CONFIG',
                error_message=str(exc),
            )

        try:
            # Build SES message structure
            ses_message = {
                'Subject': {
                    'Data': message.subject,
                    'Charset': 'UTF-8',
                },
                'Body': {},
            }

            if message.has_text():
                ses_message['Body']['Text'] = {
                    'Data': message.body_text,
                    'Charset': 'UTF-8',
                }

            if message.has_html():
                ses_message['Body']['Html'] = {
                    'Data': message.body_html,
                    'Charset': 'UTF-8',
                }

            params = {
                'Source': message.from_header,
                'Destination': {
                    'ToAddresses': [message.to],
                },
                'Message': ses_message,
            }

            if message.reply_to:
                params['ReplyToAddresses'] = [message.reply_to]

            if message.cc:
                params['Destination']['CcAddresses'] = message.cc

            if message.bcc:
                params['Destination']['BccAddresses'] = message.bcc

            # SES tags for CloudWatch metrics
            if message.tags:
                params['Tags'] = [
                    {'Name': tag[:128], 'Value': 'true'}
                    for tag in message.tags[:10]  # SES max 10 tags
                ]

            response = client.send_email(**params)

            message_id = response.get('MessageId', '')

            logger.info(
                "SESBackend: sent to=%s message_id=%s.",
                message.to,
                message_id,
            )

            return EmailSendResult(
                success=True,
                message_id=message_id,
                status_code=200,
                meta={
                    'request_id': response.get(
                        'ResponseMetadata', {}
                    ).get('RequestId', ''),
                },
            )

        except Exception as exc:
            error_str = str(exc)
            error_code = 'SEND_FAILED'

            # Classify boto3 / SES errors
            if hasattr(exc, 'response'):
                aws_code = (
                    exc.response.get('Error', {}).get('Code', '')
                )
                if aws_code in ('InvalidClientTokenId', 'AuthFailure'):
                    error_code = 'AUTH_ERROR'
                elif aws_code == 'Throttling':
                    error_code = 'RATE_LIMITED'
                elif aws_code in (
                    'MessageRejected',
                    'InvalidParameterValue',
                ):
                    error_code = 'INVALID_RECIPIENT'
                elif aws_code == 'MailFromDomainNotVerified':
                    error_code = 'NO_CONFIG'

            logger.exception(
                "SESBackend: failed to=%s error=%s.",
                message.to,
                exc,
            )

            return EmailSendResult(
                success=False,
                error_code=error_code,
                error_message=error_str,
            )

    def health_check(self) -> bool:
        """Verify SES credentials and check sending quota."""
        try:
            client = self._get_client()
            client.get_send_quota()
            return True
        except Exception:
            return False

    def get_provider_info(self) -> dict:
        return {
            'provider': self.provider_name,
            'region': self.config.get('region_name', 'us-east-1'),
        }