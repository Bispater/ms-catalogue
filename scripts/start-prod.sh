#!/bin/bash

# Script para levantar el entorno de PRODUCCIÓN con Docker
# Autor: Catalogue API Team
# Fecha: 2026-01-20

set -e  # Detener el script si hay algún error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
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
echo -e "${RED}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         CATALOGUE API - PRODUCCIÓN                     ║"
echo "║              Iniciando entorno Docker...              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Advertencia de producción
print_warning "⚠️  MODO PRODUCCIÓN - Este script desplegará en producción"
read -p "¿Estás seguro de continuar? (s/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Ss]$ ]]; then
    print_message "Operación cancelada"
    exit 0
fi

# 1. Verificar que Docker esté corriendo
print_message "Verificando que Docker esté corriendo..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker."
    exit 1
fi
print_success "Docker está corriendo ✓"

# 2. Verificar que existe el archivo .env.prod
print_message "Verificando archivo .env.prod..."
if [ ! -f .env.prod ]; then
    print_error "No se encontró el archivo .env.prod"
    print_message "Por favor crea .env.prod con las variables de producción"
    exit 1
fi
print_success "Archivo .env.prod encontrado ✓"

# 3. Verificar variables críticas
print_message "Verificando variables críticas..."

# Leer variables sin ejecutar el archivo (evita errores con sintaxis Python)
DEBUG_VALUE=$(grep "^DEBUG=" .env.prod | cut -d '=' -f2)
SECRET_KEY_VALUE=$(grep "^SECRET_KEY=" .env.prod | cut -d '=' -f2)
POSTGRES_PASSWORD_VALUE=$(grep "^POSTGRES_PASSWORD=" .env.prod | cut -d '=' -f2)

if [ "$DEBUG_VALUE" != "False" ]; then
    print_error "DEBUG debe estar en False para producción (actual: $DEBUG_VALUE)"
    exit 1
fi

if [ -z "$SECRET_KEY_VALUE" ] || [ "$SECRET_KEY_VALUE" == "your-secret-key-here" ]; then
    print_error "SECRET_KEY no está configurada correctamente"
    exit 1
fi

if [ -z "$POSTGRES_PASSWORD_VALUE" ] || [ "$POSTGRES_PASSWORD_VALUE" == "postgres" ]; then
    print_warning "⚠️  Usando contraseña de base de datos por defecto (no recomendado)"
fi

print_success "Variables críticas verificadas ✓"

# 4. Verificar certificados SSL
print_message "Verificando certificados SSL..."
if [ ! -f "/etc/letsencrypt/live/catalogue.favric.cl/fullchain.pem" ]; then
    print_warning "⚠️  No se encontraron certificados SSL en /etc/letsencrypt/"
    print_message "El servidor funcionará pero sin HTTPS"
    read -p "¿Deseas continuar sin SSL? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    print_success "Certificados SSL encontrados ✓"
fi

# 5. Backup de base de datos (si existe)
print_message "Verificando si hay base de datos existente..."
if docker compose -f docker-compose.prod.yml ps db | grep -q "Up"; then
    print_warning "Base de datos en ejecución detectada"
    read -p "¿Deseas hacer un backup antes de continuar? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        # Leer variables de base de datos del .env.prod
        POSTGRES_USER=$(grep "^POSTGRES_USER=" .env.prod | cut -d '=' -f2)
        POSTGRES_DB=$(grep "^POSTGRES_DB=" .env.prod | cut -d '=' -f2)
        
        BACKUP_FILE="./backups/backup_$(date +%Y%m%d_%H%M%S).sql"
        mkdir -p ./backups
        print_message "Creando backup en $BACKUP_FILE..."
        docker compose -f docker-compose.prod.yml exec -T db pg_dump -U $POSTGRES_USER $POSTGRES_DB > $BACKUP_FILE
        print_success "Backup creado ✓"
    fi
fi

# 6. Detener contenedores existentes
print_message "Deteniendo contenedores existentes..."
docker compose -f docker-compose.prod.yml down
print_success "Contenedores detenidos ✓"

