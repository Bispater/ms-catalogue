#!/bin/bash

# Script para crear superusuario de Django
# Autor: Catalogue API Team
# Fecha: 2026-01-19

set -e

# Colores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         CATALOGUE API - CREAR SUPERUSUARIO            ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar que Docker esté corriendo
print_message "Verificando que Docker esté corriendo..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi

# Detectar si es producción o desarrollo
if [ -f "docker-compose.prod.yml" ] && docker compose -f docker-compose.prod.yml ps | grep -q "web"; then
    COMPOSE_FILE="docker-compose.prod.yml"
    ENV_TYPE="PRODUCCIÓN"
else
    COMPOSE_FILE="docker-compose.yml"
    ENV_TYPE="DESARROLLO"
fi

# Verificar que el contenedor web esté corriendo
print_message "Verificando que el contenedor web esté corriendo..."
if ! docker compose -f $COMPOSE_FILE ps | grep -q "web.*Up"; then
    print_error "El contenedor web no está corriendo."
    if [ "$ENV_TYPE" = "PRODUCCIÓN" ]; then
        print_message "Por favor ejecuta primero: ./quick-deploy.sh o ./start-prod"
    else
        print_message "Por favor ejecuta primero: ./start"
    fi
    exit 1
fi

print_success "Contenedor web está corriendo ✓ (${ENV_TYPE})"
echo ""

# Opción 1: Crear superusuario interactivo
echo -e "${YELLOW}Opciones:${NC}"
echo ""
echo "  [1] Crear superusuario interactivo (te pedirá usuario, email y password)"
echo "  [2] Crear superusuario con valores predefinidos (admin/admin@admin.com/admin)"
echo "  [3] Cancelar"
echo ""
read -p "Selecciona una opción (1-3): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        print_message "Creando superusuario interactivo..."
        echo ""
        docker compose -f $COMPOSE_FILE exec web python manage.py createsuperuser
        echo ""
        print_success "✨ Superusuario creado exitosamente ✨"
        ;;
        
    2)
        print_message "Creando superusuario con valores predefinidos..."
        echo ""
        echo -e "${YELLOW}Usuario:${NC} admin"
        echo -e "${YELLOW}Email:${NC} admin@admin.com"
        echo -e "${YELLOW}Password:${NC} admin"
        echo ""
        
        docker compose -f $COMPOSE_FILE exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()

if User.objects.filter(username='admin').exists():
    print('⚠️  El usuario "admin" ya existe')
else:
    User.objects.create_superuser('admin', 'admin@admin.com', 'admin')
    print('✅ Superusuario "admin" creado exitosamente')
EOF
        
        echo ""
        print_success "✨ Superusuario creado exitosamente ✨"
        print_message "Puedes acceder con: admin / admin"
        ;;
        
    3)
        print_message "Operación cancelada"
        exit 0
        ;;
        
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
if [ "$ENV_TYPE" = "PRODUCCIÓN" ]; then
    print_message "Puedes acceder al admin de Django en: ${GREEN}https://catalogue.favric.cl/admin/${NC}"
else
    print_message "Puedes acceder al admin de Django en: ${GREEN}http://localhost:8050/admin${NC}"
fi
echo ""
