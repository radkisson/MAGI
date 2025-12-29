#!/bin/bash
# RIN Common Functions Library
# Shared utilities for setup and password management scripts

# --- Color Definitions ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Print Functions ---

print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}🔐 RIN - $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# --- Validation Functions ---

# Validate email format
# Note: Basic validation only. International domains and some edge cases not fully supported.
validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Validate password strength
# Requirements: minimum 8 characters
# Note: Only enforces minimum length. Consider adding complexity requirements for better security.
validate_password() {
    local password="$1"
    local length=${#password}
    
    if [ "$length" -lt 8 ]; then
        echo "Password must be at least 8 characters long"
        return 1
    fi
    
    return 0
}

# Generate bcrypt hash for password
# Reads password from stdin to prevent command injection
generate_bcrypt_hash() {
    python3 << 'PYSCRIPT'
import bcrypt
import sys

password = sys.stdin.read().strip()
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
PYSCRIPT
}

# Update .env file with credentials using Python for safe handling
# Arguments: email, password, env_file_path
update_env_credentials() {
    local email="$1"
    local password="$2"
    local env_file="$3"
    
    EMAIL="$email" PASSWORD="$password" ENV_FILE="$env_file" python3 << 'PYSCRIPT'
import sys
import re
import os

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
env_file = os.environ.get('ENV_FILE')

try:
    with open(env_file, 'r') as f:
        content = f.read()
    
    content = re.sub(r'^MAGI_ADMIN_EMAIL=.*$', f'MAGI_ADMIN_EMAIL={email}', content, flags=re.MULTILINE)
    content = re.sub(r'^MAGI_ADMIN_PASSWORD=.*$', f'MAGI_ADMIN_PASSWORD={password}', content, flags=re.MULTILINE)
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    sys.exit(0)
except Exception as e:
    print(f"Error updating .env: {e}", file=sys.stderr)
    sys.exit(1)
PYSCRIPT
}