# 7. Construir las imágenes
print_message "Construyendo imágenes Docker para producción..."
docker compose -f docker-compose.prod.yml build --no-cache
print_success "Imágenes construidas ✓"

# 8. Levantar los servicios
print_message "Levantando servicios de producción..."
docker compose -f docker-compose.prod.yml up -d
print_success "Servicios levantados ✓"

# 9. Esperar a que PostgreSQL esté listo
print_message "Esperando a que PostgreSQL esté listo..."

# Leer variables de base de datos
POSTGRES_USER=$(grep "^POSTGRES_USER=" .env.prod | cut -d '=' -f2)
POSTGRES_DB=$(grep "^POSTGRES_DB=" .env.prod | cut -d '=' -f2)

MAX_TRIES=30
COUNTER=0
until docker compose -f docker-compose.prod.yml exec -T db pg_isready -U $POSTGRES_USER -d $POSTGRES_DB > /dev/null 2>&1; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -gt $MAX_TRIES ]; then
        print_error "PostgreSQL no respondió a tiempo"
        docker compose -f docker-compose.prod.yml logs db
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "PostgreSQL está listo ✓"

# 10. Esperar a que el servicio web esté listo
print_message "Esperando a que el servicio web esté listo..."
sleep 5
print_success "Servicio web iniciado ✓"

# 11. Mostrar estado de los contenedores
echo ""
print_message "Estado de los contenedores:"
docker compose -f docker-compose.prod.yml ps

# 12. Verificar health checks
print_message "Verificando health checks..."
sleep 10
docker compose -f docker-compose.prod.yml ps

# 13. Información de acceso
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║          🎉 PRODUCCIÓN DESPLEGADA CON ÉXITO 🎉         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Servicios disponibles:${NC}"
echo ""
echo -e "  🌐 API (HTTP):      ${GREEN}http://catalogue.favric.cl${NC}"
echo -e "  🔒 API (HTTPS):     ${GREEN}https://catalogue.favric.cl${NC}"
echo -e "  🗄️  PostgreSQL:      ${GREEN}localhost:5432${NC} (interno)"
echo ""
echo -e "${BLUE}📝 Comandos útiles:${NC}"
echo ""
echo -e "  Ver logs:           ${YELLOW}docker compose -f docker-compose.prod.yml logs -f${NC}"
echo -e "  Ver logs de web:    ${YELLOW}docker compose -f docker-compose.prod.yml logs -f web${NC}"
echo -e "  Ver logs de nginx:  ${YELLOW}docker compose -f docker-compose.prod.yml logs -f nginx${NC}"
echo -e "  Ver logs de db:     ${YELLOW}docker compose -f docker-compose.prod.yml logs -f db${NC}"
echo -e "  Detener servicios:  ${YELLOW}docker compose -f docker-compose.prod.yml down${NC}"
echo -e "  Reiniciar:          ${YELLOW}./scripts/start-prod.sh${NC}"
echo -e "  Shell Django:       ${YELLOW}docker compose -f docker-compose.prod.yml exec web python manage.py shell${NC}"
echo -e "  Ver backups:        ${YELLOW}ls -lh ./backups/${NC}"
echo ""
echo -e "${BLUE}🔍 Monitoreo:${NC}"
echo ""
echo -e "  Health check web:   ${YELLOW}curl http://localhost/admin/${NC}"
echo -e "  Health check nginx: ${YELLOW}curl http://localhost/health/${NC}"
echo -e "  Estado contenedor:  ${YELLOW}docker compose -f docker-compose.prod.yml ps${NC}"
echo ""
echo -e "${GREEN}✨ El entorno de producción está listo ✨${NC}"
echo ""

# 14. Preguntar si desea ver los logs en tiempo real
read -p "¿Deseas ver los logs en tiempo real? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_message "Mostrando logs en tiempo real (Ctrl+C para salir)..."
    docker compose -f docker-compose.prod.yml logs -f
fi
