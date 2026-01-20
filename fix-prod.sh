#!/bin/bash

# Script rápido para arreglar producción

echo "🔧 Arreglando producción..."

# 1. Crear migraciones
echo "📝 Creando migraciones..."
docker compose -f docker-compose.prod.yml exec web python manage.py makemigrations

# 2. Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 3. Crear superuser directamente
echo "👤 Creando superuser..."
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

echo "✅ Listo!"
