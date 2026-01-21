#!/bin/bash

# Script para configurar Nginx en el HOST (no Docker)
# Ejecutar como root o con sudo

set -e

echo "🔧 Configurando Nginx en el host..."
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar que se ejecuta como root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}❌ Este script debe ejecutarse como root${NC}"
    echo "Usa: sudo ./setup-nginx-host.sh"
    exit 1
fi

# 1. Instalar Nginx (si no está instalado)
echo -e "${YELLOW}📦 Verificando Nginx...${NC}"
if ! command -v nginx &> /dev/null; then
    echo "Instalando Nginx..."
    apt update
    apt install -y nginx
    echo -e "${GREEN}✅ Nginx instalado${NC}"
else
    echo -e "${GREEN}✅ Nginx ya está instalado${NC}"
fi

# 2. Copiar configuración
echo ""
echo -e "${YELLOW}📝 Copiando configuración...${NC}"
cp nginx-host.conf /etc/nginx/sites-available/catalogue.favric.cl
echo -e "${GREEN}✅ Configuración copiada${NC}"

# 3. Crear symlink
echo ""
echo -e "${YELLOW}🔗 Creando symlink...${NC}"
ln -sf /etc/nginx/sites-available/catalogue.favric.cl /etc/nginx/sites-enabled/
echo -e "${GREEN}✅ Symlink creado${NC}"

# 4. Eliminar configuración default (si existe)
echo ""
echo -e "${YELLOW}🗑️  Eliminando configuración default...${NC}"
rm -f /etc/nginx/sites-enabled/default
echo -e "${GREEN}✅ Default eliminado${NC}"

# 5. Crear directorios para static y media
echo ""
echo -e "${YELLOW}📁 Creando directorios...${NC}"
mkdir -p /var/ms-catalogue/staticfiles
mkdir -p /var/ms-catalogue/media
chown -R www-data:www-data /var/ms-catalogue/staticfiles
chown -R www-data:www-data /var/ms-catalogue/media
echo -e "${GREEN}✅ Directorios creados${NC}"

# 6. Verificar sintaxis de Nginx
echo ""
echo -e "${YELLOW}✅ Verificando sintaxis...${NC}"
if nginx -t; then
    echo -e "${GREEN}✅ Sintaxis correcta${NC}"
else
    echo -e "${RED}❌ Error en la configuración${NC}"
    exit 1
fi

# 7. Generar certificados SSL (si no existen)
echo ""
if [ ! -f "/etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem" ]; then
    echo -e "${YELLOW}🔐 Generando certificados SSL...${NC}"
    echo "Esto puede tardar un momento..."
    
    # Instalar certbot si no está
    if ! command -v certbot &> /dev/null; then
        apt install -y certbot python3-certbot-nginx
    fi
    
    # Generar certificado
    certbot --nginx -d catalogue.favric.cl --non-interactive --agree-tos --email admin@favric.cl
    
    echo -e "${GREEN}✅ Certificados generados${NC}"
else
    echo -e "${GREEN}✅ Certificados SSL ya existen${NC}"
fi

# 8. Iniciar o recargar Nginx
echo ""
if systemctl is-active --quiet nginx; then
    echo -e "${YELLOW}🔄 Recargando Nginx...${NC}"
    systemctl reload nginx
    echo -e "${GREEN}✅ Nginx recargado${NC}"
else
    echo -e "${YELLOW}🚀 Iniciando Nginx...${NC}"
    systemctl start nginx
    echo -e "${GREEN}✅ Nginx iniciado${NC}"
fi

# 9. Habilitar Nginx al inicio
echo ""
echo -e "${YELLOW}⚙️  Habilitando Nginx al inicio...${NC}"
systemctl enable nginx
echo -e "${GREEN}✅ Nginx habilitado${NC}"

# Resumen
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✅ NGINX CONFIGURADO                      ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${YELLOW}📋 Configuración:${NC}"
echo "  - Nginx escucha en puertos 80 y 443"
echo "  - Redirige HTTP → HTTPS"
echo "  - Proxy a Django en http://127.0.0.1:8000"
echo "  - Archivos estáticos: /var/ms-catalogue/staticfiles/"
echo "  - Archivos media: /var/ms-catalogue/media/"
echo ""
echo -e "${YELLOW}🔍 Comandos útiles:${NC}"
echo "  sudo systemctl status nginx    # Ver estado"
echo "  sudo systemctl reload nginx    # Recargar configuración"
echo "  sudo nginx -t                  # Verificar sintaxis"
echo "  sudo tail -f /var/log/nginx/catalogue.favric.cl.error.log"
echo ""
echo -e "${YELLOW}🚀 Próximos pasos:${NC}"
echo "  1. Levantar Django: cd /var/ms-catalogue && ./quick-deploy.sh"
echo "  2. Acceder a: https://catalogue.favric.cl/admin/"
echo ""
