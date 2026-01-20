#!/bin/bash

# Script para actualizar dependencias de Python
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

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║      CATALOGUE API - ACTUALIZAR DEPENDENCIAS          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Verificar que Docker esté corriendo
print_message "Verificando que Docker esté corriendo..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi
print_success "Docker está corriendo ✓"

# Verificar si hay contenedores corriendo
if docker compose ps | grep -q "running"; then
    print_warning "Hay contenedores corriendo. Se reconstruirán con las nuevas dependencias."
    echo ""
    read -p "¿Deseas continuar? (s/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        print_message "Operación cancelada"
        exit 0
    fi
fi

echo ""
print_message "Iniciando actualización de dependencias..."
echo ""

# 1. Detener contenedores
print_message "1/4 - Deteniendo contenedores..."
docker compose down

# 2. Reconstruir imagen sin caché
print_message "2/4 - Reconstruyendo imagen con nuevas dependencias..."
print_warning "Esto puede tardar varios minutos..."
docker compose build --no-cache web

# 3. Levantar servicios
print_message "3/4 - Levantando servicios..."
docker compose up -d

# 4. Verificar instalación
print_message "4/4 - Verificando versiones instaladas..."
echo ""
docker compose exec web pip list | grep -i ckeditor || true
echo ""

print_success "✅ Dependencias actualizadas correctamente"
echo ""
print_message "Servicios disponibles:"
docker compose ps
echo ""

print_success "🎉 Actualización completada"
echo ""
print_message "Puedes verificar que CKEditor esté actualizado accediendo al admin de Django"
echo ""
