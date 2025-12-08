# Branching Strategy

## 🌳 Branch Structure

We follow **Git Flow** with some modifications for our development workflow.

### Main Branches

#### `main` (Production)
- **Purpose**: Production-ready code
- **Protection**: ✅ Protected
- **Merges**: Only from `develop` or `hotfix/*` branches
- **Deployment**: Automatic to production (when configured)
- **Tagging**: Semantic version tags (v1.0.0, v1.1.0, etc.)

#### `develop` (Development)
- **Purpose**: Integration branch for features
- **Protection**: ✅ Protected
- **Merges**: From `feature/*`, `bugfix/*` branches
- **Deployment**: Automatic to staging (when configured)
- **Status**: Always deployable

### Supporting Branches

#### `feature/*` (Feature Development)
- **Purpose**: New features and enhancements
- **Naming**: `feature/feature-name` or `feature/ticket-number-feature-name`
- **Source**: Branch from `develop`
- **Merge**: Back to `develop`
- **Examples**:
  - `feature/user-authentication`
  - `feature/123-order-tracking`
  - `feature/payment-integration`

#### `bugfix/*` (Bug Fixes)
- **Purpose**: Fix bugs in development
- **Naming**: `bugfix/bug-description` or `bugfix/ticket-number-description`
- **Source**: Branch from `develop`
- **Merge**: Back to `develop`
- **Examples**:
  - `bugfix/login-error`
  - `bugfix/456-payment-calculator`

#### `hotfix/*` (Production Fixes)
- **Purpose**: Critical fixes for production
- **Naming**: `hotfix/issue-description` or `hotfix/ticket-number-description`
- **Source**: Branch from `main`
- **Merge**: Back to `main` AND `develop`
- **Examples**:
  - `hotfix/security-patch`
  - `hotfix/789-critical-bug`

#### `release/*` (Release Preparation)
- **Purpose**: Prepare for a new release
- **Naming**: `release/v1.0.0` or `release/version-number`
- **Source**: Branch from `develop`
- **Merge**: Back to `main` (tagged) AND `develop`
- **Examples**:
  - `release/v1.2.0`
  - `release/v2.0.0`

## 🔄 Workflow

### Feature Development

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create feature branch
git checkout -b feature/my-new-feature

# 3. Develop and commit
git add .
git commit -m "feat: add new feature"

# 4. Push and create PR
git push origin feature/my-new-feature
# Create PR to develop on GitHub

# 5. After PR approval, merge to develop
# (Done via GitHub PR merge)
```

### Bug Fixes

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create bugfix branch
git checkout -b bugfix/fix-description

# 3. Fix and commit
git add .
git commit -m "fix: resolve issue description"

# 4. Push and create PR
git push origin bugfix/fix-description
# Create PR to develop on GitHub
```

### Hotfixes (Production)

```bash
# 1. Start from main
git checkout main
git pull origin main

# 2. Create hotfix branch
git checkout -b hotfix/critical-fix

# 3. Fix and commit
git add .
git commit -m "fix: critical production fix"

# 4. Push and create PRs
git push origin hotfix/critical-fix
# Create PR to main AND develop on GitHub
```

### Releases

```bash
# 1. Start from develop
git checkout develop
git pull origin develop

# 2. Create release branch
git checkout -b release/v1.2.0

# 3. Final testing and version bumping
# Update version numbers, CHANGELOG, etc.

# 4. Merge to main (with tag)
git checkout main
git merge release/v1.2.0
git tag -a v1.2.0 -m "Release version 1.2.0"
git push origin main --tags

# 5. Merge back to develop
git checkout develop
git merge release/v1.2.0
git push origin develop
```

## 📝 Commit Message Convention

We follow **Conventional Commits**:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Test additions/changes
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```
feat(orders): add order tracking feature

fix(auth): resolve login timeout issue

docs(api): update authentication documentation

refactor(payments): simplify payment processing logic
```

## 🛡️ Branch Protection Rules

### `main` Branch
- ✅ Require pull request reviews (2 approvals)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ Require conversation resolution
- ✅ No force pushes
- ✅ No deletions

### `develop` Branch
- ✅ Require pull request reviews (1 approval)
- ✅ Require status checks to pass
- ✅ Require branches to be up to date
- ✅ No force pushes
- ✅ No deletions

## 🔍 Branch Naming Guidelines

### Do ✅
- Use lowercase
- Use hyphens to separate words
- Be descriptive but concise
- Include ticket numbers if applicable
- Examples:
  - `feature/user-dashboard`
  - `bugfix/456-payment-error`
  - `hotfix/security-patch`

### Don't ❌
- Use spaces or underscores
- Use special characters
- Be too vague
- Use your name or initials
- Examples:
  - ❌ `feature/user dashboard`
  - ❌ `bugfix/fix`
  - ❌ `feature/johns-feature`

## 🚀 Quick Reference

| Action | Command |
|--------|---------|
| Create feature branch | `git checkout -b feature/name` |
| Create bugfix branch | `git checkout -b bugfix/name` |
| Create hotfix branch | `git checkout -b hotfix/name` |
| Update from develop | `git checkout develop && git pull` |
| Sync feature branch | `git checkout feature/name && git merge develop` |
| Delete local branch | `git branch -d branch-name` |
| Delete remote branch | `git push origin --delete branch-name` |

## 📚 Additional Resources

- [Git Flow Documentation](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitHub Flow](https://guides.github.com/introduction/flow/)

