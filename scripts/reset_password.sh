#!/bin/bash
set -e

# Rhyzomic Intelligence Node (RIN) - Password Reset Tool
# Resets admin password for OpenWebUI or n8n

# --- Color Definitions ---
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# --- Base Directory ---
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

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

# Validate email format
validate_email() {
    local email="$1"
    if [[ "$email" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
        return 0
    else
        return 1
    fi
}

# Validate password strength
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
# Reads password from stdin to avoid command injection
generate_bcrypt_hash() {
    # Use Python with stdin to avoid command injection
    python3 << 'PYSCRIPT'
import bcrypt
import sys

password = sys.stdin.read().strip()
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode('utf-8'))
PYSCRIPT
}

# Reset OpenWebUI password
reset_openwebui_password() {
    local email="$1"
    local password="$2"
    
    print_info "Resetting OpenWebUI password for: $email"
    
    # Check if OpenWebUI is running
    if ! docker ps | grep -q rin-cortex; then
        print_error "OpenWebUI container is not running"
        print_info "Start RIN first: ./rin start"
        return 1
    fi
    
    # Generate password hash
    print_info "Generating password hash..."
    local password_hash=$(echo -n "$password" | generate_bcrypt_hash)
    
    if [ -z "$password_hash" ]; then
        print_error "Failed to generate password hash"
        return 1
    fi
    
    # Escape single quotes in email and hash for SQL safety
    local safe_email=$(echo "$email" | sed "s/'/''/g")
    local safe_hash=$(echo "$password_hash" | sed "s/'/''/g")
    
    # Update password in database
    print_info "Updating password in database..."
    docker exec rin-cortex sqlite3 /app/backend/data/webui.db \
        "UPDATE user SET password='$safe_hash' WHERE email='$safe_email';" 2>/dev/null
    
    local affected_rows=$(docker exec rin-cortex sqlite3 /app/backend/data/webui.db \
        "SELECT changes();" 2>/dev/null)
    
    if [ "$affected_rows" = "0" ]; then
        print_error "User not found: $email"
        print_info "Available users:"
        docker exec rin-cortex sqlite3 /app/backend/data/webui.db \
            "SELECT email FROM user;" 2>/dev/null | sed 's/^/  /'
        return 1
    fi
    
    print_success "OpenWebUI password reset successfully"
    return 0
}

# Reset n8n password
reset_n8n_password() {
    local email="$1"
    local password="$2"
    
    print_info "Resetting n8n password for: $email"
    
    # Check if n8n is running
    if ! docker ps | grep -q rin-reflex-automation; then
        print_error "n8n container is not running"
        print_info "Start RIN first: ./rin start"
        return 1
    fi
    
    # Generate password hash
    print_info "Generating password hash..."
    local password_hash=$(echo -n "$password" | generate_bcrypt_hash)
    
    if [ -z "$password_hash" ]; then
        print_error "Failed to generate password hash"
        return 1
    fi
    
    # Escape single quotes in email and hash for SQL safety
    local safe_email=$(echo "$email" | sed "s/'/''/g")
    local safe_hash=$(echo "$password_hash" | sed "s/'/''/g")
    
    # Update password in database
    print_info "Updating password in database..."
    docker exec rin-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
        "UPDATE user SET password='$safe_hash' WHERE email='$safe_email';" 2>/dev/null
    
    local affected_rows=$(docker exec rin-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
        "SELECT changes();" 2>/dev/null)
    
    if [ "$affected_rows" = "0" ]; then
        print_error "User not found: $email"
        print_info "Available users:"
        docker exec rin-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
            "SELECT email FROM user;" 2>/dev/null | sed 's/^/  /'
        return 1
    fi
    
    print_success "n8n password reset successfully"
    return 0
}

# Show usage
show_usage() {
    cat <<EOF
RIN Password Reset Tool

USAGE:
    ./rin reset-password <service> [email]

SERVICES:
    openwebui    - Reset OpenWebUI admin password
    n8n          - Reset n8n owner password
    all          - Reset password for both services

EXAMPLES:
    ./rin reset-password openwebui
    ./rin reset-password n8n admin@example.com
    ./rin reset-password all

If email is not provided, the script will use the email from .env file
or prompt you to enter it.
EOF
}

# Main function
main() {
    local service="${1:-}"
    local email="${2:-}"
    
    # Load port configuration
    if [ -f "$BASE_DIR/.env" ]; then
        while IFS='=' read -r key value; do
            [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
            if [[ "$key" =~ ^(PORT_|RIN_ADMIN_) ]]; then
                export "$key=$value"
            fi
        done < <(grep -E '^(PORT_|RIN_ADMIN_)' "$BASE_DIR/.env" 2>/dev/null || true)
    fi
    
    PORT_WEBUI=${PORT_WEBUI:-3000}
    PORT_N8N=${PORT_N8N:-5678}
    
    # Validate service parameter
    if [ -z "$service" ]; then
        print_error "Service not specified"
        echo ""
        show_usage
        exit 1
    fi
    
    if [[ ! "$service" =~ ^(openwebui|n8n|all)$ ]]; then
        print_error "Invalid service: $service"
        echo ""
        show_usage
        exit 1
    fi
    
    # Get email
    if [ -z "$email" ]; then
        if [ -n "$RIN_ADMIN_EMAIL" ]; then
            email="$RIN_ADMIN_EMAIL"
            print_info "Using email from .env: $email"
        else
            read -p "Enter email address: " email
        fi
    fi
    
    # Validate email
    if ! validate_email "$email"; then
        print_error "Invalid email format"
        exit 1
    fi
    
    # Get new password
    print_header "Password Reset for $service"
    echo ""
    
    while true; do
        read -s -p "Enter new password (min 8 characters): " password
        echo ""
        
        validation_error=$(validate_password "$password")
        if [ $? -eq 0 ]; then
            read -s -p "Confirm new password: " password_confirm
            echo ""
            
            if [ "$password" = "$password_confirm" ]; then
                break
            else
                print_error "Passwords do not match. Please try again."
            fi
        else
            print_error "$validation_error"
        fi
    done
    
    echo ""
    
    # Reset password(s)
    case "$service" in
        openwebui)
            reset_openwebui_password "$email" "$password"
            ;;
        n8n)
            reset_n8n_password "$email" "$password"
            ;;
        all)
            reset_openwebui_password "$email" "$password"
            echo ""
            reset_n8n_password "$email" "$password"
            ;;
    esac
    
    # Update .env if needed
    if grep -q "^RIN_ADMIN_EMAIL=" "$BASE_DIR/.env" 2>/dev/null; then
        print_info "Updating credentials in .env..."
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^RIN_ADMIN_EMAIL=.*|RIN_ADMIN_EMAIL=${email}|" "$BASE_DIR/.env"
            sed -i '' "s|^RIN_ADMIN_PASSWORD=.*|RIN_ADMIN_PASSWORD=${password}|" "$BASE_DIR/.env"
        else
            sed -i "s|^RIN_ADMIN_EMAIL=.*|RIN_ADMIN_EMAIL=${email}|" "$BASE_DIR/.env"
            sed -i "s|^RIN_ADMIN_PASSWORD=.*|RIN_ADMIN_PASSWORD=${password}|" "$BASE_DIR/.env"
        fi
    fi
    
    echo ""
    print_success "Password reset complete!"
    echo ""
    print_info "You can now log in with your new password."
}

# Execute main function
main "$@"
