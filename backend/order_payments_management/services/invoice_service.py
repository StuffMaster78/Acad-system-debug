"""
Invoice service for creating, managing, and processing invoices.
"""
import logging
import uuid
from decimal import Decimal
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from datetime import timedelta
from typing import Optional, Dict, Any

from ..models import Invoice, OrderPayment
from ..services.unified_payment_service import UnifiedPaymentService
from django.core.mail import send_mail, EmailMultiAlternatives
from websites.models import Website

logger = logging.getLogger(__name__)


class InvoiceService:
    """Service for managing invoices and payment links."""
    
    @staticmethod
    @transaction.atomic
    def create_invoice(
        recipient_email: str,
        website: Website,
        amount: Decimal,
        title: str,
        due_date,
        issued_by,
        recipient_name: str = "",
        purpose: str = "",
        description: str = "",
        order_number: str = "",
        payment_method: str = None,
        client=None,
        order=None,
        special_order=None,
        class_purchase=None,
        send_email: bool = True,
        token_expires_in_days: int = 30
    ) -> Invoice:
        """
        Create a new invoice with payment link generation.
        
        Args:
            recipient_email: Email address to send invoice to
            website: Website context
            amount: Invoice amount
            title: Invoice title
            due_date: Payment due date
            issued_by: Admin/superadmin creating the invoice
            recipient_name: Name of recipient (optional)
            purpose: Purpose of invoice (optional)
            description: Detailed description (optional)
            order_number: Optional order/reference number (optional)
            client: Client user (if exists in system, optional)
            order: Optional reference to Order
            special_order: Optional reference to SpecialOrder
            class_purchase: Optional reference to ClassPurchase
            send_email: Whether to send email immediately
            token_expires_in_days: Days until payment token expires (default: 30)
            
        Returns:
            Invoice: Created invoice instance
        """
        # Validate recipient
        if not recipient_email:
            raise ValidationError("recipient_email is required")
        
        # If client is provided, use client's email
        if client:
            recipient_email = client.email
        
        # Generate payment token
        payment_token = InvoiceService._generate_payment_token()
        token_expires_at = timezone.now() + timedelta(days=token_expires_in_days)
        
        # Create invoice
        invoice = Invoice.objects.create(
            client=client,
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            website=website,
            issued_by=issued_by,
            title=title,
            purpose=purpose,
            description=description,
            order_number=order_number,
            amount=amount,
            due_date=due_date,
            payment_method=payment_method,
            payment_token=payment_token,
            token_expires_at=token_expires_at,
            order=order,
            special_order=special_order,
            class_purchase=class_purchase,
        )
        
        # Send email if requested
        if send_email:
            try:
                InvoiceService.send_invoice_email(invoice)
            except Exception as e:
                logger.error(f"Failed to send invoice email: {e}")
                # Don't fail invoice creation if email fails
        
        return invoice
    
    @staticmethod
    def _generate_payment_token() -> str:
        """Generate a secure, unique payment token."""
        return f"INV-{uuid.uuid4().hex[:32].upper()}"
    
    @staticmethod
    def get_payment_link(invoice: Invoice) -> str:
        """
        Get the full payment URL for an invoice.
        
        Args:
            invoice: Invoice instance
            
        Returns:
            str: Full payment URL
        """
        if not invoice.payment_token:
            # Regenerate token if missing
            invoice.payment_token = InvoiceService._generate_payment_token()
            invoice.token_expires_at = timezone.now() + timedelta(days=30)
            invoice.save(update_fields=['payment_token', 'token_expires_at'])
        
        base_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        if not base_url.startswith('http'):
            base_url = f'https://{base_url}'
        
        return f"{base_url}/pay/invoice/{invoice.payment_token}"
    
    @staticmethod
    def send_invoice_email(invoice: Invoice) -> bool:
        """
        Send invoice email with payment link.
        
        Args:
            invoice: Invoice instance
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        try:
            recipient_email = invoice.get_recipient_email()
            recipient_name = invoice.get_recipient_name()
            payment_link = InvoiceService.get_payment_link(invoice)
            
            # Build email content
            subject = f"Invoice #{invoice.reference_id} - Payment Due"
            
            # HTML email template
            html_message = InvoiceService._render_invoice_email_template(
                invoice=invoice,
                recipient_name=recipient_name,
                payment_link=payment_link
            )
            
            # Plain text version
            text_message = f"""
