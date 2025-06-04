#!/bin/bash

# Prismeet Microservices Setup Script
# This script helps set up the microservices architecture for testing

set -e

echo "🚀 Setting up Prismeet Microservices..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
check_docker() {
    print_status "Checking Docker..."
    if ! docker --version &> /dev/null; then
        print_error "Docker is not installed or not running"
        exit 1
    fi

    if ! docker-compose --version &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi

    print_success "Docker is ready"
}

# Create directory structure
setup_directories() {
    print_status "Setting up directory structure..."

    # Create gateway directory
    mkdir -p gateway

    # Create scripts directory if it doesn't exist
    mkdir -p scripts

    # Create media and static directories
    mkdir -p media static

    print_success "Directory structure created"
}

# Create environment file if it doesn't exist
setup_env() {
    print_status "Setting up environment variables..."

    if [ ! -f .env ]; then
        print_status "Creating .env file..."
        cat > .env << EOF
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@db:5432/prismeet
DB_NAME=prismeet
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Django Configuration
DEBUG=True
SECRET_KEY=your-secret-key-change-this-in-production
DJANGO_SETTINGS_MODULE=config.settings

# CORS Configuration
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:80

# Service URLs
AUTH_SERVICE_URL=http://auth_service:8001
AI_SERVICE_URL=http://ai_service:8002
MEDIA_SERVICE_URL=http://media_service:8003
MEETING_SERVICE_URL=http://meeting_service:8004
RECORDING_SERVICE_URL=http://recording_service:8005
TRANSCRIPTION_SERVICE_URL=http://transcription_service:8006

# Frontend Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_AUTH_SERVICE_URL=http://localhost:8001
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

# Email Configuration (for testing)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google OAuth (optional)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key-change-this
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400

# Security
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0,backend,auth_service
CSRF_TRUSTED_ORIGINS=http://localhost:3000,http://localhost:8000,http://localhost:80
EOF
        print_success ".env file created"
    else
        print_warning ".env file already exists, skipping..."
    fi
}

# Build and start services
start_services() {
    local compose_file=${1:-docker-compose.yml}

    print_status "Building and starting services using $compose_file..."

    # Stop any running containers
    docker-compose -f $compose_file down --remove-orphans

    # Build and start services
    docker-compose -f $compose_file up --build -d

    print_success "Services started successfully"
}

# Wait for services to be ready
wait_for_services() {
    print_status "Waiting for services to be ready..."

    # Wait for database
    print_status "Waiting for database..."
    sleep 10

    # Check if auth service is ready
    print_status "Checking auth service..."
    for i in {1..30}; do
        if curl -s http://localhost:8001/api/auth/ > /dev/null 2>&1; then
            print_success "Auth service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Auth service failed to start"
            docker-compose logs auth_service
            exit 1
        fi
        sleep 2
    done

    # Check if backend is ready
    print_status "Checking backend service..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/api/ > /dev/null 2>&1; then
            print_success "Backend service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_error "Backend service failed to start"
            docker-compose logs backend
            exit 1
        fi
        sleep 2
    done

    # Check if frontend is ready
    print_status "Checking frontend service..."
    for i in {1..30}; do
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            print_success "Frontend service is ready"
            break
        fi
        if [ $i -eq 30 ]; then
            print_warning "Frontend service may not be ready yet"
            break
        fi
        sleep 2
    done
}

# Run authentication tests
run_auth_tests() {
    print_status "Running authentication endpoint tests..."

    if [ -f scripts/test_auth_endpoints.py ]; then
        python3 scripts/test_auth_endpoints.py
    else
        print_warning "Test script not found, skipping tests"
    fi
}

# Display service URLs
show_services() {
    print_success "🎉 Prismeet Microservices are ready!"
    echo ""
    echo "Service URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📱 Frontend:              http://localhost:3000"
    echo "🔧 Main Backend:          http://localhost:8000"
    echo "🔐 Auth Service:          http://localhost:8001"
    echo "🤖 AI Service:            http://localhost:8002"
    echo "📁 Media Service:         http://localhost:8003"
    echo "🎯 Meeting Service:       http://localhost:8004"
    echo "🎥 Recording Service:     http://localhost:8005"
    echo "📝 Transcription Service: http://localhost:8006"
    echo "🌐 Gateway (Nginx):       http://localhost:80"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Database URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🗄️  PostgreSQL:           localhost:5432"
    echo "⚡ Redis:                 localhost:6379"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Admin URLs:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "👤 Main Admin:            http://localhost:8000/admin/"
    echo "🔐 Auth Admin:            http://localhost:8001/admin/"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "Useful Commands:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "🔍 View logs:             docker-compose logs -f [service_name]"
    echo "🛑 Stop services:         docker-compose down"
    echo "🔄 Restart service:       docker-compose restart [service_name]"
    echo "🧪 Run auth tests:        python3 scripts/test_auth_endpoints.py"
    echo "🏗️  Rebuild services:      docker-compose up --build -d"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Main function
main() {
    local mode=${1:-full}

    case $mode in
        "auth-only")
            print_status "Setting up authentication service only..."
            check_docker
            setup_directories
            setup_env
            start_services "docker-compose.auth-test.yml"
            wait_for_services
            run_auth_tests
            echo ""
            echo "🔐 Authentication Service Setup Complete!"
            echo ""
            echo "Service URLs:"
            echo "🔐 Auth Service: http://localhost:8001"
            echo "🔧 Backend:      http://localhost:8000"
            echo "📱 Frontend:     http://localhost:3000"
            ;;
        "full")
            print_status "Setting up full microservices architecture..."
            check_docker
            setup_directories
            setup_env
            start_services "docker-compose.yml"
            wait_for_services
            run_auth_tests
            show_services
            ;;
        "test")
            print_status "Running tests only..."
            run_auth_tests
            ;;
        *)
            echo "Usage: $0 [auth-only|full|test]"
            echo ""
            echo "Options:"
            echo "  auth-only  - Setup only authentication service for testing"
            echo "  full       - Setup complete microservices architecture (default)"
            echo "  test       - Run authentication endpoint tests only"
            exit 1
            ;;
    esac
}

# Run main function with arguments
main "$@"