#!/bin/bash
# Script to check and apply missing migrations

echo "=========================================="
echo "Migration Check and Apply Script"
echo "=========================================="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ] || [ -n "$DOCKER_CONTAINER" ]; then
    echo "⚠️  Running inside Docker container"
    echo ""
    echo "To apply migrations from outside Docker, run:"
    echo "  docker-compose exec web python manage.py migrate"
    echo "  OR"
    echo "  docker exec -it <container_name> python manage.py migrate"
    echo ""
    exit 0
fi

echo "Checking migration status..."
python3 manage.py showmigrations orders communications 2>&1 | tail -15

echo ""
echo "Applying migrations..."
echo ""

# Apply orders migration
echo "1. Applying orders migrations..."
python3 manage.py migrate orders --verbosity 2

# Apply communications migration
echo ""
echo "2. Applying communications migrations..."
python3 manage.py migrate communications --verbosity 2

echo ""
echo "3. Verifying migrations applied..."
python3 manage.py showmigrations orders communications 2>&1 | tail -10

echo ""
echo "=========================================="
echo "✅ Migration script completed!"
echo "=========================================="

