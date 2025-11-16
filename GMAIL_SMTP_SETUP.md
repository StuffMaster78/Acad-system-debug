# Gmail SMTP Setup Guide

**For Test System Email Notifications**

---

## 📋 Prerequisites

1. A Gmail account (personal or test account)
2. 2-Step Verification enabled on your Gmail account
3. App Password generated (see steps below)

---

## 🔐 Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click **Security** in the left sidebar
3. Under **Signing in to Google**, click **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification
   - You'll need to verify your phone number
   - You'll receive a verification code via SMS

**Why?** Gmail requires 2-Step Verification to generate App Passwords for SMTP.

---

## 🔑 Step 2: Generate App Password

1. Go back to **Security** settings: https://myaccount.google.com/security
2. Under **Signing in to Google**, click **App passwords**
   - If you don't see this option, make sure 2-Step Verification is enabled
3. Select **Mail** as the app
4. Select **Other (Custom name)** as the device
5. Enter a name like: **"Writing System Backend"**
6. Click **Generate**
7. **Copy the 16-character password** (you'll see it only once!)
   - Format: `xxxx xxxx xxxx xxxx` (remove spaces when using)

**Important:** This is a one-time password. Save it securely!

---

## ⚙️ Step 3: Configure Environment Variables

### Option A: Using `.env` file (Recommended for Development)

Create a `.env` file in your project root (`/Users/awwy/writing_system_backend/.env`):

```bash
# Gmail SMTP Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-char-app-password
DEFAULT_FROM_EMAIL=your-email@gmail.com
```

**Replace:**
- `your-email@gmail.com` with your Gmail address
- `your-16-char-app-password` with the App Password (remove spaces)

### Option B: Using Docker Environment Variables

If using Docker, add to `docker-compose.yml`:

```yaml
services:
  web:
    environment:
      - EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
      - EMAIL_HOST=smtp.gmail.com
      - EMAIL_PORT=587
      - EMAIL_USE_TLS=True
      - EMAIL_HOST_USER=your-email@gmail.com
      - EMAIL_HOST_PASSWORD=your-16-char-app-password
      - DEFAULT_FROM_EMAIL=your-email@gmail.com
```

### Option C: Export in Shell (Temporary)

```bash
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-16-char-app-password"
export DEFAULT_FROM_EMAIL="your-email@gmail.com"
```

---

## ✅ Step 4: Verify Configuration

### Test Email Sending

Run the test script:

```bash
python manage.py shell
```

Then run:

```python
from django.core.mail import send_mail
from django.conf import settings

# Test email
send_mail(
    subject='Test Email from Writing System',
    message='This is a test email to verify Gmail SMTP configuration.',
    from_email=settings.DEFAULT_FROM_EMAIL,
    recipient_list=['your-test-email@gmail.com'],
    fail_silently=False,
)
print("Email sent successfully!")
```

Or use the provided test script:

```bash
python test_email_setup.py
```

---

## 🔒 Security Best Practices

### 1. **Never Commit `.env` to Git**

Add to `.gitignore`:
```
.env
*.env
.env.local
```

### 2. **Use Different Accounts for Test/Production**

- **Test:** Use a personal Gmail account or dedicated test account
- **Production:** Use a dedicated business email (Gmail Workspace or custom domain)

### 3. **Rotate App Passwords Regularly**

- Generate new App Passwords every 3-6 months
- Revoke old App Passwords in Google Account settings

### 4. **Limit Email Sending**

Your current settings already include limits:
```python
NOTIFY_EMAIL_COOLDOWN_MINUTES = 30
NOTIFY_DAILY_EMAIL_LIMIT = 5
NOTIFY_WEEKLY_EMAIL_LIMIT = 20
```

---

## 🚨 Troubleshooting

### Error: "Username and Password not accepted"

**Solution:**
1. Make sure you're using the **App Password**, not your regular Gmail password
2. Verify 2-Step Verification is enabled
3. Check that the App Password was copied correctly (no spaces)

### Error: "Connection refused" or "Timeout"

**Solution:**
1. Check firewall settings
2. Verify `EMAIL_PORT=587` (TLS) or try `EMAIL_PORT=465` (SSL)
3. If using SSL, set `EMAIL_USE_SSL=True` instead of `EMAIL_USE_TLS=True`

### Error: "Less secure app access"

**Solution:**
- This error shouldn't appear if using App Passwords
- If it does, make sure you're using App Passwords, not regular passwords

### Emails Going to Spam

**Solution:**
1. Add SPF record (if using custom domain)
2. Use a dedicated email account for sending
3. Warm up the email account by sending a few test emails first
4. Include proper email templates with unsubscribe links

---

## 📊 Gmail Sending Limits

**Free Gmail Account:**
- **Daily limit:** 500 emails/day
- **Per recipient:** 100 emails/day
- **Rate limit:** ~20 emails/second

**Gmail Workspace (Paid):**
- **Daily limit:** 2,000 emails/day
- **Per recipient:** No specific limit
- **Rate limit:** Higher

**For Production:**
Consider using:
- **SendGrid** (free tier: 100 emails/day)
- **Mailgun** (free tier: 5,000 emails/month)
- **Amazon SES** (very cheap, pay per email)
- **Postmark** (great deliverability)

---

## 🔄 Switching to Production Email Service

When ready for production, update settings:

### SendGrid Example:
```python
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'  # Literally the string 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
```

### Mailgun Example:
```python
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@your-domain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
```

---

## ✅ Verification Checklist

- [ ] 2-Step Verification enabled on Gmail
- [ ] App Password generated
- [ ] Environment variables set (`.env` or Docker)
- [ ] Test email sent successfully
- [ ] `.env` added to `.gitignore`
- [ ] Email limits configured
- [ ] Test notifications working

---

## 📚 Additional Resources

- [Gmail App Passwords Guide](https://support.google.com/accounts/answer/185833)
- [Django Email Documentation](https://docs.djangoproject.com/en/4.2/topics/email/)
- [Email Service Comparison](https://www.sendgrid.com/compare-email-services/)

---

**Last Updated:** December 2024  
**Status:** Ready for Gmail SMTP setup ✅

