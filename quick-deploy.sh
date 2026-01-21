#!/bin/bash

# Script de despliegue rápido para producción
# Hace git pull, rebuild y restart automáticamente

set -e

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║         CATALOGUE API - DESPLIEGUE RÁPIDO             ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# 1. Git pull
echo -e "${YELLOW}📥 Actualizando código...${NC}"
git pull origin develop || {
    echo -e "${YELLOW}⚠️  No se pudo hacer pull (puede que no haya cambios)${NC}"
}

# 2. Down
echo -e "${YELLOW}🛑 Deteniendo servicios...${NC}"
docker compose -f docker-compose.prod.yml down

# 3. Build (opcional)
if [ "$1" == "--rebuild" ]; then
    echo -e "${YELLOW}🔨 Rebuild completo...${NC}"
    docker compose -f docker-compose.prod.yml build --no-cache
else
    echo -e "${YELLOW}🔨 Build rápido...${NC}"
    docker compose -f docker-compose.prod.yml build
fi

# 4. Up
echo -e "${YELLOW}🚀 Levantando servicios...${NC}"
docker compose -f docker-compose.prod.yml up -d

# 5. Esperar
echo -e "${YELLOW}⏳ Esperando 30 segundos...${NC}"
sleep 30

# 6. Estado
echo ""
echo -e "${GREEN}✅ DESPLIEGUE COMPLETADO${NC}"
echo ""
echo -e "${YELLOW}📊 Estado de contenedores:${NC}"
docker compose -f docker-compose.prod.yml ps

echo ""
echo -e "${YELLOW}🔍 Ver logs:${NC}"
echo "  docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${YELLOW}🌐 Acceder:${NC}"
echo "  https://catalogue.favric.cl/admin/"
echo ""
echo -e "${YELLOW}💡 Uso:${NC}"
echo "  ./quick-deploy.sh           # Deploy rápido"
echo "  ./quick-deploy.sh --rebuild # Deploy con rebuild completo"
echo ""
