# CI/CD Setup Guide

## 🎯 Overview

This guide explains the CI/CD infrastructure set up for the Writing System Platform, including GitHub Actions workflows, branch protection, and deployment preparation.

## 📦 What's Included

### 1. GitHub Actions Workflows

#### CI Pipeline (`.github/workflows/ci.yml`)
- **Triggers**: Push to main/develop/feature branches, PRs
- **Jobs**:
  - Backend linting (Black, isort, Flake8, Pylint)
  - Backend tests (pytest with coverage)
  - Frontend linting (ESLint, formatting)
  - Frontend tests (Vitest with coverage)
  - Build verification
  - Security scanning (Trivy)
  - CI summary

#### PR Checks (`.github/workflows/pr-checks.yml`)
- **Triggers**: PR opened/updated
- **Jobs**:
  - PR validation (semantic PR titles)
  - Merge conflict detection
  - File size checks
  - Code review checklist (TODO/FIXME, console.log, secrets)
  - Dependency security checks

#### Deployment Workflows
- **Staging** (`.github/workflows/deploy-staging.yml`): Prepared for develop branch
- **Production** (`.github/workflows/deploy-production.yml`): Prepared for version tags

### 2. Branch Protection Rules

#### `main` Branch
- ✅ Require 2 PR approvals
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ✅ No force pushes
- ✅ No deletions

#### `develop` Branch
- ✅ Require 1 PR approval
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ No force pushes
- ✅ No deletions

### 3. Documentation

- **Branching Strategy** (`BRANCHING_STRATEGY.md`): Git Flow workflow
- **Development Workflow** (`DEVELOPMENT_WORKFLOW.md`): Daily development guide
- **PR Template** (`.github/PULL_REQUEST_TEMPLATE.md`): Standardized PR format
- **Issue Templates**: Bug reports and feature requests

## 🚀 Setup Instructions

### 1. Enable GitHub Actions

1. Go to repository **Settings** → **Actions** → **General**
2. Enable **"Allow all actions and reusable workflows"**
3. Save changes

### 2. Configure Branch Protection

#### For `main` Branch:

1. Go to **Settings** → **Branches**
2. Click **"Add rule"** or edit existing rule for `main`
3. Configure:
   - ✅ Require a pull request before merging
     - Require approvals: **2**
     - Dismiss stale pull request approvals when new commits are pushed
   - ✅ Require status checks to pass before merging
     - Require branches to be up to date before merging
     - Status checks: Select all CI checks
   - ✅ Require conversation resolution before merging
   - ✅ Do not allow bypassing the above settings
   - ✅ Restrict who can push to matching branches: Admins only
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

#### For `develop` Branch:

1. Add/edit rule for `develop`
2. Configure:
   - ✅ Require a pull request before merging
     - Require approvals: **1**
   - ✅ Require status checks to pass before merging
     - Require branches to be up to date before merging
     - Status checks: Select all CI checks
   - ✅ Do not allow force pushes
   - ✅ Do not allow deletions

### 3. Configure Secrets (Optional)

For future deployment, you may need to add secrets:

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Add secrets as needed:
   - `DEPLOY_KEY`: SSH key for deployment
   - `DOCKER_REGISTRY_TOKEN`: Container registry token
   - `PRODUCTION_API_KEY`: Production API key
   - etc.

### 4. Set Up Codecov (Optional)

For coverage reporting:

