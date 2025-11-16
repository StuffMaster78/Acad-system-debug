# GitHub Actions CI/CD Workflows

This directory contains GitHub Actions workflows for continuous integration and deployment to **DigitalOcean**.

## Workflows

### 1. CI Workflow (`ci.yml`)

Runs on every push and pull request to main/master/develop branches.

**What it does:**
- ✅ Runs tests with pytest and Django test suite
- ✅ Checks code quality with flake8
- ✅ Builds Docker image to verify it works
- ✅ Runs database migrations check
- ✅ Runs Django system checks

**Services:**
- PostgreSQL 15
- Redis (latest)

### 2. Deploy Workflow (`deploy.yml`)

Runs on pushes to main/master branches and tags starting with `v*`.

**What it does:**
- ✅ Builds Docker image
- ✅ Pushes to **DigitalOcean Container Registry (DOCR)**
- ✅ Also pushes to GitHub Container Registry (backup)
- ✅ Deploys to **DigitalOcean Droplet** via SSH
- ✅ Runs migrations and collects static files
- ✅ Performs health checks

## DigitalOcean Setup Instructions

### Step 1: Create DigitalOcean Container Registry

1. **Log in** to [DigitalOcean Console](https://cloud.digitalocean.com)
2. **Navigate** to Container Registry (left sidebar)
3. **Click** "Create Container Registry"
4. **Configure**:
   - **Name**: Choose a unique name (e.g., `your-org-registry`)
   - **Subscription Plan**: Choose a plan ($5/month for starter)
5. **Click** "Create Registry"
6. **Note** your registry name - you'll need it for secrets

### Step 2: Generate DigitalOcean API Token

1. **Go to** API → **Tokens/Keys** (left sidebar)
2. **Click** "Generate New Token"
3. **Name**: `github-actions-deploy`
4. **Scopes**: Select **Read** and **Write**
5. **Click** "Generate Token"
6. **Copy** the token immediately (shown only once!)

### Step 3: Set Up SSH Access to Droplet

1. **Generate SSH Key Pair** (if you don't have one):
   ```bash
   ssh-keygen -t ed25519 -C "github-actions-deploy" -f ~/.ssh/do_deploy_key
   ```

2. **Add Public Key to Droplet**:
   ```bash
   # Copy public key
   cat ~/.ssh/do_deploy_key.pub
   
   # On your droplet, add to authorized_keys
   ssh root@your-droplet-ip
   echo "your-public-key" >> ~/.ssh/authorized_keys
   ```

3. **Copy Private Key** for GitHub Secrets:
   ```bash
   cat ~/.ssh/do_deploy_key
   # Copy the entire output including -----BEGIN and -----END lines
   ```

### Step 4: Configure GitHub Secrets

1. **Go to** your GitHub repository
2. **Navigate** to: `Settings` → `Secrets and variables` → `Actions`
3. **Click** "New repository secret"
4. **Add the following secrets:**

#### Required Secrets:

| Secret Name | Description | Example |
|------------|-------------|---------|
| `DO_REGISTRY_TOKEN` | DigitalOcean API token (from Step 2) | `dop_v1_abc123...` |
| `DO_REGISTRY_NAME` | Your container registry name | `your-org-registry` |
| `DO_DROPLET_HOST` | Your droplet IP or hostname | `123.45.67.89` or `app.example.com` |
| `DO_DROPLET_USER` | SSH username (usually `root`) | `root` |
| `DO_DROPLET_SSH_KEY` | Private SSH key (from Step 3) | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `DO_APP_PATH` | Path to your app on droplet | `/opt/writing_system_backend` |

#### Optional Secrets:

| Secret Name | Description | Default |
|------------|-------------|---------|
| `DO_DROPLET_PORT` | SSH port | `22` |

### Step 5: Prepare Your Droplet

On your DigitalOcean Droplet, set up the application:

```bash
# SSH into your droplet
ssh root@your-droplet-ip

# Create application directory
mkdir -p /opt/writing_system_backend
cd /opt/writing_system_backend

# Clone your repository (or copy files)
git clone https://github.com/your-username/writing_system_backend.git .

# Or if you prefer to copy files manually:
# Upload docker-compose.prod.yml and .env file

# Install Docker and Docker Compose (if not already installed)
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt-get update
apt-get install -y docker-compose-plugin

# Create .env file with your production settings
nano .env
# Add all your environment variables (see PRODUCTION_DEPLOYMENT_GUIDE.md)

# Log in to DigitalOcean Container Registry
doctl registry login
# Or manually:
echo "YOUR_DO_REGISTRY_TOKEN" | docker login registry.digitalocean.com -u YOUR_DO_REGISTRY_TOKEN --password-stdin

# Update docker-compose.prod.yml to use DOCR images
# Edit docker-compose.prod.yml and update image references:
# image: registry.digitalocean.com/your-registry-name/writing-system-backend:latest
```

### Step 6: Update docker-compose.prod.yml (Optional)

If you want to use images from DOCR instead of building on the droplet, update your `docker-compose.prod.yml`:

```yaml
services:
  web:
    image: registry.digitalocean.com/your-registry-name/writing-system-backend:latest
    # Remove or comment out the build section
    # build:
    #   context: .
    #   dockerfile: Dockerfile
```

### Step 7: Test the Deployment

1. **Push to main/master branch** or use **workflow_dispatch**:
   - Go to `Actions` tab
   - Select "Deploy" workflow
   - Click "Run workflow"
   - Choose environment and click "Run workflow"

2. **Monitor the deployment**:
   - Watch the workflow logs in GitHub Actions
   - Check your droplet logs: `docker-compose -f docker-compose.prod.yml logs -f`

3. **Verify deployment**:
   ```bash
   ssh root@your-droplet-ip
   cd /opt/writing_system_backend
   docker-compose -f docker-compose.prod.yml ps
   ```

## Workflow Triggers

### CI Workflow
- **Triggers on**: Push to main/master/develop, Pull requests to main/master/develop

### Deploy Workflow
- **Triggers on**: 
  - Push to main/master branches
  - Tags starting with `v*` (e.g., `v1.0.0`)
  - Manual dispatch (via GitHub UI)

## Deployment Process

When you push to main/master, the workflow will:

1. ✅ **Build** Docker image
2. ✅ **Push** to DigitalOcean Container Registry
3. ✅ **SSH** into your droplet
4. ✅ **Pull** latest code (if using git)
5. ✅ **Pull** latest Docker images from DOCR
6. ✅ **Stop** existing containers
7. ✅ **Start** new containers
8. ✅ **Run** database migrations
9. ✅ **Collect** static files
10. ✅ **Verify** all services are running

## Troubleshooting

### Deployment fails with "Permission denied"
- **Solution**: Verify SSH key is correctly added to GitHub secrets
- Check that public key is in `~/.ssh/authorized_keys` on droplet
- Ensure SSH key has correct permissions: `chmod 600 ~/.ssh/authorized_keys`

### Docker login fails
- **Solution**: Verify `DO_REGISTRY_TOKEN` is correct
- Test login manually: `echo "TOKEN" | docker login registry.digitalocean.com -u TOKEN --password-stdin`

### Container registry not found
- **Solution**: Verify `DO_REGISTRY_NAME` matches your registry name exactly
- Check registry exists in DigitalOcean console

### Services not starting
- **Solution**: Check `.env` file is configured correctly on droplet
- Verify `docker-compose.prod.yml` is in the correct path
- Check logs: `docker-compose -f docker-compose.prod.yml logs`

### Migrations failing
- **Solution**: Ensure database is accessible from container
- Check database credentials in `.env` file
- Verify database container is running: `docker-compose -f docker-compose.prod.yml ps db`

## Security Best Practices

1. ✅ **Use SSH keys** instead of passwords
2. ✅ **Rotate tokens** periodically
3. ✅ **Limit SSH access** to specific IPs (use DigitalOcean Firewall)
4. ✅ **Use non-root user** for deployment (create a deploy user)
5. ✅ **Store secrets** only in GitHub Secrets (never commit)
6. ✅ **Enable 2FA** on your GitHub account
7. ✅ **Review workflow logs** regularly

## Cost Optimization

- **Container Registry**: $5/month for starter plan (includes 500MB storage)
- **Bandwidth**: First 500GB/month free, then $0.01/GB
- **Storage**: $0.10/GB/month after included storage

## Next Steps

1. ✅ Push workflows to repository
2. ✅ Set up DigitalOcean Container Registry
3. ✅ Configure GitHub Secrets
4. ✅ Prepare droplet
5. ✅ Test deployment with workflow_dispatch
6. ✅ Monitor first automatic deployment
7. ✅ Set up branch protection rules (recommended)
8. ✅ Configure monitoring and alerts

## Additional Resources

- [DigitalOcean Container Registry Docs](https://docs.digitalocean.com/products/container-registry/)
- [DigitalOcean API Tokens](https://docs.digitalocean.com/reference/api/create-personal-access-token/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Docker Compose Production Guide](./DOCKER_README.md)