Dear {recipient_name},

You have a new invoice for ${invoice.amount}.

Invoice Details:
- Invoice #: {invoice.reference_id}
- Amount: ${invoice.amount}
- Due Date: {invoice.due_date.strftime('%B %d, %Y')}
- Purpose: {invoice.purpose or invoice.title}
{f"- Order Number: {invoice.order_number}" if invoice.order_number else ""}

Description:
{invoice.description or 'No description provided.'}

Please pay your invoice by clicking the link below:
{payment_link}

If you have any questions, please contact support.

Thank you,
{invoice.website.name}
"""
            
            # Send email using Django's send_mail
            try:
                from_email = invoice.website.get_from_email() if hasattr(invoice.website, 'get_from_email') else settings.DEFAULT_FROM_EMAIL
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_message,
                    from_email=from_email,
                    to=[recipient_email],
                )
                email.attach_alternative(html_message, "text/html")
                email.send()
                success = True
            except Exception as e:
                logger.error(f"Failed to send invoice email: {e}")
                success = False
            
            if success:
                # Update email tracking
                invoice.email_sent = True
                invoice.email_sent_at = timezone.now()
                invoice.email_sent_count += 1
                invoice.save(update_fields=['email_sent', 'email_sent_at', 'email_sent_count'])
                
                logger.info(f"Invoice email sent to {recipient_email} for invoice #{invoice.reference_id}")
                return True
            else:
                logger.error(f"Failed to send invoice email to {recipient_email}")
                return False
                
        except Exception as e:
            logger.exception(f"Error sending invoice email: {e}")
            return False
    
    @staticmethod
    def _render_invoice_email_template(invoice: Invoice, recipient_name: str, payment_link: str) -> str:
        """Render HTML email template for invoice."""
        website = invoice.website
        website_name = website.name
        website_url = f"https://{website.domain}" if website.domain else "#"
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
        .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
        .header {{ background-color: #4F46E5; color: white; padding: 20px; text-align: center; border-radius: 8px 8px 0 0; }}
        .content {{ background-color: #f9fafb; padding: 30px; border: 1px solid #e5e7eb; }}
        .invoice-details {{ background-color: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .detail-row {{ display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #e5e7eb; }}
        .detail-row:last-child {{ border-bottom: none; }}
        .detail-label {{ font-weight: bold; color: #6b7280; }}
        .detail-value {{ color: #111827; }}
        .amount {{ font-size: 24px; font-weight: bold; color: #4F46E5; text-align: center; margin: 20px 0; }}
        .button {{ display: inline-block; background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 6px; margin: 20px 0; }}
        .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invoice #{invoice.reference_id}</h1>
        </div>
        <div class="content">
            <p>Dear {recipient_name},</p>
            <p>You have a new invoice for <strong>${invoice.amount}</strong>.</p>
            
            <div class="invoice-details">
                <div class="detail-row">
                    <span class="detail-label">Invoice Number:</span>
                    <span class="detail-value">{invoice.reference_id}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Amount:</span>
                    <span class="detail-value">${invoice.amount}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Due Date:</span>
                    <span class="detail-value">{invoice.due_date.strftime('%B %d, %Y')}</span>
                </div>
                {f'<div class="detail-row"><span class="detail-label">Purpose:</span><span class="detail-value">{invoice.purpose or invoice.title}</span></div>' if invoice.purpose or invoice.title else ''}
                {f'<div class="detail-row"><span class="detail-label">Order Number:</span><span class="detail-value">{invoice.order_number}</span></div>' if invoice.order_number else ''}
            </div>
            
            {f'<p><strong>Description:</strong><br>{invoice.description}</p>' if invoice.description else ''}
            
            <div style="text-align: center;">
                <a href="{payment_link}" class="button">Pay Invoice Now</a>
            </div>
            
            <p style="margin-top: 30px;">If you have any questions, please contact our support team.</p>
            
            <p>Thank you,<br>{website_name}</p>
        </div>
        <div class="footer">
            <p>This is an automated invoice from {website_name}.<br>
            <a href="{website_url}">{website_url}</a></p>
        </div>
    </div>
</body>
</html>
"""
        return html
    
    @staticmethod
    @transaction.atomic
    def process_invoice_payment(
        invoice: Invoice,
        payment_method: str,
        payment_data: Dict[str, Any]
    ) -> OrderPayment:
        """
        Process payment for an invoice.
        
        Args:
            invoice: Invoice instance
            payment_method: Payment method ('wallet', 'stripe', 'manual', etc.
            payment_data: Additional payment data
            
        Returns:
            OrderPayment: Created payment record
            
        Raises:
            ValidationError: If invoice is already paid or invalid
        """
        # Validate invoice
        if invoice.is_paid:
            raise ValidationError("Invoice has already been paid")
        
        if not invoice.is_token_valid():
            raise ValidationError("Payment link has expired")
        
        # Get or create client user if needed
        client = invoice.client
        if not client:
            # Try to find user by email
            from users.models import User
            try:
                client = User.objects.get(email=invoice.recipient_email)
                invoice.client = client
                invoice.save(update_fields=['client'])
            except User.DoesNotExist:
                # For now, we require a user account for payment
                # In future, could support guest payments
                raise ValidationError("Client account required for payment. Please contact support.")
        
        # Process payment via UnifiedPaymentService
        # For standalone invoices, we'll use a special payment type
        payment = UnifiedPaymentService.create_payment(
            payment_type='invoice',  # New payment type for standalone invoices
            client=client,
            website=invoice.website,
            amount=invoice.amount,
            payment_method=payment_method,
            order=invoice.order,
            special_order=invoice.special_order,
            class_purchase=invoice.class_purchase,
            **payment_data
        )
        
        # Link payment to invoice
        invoice.payment = payment
        invoice.is_paid = True
        invoice.paid_at = timezone.now()
        invoice.save(update_fields=['payment', 'is_paid', 'paid_at'])
        
        # Send payment confirmation email
        try:
            InvoiceService.send_payment_confirmation_email(invoice)
        except Exception as e:
            logger.error(f"Failed to send payment confirmation email: {e}")
        
        logger.info(f"Invoice #{invoice.reference_id} paid via {payment_method}")
        return payment
    
    @staticmethod
    def send_payment_confirmation_email(invoice: Invoice) -> bool:
        """Send payment confirmation email."""
        try:
            recipient_email = invoice.get_recipient_email()
            recipient_name = invoice.get_recipient_name()
            
            subject = f"Payment Confirmed - Invoice #{invoice.reference_id}"
            
            text_message = f"""
Dear {recipient_name},

Your payment for Invoice #{invoice.reference_id} has been confirmed.

Payment Details:
- Invoice #: {invoice.reference_id}
- Amount Paid: ${invoice.amount}
- Payment Date: {invoice.paid_at.strftime('%B %d, %Y at %I:%M %p')}

Thank you for your payment!

Best regards,
{invoice.website.name}
"""
            
            # Send email using Django's send_mail
            try:
                from_email = invoice.website.get_from_email() if hasattr(invoice.website, 'get_from_email') else settings.DEFAULT_FROM_EMAIL
                send_mail(
                    subject=subject,
                    message=text_message,
                    from_email=from_email,
                    recipient_list=[recipient_email],
                    fail_silently=False,
                )
                success = True
            except Exception as e:
                logger.error(f"Failed to send payment confirmation email: {e}")
                success = False
            
            return success
        except Exception as e:
            logger.exception(f"Error sending payment confirmation email: {e}")
            return False
    
    @staticmethod
    def get_invoice_by_token(token: str) -> Optional[Invoice]:
        """
        Get invoice by payment token (for public payment page).
        
        Args:
            token: Payment token
            
        Returns:
            Invoice instance or None if not found/invalid
        """
        try:
            invoice = Invoice.objects.get(payment_token=token)
            if not invoice.is_token_valid():
                return None
            return invoice
        except Invoice.DoesNotExist:
            return None

