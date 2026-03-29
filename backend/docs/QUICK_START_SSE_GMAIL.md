# Quick Start: SSE & Gmail Setup

**5-minute setup guide for SSE and Gmail email notifications**

---

## 🚀 Quick Setup Steps

### 1. Gmail App Password (2 minutes)

1. Go to: https://myaccount.google.com/security
2. Enable **2-Step Verification** (if not already enabled)
3. Click **App passwords** → Generate new
4. Name it: "Writing System Backend"
5. **Copy the 16-character password** (remove spaces when using)

### 2. Create `.env` File (1 minute)

Copy `env.template` to `.env`:

```bash
cp env.template .env
```

Edit `.env` and add your Gmail credentials:

```bash
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### 3. Test Configuration (2 minutes)

Run the test script:

```bash
python test_sse_and_email.py
```

**Expected output:**
- ✅ Email Configuration: PASS
- ✅ SSE Configuration: PASS
- ✅ Notification Creation: PASS

---

## ✅ That's It!

Your system is now configured for:
- ✅ **SSE** - Real-time notifications (already implemented)
- ✅ **Gmail** - Email notifications via SMTP

---

## 📍 SSE Endpoints

Your SSE endpoints are ready:

- `GET /api/v1/notifications/sse/stream/` - Connect to SSE stream
- `GET /api/v1/notifications/sse/status/` - Check connection status
- `POST /api/v1/notifications/sse/close/` - Close connection

**Note:** SSE is already fully implemented in the backend! ✅

---

## 🔧 Troubleshooting

### Email not working?

1. Check `.env` file exists and has correct values
2. Verify App Password (no spaces, 16 characters)
3. Ensure 2-Step Verification is enabled
4. Run: `python test_sse_and_email.py`

### SSE not working?

1. Ensure Redis is running: `docker-compose up redis`
2. Check user is authenticated
3. Verify notification preferences allow SSE

---

## 📚 Full Documentation

See `SSE_AND_GMAIL_SETUP.md` for complete details.

---

**Last Updated:** December 2024

