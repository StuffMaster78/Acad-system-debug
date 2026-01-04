#!/bin/bash

# Setup script for log directories
# Creates log directories with proper permissions

set -e

LOG_DIR=${LOG_DIR:-/var/log/writing-system}

echo "📁 Setting up log directories..."

# Create log directory
if [ ! -d "$LOG_DIR" ]; then
    echo "   Creating log directory: $LOG_DIR"
    sudo mkdir -p "$LOG_DIR"
    
    # Set ownership to current user (or www-data in production)
    if [ "$EUID" -eq 0 ]; then
        # Running as root, use www-data
        chown -R www-data:www-data "$LOG_DIR"
        chmod -R 755 "$LOG_DIR"
        echo "   ✅ Log directory created with www-data ownership"
    else
        # Running as regular user, use current user
        sudo chown -R "$USER:$USER" "$LOG_DIR"
        sudo chmod -R 755 "$LOG_DIR"
        echo "   ✅ Log directory created with $USER ownership"
    fi
else
    echo "   ✅ Log directory already exists: $LOG_DIR"
fi

# Create subdirectories if needed
mkdir -p "$LOG_DIR"

echo ""
echo "📋 Log directory configuration:"
echo "   Location: $LOG_DIR"
echo "   Permissions: $(ls -ld "$LOG_DIR" | awk '{print $1, $3, $4}')"
echo ""
echo "💡 To customize log directory, set LOG_DIR environment variable:"
echo "   export LOG_DIR=/path/to/logs"
echo "   ./setup_logs.sh"

