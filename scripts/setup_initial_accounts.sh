#!/bin/bash
set -e

# Rhyzomic Intelligence Node (RIN) - Initial Account Setup
# Creates initial admin accounts for OpenWebUI and n8n

# --- Base Directory ---
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Load shared utilities
# shellcheck source=/dev/null
. "$BASE_DIR/scripts/common.sh"

# Prompt for credentials with validation
# Note: All interactive output goes to stderr so only the result goes to stdout
prompt_credentials() {
    local service_name="$1"
    local email_var=""
    local password_var=""
    
    print_header "Initial Account Setup for $service_name" >&2
    echo "" >&2
    echo "RIN needs to create an initial admin account for $service_name." >&2
    echo "This account will have full administrative privileges." >&2
    echo "" >&2
    
    # Prompt for email
    while true; do
        read -p "Enter email address: " email_var </dev/tty
        # Trim whitespace from input
        email_var=$(echo "$email_var" | xargs)
        if validate_email "$email_var"; then
            break
        else
            print_error "Invalid email format. Please try again." >&2
        fi
    done
    
    # Prompt for password
    while true; do
        read -s -p "Enter password (min 8 characters): " password_var </dev/tty
        echo "" >&2
        
        if validate_password "$password_var"; then
            read -s -p "Confirm password: " password_confirm </dev/tty
            echo "" >&2
            
            if [ "$password_var" = "$password_confirm" ]; then
                break
            else
                print_error "Passwords do not match. Please try again." >&2
            fi
        else
            print_error "$(validate_password "$password_var" 2>&1 || true)" >&2
        fi
    done
    
    echo "$email_var|$password_var"
}

