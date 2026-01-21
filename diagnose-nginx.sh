#!/bin/bash

# Script de diagnóstico para problemas de Nginx

echo "🔍 Diagnóstico de Nginx"
echo "======================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Estado de contenedores
echo -e "${YELLOW}📊 Estado de contenedores:${NC}"
docker compose -f docker-compose.prod.yml ps
echo ""

# 2. Verificar certificados SSL
echo -e "${YELLOW}🔐 Verificando certificados SSL:${NC}"
if [ -f "/etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem" ]; then
    echo -e "${GREEN}✅ Certificado encontrado${NC}"
    ls -lh /etc/letsencrypt/live/catalogue.favric.cl/
else
    echo -e "${RED}❌ Certificados SSL NO encontrados${NC}"
    echo "Ubicación esperada: /etc/letsencrypt/live/catalogue.favric.cl/"
fi
echo ""

# 3. Verificar puertos
echo -e "${YELLOW}🔌 Verificando puertos 80 y 443:${NC}"
if command -v netstat &> /dev/null; then
    netstat -tlnp | grep ':80\|:443' || echo "Puertos 80/443 libres"
elif command -v ss &> /dev/null; then
    ss -tlnp | grep ':80\|:443' || echo "Puertos 80/443 libres"
else
    echo "No se puede verificar puertos (netstat/ss no disponible)"
fi
echo ""

# 4. Logs de nginx
echo -e "${YELLOW}📋 Últimos logs de nginx:${NC}"
docker compose -f docker-compose.prod.yml logs --tail=30 nginx
echo ""

# 5. Verificar sintaxis de nginx.prod.conf
echo -e "${YELLOW}✅ Verificando sintaxis de nginx.prod.conf:${NC}"
docker run --rm -v $(pwd)/nginx.prod.conf:/etc/nginx/conf.d/default.conf:ro nginx:alpine nginx -t 2>&1
echo ""

# 6. Verificar que web está corriendo
echo -e "${YELLOW}🌐 Verificando servicio web:${NC}"
if docker compose -f docker-compose.prod.yml ps web | grep -q "Up"; then
    echo -e "${GREEN}✅ Servicio web corriendo${NC}"
    docker compose -f docker-compose.prod.yml exec web curl -s http://localhost:8000/health/ || echo "No responde en /health/"
else
    echo -e "${RED}❌ Servicio web NO está corriendo${NC}"
fi
echo ""

# 7. Recomendaciones
echo -e "${YELLOW}💡 Recomendaciones:${NC}"
echo ""

if [ ! -f "/etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem" ]; then
    echo -e "${RED}⚠️  PROBLEMA: Certificados SSL no encontrados${NC}"
    echo ""
    echo "Opciones:"
    echo "1. Generar certificados con certbot:"
    echo "   sudo certbot certonly --nginx -d catalogue.favric.cl"
    echo ""
    echo "2. Usar configuración temporal sin SSL:"
    echo "   # En docker-compose.prod.yml, cambiar:"
    echo "   - ./nginx.simple.conf:/etc/nginx/conf.d/default.conf"
    echo "   # Y reiniciar:"
    echo "   docker compose -f docker-compose.prod.yml restart nginx"
    echo ""
fi

echo -e "${YELLOW}🔧 Comandos útiles:${NC}"
echo "Ver logs en tiempo real:"
echo "  docker compose -f docker-compose.prod.yml logs -f nginx"
echo ""
echo "Reiniciar nginx:"
echo "  docker compose -f docker-compose.prod.yml restart nginx"
echo ""
echo "Probar sintaxis nginx:"
echo "  docker compose -f docker-compose.prod.yml exec nginx nginx -t"
echo ""
echo "Usar configuración simple (sin SSL):"
echo "  # Editar docker-compose.prod.yml:"
echo "  # - ./nginx.simple.conf:/etc/nginx/conf.d/default.conf"
echo ""
