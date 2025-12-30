#!/bin/bash
set -e

# Rhyzomic Intelligence Node (RIN) - Password Reset Tool
# Resets admin password for OpenWebUI or n8n

# --- Base Directory ---
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load shared utilities
# shellcheck source=/dev/null
. "$BASE_DIR/scripts/common.sh"

# Reset OpenWebUI password
reset_openwebui_password() {
    local email="$1"
    local password="$2"
    
    print_info "Resetting OpenWebUI password for: $email"
    
    # Check if OpenWebUI is running
    if ! docker ps | grep -q magi-cortex; then
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
    docker exec magi-cortex sqlite3 /app/backend/data/webui.db \
        "UPDATE user SET password='$safe_hash' WHERE email='$safe_email';" 2>/dev/null
    
    local affected_rows=$(docker exec magi-cortex sqlite3 /app/backend/data/webui.db \
        "SELECT changes();" 2>/dev/null)
    
    if [ "$affected_rows" = "0" ]; then
        print_error "User not found: $email"
        print_info "Available users:"
        docker exec magi-cortex sqlite3 /app/backend/data/webui.db \
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
    if ! docker ps | grep -q magi-reflex-automation; then
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
    docker exec magi-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
        "UPDATE user SET password='$safe_hash' WHERE email='$safe_email';" 2>/dev/null
    
    local affected_rows=$(docker exec magi-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
        "SELECT changes();" 2>/dev/null)
    
    if [ "$affected_rows" = "0" ]; then
        print_error "User not found: $email"
        print_info "Available users:"
        docker exec magi-reflex-automation sqlite3 /home/node/.n8n/database.sqlite \
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
        if [ -n "$MAGI_ADMIN_EMAIL" ]; then
            email="$MAGI_ADMIN_EMAIL"
            print_info "Using email from .env: $email"
        else
            read -p "Enter email address: " email
            # Trim whitespace from input
            email=$(echo "$email" | xargs)
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
    if grep -q "^MAGI_ADMIN_EMAIL=" "$BASE_DIR/.env" 2>/dev/null; then
        print_info "Updating credentials in .env..."
        if update_env_credentials "$email" "$password" "$BASE_DIR/.env"; then
            print_success "Credentials updated in .env"
        else
            print_warning "Failed to update credentials in .env"
        fi
    fi
    
    echo ""
    print_success "Password reset complete!"
    echo ""
    print_info "You can now log in with your new password."
}

# Execute main function
main "$@"
