#!/bin/bash

# Crypto Platform Deployment Script
# Usage: ./scripts/deploy.sh [environment] [action]
# Example: ./scripts/deploy.sh production deploy

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="crypto-platform"
DOCKER_REGISTRY="your-registry.com"  # Update this
GIT_REPO="https://github.com/your-username/crypto-platform.git"  # Update this

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

check_requirements() {
    log_info "Checking deployment requirements..."
    
    # Check if running as root
    if [[ $EUID -eq 0 ]]; then
        log_error "This script should not be run as root"
        exit 1
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed"
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check Git
    if ! command -v git &> /dev/null; then
        log_error "Git is not installed"
        exit 1
    fi
    
    log_success "All requirements satisfied"
}

setup_vps() {
    log_info "Setting up VPS environment..."
    
    # Update system
    sudo apt update && sudo apt upgrade -y
    
    # Install essential packages
    sudo apt install -y \
        curl \
        wget \
        git \
        nginx \
        certbot \
        python3-certbot-nginx \
        ufw \
        fail2ban \
        htop \
        tree \
        jq
    
    # Configure firewall
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80
    sudo ufw allow 443
    sudo ufw --force enable
    
    # Configure fail2ban
    sudo systemctl enable fail2ban
    sudo systemctl start fail2ban
    
    # Create application directory
    sudo mkdir -p /opt/${PROJECT_NAME}
    sudo chown $USER:$USER /opt/${PROJECT_NAME}
    
    log_success "VPS setup completed"
}

setup_docker() {
    log_info "Installing Docker..."
    
    # Install Docker
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    
    # Install Docker Compose
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    # Start Docker service
    sudo systemctl enable docker
    sudo systemctl start docker
    
    log_success "Docker installation completed"
    log_warning "Please log out and log back in for Docker group changes to take effect"
}

clone_repository() {
    local target_dir="/opt/${PROJECT_NAME}"
    
    log_info "Cloning repository to ${target_dir}..."
    
    if [ -d "${target_dir}/.git" ]; then
        log_info "Repository already exists, pulling latest changes..."
        cd ${target_dir}
        git pull origin main
    else
        git clone ${GIT_REPO} ${target_dir}
        cd ${target_dir}
    fi
    
    log_success "Repository setup completed"
}

setup_environment() {
    local env=$1
    local env_file=".env.${env}"
    
    log_info "Setting up ${env} environment..."
    
    if [ ! -f "${env_file}" ]; then
        log_warning "${env_file} not found, creating from template..."
        cp .env.example ${env_file}
        
        # Generate secure secrets
        JWT_SECRET=$(openssl rand -hex 32)
        SECRET_KEY=$(openssl rand -hex 32)
        DB_PASSWORD=$(openssl rand -hex 16)
        REDIS_PASSWORD=$(openssl rand -hex 16)
        NEO4J_PASSWORD=$(openssl rand -hex 16)
        GRAFANA_PASSWORD=$(openssl rand -hex 16)
        
        # Update environment file
        sed -i "s/your-super-secure-jwt-secret-here/${JWT_SECRET}/g" ${env_file}
        sed -i "s/your-django-secret-key-here/${SECRET_KEY}/g" ${env_file}
        sed -i "s/secure_password/${DB_PASSWORD}/g" ${env_file}
        sed -i "s/secure_redis_password/${REDIS_PASSWORD}/g" ${env_file}
        sed -i "s/secure_neo4j_password/${NEO4J_PASSWORD}/g" ${env_file}
        sed -i "s/secure_grafana_password/${GRAFANA_PASSWORD}/g" ${env_file}
        
        log_warning "Please review and update ${env_file} with your specific configuration"
        log_warning "Generated passwords have been set, please save them securely"
    fi
    
    log_success "Environment setup completed"
}

