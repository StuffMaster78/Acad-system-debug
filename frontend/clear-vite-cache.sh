#!/bin/bash
# Clear Vite cache and force rebuild

echo "🧹 Clearing Vite caches..."

# Kill any running Vite processes
pkill -f "vite" 2>/dev/null || true
sleep 1

# Remove all Vite cache directories
rm -rf node_modules/.vite
rm -rf .vite
rm -rf dist
find . -type d -name ".vite" -exec rm -rf {} + 2>/dev/null || true

# Clear browser cache hint
echo ""
echo "✅ Vite caches cleared!"
echo ""
echo "📋 Next steps:"
echo "1. Restart your dev server: npm run dev (or pnpm dev)"
echo "2. Hard refresh your browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)"
echo "3. If issues persist, try incognito/private mode"
echo ""

