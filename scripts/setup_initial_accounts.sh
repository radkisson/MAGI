#!/bin/bash
set -e

# Rhyzomic Intelligence Node (RIN) - Initial Account Setup
# Creates initial admin accounts for OpenWebUI and n8n

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
# Requirements: minimum 8 characters
validate_password() {
    local password="$1"
    local length=${#password}
    
    if [ "$length" -lt 8 ]; then
        echo "Password must be at least 8 characters long"
        return 1
    fi
    
    return 0
}

# Prompt for credentials with validation
prompt_credentials() {
    local service_name="$1"
    local email_var=""
    local password_var=""
    
    print_header "Initial Account Setup for $service_name"
    echo ""
    echo "RIN needs to create an initial admin account for $service_name."
    echo "This account will have full administrative privileges."
    echo ""
    
    # Prompt for email
    while true; do
        read -p "Enter email address: " email_var
        if validate_email "$email_var"; then
            break
        else
            print_error "Invalid email format. Please try again."
        fi
    done
    
    # Prompt for password
    while true; do
        read -s -p "Enter password (min 8 characters): " password_var
        echo ""
        
        validation_error=$(validate_password "$password_var")
        if [ $? -eq 0 ]; then
            read -s -p "Confirm password: " password_confirm
            echo ""
            
            if [ "$password_var" = "$password_confirm" ]; then
                break
            else
                print_error "Passwords do not match. Please try again."
            fi
        else
            print_error "$validation_error"
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
        if docker exec rin-cortex test -f /app/backend/data/webui.db 2>/dev/null; then
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
    local user_count=$(docker exec rin-cortex sqlite3 /app/backend/data/webui.db "SELECT COUNT(*) FROM user;" 2>/dev/null || echo "0")
    
    if [ "$user_count" != "0" ]; then
        print_warning "OpenWebUI already has users. Skipping account creation."
        return 0
    fi
    
    # Create account via API
    local response=$(curl -s -X POST "http://localhost:${PORT_WEBUI:-3000}/api/v1/auths/signup" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"password\":\"$password\",\"name\":\"Admin\"}" 2>/dev/null)
    
    if echo "$response" | grep -q "email"; then
        print_success "OpenWebUI admin account created successfully"
        print_info "Email: $email"
        return 0
    else
        print_error "Failed to create OpenWebUI account"
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
        return 0
    fi
    
    # Create owner account via API
    response=$(curl -s -X POST "http://localhost:${PORT_N8N:-5678}/rest/owner" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$email\",\"password\":\"$password\",\"firstName\":\"$first_name\",\"lastName\":\"$last_name\"}" 2>/dev/null)
    
    if echo "$response" | grep -q "email"; then
        print_success "n8n owner account created successfully"
        print_info "Email: $email"
        return 0
    else
        print_error "Failed to create n8n account"
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
        cat <<EOF >> "$BASE_DIR/.env"

# --- INITIAL ADMIN CREDENTIALS ---
# These are used for initial account setup
# Change these if you want to reset passwords
RIN_ADMIN_EMAIL=${email}
RIN_ADMIN_PASSWORD=${password}
EOF
        print_success "Credentials stored in .env"
    else
        # Update existing credentials
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s|^RIN_ADMIN_EMAIL=.*|RIN_ADMIN_EMAIL=${email}|" "$BASE_DIR/.env"
            sed -i '' "s|^RIN_ADMIN_PASSWORD=.*|RIN_ADMIN_PASSWORD=${password}|" "$BASE_DIR/.env"
        else
            sed -i "s|^RIN_ADMIN_EMAIL=.*|RIN_ADMIN_EMAIL=${email}|" "$BASE_DIR/.env"
            sed -i "s|^RIN_ADMIN_PASSWORD=.*|RIN_ADMIN_PASSWORD=${password}|" "$BASE_DIR/.env"
        fi
        print_success "Credentials updated in .env"
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
    if grep -q "^RIN_ADMIN_EMAIL=" "$BASE_DIR/.env" 2>/dev/null; then
        local existing_email=$(grep "^RIN_ADMIN_EMAIL=" "$BASE_DIR/.env" | cut -d '=' -f2)
        local existing_password=$(grep "^RIN_ADMIN_PASSWORD=" "$BASE_DIR/.env" | cut -d '=' -f2)
        
        if [ -n "$existing_email" ] && [ -n "$existing_password" ]; then
            print_info "Found existing admin credentials in .env"
            read -p "Use existing credentials? (y/n) [y]: " use_existing
            use_existing=${use_existing:-y}
            
            if [[ "$use_existing" =~ ^[Yy]$ ]]; then
                create_openwebui_account "$existing_email" "$existing_password"
                create_n8n_account "$existing_email" "$existing_password"
                
                echo ""
                print_success "Initial account setup complete!"
                echo ""
                echo "Access your services:"
                echo "  🧠 OpenWebUI: http://localhost:${PORT_WEBUI}"
                echo "  🔄 n8n:       http://localhost:${PORT_N8N}"
                echo ""
                echo "Email:    $existing_email"
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
    
    # Store credentials
    store_credentials "$email" "$password"
    
    # Create accounts
    create_openwebui_account "$email" "$password"
    create_n8n_account "$email" "$password"
    
    echo ""
    print_success "Initial account setup complete!"
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