# Create OpenWebUI admin account
create_openwebui_account() {
    local email="$1"
    local password="$2"
    
    print_info "Creating OpenWebUI admin account..."
    
    # Wait for OpenWebUI to be ready
    local max_wait=60
    local waited=0
    while [ $waited -lt $max_wait ]; do
        if docker exec magi-cortex test -f /app/backend/data/webui.db 2>/dev/null; then
            break
        fi
        sleep 2
        waited=$((waited + 2))
    done
    
    if [ $waited -ge $max_wait ]; then
        print_error "Timeout waiting for OpenWebUI. Please try manual setup."
        return 1
    fi
    
    # Check if any users exist
    local user_count=$(docker exec magi-cortex sqlite3 /app/backend/data/webui.db "SELECT COUNT(*) FROM user;" 2>/dev/null || echo "0")
    
    if [ "$user_count" != "0" ]; then
        print_warning "OpenWebUI already has users. Skipping account creation."
        # Return 2 to indicate account already exists (idempotent success)
        return 2
    fi
    
    # Create account via API using Python for proper JSON escaping
    print_info "Creating account via API..."
    local response
    response=$(EMAIL="$email" PASSWORD="$password" PORT_WEBUI="${PORT_WEBUI:-3000}" python3 << 'PYSCRIPT'
import json
import os
import sys
import urllib.request
import urllib.error

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
port = os.environ.get('PORT_WEBUI', '3000')

data = {
    "email": email,
    "password": password,
    "name": "Admin"
}

try:
    req = urllib.request.Request(
        f"http://localhost:{port}/api/v1/auths/signup",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        print(response.read().decode('utf-8'))
        sys.exit(0)
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
PYSCRIPT
)
    local python_exit_code=$?
    
    if [ "$python_exit_code" -ne 0 ]; then
        print_error "Failed to create OpenWebUI account: API call failed"
        print_info "Response: $response"
        print_info "You can create it manually at: http://localhost:${PORT_WEBUI:-3000}"
        return 1
    elif echo "$response" | grep -q '"email"'; then
        print_success "OpenWebUI admin account created successfully"
        print_info "Email: $email"
        return 0
    else
        print_error "Failed to create OpenWebUI account: Unexpected response"
        print_info "You can create it manually at: http://localhost:${PORT_WEBUI:-3000}"
        return 1
    fi
}

# Create n8n owner account
create_n8n_account() {
    local email="$1"
    local password="$2"
    local first_name="${3:-Admin}"
    local last_name="${4:-User}"
    
    print_info "Creating n8n owner account..."
    
    # Wait for n8n to be ready
    local max_wait=60
    local waited=0
    while [ $waited -lt $max_wait ]; do
        if curl -s -f "http://localhost:${PORT_N8N:-5678}/healthz" >/dev/null 2>&1; then
            break
        fi
        sleep 2
        waited=$((waited + 2))
    done
    
    if [ $waited -ge $max_wait ]; then
        print_error "Timeout waiting for n8n. Please try manual setup."
        return 1
    fi
    
    # Check if owner exists
    local response=$(curl -s "http://localhost:${PORT_N8N:-5678}/rest/owner" 2>/dev/null)
    
    if echo "$response" | grep -q "email"; then
        print_warning "n8n already has an owner account. Skipping account creation."
        # Return 2 to indicate account already exists (idempotent success)
        return 2
    fi
    
    # Create owner account via API using Python for proper JSON escaping
    print_info "Creating account via API..."
    response=$(EMAIL="$email" PASSWORD="$password" FIRST_NAME="$first_name" LAST_NAME="$last_name" PORT_N8N="${PORT_N8N:-5678}" python3 << 'PYSCRIPT'
import json
import os
import sys
import urllib.request
import urllib.error

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
first_name = os.environ.get('FIRST_NAME')
last_name = os.environ.get('LAST_NAME')
port = os.environ.get('PORT_N8N', '5678')

data = {
    "email": email,
    "password": password,
    "firstName": first_name,
    "lastName": last_name
}

try:
    req = urllib.request.Request(
        f"http://localhost:{port}/rest/owner",
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        print(response.read().decode('utf-8'))
        sys.exit(0)
except Exception as e:
    print(json.dumps({"error": str(e)}))
    sys.exit(1)
PYSCRIPT
)
    local python_exit_code=$?
    
    if [ "$python_exit_code" -ne 0 ]; then
        print_error "Failed to create n8n account: API call failed"
        print_info "Response: $response"
        print_info "You can create it manually at: http://localhost:${PORT_N8N:-5678}"
        return 1
    elif echo "$response" | grep -q '"email"'; then
        print_success "n8n owner account created successfully"
        print_info "Email: $email"
        return 0
    else
        print_error "Failed to create n8n account: Unexpected response"
        print_info "You can create it manually at: http://localhost:${PORT_N8N:-5678}"
        return 1
    fi
}

# Store credentials securely in .env
store_credentials() {
    local email="$1"
    local password="$2"
    
    # Check if .env exists
    if [ ! -f "$BASE_DIR/.env" ]; then
        print_error ".env file not found"
        return 1
    fi
    
    # Add or update credentials section
    if ! grep -q "# --- INITIAL ADMIN CREDENTIALS ---" "$BASE_DIR/.env"; then
        cat <<'EOF' >> "$BASE_DIR/.env"

# --- INITIAL ADMIN CREDENTIALS ---
# These are used for initial account setup
# Change these if you want to reset passwords
# WARNING: These are stored in plaintext. Change passwords after first login!
MAGI_ADMIN_EMAIL=PLACEHOLDER_EMAIL
MAGI_ADMIN_PASSWORD=PLACEHOLDER_PASSWORD
EOF
        # Now replace placeholders safely using Python
        EMAIL="$email" PASSWORD="$password" ENV_FILE="$BASE_DIR/.env" python3 << 'PYSCRIPT'
import sys
import os

email = os.environ.get('EMAIL')
password = os.environ.get('PASSWORD')
env_file = os.environ.get('ENV_FILE')

try:
    with open(env_file, 'r') as f:
        content = f.read()
    
    content = content.replace('PLACEHOLDER_EMAIL', email)
    content = content.replace('PLACEHOLDER_PASSWORD', password)
    
    with open(env_file, 'w') as f:
        f.write(content)
    
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
PYSCRIPT
        if [ $? -eq 0 ]; then
            print_success "Credentials stored in .env"
        else
            print_error "Failed to store credentials in .env"
            return 1
        fi
    else
        # Update existing credentials using shared function
        if update_env_credentials "$email" "$password" "$BASE_DIR/.env"; then
            print_success "Credentials updated in .env"
        else
            print_error "Failed to update credentials in .env"
            return 1
        fi
    fi
}

# Main function
main() {
    # Load port configuration
    if [ -f "$BASE_DIR/.env" ]; then
        while IFS='=' read -r key value; do
            [[ -z "$key" || "$key" =~ ^[[:space:]]*# ]] && continue
            if [[ "$key" =~ ^PORT_ ]]; then
                export "$key=$value"
            fi
        done < <(grep -E '^PORT_' "$BASE_DIR/.env" 2>/dev/null || true)
    fi
    
    PORT_WEBUI=${PORT_WEBUI:-3000}
    PORT_N8N=${PORT_N8N:-5678}
    
    # Check if running in non-interactive mode
    if [ ! -t 0 ]; then
        print_warning "Non-interactive mode detected. Skipping initial account setup."
        print_info "You can set up accounts manually:"
        print_info "  OpenWebUI: http://localhost:${PORT_WEBUI}"
        print_info "  n8n:       http://localhost:${PORT_N8N}"
        exit 0
    fi
    
    # Check if credentials are already in .env
    if grep -q "^MAGI_ADMIN_EMAIL=" "$BASE_DIR/.env" 2>/dev/null; then
        local existing_email=$(grep "^MAGI_ADMIN_EMAIL=" "$BASE_DIR/.env" | cut -d '=' -f2)
        local existing_password=$(grep "^MAGI_ADMIN_PASSWORD=" "$BASE_DIR/.env" | cut -d '=' -f2)
        
        if [ -n "$existing_email" ] && [ -n "$existing_password" ]; then
            print_info "Found existing admin credentials in .env"
            read -p "Use existing credentials? (y/n) [y]: " use_existing
            use_existing=${use_existing:-y}
            
            if [[ "$use_existing" =~ ^[Yy]$ ]]; then
                email="$existing_email"
                password="$existing_password"
                
                # Try to create accounts with existing credentials
                local openwebui_result=0
                local n8n_result=0
                
                create_openwebui_account "$email" "$password"
                openwebui_result=$?
                
                create_n8n_account "$email" "$password"
                n8n_result=$?
                
                echo ""
                if [ $openwebui_result -eq 0 ] || [ $openwebui_result -eq 2 ]; then
                    if [ $n8n_result -eq 0 ] || [ $n8n_result -eq 2 ]; then
                        print_success "Account setup complete!"
                    fi
                fi
                
                echo ""
                echo "Access your services:"
                echo "  🧠 OpenWebUI: http://localhost:${PORT_WEBUI}"
                echo "  🔄 n8n:       http://localhost:${PORT_N8N}"
                echo ""
                echo "Email:    $email"
                echo "Password: (stored in .env)"
                return 0
            fi
        fi
    fi
    
    # Prompt for new credentials
    credentials=$(prompt_credentials "OpenWebUI and n8n")
    email=$(echo "$credentials" | cut -d '|' -f1)
    password=$(echo "$credentials" | cut -d '|' -f2)
    
    echo ""
    print_info "Setting up accounts with provided credentials..."
    echo ""
    
    # Store credentials first (only if accounts need to be created)
    store_credentials "$email" "$password"
    
    # Create accounts
    local openwebui_result=0
    local n8n_result=0
    
    create_openwebui_account "$email" "$password"
    openwebui_result=$?
    
    create_n8n_account "$email" "$password"
    n8n_result=$?
    
    echo ""
    if [ $openwebui_result -eq 0 ] || [ $openwebui_result -eq 2 ]; then
        if [ $n8n_result -eq 0 ] || [ $n8n_result -eq 2 ]; then
            print_success "Account setup complete!"
        fi
    fi
    
    echo ""
    echo "Access your services:"
    echo "  🧠 OpenWebUI: http://localhost:${PORT_WEBUI}"
    echo "  🔄 n8n:       http://localhost:${PORT_N8N}"
    echo ""
    echo "Email:    $email"
    echo "Password: (stored in .env)"
    echo ""
    print_warning "IMPORTANT: Change your passwords after first login!"
    echo "Use: ./rin reset-password <service>"
}

# Execute main function
main "$@"