setup_ssl() {
    local domain=$1
    
    if [ -z "$domain" ]; then
        log_error "Domain name is required for SSL setup"
        return 1
    fi
    
    log_info "Setting up SSL certificate for ${domain}..."
    
    # Create nginx configuration
    sudo tee /etc/nginx/sites-available/${PROJECT_NAME} > /dev/null <<EOF
server {
    listen 80;
    server_name ${domain} www.${domain};
    
    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }
    
    location / {
        return 301 https://\$server_name\$request_uri;
    }
}
EOF
    
    # Enable site
    sudo ln -sf /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl reload nginx
    
    # Get SSL certificate
    sudo certbot --nginx -d ${domain} -d www.${domain} --non-interactive --agree-tos --email admin@${domain}
    
    log_success "SSL certificate setup completed"
}

build_images() {
    local env=$1
    
    log_info "Building Docker images for ${env}..."
    
    # Build application image
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:latest .
    docker build -t ${DOCKER_REGISTRY}/${PROJECT_NAME}:$(git rev-parse --short HEAD) .
    
    log_success "Docker images built successfully"
}

deploy_application() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"
    
    log_info "Deploying application to ${env}..."
    
    # Check if compose file exists
    if [ ! -f "${compose_file}" ]; then
        log_error "Compose file ${compose_file} not found"
        return 1
    fi
    
    # Pull latest images
    docker-compose -f ${compose_file} pull
    
    # Deploy with zero downtime
    docker-compose -f ${compose_file} up -d --remove-orphans
    
    # Wait for services to be healthy
    log_info "Waiting for services to be healthy..."
    sleep 30
    
    # Check service health
    if docker-compose -f ${compose_file} ps | grep -q "unhealthy\|Exit"; then
        log_error "Some services are not healthy"
        docker-compose -f ${compose_file} ps
        return 1
    fi
    
    log_success "Application deployed successfully"
}

run_health_checks() {
    local env=$1
    
    log_info "Running health checks..."
    
    # Define health check endpoints
    local endpoints=(
        "http://localhost:8000/health"
        "http://localhost:8000/metrics"
    )
    
    for endpoint in "${endpoints[@]}"; do
        log_info "Checking ${endpoint}..."
        
        if curl -f -s "${endpoint}" > /dev/null; then
            log_success "${endpoint} is healthy"
        else
            log_error "${endpoint} is not responding"
            return 1
        fi
    done
    
    log_success "All health checks passed"
}

