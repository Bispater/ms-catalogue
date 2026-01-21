#!/bin/bash

# ⚠️ SCRIPT PELIGROSO - Ejecuta makemigrations en producción
# Solo usar si estás seguro de lo que haces

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${RED}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${RED}║      ⚠️  ACTUALIZACIÓN DJANGO EN PRODUCCIÓN ⚠️        ║${NC}"
echo -e "${RED}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${YELLOW}⚠️  ADVERTENCIA:${NC}"
echo "Este script ejecutará makemigrations en producción."
echo "Esto puede ser peligroso y NO es una buena práctica."
echo ""
echo -e "${YELLOW}Recomendación:${NC}"
echo "1. Hacer makemigrations en desarrollo"
echo "2. Commit y push a Git"
echo "3. Pull en producción"
echo "4. Solo ejecutar migrate"
echo ""

read -p "¿Estás SEGURO de continuar? (escribe 'SI' en mayúsculas): " -r
echo
if [[ ! $REPLY == "SI" ]]; then
    echo -e "${GREEN}Operación cancelada (buena decisión)${NC}"
    exit 0
fi

COMPOSE_FILE="docker-compose.prod.yml"

# Verificar que el contenedor web esté corriendo
if ! docker compose -f $COMPOSE_FILE ps | grep -q "web.*Up"; then
    echo -e "${RED}❌ El contenedor web no está corriendo${NC}"
    echo "Ejecuta primero: ./quick-deploy.sh"
    exit 1
fi

echo ""
echo -e "${BLUE}1️⃣  Verificando estado actual...${NC}"
docker compose -f $COMPOSE_FILE exec web python manage.py showmigrations

echo ""
echo -e "${YELLOW}2️⃣  Creando migraciones (makemigrations)...${NC}"
docker compose -f $COMPOSE_FILE exec web python manage.py makemigrations

echo ""
echo -e "${YELLOW}3️⃣  Aplicando migraciones (migrate)...${NC}"
docker compose -f $COMPOSE_FILE exec web python manage.py migrate

echo ""
echo -e "${YELLOW}4️⃣  Colectando archivos estáticos (collectstatic)...${NC}"
docker compose -f $COMPOSE_FILE exec web python manage.py collectstatic --noinput

echo ""
echo -e "${GREEN}✅ Actualización completada${NC}"
echo ""

echo -e "${YELLOW}📝 IMPORTANTE:${NC}"
echo "Si se crearon nuevas migraciones, deberías:"
echo ""
echo "1. Copiar las migraciones del contenedor a tu repo:"
echo "   docker compose -f $COMPOSE_FILE cp web:/app/api/migrations ./api/"
echo ""
echo "2. Commit y push:"
echo "   git add api/migrations/"
echo "   git commit -m 'add migrations from production'"
echo "   git push origin develop"
echo ""
echo "3. Así otros servidores/desarrolladores tendrán las mismas migraciones"
echo ""