1. Sign up at [codecov.io](https://codecov.io)
2. Connect your GitHub repository
3. Get the upload token
4. Add as secret: `CODECOV_TOKEN`

## 🔍 Workflow Details

### CI Pipeline Flow

```
Push/PR → Backend Lint → Backend Test → Frontend Lint → Frontend Test → Build → Security Scan → Summary
```

### PR Check Flow

```
PR Created → Validation → Review Checklist → Dependency Check → Ready for Review
```

## 📊 Status Checks

The following status checks are configured:

### Required Checks (for branch protection)

- ✅ `backend-lint` - Backend code quality
- ✅ `backend-test` - Backend tests
- ✅ `frontend-lint` - Frontend code quality
- ✅ `frontend-test` - Frontend tests
- ✅ `build-verification` - Build success
- ✅ `pr-validation` - PR validation

### Optional Checks

- ⚠️ `security-scan` - Security vulnerability scanning
- ⚠️ `review-checklist` - Code review reminders
- ⚠️ `dependency-check` - Dependency security

## 🛠️ Customization

### Adjusting Linting Rules

**Backend** (`backend/.flake8`, `backend/pyproject.toml`):
```ini
[flake8]
max-line-length = 127
exclude = migrations,venv,node_modules

[tool.black]
line-length = 127
```

**Frontend** (`frontend/.eslintrc.js`, `frontend/.prettierrc`):
```javascript
// Customize ESLint and Prettier rules
```

### Adjusting Test Coverage

**Backend** (`backend/pytest.ini`):
```ini
[pytest]
addopts = --cov=. --cov-fail-under=70
```

**Frontend** (`frontend/vitest.config.js`):
```javascript
coverage: {
  thresholds: {
    lines: 70,
    functions: 70,
    branches: 70,
    statements: 70
  }
}
```

### Adding New Checks

1. Create new job in `.github/workflows/ci.yml`
2. Add to required status checks in branch protection
3. Update documentation

## 🚢 Deployment Preparation

### When Ready to Deploy

1. **Uncomment deployment workflows**
   - Edit `.github/workflows/deploy-staging.yml`
   - Edit `.github/workflows/deploy-production.yml`
   - Set `if: false` to `if: true` or remove condition

2. **Configure deployment steps**
   - Add Docker build steps
   - Add container registry push
   - Add deployment commands
   - Add smoke tests
   - Add rollback procedures

3. **Set up environments**
   - Go to **Settings** → **Environments**
   - Create `staging` and `production` environments
   - Configure environment secrets
   - Set deployment protection rules

4. **Test deployment**
   - Test staging deployment first
   - Verify all steps work
   - Test rollback procedure
   - Document deployment process

## 📝 Best Practices

### For Developers

1. **Always run checks locally before pushing**
   ```bash
   # Backend
   black . && isort . && flake8 . && pytest
   
   # Frontend
   npm run lint && npm test && npm run build
   ```

2. **Keep PRs focused and small**
   - One feature/fix per PR
   - Easier to review
   - Faster CI runs

3. **Write meaningful commit messages**
   - Follow conventional commits
   - Reference issues/tickets

4. **Address CI failures promptly**
   - Don't merge with failing checks
   - Fix issues before requesting review

### For Reviewers

1. **Review code quality**
   - Check style and formatting
   - Verify test coverage
   - Look for security issues

2. **Test locally if needed**
   - Checkout PR branch
   - Run tests
   - Verify functionality

3. **Provide constructive feedback**
   - Be specific
   - Suggest improvements
   - Approve when ready

## 🐛 Troubleshooting

### CI Failing Locally but Passing in GitHub

- Check environment differences
- Verify all dependencies are in requirements/package.json
- Check for environment-specific issues

### Tests Failing in CI

- Check service dependencies (PostgreSQL, Redis)
- Verify test data setup
- Check for timing issues

### Linting Failing

- Run formatters locally: `black .` and `npm run format`
- Fix linting errors
- Commit formatted code

### Coverage Too Low

- Add more tests
- Adjust coverage thresholds (temporarily)
- Focus on critical paths first

## 📚 Related Documentation

- [Branching Strategy](./BRANCHING_STRATEGY.md)
- [Development Workflow](./DEVELOPMENT_WORKFLOW.md)
- [Testing Guide](./TESTING_GUIDE.md)

## ✅ Checklist

- [x] GitHub Actions workflows created
- [x] Branch protection rules documented
- [x] PR template created
- [x] Issue templates created
- [x] Development workflow documented
- [x] Branching strategy documented
- [ ] Branch protection rules configured (manual step)
- [ ] Codecov configured (optional)
- [ ] Deployment workflows ready (when needed)

## 🎉 Status

**CI/CD Infrastructure**: ✅ **COMPLETE**

All workflows, templates, and documentation are in place. Configure branch protection and enable GitHub Actions to start using the CI/CD pipeline.