setup_monitoring() {
    log_info "Setting up monitoring and alerting..."
    
    # Create monitoring directories
    mkdir -p monitoring/{prometheus,grafana,alertmanager}
    
    # Copy monitoring configurations
    if [ -d "monitoring/configs" ]; then
        cp -r monitoring/configs/* monitoring/
    fi
    
    log_success "Monitoring setup completed"
}

setup_backups() {
    log_info "Setting up automated backups..."
    
    # Create backup directory
    sudo mkdir -p /opt/backups/${PROJECT_NAME}
    sudo chown $USER:$USER /opt/backups/${PROJECT_NAME}
    
    # Create backup script
    cat > /opt/backups/${PROJECT_NAME}/backup.sh << 'EOF'
#!/bin/bash

BACKUP_DIR="/opt/backups/crypto-platform"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup PostgreSQL
docker exec crypto-platform_postgres_1 pg_dump -U crypto_user crypto_production > "${BACKUP_DIR}/postgres_${DATE}.sql"

# Backup Neo4j
docker exec crypto-platform_neo4j_1 neo4j-admin dump --database=neo4j --to=/backups/neo4j_${DATE}.dump

# Backup Qdrant
docker exec crypto-platform_qdrant_1 tar -czf /qdrant/storage/backup_${DATE}.tar.gz /qdrant/storage

# Compress and encrypt backups
tar -czf "${BACKUP_DIR}/full_backup_${DATE}.tar.gz" "${BACKUP_DIR}"/*_${DATE}.*

# Clean up old backups (keep last 7 days)
find "${BACKUP_DIR}" -name "*.tar.gz" -mtime +7 -delete
find "${BACKUP_DIR}" -name "*.sql" -mtime +7 -delete
find "${BACKUP_DIR}" -name "*.dump" -mtime +7 -delete

echo "Backup completed: ${DATE}"
EOF
    
    chmod +x /opt/backups/${PROJECT_NAME}/backup.sh
    
    # Setup cron job for daily backups
    (crontab -l 2>/dev/null; echo "0 2 * * * /opt/backups/${PROJECT_NAME}/backup.sh >> /var/log/backup.log 2>&1") | crontab -
    
    log_success "Backup automation setup completed"
}

rollback() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"
    
    log_warning "Rolling back deployment..."
    
    # Stop current deployment
    docker-compose -f ${compose_file} down
    
    # Restore from backup compose file
    if [ -f "docker-compose.${env}.backup.yml" ]; then
        docker-compose -f "docker-compose.${env}.backup.yml" up -d
        log_success "Rollback completed"
    else
        log_error "No backup compose file found"
        return 1
    fi
}

show_status() {
    local env=$1
    local compose_file="docker-compose.${env}.yml"
    
    log_info "Deployment status for ${env}:"
    
    if [ -f "${compose_file}" ]; then
        docker-compose -f ${compose_file} ps
        echo ""
        docker-compose -f ${compose_file} logs --tail=20
    else
        log_error "Compose file ${compose_file} not found"
    fi
}

show_usage() {
    echo "Usage: $0 [environment] [action] [options]"
    echo ""
    echo "Environments:"
    echo "  local       - Local development"
    echo "  staging     - Staging environment"
    echo "  production  - Production environment"
    echo ""
    echo "Actions:"
    echo "  setup-vps   - Initial VPS setup"
    echo "  setup-docker - Install Docker and Docker Compose"
    echo "  clone       - Clone repository"
    echo "  env         - Setup environment variables"
    echo "  ssl         - Setup SSL certificate (requires domain)"
    echo "  build       - Build Docker images"
    echo "  deploy      - Deploy application"
    echo "  health      - Run health checks"
    echo "  monitoring - Setup monitoring"
    echo "  backups     - Setup automated backups"
    echo "  rollback    - Rollback deployment"
    echo "  status      - Show deployment status"
    echo "  full-deploy - Complete deployment (build + deploy + health)"
    echo ""
    echo "Examples:"
    echo "  $0 production setup-vps"
    echo "  $0 production ssl your-domain.com"
    echo "  $0 production full-deploy"
    echo "  $0 staging deploy"
    echo "  $0 production status"
}

# Main script logic
ENVIRONMENT=${1:-local}
ACTION=${2:-help}
OPTION=${3}

# Change to project directory if it exists
if [ -d "/opt/${PROJECT_NAME}" ]; then
    cd "/opt/${PROJECT_NAME}"
fi

case $ACTION in
    "setup-vps")
        check_requirements
        setup_vps
        ;;
    "setup-docker")
        setup_docker
        ;;
    "clone")
        clone_repository
        ;;
    "env")
        setup_environment $ENVIRONMENT
        ;;
    "ssl")
        if [ -z "$OPTION" ]; then
            log_error "Domain name is required for SSL setup"
            echo "Usage: $0 $ENVIRONMENT ssl your-domain.com"
            exit 1
        fi
        setup_ssl $OPTION
        ;;
    "build")
        check_requirements
        build_images $ENVIRONMENT
        ;;
    "deploy")
        check_requirements
        deploy_application $ENVIRONMENT
        ;;
    "health")
        run_health_checks $ENVIRONMENT
        ;;
    "monitoring")
        setup_monitoring
        ;;
    "backups")
        setup_backups
        ;;
    "rollback")
        rollback $ENVIRONMENT
        ;;
    "status")
        show_status $ENVIRONMENT
        ;;
    "full-deploy")
        check_requirements
        build_images $ENVIRONMENT
        deploy_application $ENVIRONMENT
        run_health_checks $ENVIRONMENT
        ;;
    "help"|*)
        show_usage
        ;;
esac

log_success "Script execution completed"