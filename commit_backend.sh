#!/bin/bash

cd /Users/awwy/writing_system_backend

echo "=========================================="
echo "COMMITTING BACKEND CHANGES"
echo "=========================================="
echo ""

# Check if git repo
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Initializing..."
    git init
    git branch -M main
fi

# Check status
echo "▶ Checking git status..."
git status --short | head -20
echo ""

# Add all changes
echo "▶ Staging all changes..."
git add -A
STAGED=$(git diff --cached --name-only | wc -l | tr -d ' ')
echo "✅ Staged $STAGED files"
echo ""

# Commit
echo "▶ Committing changes..."
git commit -m "Backend: fix auth flow, CORS/CSRF for port 5175, integration tests, Celery beat cleanup, login session safety, and error improvements"
COMMIT_HASH=$(git rev-parse --short HEAD)
echo "✅ Committed: $COMMIT_HASH"
echo ""

# Check remotes
echo "▶ Checking remotes..."
git remote -v
echo ""

# Push to origin (stuffmaster)
if git remote get-url origin >/dev/null 2>&1; then
    echo "▶ Pushing to origin (stuffmaster)..."
    git push -u origin HEAD || echo "⚠️  Push to origin failed (may need authentication)"
else
    echo "⚠️  No 'origin' remote configured"
fi

# Push to public (awinooliyo)
if git remote get-url public >/dev/null 2>&1; then
    echo "▶ Pushing to public (awinooliyo)..."
    git push -u public HEAD || echo "⚠️  Push to public failed (may need authentication)"
else
    echo "⚠️  No 'public' remote configured"
fi

echo ""
echo "=========================================="
echo "✅ Commit complete!"
echo "=========================================="

