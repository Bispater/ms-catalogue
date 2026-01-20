#!/bin/bash

# Script para levantar el entorno de desarrollo local con Docker
# Autor: Catalogue API Team
# Fecha: 2026-01-19

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
echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         CATALOGUE API - DESARROLLO LOCAL              ║"
echo "║              Iniciando entorno Docker...              ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# 1. Verificar que Docker esté corriendo
print_message "Verificando que Docker esté corriendo..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker no está corriendo. Por favor inicia Docker Desktop."
    exit 1
fi
print_success "Docker está corriendo ✓"

# 2. Verificar que existe el archivo .env
print_message "Verificando archivo .env..."
if [ ! -f .env ]; then
    print_warning "No se encontró el archivo .env"
    if [ -f .env.example ]; then
        print_message "Copiando .env.example a .env..."
        cp .env.example .env
        print_success "Archivo .env creado desde .env.example"
        print_warning "⚠️  Por favor revisa y configura las variables en .env antes de continuar"
        read -p "¿Deseas continuar? (s/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            exit 1
        fi
    else
        print_error "No existe .env ni .env.example"
        exit 1
    fi
else
    print_success "Archivo .env encontrado ✓"
fi

# 3. Detener contenedores existentes (si los hay)
print_message "Deteniendo contenedores existentes (si los hay)..."
docker compose down 2>/dev/null || true
print_success "Contenedores detenidos ✓"

# 4. Construir las imágenes
print_message "Construyendo imágenes Docker..."
docker compose build --no-cache
print_success "Imágenes construidas ✓"

# 5. Levantar los servicios
print_message "Levantando servicios (db, web, pgadmin)..."
docker compose up -d
print_success "Servicios levantados ✓"

# 6. Esperar a que PostgreSQL esté listo
print_message "Esperando a que PostgreSQL esté listo..."
MAX_TRIES=30
COUNTER=0
until docker compose exec -T db pg_isready -U postgres -d ms_catalogue_db > /dev/null 2>&1; do
    COUNTER=$((COUNTER+1))
    if [ $COUNTER -gt $MAX_TRIES ]; then
        print_error "PostgreSQL no respondió a tiempo"
        docker compose logs db
        exit 1
    fi
    echo -n "."
    sleep 1
done
echo ""
print_success "PostgreSQL está listo ✓"

# 7. Mostrar logs iniciales
print_message "Mostrando logs de inicio..."
sleep 2
docker compose logs --tail=50

# 8. Mostrar estado de los contenedores
echo ""
print_message "Estado de los contenedores:"
docker compose ps

# 9. Información de acceso
echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              🎉 ENTORNO LEVANTADO CON ÉXITO 🎉         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📍 Servicios disponibles:${NC}"
echo ""
echo -e "  🌐 Django API:      ${GREEN}http://localhost:8050${NC}"
echo -e "  🗄️  PostgreSQL:      ${GREEN}localhost:5333${NC}"
echo -e "     └─ Database:     ${YELLOW}ms_catalogue_db${NC}"
echo -e "     └─ User:         ${YELLOW}postgres${NC}"
echo -e "     └─ Password:     ${YELLOW}postgres${NC}"
echo ""
echo -e "  🔧 pgAdmin:         ${GREEN}http://localhost:5050${NC}"
echo -e "     └─ Email:        ${YELLOW}admin@admin.com${NC}"
echo -e "     └─ Password:     ${YELLOW}admin${NC}"
echo ""
echo -e "${BLUE}📝 Comandos útiles:${NC}"
echo ""
echo -e "  Ver logs:           ${YELLOW}docker compose logs -f${NC}"
echo -e "  Ver logs de web:    ${YELLOW}docker compose logs -f web${NC}"
echo -e "  Ver logs de db:     ${YELLOW}docker compose logs -f db${NC}"
echo -e "  Detener servicios:  ${YELLOW}docker compose down${NC}"
echo -e "  Reiniciar:          ${YELLOW}./start-local.sh${NC}"
echo -e "  Shell Django:       ${YELLOW}docker compose exec web python manage.py shell${NC}"
echo -e "  Crear superuser:    ${YELLOW}docker compose exec web python manage.py createsuperuser${NC}"
echo ""
echo -e "${GREEN}✨ El entorno está listo para desarrollo ✨${NC}"
echo ""

# 10. Preguntar si desea crear superusuario
read -p "¿Deseas crear un superusuario de Django ahora? (s/n): " -n 1 -r
echo
echo ""
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_message "Creando superusuario..."
    docker compose exec web python manage.py createsuperuser
    echo ""
fi

# 11. Preguntar si desea ver los logs en tiempo real
read -p "¿Deseas ver los logs en tiempo real? (s/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Ss]$ ]]; then
    print_message "Mostrando logs en tiempo real (Ctrl+C para salir)..."
    docker compose logs -f
fi
