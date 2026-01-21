# ⚡ Referencia Rápida - Catalogue API

## 🚀 Comandos Más Usados

### Desarrollo Local

```bash
# Iniciar proyecto
./start

# Detener proyecto
./stop

# Ver logs
docker compose logs -f

# Crear superuser
./scripts/create-superuser.sh

# Crear migraciones
docker compose exec web python manage.py makemigrations

# Aplicar migraciones
docker compose exec web python manage.py migrate

# Shell de Django
docker compose exec web python manage.py shell

# Acceder
http://localhost:8050/admin/
```

---

### Producción

```bash
# Conectar al servidor
ssh root@srv702740
cd /var/ms-catalogue

# Deploy completo (primera vez)
./start-prod

# Deploy rápido (uso diario)
./quick-deploy.sh

# Deploy con rebuild completo
./quick-deploy.sh --rebuild

# Ver logs
docker compose -f docker-compose.prod.yml logs -f web

# Crear superuser
./scripts/create-superuser.sh

# Acceder
https://catalogue.favric.cl/admin/
```

---

## 📋 Flujo de Trabajo Típico

### 1. Cambio de Código Normal

```bash
# En tu máquina
git add .
git commit -m "descripción del cambio"
git push origin develop

# En el servidor
ssh root@srv702740
cd /var/ms-catalogue
git pull origin develop
./quick-deploy.sh
```

---

### 2. Cambio de Modelos (con migración)

```bash
# En tu máquina
# 1. Editar api/models.py
# 2. Crear migración
docker compose exec web python manage.py makemigrations
# 3. Aplicar localmente
docker compose exec web python manage.py migrate
# 4. Probar
# 5. Commit y push
git add api/models.py api/migrations/
git commit -m "add new field"
git push origin develop

# En el servidor
ssh root@srv702740
cd /var/ms-catalogue
git pull origin develop
./quick-deploy.sh  # Aplica migraciones automáticamente
```

---

### 3. Agregar Dependencia

```bash
# En tu máquina
# 1. Agregar a requirements.txt
# 2. Commit y push
git add requirements.txt
git commit -m "add new dependency"
git push origin develop

# En el servidor
ssh root@srv702740
cd /var/ms-catalogue
git pull origin develop
./quick-deploy.sh --rebuild  # Rebuild con nuevas dependencias
```

---

## 🔧 Troubleshooting

### Error: Puerto en uso

```bash
# Ver qué está usando el puerto
sudo lsof -i :8050  # Local
sudo lsof -i :80    # Producción

# Matar proceso
sudo kill -9 <PID>
```

---

### Error: Contenedor no inicia

```bash
# Ver logs
docker compose logs web

# Reiniciar contenedor
docker compose restart web

# Rebuild completo
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

### Error: Migración falla

```bash
# Ver estado
docker compose exec web python manage.py showmigrations

# Ver SQL de migración
docker compose exec web python manage.py sqlmigrate api 0002

# Revertir migración
docker compose exec web python manage.py migrate api 0001

# Volver a aplicar
docker compose exec web python manage.py migrate
```

---

### Error: Base de datos corrupta

```bash
# Backup primero (si es posible)
docker compose exec db pg_dump -U catalogue_user catalogue_db > backup.sql

# Resetear (⚠️ BORRA TODO)
docker compose down
docker volume rm catalogue_api_postgres_data
docker compose up -d
docker compose exec web python manage.py migrate
docker compose exec web python manage.py createsuperuser
```

---

## 📁 Estructura de Archivos Importante

```
catalogue_api/
├── api/                    # App principal
│   ├── models.py          # Modelos de datos
│   ├── views.py           # Vistas/endpoints
│   ├── serializers.py     # Serializers DRF
│   └── migrations/        # Migraciones (NO borrar)
├── core/                   # Configuración Django
│   ├── settings.py        # Settings principal
│   └── urls.py            # URLs principales
├── docs/                   # Documentación
│   ├── MIGRATIONS_GUIDE.md
│   └── QUICK_REFERENCE.md
├── scripts/               # Scripts útiles
│   ├── create-superuser.sh
│   └── start-prod.sh
├── .env                   # Variables desarrollo
├── .env.prod             # Variables producción
├── docker-compose.yml    # Docker desarrollo
├── docker-compose.prod.yml # Docker producción
├── quick-deploy.sh       # Deploy rápido
├── start                 # Iniciar desarrollo
└── stop                  # Detener desarrollo
```

---

## 🌐 URLs Importantes

### Desarrollo
- Admin: http://localhost:8050/admin/
- API: http://localhost:8050/api/
- Swagger: http://localhost:8050/api/docs/

### Producción
- Admin: https://catalogue.favric.cl/admin/
- API: https://catalogue.favric.cl/api/
- Swagger: https://catalogue.favric.cl/api/docs/

---

## 📞 Contactos y Recursos

- Repositorio: https://github.com/Bispater/ms-catalogue
- Servidor: srv702740 (root@srv702740)
- Dominio: catalogue.favric.cl

---

**Última actualización**: 2026-01-21
