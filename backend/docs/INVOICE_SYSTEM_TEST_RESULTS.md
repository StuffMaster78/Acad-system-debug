# Invoice Payment System - Testing Guide

## ✅ Migration Complete

The invoice system migration has been successfully applied. All new fields have been added to the Invoice model.

## 🧪 Testing the Invoice System

### **1. Test Invoice Creation via API**

```bash
# Get admin token first
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "superadmin@test.com",
    "password": "your_password"
  }'

# Create an invoice
curl -X POST http://localhost:8000/api/v1/order-payments/invoices/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "recipient_email": "client@example.com",
    "recipient_name": "John Doe",
    "website_id": 1,
    "title": "Order Payment Invoice",
    "purpose": "Order Payment",
    "description": "Payment for order #12345",
    "order_number": "ORD-12345",
    "amount": "150.00",
    "due_date": "2024-12-31",
    "send_email": true
  }'
```

### **2. Test Invoice List**

```bash
curl -X GET http://localhost:8000/api/v1/order-payments/invoices/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### **3. Test Payment Link Generation**

After creating an invoice, you'll receive a `payment_token`. Test the payment link:

```bash
# Get invoice by token (public endpoint)
curl -X GET http://localhost:8000/api/v1/order-payments/invoices/pay/INV-TOKEN-HERE/
```

### **4. Test Invoice Statistics**

```bash
curl -X GET http://localhost:8000/api/v1/order-payments/invoices/stats/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 📋 Expected Results

1. **Invoice Creation**: Should return invoice with:
   - `reference_id` (unique)
   - `payment_token` (secure token)
   - `payment_link` (full URL)
   - All fields populated

2. **Email Sending**: If `send_email: true`, email should be sent with:
   - Professional HTML template
   - Payment link button
   - Invoice details

3. **Payment Processing**: Client can click link and pay via:
   - Wallet
   - Stripe
   - Other payment methods

## 🔍 Verification Checklist

- [x] Migration applied successfully
- [ ] Invoice creation works
- [ ] Payment link generation works
- [ ] Email sending works
- [ ] Payment processing works
- [ ] Invoice statistics work
- [ ] Multi-tenant filtering works

## 🚀 Next Steps

1. Test invoice creation via API
2. Verify email delivery
3. Test payment link functionality
4. Test payment processing
5. Frontend integration

---

**Status**: ✅ **Backend Ready for Testing!**

