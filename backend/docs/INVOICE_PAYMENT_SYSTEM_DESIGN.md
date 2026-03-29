# Invoice Payment System Design

## Overview

Yes, it's absolutely possible! This document outlines the design for a comprehensive invoice payment system where superadmins and admins can create invoices, send them via email with secure payment links, and clients can pay directly through those links.

---

## ✅ Existing Infrastructure

### 1. **Invoice Model** ✅
- Location: `order_pages_management/models.py`
- Fields: `client`, `issued_by`, `title`, `description`, `amount`, `due_date`, `is_paid`, `payment`, `reference_id`
- **Missing**: `website` field (needs to be added for multi-tenant support)

### 2. **Payment Processing** ✅
- `UnifiedPaymentService` - Handles all payment types
- `OrderPayment` model - Tracks payment records
- Payment methods: wallet, stripe, manual, etc.

### 3. **Email Infrastructure** ✅
- Email sending via Django's `send_mail`
- Notification templates for invoices (`payment.invoice_generated`)
- Gmail SMTP setup available

### 4. **Secure Links** ✅
- Magic link infrastructure for secure token generation
- Token expiration and validation
- Can be adapted for payment links

---

## 🎯 System Design

### **Core Features**

1. **Invoice Creation**
   - Admin/Superadmin creates invoice
   - Invoice linked to client, website, and issuer
   - Auto-generates unique reference ID
   - Sets due date

2. **Payment Link Generation**
   - Secure, unique payment token per invoice
   - Token expires after due date (or configurable time)
   - One-time use or reusable until paid
   - Includes invoice reference in link

3. **Email Sending**
   - Professional invoice email template
   - Includes invoice details (amount, due date, description)
   - Payment link embedded as button/link
   - PDF attachment (optional)

4. **Payment Processing**
   - Client clicks payment link
   - Redirects to payment page
   - Supports multiple payment methods (wallet, Stripe, etc.)
   - Updates invoice status on payment

5. **Invoice Management**
   - List all invoices (filtered by website for admins)
   - View invoice details
   - Resend invoice email
   - Mark as paid manually (if needed)
   - Cancel/void invoices

---

## 📋 Implementation Plan

### **Phase 1: Backend - Invoice Model Enhancement**

#### 1.1 Add Website Field to Invoice Model
```python
# order_payments_management/models.py
class Invoice(models.Model):
    # ... existing fields ...
    website = models.ForeignKey(
        Website, on_delete=models.CASCADE,
        related_name="invoices",
        null=True, blank=True  # Allow null for backward compatibility
    )
    payment_token = models.CharField(
        max_length=128, unique=True, null=True, blank=True,
        help_text="Secure token for payment link"
    )
    token_expires_at = models.DateTimeField(null=True, blank=True)
    email_sent = models.BooleanField(default=False)
    email_sent_at = models.DateTimeField(null=True, blank=True)
    email_sent_count = models.IntegerField(default=0)
```

#### 1.2 Create Invoice Service
```python
# order_payments_management/services/invoice_service.py
class InvoiceService:
    @staticmethod
    def create_invoice(client, website, amount, title, description, due_date, issued_by):
        """Create invoice and generate payment link"""
        
    @staticmethod
    def generate_payment_link(invoice):
        """Generate secure payment token and return full URL"""
        
    @staticmethod
    def send_invoice_email(invoice):
        """Send invoice email with payment link"""
        
    @staticmethod
    def process_invoice_payment(invoice, payment_method, payment_data):
        """Process payment for invoice"""
```

#### 1.3 Create Invoice ViewSet
```python
# order_payments_management/views.py
class InvoiceViewSet(viewsets.ModelViewSet):
    """CRUD operations for invoices"""
    
    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Resend invoice email"""
        
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Manually mark invoice as paid"""
        
    @action(detail=False, methods=['get'])
    def payment_link(self, request):
        """Get payment link for invoice (by token)"""
        
    @action(detail=True, methods=['post'])
    def process_payment(self, request, pk=None):
        """Process payment for invoice"""
```

### **Phase 2: Payment Link Generation**

#### 2.1 Secure Token Generation
- Use UUID or cryptographically secure random string
- Store token in `Invoice.payment_token`
- Set expiration (default: due_date + 30 days)
- Token format: `INV-{reference_id}-{random_token}`

#### 2.2 Payment Link Format
```
https://{website.domain}/pay/invoice/{token}
or
https://{website.domain}/api/v1/order-payments/invoices/pay/{token}/
```

### **Phase 3: Email Template**

#### 3.1 Invoice Email Template
- Professional HTML email
- Invoice details table
- Payment link button
- Due date reminder
- Company branding
- PDF attachment (optional)

### **Phase 4: Payment Processing**

#### 4.1 Payment Endpoint
- Verify token validity
- Check if invoice is already paid
- Display invoice details
- Process payment via `UnifiedPaymentService`
- Update invoice status
- Send confirmation email

---

## 🔌 API Endpoints

### **Invoice Management**
```
GET    /api/v1/order-payments/invoices/              # List invoices
POST   /api/v1/order-payments/invoices/              # Create invoice
GET    /api/v1/order-payments/invoices/{id}/         # Get invoice details
PUT    /api/v1/order-payments/invoices/{id}/         # Update invoice
DELETE /api/v1/order-payments/invoices/{id}/         # Delete invoice
POST   /api/v1/order-payments/invoices/{id}/send_email/  # Send invoice email
POST   /api/v1/order-payments/invoices/{id}/mark_paid/    # Mark as paid manually
```

