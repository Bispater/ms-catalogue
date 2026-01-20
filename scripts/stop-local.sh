#!/bin/bash

# Script para detener el entorno de desarrollo local con Docker
# Autor: Catalogue API Team
# Fecha: 2026-01-19

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo -e "${YELLOW}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         CATALOGUE API - DETENER ENTORNO               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Preguntar si desea eliminar volúmenes
echo ""
print_warning "⚠️  ¿Deseas eliminar también los volúmenes (datos de la base de datos)?"
echo ""
echo "  [1] No, solo detener los contenedores (RECOMENDADO)"
echo "  [2] Sí, eliminar todo incluyendo datos de la base de datos"
echo ""
read -p "Selecciona una opción (1/2): " -n 1 -r
echo ""

if [[ $REPLY == "2" ]]; then
    print_warning "Deteniendo contenedores y eliminando volúmenes..."
    docker compose down -v
    print_success "Contenedores detenidos y volúmenes eliminados ✓"
    print_warning "⚠️  Todos los datos de la base de datos han sido eliminados"
else
    print_message "Deteniendo contenedores (manteniendo datos)..."
    docker compose down
    print_success "Contenedores detenidos ✓"
    print_success "Los datos de la base de datos se mantienen seguros ✓"
fi

echo ""
print_success "🎉 Entorno detenido correctamente"
echo ""
