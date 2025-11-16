#!/bin/bash

# Script to commit changes to both private and public repositories
# Private: includes all files including sensitive .md files
# Public: excludes sensitive deployment/internal documentation

set -e

echo "📦 Preparing commits for private and public repositories..."

# Files to exclude from public repo (sensitive documentation)
SENSITIVE_MD_FILES=(
    "MULTI_DOMAIN_DEPLOYMENT_GUIDE.md"
    "PRODUCTION_DEPLOYMENT_GUIDE.md"
    "DEPLOYMENT_CHECKLIST.md"
    "DEPLOYMENT_READY.md"
    "DEPLOYMENT_READY_FINAL.md"
    "DEPLOYMENT_STATUS.md"
    "DEPLOYMENT_STATUS_FINAL.md"
    "DEPLOYMENT_COMPLETE.md"
    "DEPLOYMENT_ISSUES_FIXED.md"
    "GMAIL_SMTP_SETUP.md"
    "SSE_AND_GMAIL_SETUP.md"
    "QUICK_START_SSE_GMAIL.md"
    "DIGITALOCEAN_STORAGE_SETUP.md"
    "PRODUCTION_FILE_STORAGE.md"
    "TEST_USERS_AND_URLS.md"
    "test_users_info.md"
    "CREATE_SUPERUSER.md"
    "*.md"  # We'll handle this differently
)

# Step 1: Commit everything to private repo
echo ""
echo "🔒 Step 1: Committing to PRIVATE repository (all files)..."
echo ""

# Add all changes
git add -A

# Create commit message
COMMIT_MSG="Add multi-domain deployment support and fix WriterPerformanceSnapshot migration

- Add multi-domain deployment guide and configuration
- Add nginx config generation script for multiple client domains
- Add frontend environment configuration for separate dashboards
- Create migration for WriterPerformanceSnapshot model
- Update API client to support multiple domains
- Add website store for frontend branding
- Update deployment scripts for multi-domain setup"

# Commit to private
git commit -m "$COMMIT_MSG" || echo "⚠️  No changes to commit or already committed"

# Push to private
echo ""
echo "📤 Pushing to private repository..."
git push private main || git push private master

echo ""
echo "✅ Private repository updated!"

# Step 2: Commit to public repo (excluding sensitive files)
echo ""
echo "🌐 Step 2: Committing to PUBLIC repository (excluding sensitive docs)..."
echo ""

# Reset staging area
git reset HEAD

# Add all files except sensitive .md files
git add -A

# Unstage sensitive .md files
for file in "${SENSITIVE_MD_FILES[@]}"; do
    if [[ "$file" == "*.md" ]]; then
        # Unstage all .md files that match sensitive patterns
        git reset HEAD -- "MULTI_DOMAIN_DEPLOYMENT_GUIDE.md" 2>/dev/null || true
        git reset HEAD -- "PRODUCTION_DEPLOYMENT_GUIDE.md" 2>/dev/null || true
        git reset HEAD -- "DEPLOYMENT_*.md" 2>/dev/null || true
        git reset HEAD -- "*DEPLOYMENT*.md" 2>/dev/null || true
        git reset HEAD -- "*SMTP*.md" 2>/dev/null || true
        git reset HEAD -- "*STORAGE*.md" 2>/dev/null || true
        git reset HEAD -- "TEST_USERS*.md" 2>/dev/null || true
        git reset HEAD -- "test_users*.md" 2>/dev/null || true
    else
        git reset HEAD -- "$file" 2>/dev/null || true
    fi
done

# Check if there are staged changes
if git diff --cached --quiet; then
    echo "⚠️  No changes to commit to public repo (all changes are in sensitive files)"
else
    # Commit to public
    git commit -m "$COMMIT_MSG" || echo "⚠️  No changes to commit"
    
    # Push to public
    echo ""
    echo "📤 Pushing to public repository..."
    git push origin main || git push origin master
    
    echo ""
    echo "✅ Public repository updated!"
fi

echo ""
echo "🎉 Done! Both repositories updated."
echo ""
echo "📝 Note: Sensitive documentation files were excluded from public repo:"
for file in "${SENSITIVE_MD_FILES[@]}"; do
    if [[ "$file" != "*.md" ]]; then
        echo "   - $file"
    fi
done

