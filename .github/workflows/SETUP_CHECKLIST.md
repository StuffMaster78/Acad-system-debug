# DigitalOcean CI/CD Setup Checklist

Quick checklist to get your CI/CD pipeline running on DigitalOcean.

## ✅ Pre-Setup

- [ ] GitHub repository is ready
- [ ] DigitalOcean account is active
- [ ] DigitalOcean Droplet is created and accessible via SSH

## ✅ Step 1: DigitalOcean Container Registry

- [ ] Created Container Registry in DigitalOcean Console
- [ ] Noted registry name (e.g., `my-registry`)
- [ ] Generated API token with Read/Write permissions
- [ ] Saved API token securely

## ✅ Step 2: SSH Setup

- [ ] Generated SSH key pair: `ssh-keygen -t ed25519 -f ~/.ssh/do_deploy_key`
- [ ] Added public key to droplet: `cat ~/.ssh/do_deploy_key.pub >> ~/.ssh/authorized_keys`
- [ ] Tested SSH connection: `ssh -i ~/.ssh/do_deploy_key root@your-droplet-ip`
- [ ] Copied private key content (for GitHub Secrets)

## ✅ Step 3: GitHub Secrets

Go to: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

- [ ] `DO_REGISTRY_TOKEN` - DigitalOcean API token
- [ ] `DO_REGISTRY_NAME` - Your registry name (e.g., `my-registry`)
- [ ] `DO_DROPLET_HOST` - Droplet IP or hostname
- [ ] `DO_DROPLET_USER` - SSH username (usually `root`)
- [ ] `DO_DROPLET_SSH_KEY` - Private SSH key (full content)
- [ ] `DO_APP_PATH` - App path on droplet (e.g., `/opt/writing_system_backend`)
- [ ] `DO_DROPLET_PORT` - SSH port (optional, default: 22)

## ✅ Step 4: Droplet Preparation

SSH into your droplet and run:

- [ ] Created app directory: `mkdir -p /opt/writing_system_backend`
- [ ] Installed Docker: `curl -fsSL https://get.docker.com | sh`
- [ ] Installed Docker Compose: `apt-get install -y docker-compose-plugin`
- [ ] Cloned repository or uploaded files
- [ ] Created `.env` file with production settings
- [ ] Tested Docker login: `echo "TOKEN" | docker login registry.digitalocean.com -u TOKEN --password-stdin`
- [ ] Verified `docker-compose.prod.yml` exists

## ✅ Step 5: Test Deployment

- [ ] Pushed workflows to repository
- [ ] Went to GitHub Actions tab
- [ ] Selected "Deploy" workflow
- [ ] Clicked "Run workflow" → "Run workflow"
- [ ] Monitored deployment logs
- [ ] Verified services are running on droplet

## ✅ Step 6: Verify

On your droplet:

```bash
cd /opt/writing_system_backend
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs web
```

- [ ] All containers are running
- [ ] Application is accessible
- [ ] No errors in logs

## 🎉 Done!

Your CI/CD pipeline is now set up. Every push to `main`/`master` will automatically:
- Run tests
- Build Docker image
- Push to DigitalOcean Container Registry
- Deploy to your droplet

## 🔧 Troubleshooting

If something fails:

1. **Check GitHub Actions logs** - Look for error messages
2. **Verify secrets** - Ensure all secrets are set correctly
3. **Test SSH connection** - `ssh -i ~/.ssh/do_deploy_key root@your-droplet-ip`
4. **Check droplet logs** - `docker-compose -f docker-compose.prod.yml logs`
5. **Verify registry access** - Test Docker login manually

## 📚 Need Help?

See the full documentation in [README.md](./README.md)

