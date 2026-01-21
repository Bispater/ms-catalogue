#!/bin/bash

# Script para arreglar el loop de redirección en producción

echo "🔧 Arreglando loop de redirección..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Verificar que estamos en el directorio correcto
if [ ! -f "docker-compose.prod.yml" ]; then
    echo -e "${RED}❌ Error: No se encontró docker-compose.prod.yml${NC}"
    echo "Por favor ejecuta este script desde el directorio raíz del proyecto"
    exit 1
fi

# 2. Verificar configuración de .env.prod
echo -e "${YELLOW}📋 Verificando .env.prod...${NC}"
SECURE_SSL=$(grep "^SECURE_SSL_REDIRECT=" .env.prod | cut -d '=' -f2)
if [ "$SECURE_SSL" == "True" ]; then
    echo -e "${RED}❌ SECURE_SSL_REDIRECT está en True${NC}"
    echo "Debe estar en False porque Nginx maneja HTTPS"
    exit 1
fi
echo -e "${GREEN}✅ SECURE_SSL_REDIRECT=False${NC}"

# 3. Verificar que nginx.prod.conf existe
if [ ! -f "nginx.prod.conf" ]; then
    echo -e "${RED}❌ Error: No se encontró nginx.prod.conf${NC}"
    exit 1
fi
echo -e "${GREEN}✅ nginx.prod.conf encontrado${NC}"

# 4. Detener contenedores
echo ""
echo -e "${YELLOW}🛑 Deteniendo contenedores...${NC}"
docker compose -f docker-compose.prod.yml down

# 5. Limpiar volúmenes de nginx (opcional)
read -p "¿Deseas limpiar la caché de nginx? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo -e "${YELLOW}🧹 Limpiando logs de nginx...${NC}"
    rm -rf ./logs/nginx/*
fi

# 6. Levantar servicios
echo ""
echo -e "${YELLOW}🚀 Levantando servicios...${NC}"
docker compose -f docker-compose.prod.yml up -d

# 7. Esperar a que los servicios estén listos
echo ""
echo -e "${YELLOW}⏳ Esperando a que los servicios estén listos (30 segundos)...${NC}"
sleep 30

# 8. Verificar estado
echo ""
echo -e "${YELLOW}📊 Estado de los contenedores:${NC}"
docker compose -f docker-compose.prod.yml ps

# 9. Verificar configuración de Django
echo ""
echo -e "${YELLOW}🔍 Verificando configuración de Django...${NC}"
docker compose -f docker-compose.prod.yml exec web python -c "
from django.conf import settings
print('✅ SECURE_SSL_REDIRECT:', settings.SECURE_SSL_REDIRECT)
print('✅ CSRF_TRUSTED_ORIGINS:', settings.CSRF_TRUSTED_ORIGINS)
print('✅ ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)
print('✅ DEBUG:', settings.DEBUG)
" 2>/dev/null || echo -e "${RED}❌ No se pudo verificar (el contenedor aún no está listo)${NC}"

# 10. Instrucciones finales
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                 ✅ PROCESO COMPLETADO                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📝 Pasos siguientes:${NC}"
echo ""
echo "1. Limpia las cookies del navegador:"
echo "   Chrome: chrome://settings/clearBrowserData"
echo "   Selecciona 'Cookies' y 'Desde siempre'"
echo ""
echo "2. O usa modo incógnito: Ctrl+Shift+N"
echo ""
echo "3. Accede a: https://catalogue.favric.cl/admin/"
echo ""
echo -e "${YELLOW}🔍 Ver logs en tiempo real:${NC}"
echo "   docker compose -f docker-compose.prod.yml logs -f"
echo ""
echo -e "${YELLOW}🔍 Ver logs de nginx:${NC}"
echo "   docker compose -f docker-compose.prod.yml logs -f nginx"
echo ""
echo -e "${YELLOW}🔍 Ver logs de web:${NC}"
echo "   docker compose -f docker-compose.prod.yml logs -f web"
echo ""
