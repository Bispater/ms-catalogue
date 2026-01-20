#!/bin/bash

# Script para cambiar entre entornos (desarrollo/producción)
# Autor: Catalogue API Team
# Fecha: 2026-01-19

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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
echo "║         CATALOGUE API - CAMBIAR ENTORNO               ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Mostrar entorno actual
if [ -f .env ]; then
    CURRENT_DEBUG=$(grep "^DEBUG=" .env | cut -d'=' -f2)
    if [ "$CURRENT_DEBUG" = "True" ]; then
        print_message "Entorno actual: ${GREEN}DESARROLLO${NC}"
    else
        print_message "Entorno actual: ${RED}PRODUCCIÓN${NC}"
    fi
else
    print_warning "No hay archivo .env configurado"
fi

echo ""
echo "Selecciona el entorno:"
echo ""
echo "  [1] Desarrollo (local con Docker)"
echo "  [2] Producción"
echo "  [3] Crear .env personalizado"
echo "  [4] Cancelar"
echo ""
read -p "Opción (1-4): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        print_message "Cambiando a entorno de DESARROLLO..."
        
        # Crear .env de desarrollo
        cat > .env << 'EOF'
# DESARROLLO LOCAL
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production-12345678901234567890
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

LANGUAGE_CODE=es-cl
TIME_ZONE=America/Santiago
USE_I18N=True
USE_L10N=True
USE_TZ=True

# Base de Datos - Docker
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ms_catalogue_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_URL=redis://redis:6379/0
REDIS_PASSWORD=

# Email - Console
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
DEFAULT_FROM_EMAIL=noreply@localhost

# Almacenamiento Local
USE_S3=False
MEDIA_URL=/media/
STATIC_URL=/static/

# Seguridad - Deshabilitada
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False
CSRF_TRUSTED_ORIGINS=http://localhost:8050,http://127.0.0.1:8050

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:8050,http://127.0.0.1:8050,http://localhost:3000
CORS_ALLOW_CREDENTIALS=True

# CKEditor
CKEDITOR_UPLOAD_PATH=uploads/
CKEDITOR_IMAGE_BACKEND=pillow

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0
CELERY_ACCEPT_CONTENT=json
CELERY_TASK_SERIALIZER=json
CELERY_RESULT_SERIALIZER=json
CELERY_TIMEZONE=America/Santiago
EOF
        
        print_success "Entorno cambiado a DESARROLLO ✓"
        print_message "Puedes ejecutar: ./start-local.sh"
        ;;
        
    2)
        print_warning "⚠️  Cambiando a entorno de PRODUCCIÓN"
        
        if [ ! -f .env.prod ]; then
            print_error "No existe el archivo .env.prod"
            print_message "Crea primero el archivo .env.prod con las configuraciones de producción"
            exit 1
        fi
        
        # Verificar que .env.prod tenga valores reales
        if grep -q "CAMBIAR-POR" .env.prod; then
            print_error "El archivo .env.prod contiene valores de ejemplo (CAMBIAR-POR)"
            print_warning "Por favor, edita .env.prod y reemplaza todos los valores de ejemplo"
            exit 1
        fi
        
        print_message "Copiando .env.prod a .env..."
        cp .env.prod .env
        
        print_success "Entorno cambiado a PRODUCCIÓN ✓"
        print_warning "⚠️  Asegúrate de que todas las variables estén configuradas correctamente"
        ;;
        
    3)
        print_message "Creando .env personalizado desde .env.example..."
        
        if [ ! -f .env.example ]; then
            print_error "No existe .env.example"
            exit 1
        fi
        
        cp .env.example .env
        print_success ".env creado desde .env.example ✓"
        print_warning "Por favor, edita .env y configura las variables necesarias"
        ;;
        
    4)
        print_message "Operación cancelada"
        exit 0
        ;;
        
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
print_success "✨ Cambio de entorno completado ✨"
echo ""
