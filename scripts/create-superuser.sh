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

# Verificar que el contenedor web esté corriendo
print_message "Verificando que el contenedor web esté corriendo..."
if ! docker compose ps | grep -q "web.*running"; then
    print_error "El contenedor web no está corriendo."
    print_message "Por favor ejecuta primero: ./start-local.sh"
    exit 1
fi

print_success "Contenedor web está corriendo ✓"
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
        docker compose exec web python manage.py createsuperuser
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
        
        docker compose exec -T web python manage.py shell << EOF
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
print_message "Puedes acceder al admin de Django en: ${GREEN}http://localhost:8050/admin${NC}"
echo ""
