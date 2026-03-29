# Invoice Feature Access Guide

## 📍 How to Access Invoice Feature

### **1. API Access (Available Now)**

The invoice feature is available via REST API endpoints.

**Base URL**: `/api/v1/order-payments/invoices/`

#### **Available Endpoints**:

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/order-payments/invoices/` | List all invoices | ✅ Admin/Superadmin |
| `POST` | `/api/v1/order-payments/invoices/` | Create new invoice | ✅ Admin/Superadmin |
| `GET` | `/api/v1/order-payments/invoices/{id}/` | Get invoice details | ✅ Admin/Superadmin |
| `PUT` | `/api/v1/order-payments/invoices/{id}/` | Update invoice | ✅ Admin/Superadmin |
| `PATCH` | `/api/v1/order-payments/invoices/{id}/` | Partial update | ✅ Admin/Superadmin |
| `DELETE` | `/api/v1/order-payments/invoices/{id}/` | Delete invoice | ✅ Admin/Superadmin |
| `POST` | `/api/v1/order-payments/invoices/{id}/send_email/` | Send invoice email | ✅ Admin/Superadmin |
| `POST` | `/api/v1/order-payments/invoices/{id}/regenerate_payment_link/` | Regenerate payment link | ✅ Admin/Superadmin |
| `GET` | `/api/v1/order-payments/invoices/pay/{token}/` | View payment page (public) | ❌ Public |
| `POST` | `/api/v1/order-payments/invoices/pay/{token}/` | Process payment (public) | ❌ Public |
| `GET` | `/api/v1/order-payments/invoices/statistics/` | Get invoice statistics | ✅ Admin/Superadmin |

---

### **2. Testing via API**

#### **Example: List Invoices**
```bash
curl -X GET "http://localhost:8000/api/v1/order-payments/invoices/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

#### **Example: Create Invoice**
```bash
curl -X POST "http://localhost:8000/api/v1/order-payments/invoices/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": 1,
    "website_id": 1,
    "title": "Monthly Service Invoice",
    "description": "Invoice for services rendered",
    "amount": 1000.00,
    "due_date": "2024-12-31",
    "send_email": true
  }'
```

#### **Example: Send Invoice Email**
```bash
curl -X POST "http://localhost:8000/api/v1/order-payments/invoices/1/send_email/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json"
```

---

### **3. Query Parameters**

When listing invoices, you can filter using query parameters:

- `?status=paid` - Show only paid invoices
- `?status=unpaid` - Show only unpaid invoices
- `?status=overdue` - Show only overdue invoices
- `?client_id=1` - Filter by client
- `?website_id=1` - Filter by website
- `?search=INV-001` - Search by reference ID, email, title, or order number

**Example**:
```
GET /api/v1/order-payments/invoices/?status=unpaid&client_id=1
```

---

### **4. Frontend Access (Not Yet Created)**

Currently, there is **no frontend page** for invoice management. You can:

1. **Use API directly** (Postman, curl, etc.)
2. **Create a frontend page** (I can help with this)
3. **Access via Django Admin** (if models are registered)

---

### **5. Payment Link Access (Public)**

Clients receive payment links via email. The link format is:
```
https://yourdomain.com/api/v1/order-payments/invoices/pay/{token}/
```

This is a **public endpoint** that doesn't require authentication. Clients can:
- View invoice details
- Make payment via wallet or Stripe
- See payment status

---

### **6. Permissions**

- **Admin/Superadmin**: Full access to all invoice operations
- **Clients**: Can only access invoices via payment links (public token)
- **Other roles**: No direct access

---

## 🚀 Quick Start

1. **Get your access token** (login via `/api/v1/auth/login/`)
2. **List invoices**: `GET /api/v1/order-payments/invoices/`
3. **Create invoice**: `POST /api/v1/order-payments/invoices/`
4. **Send email**: `POST /api/v1/order-payments/invoices/{id}/send_email/`

---

## 📝 Next Steps

Would you like me to:
1. ✅ Create a frontend Invoice Management page?
2. ✅ Add invoice routes to the router?
3. ✅ Add invoice link to the admin dashboard sidebar?

Let me know and I'll create the frontend interface!