### **Payment Processing**
```
GET    /api/v1/order-payments/invoices/pay/{token}/  # Get invoice by token (public)
POST   /api/v1/order-payments/invoices/pay/{token}/  # Process payment (public)
```

### **Statistics**
```
GET    /api/v1/order-payments/invoices/stats/        # Invoice statistics
```

---

## 📧 Email Template Structure

```html
Subject: Invoice #{reference_id} - Payment Due

Dear {client_name},

You have a new invoice for {amount}.

Invoice Details:
- Invoice #: {reference_id}
- Amount: ${amount}
- Due Date: {due_date}
- Description: {description}

[PAY NOW BUTTON] → {payment_link}

If you have any questions, please contact support.

Thank you,
{website_name}
```

---

## 🔒 Security Features

1. **Token Security**
   - Cryptographically secure tokens
   - Token expiration
   - One-time use (optional)
   - Rate limiting on payment attempts

2. **Access Control**
   - Only invoice owner can view payment page
   - Token validation before payment
   - Invoice status checks

3. **Audit Trail**
   - Log all invoice actions
   - Track email sends
   - Payment history

---

## 🎨 Frontend Integration

### **Admin Interface**
1. **Invoice List Page**
   - Filter by status, client, date range
   - Search by reference ID
   - Bulk actions (send emails, mark paid)

2. **Create Invoice Form**
   - Client selection (with search)
   - Website selection (for admins)
   - Amount, title, description
   - Due date picker
   - Send email checkbox

3. **Invoice Detail Page**
   - View invoice details
   - Payment status
   - Resend email button
   - Mark as paid button
   - Payment history

### **Client Interface**
1. **Payment Page** (Public/Token-based)
   - Invoice details display
   - Payment method selection
   - Payment processing
   - Receipt generation

2. **Invoice History** (Client Dashboard)
   - List of all invoices
   - Payment status
   - Download invoice PDF

---

## 📊 Database Schema Updates

### **Migration Required**
```python
# Add to Invoice model:
- website (ForeignKey to Website)
- payment_token (CharField, unique)
- token_expires_at (DateTimeField)
- email_sent (BooleanField)
- email_sent_at (DateTimeField)
- email_sent_count (IntegerField)
```

---

## 🔄 Workflow

### **Invoice Creation Flow**
1. Admin creates invoice → `POST /invoices/`
2. System generates payment token
3. System sends email (if requested)
4. Client receives email with payment link
5. Client clicks link → redirected to payment page
6. Client selects payment method
7. Payment processed → invoice marked as paid
8. Confirmation email sent

### **Payment Processing Flow**
1. Client clicks payment link
2. System validates token
3. System checks invoice status
4. System displays invoice details
5. Client selects payment method
6. Payment processed via `UnifiedPaymentService`
7. Invoice updated: `is_paid=True`, `paid_at=now()`
8. Payment record linked to invoice
9. Confirmation sent

---

## 📈 Statistics & Reporting

- Total invoices (paid/unpaid)
- Total amount invoiced
- Total amount collected
- Overdue invoices
- Average payment time
- Payment method distribution

---

## ✅ Implementation Checklist

### **Backend**
- [ ] Add `website` field to Invoice model
- [ ] Add payment token fields to Invoice model
- [ ] Create migration
- [ ] Create `InvoiceService` class
- [ ] Create `InvoiceViewSet` with CRUD operations
- [ ] Add `send_email` action
- [ ] Add `process_payment` action
- [ ] Add public payment endpoint (token-based)
- [ ] Create email template
- [ ] Integrate with notification system
- [ ] Add invoice statistics endpoint

### **Frontend**
- [ ] Create invoice list page
- [ ] Create invoice creation form
- [ ] Create invoice detail page
- [ ] Create payment page (public)
- [ ] Add invoice section to client dashboard
- [ ] Add invoice management to admin dashboard

### **Testing**
- [ ] Test invoice creation
- [ ] Test email sending
- [ ] Test payment link generation
- [ ] Test payment processing
- [ ] Test token expiration
- [ ] Test multi-tenant filtering

---

## 🚀 Next Steps

1. **Start with Backend**
   - Enhance Invoice model
   - Create InvoiceService
   - Create InvoiceViewSet
   - Add payment link generation

2. **Email Integration**
   - Create email template
   - Integrate with email service
   - Test email delivery

3. **Payment Processing**
   - Create public payment endpoint
   - Integrate with UnifiedPaymentService
   - Handle payment callbacks

4. **Frontend Development**
   - Admin invoice management
   - Client payment page
   - Invoice history

---

## 💡 Additional Features (Future)

- **Recurring Invoices**: Auto-generate monthly invoices
- **Invoice Templates**: Customizable invoice templates
- **Partial Payments**: Support for partial invoice payments
- **Payment Plans**: Installment-based invoice payments
- **Invoice Reminders**: Automatic reminders for unpaid invoices
- **PDF Generation**: Generate downloadable invoice PDFs
- **Multi-currency**: Support for different currencies
- **Tax Calculation**: Automatic tax calculation
- **Discount Codes**: Apply discounts to invoices

---

**Status**: ✅ **Design Complete - Ready for Implementation!**

The system is fully designed and can be implemented using existing infrastructure. All required components are available or can be easily added.

