#!/bin/bash

# Script para ver logs de los servicios Docker
# Autor: Catalogue API Team
# Fecha: 2026-01-19

# Colores
BLUE='\033[0;34m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║              CATALOGUE API - LOGS                     ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Selecciona el servicio:"
echo ""
echo "  [1] Todos los servicios"
echo "  [2] Django (web)"
echo "  [3] PostgreSQL (db)"
echo "  [4] pgAdmin"
echo ""
read -p "Opción (1-4): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo -e "${GREEN}Mostrando logs de todos los servicios...${NC}"
        docker compose logs -f
        ;;
    2)
        echo -e "${GREEN}Mostrando logs de Django...${NC}"
        docker compose logs -f web
        ;;
    3)
        echo -e "${GREEN}Mostrando logs de PostgreSQL...${NC}"
        docker compose logs -f db
        ;;
    4)
        echo -e "${GREEN}Mostrando logs de pgAdmin...${NC}"
        docker compose logs -f pgadmin
        ;;
    *)
        echo "Opción inválida"
        exit 1
        ;;
esac
