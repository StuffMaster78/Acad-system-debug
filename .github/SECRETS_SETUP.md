# GitHub Secrets Configuration Guide

**IMPORTANT**: Never commit secrets to code. Always use GitHub Secrets.

---

## 🔐 Required Secrets

### For Testing (CI/CD Pipeline)

These secrets are optional - the pipeline will use default test values if not set:

- `TEST_DB_USER` - Database user for CI tests (default: `ci_test_user`)
- `TEST_DB_PASSWORD` - Database password for CI tests (default: `ci_test_password`)
- `TEST_DB_NAME` - Database name for CI tests (default: `ci_test_db`)
- `TEST_SECRET_KEY` - Django secret key for CI tests (default: auto-generated)

### For Staging Deployment

- `STAGING_HOST` - Staging server hostname or IP
- `STAGING_USER` - SSH username for staging server
- `STAGING_SSH_KEY` - SSH private key for staging server
- `STAGING_DEPLOY_PATH` - Application directory path on staging server
- `STAGING_HEALTH_URL` - Health check URL (e.g., `https://staging.example.com`)

### For Production Deployment

- `PRODUCTION_HOST` - Production server hostname or IP
- `PRODUCTION_USER` - SSH username for production server
- `PRODUCTION_SSH_KEY` - SSH private key for production server
- `PRODUCTION_DEPLOY_PATH` - Application directory path on production server
- `PRODUCTION_HEALTH_URL` - Health check URL (e.g., `https://example.com`)

### Optional: Code Coverage

- `CODECOV_TOKEN` - Codecov upload token (if using Codecov)

---

## 📝 How to Add Secrets

1. Go to your GitHub repository
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Enter the secret name and value
5. Click **Add secret**

---

## 🔒 Security Best Practices

✅ **DO**:
- Use different secrets for staging and production
- Rotate secrets regularly
- Use strong, unique passwords
- Store SSH keys securely
- Limit who can access secrets

❌ **DON'T**:
- Commit secrets to code
- Share secrets in chat/email
- Use the same secrets everywhere
- Use weak passwords
- Leave secrets in plain text files

---

## 🧪 Testing Secrets

After adding secrets, test the deployment:

1. Go to **Actions** tab
2. Select the deployment workflow
3. Click **Run workflow**
4. Monitor the logs to verify secrets are working

---

## 🔄 Rotating Secrets

If a secret is compromised:

1. Generate a new secret value
2. Update the secret in GitHub
3. Update the secret on your servers
4. Test the deployment
5. Remove old secret values

---

**Remember**: Secrets are encrypted and only visible to authorized users with repository access.

