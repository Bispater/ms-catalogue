# 🐳 Catalogue API - Guía de Docker

## 📋 Requisitos Previos

- Docker Desktop instalado y corriendo
- Archivo `.env` configurado (se creará automáticamente desde `.env.example`)

## 🚀 Inicio Rápido

### Levantar el entorno completo

```bash
./start
# o
./scripts/start-local.sh
```

Este script hará:
1. ✅ Verificar que Docker esté corriendo
2. ✅ Verificar/crear archivo `.env`
3. ✅ Construir las imágenes Docker
4. ✅ Levantar todos los servicios (PostgreSQL, Django, pgAdmin)
5. ✅ Esperar a que PostgreSQL esté listo
6. ✅ Mostrar información de acceso

### Detener el entorno

```bash
./stop
# o
./scripts/stop-local.sh
```

Opciones:
- **Opción 1**: Solo detener contenedores (mantiene datos) ✅ RECOMENDADO
- **Opción 2**: Detener y eliminar volúmenes (borra la base de datos) ⚠️

### Ver logs

```bash
./logs
# o
./scripts/logs.sh
```

Opciones:
- Ver logs de todos los servicios
- Ver logs solo de Django
- Ver logs solo de PostgreSQL
- Ver logs solo de pgAdmin

## 🌐 Acceso a los Servicios

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Django API** | http://localhost:8050 | - |
| **pgAdmin** | http://localhost:5050 | Email: `admin@admin.com`<br>Password: `admin` |
| **PostgreSQL** | `localhost:5333` | User: `postgres`<br>Password: `postgres`<br>DB: `ms_catalogue_db` |

## 🔧 Configurar PostgreSQL en pgAdmin

1. Accede a http://localhost:5050
2. Login con `admin@admin.com` / `admin`
3. Click derecho en "Servers" → "Register" → "Server"
4. **Pestaña General**:
   - Name: `Catalogue DB`
5. **Pestaña Connection**:
   - Host: `db` ⚠️ (nombre del servicio Docker, NO localhost)
   - Port: `5432` ⚠️ (puerto interno, NO 5333)
   - Maintenance database: `ms_catalogue_db`
   - Username: `postgres`
   - Password: `postgres`
   - ✅ Marcar "Save password"
6. Click "Save"

## 📝 Comandos Útiles

### Comandos básicos

```bash
# Ver estado de los contenedores
docker compose ps

# Ver logs en tiempo real
docker compose logs -f

# Ver logs de un servicio específico
docker compose logs -f web
docker compose logs -f db
docker compose logs -f pgadmin

# Reiniciar un servicio específico
docker compose restart web
docker compose restart db

# Reconstruir y levantar
docker compose build
docker compose up -d
```

### Comandos de Django

```bash
# Crear superusuario (opción 1: script automatizado)
./scripts/create-superuser.sh

# Crear superusuario (opción 2: manual)
docker compose exec web python manage.py createsuperuser

# Acceder al shell de Django
docker compose exec web python manage.py shell

# Hacer migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Ejecutar tests
docker compose exec web python manage.py test

# Acceder al bash del contenedor
docker compose exec web bash
```

### Comandos de PostgreSQL

```bash
# Acceder a psql
docker compose exec db psql -U postgres -d ms_catalogue_db

# Ver tablas
docker compose exec db psql -U postgres -d ms_catalogue_db -c "\dt"

# Backup de la base de datos
docker compose exec db pg_dump -U postgres ms_catalogue_db > backup.sql

# Restaurar backup
cat backup.sql | docker compose exec -T db psql -U postgres -d ms_catalogue_db
```

## 🔄 Workflow de Desarrollo

### Desarrollo normal

```bash
# 1. Levantar el entorno
./start-local.sh

# 2. Hacer cambios en el código
# Los cambios se reflejan automáticamente gracias al volumen montado

# 3. Ver logs si es necesario
./logs.sh

# 4. Detener cuando termines
./stop-local.sh
```

### Cambios en dependencias (requirements.txt)

```bash
# 1. Detener contenedores
docker compose down

# 2. Reconstruir imagen
docker compose build --no-cache web

# 3. Levantar de nuevo
docker compose up -d
```

### Cambios en modelos de Django

```bash
# 1. Hacer cambios en models.py

# 2. Crear migraciones
docker compose exec web python manage.py makemigrations

# 3. Aplicar migraciones
docker compose exec web python manage.py migrate
```

### Resetear base de datos completamente

```bash
# ⚠️ CUIDADO: Esto eliminará TODOS los datos

# Opción 1: Script automatizado (RECOMENDADO)
./reset
# Seleccionar nivel de limpieza deseado

# Opción 2: Manual
./stop-local.sh
# Seleccionar opción 2 (eliminar volúmenes)

# Luego levantar de nuevo
./start-local.sh
```

## 🔄 Resetear Todo desde Cero

### Script de Reset Automatizado

```bash
./reset
# o
./scripts/reset-docker.sh
```

**Niveles de limpieza disponibles:**

| Nivel | Elimina | Mantiene | Uso |
|-------|---------|----------|-----|
| **1. SUAVE** | Contenedores | Datos, Imágenes | Solo detener |
| **2. MEDIA** | Contenedores, Datos | Imágenes | Reset rápido |
| **3. COMPLETA** | Contenedores, Datos, Imágenes | - | Reset total |
| **4. NUCLEAR** | TODO en Docker | - | ⚠️ Afecta otros proyectos |

**Recomendación:** Usa nivel **2 (MEDIA)** para resetear el proyecto manteniendo las imágenes para rebuild rápido.

### Comandos Manuales

```bash
# Limpieza SUAVE (solo detener)
docker compose down

# Limpieza MEDIA (eliminar datos)
docker compose down -v

# Limpieza COMPLETA (eliminar todo del proyecto)
docker compose down -v
docker rmi $(docker images | grep catalogue | awk '{print $3}')
docker system prune -f

# Limpieza NUCLEAR (⚠️ eliminar TODO de Docker)
docker stop $(docker ps -aq)
docker rm $(docker ps -aq)
docker volume rm $(docker volume ls -q)
docker rmi $(docker images -aq) -f
docker system prune -a --volumes -f
```

## 🐛 Troubleshooting

### Docker no está corriendo

```bash
# Error: Cannot connect to the Docker daemon
# Solución: Abre Docker Desktop y espera a que inicie
```

### Puerto ya en uso

```bash
# Error: Bind for 0.0.0.0:8050 failed: port is already allocated
# Solución: Cambiar el puerto en docker-compose.yml o detener el proceso que usa el puerto

# Ver qué proceso usa el puerto
lsof -i :8050

# Matar el proceso
kill -9 <PID>
```

### PostgreSQL no inicia

```bash
# Ver logs de PostgreSQL
docker compose logs db

# Verificar archivos de configuración
ls -la config/postgres/

# Reiniciar solo PostgreSQL
docker compose restart db
```

### Cambios en código no se reflejan

```bash
# 1. Verificar que el volumen esté montado
docker compose exec web ls -la /app

# 2. Reiniciar el servicio web
docker compose restart web

# 3. Si persiste, reconstruir
docker compose build web
docker compose up -d
```

### Eliminar todo y empezar de cero

```bash
# ⚠️ CUIDADO: Esto elimina TODOS los contenedores, imágenes y volúmenes

docker compose down -v
docker system prune -a --volumes
./start-local.sh
```

## 📊 Estructura de Volúmenes

```
catalogue_api_postgres_data   → Datos de PostgreSQL (PERSISTENTE)
catalogue_api_pgadmin_data    → Configuración de pgAdmin (PERSISTENTE)
catalogue_api_static_volume   → Archivos estáticos de Django
catalogue_api_media_volume    → Archivos media de Django
```

### Ver volúmenes

```bash
# Listar volúmenes
docker volume ls

# Ver detalles de un volumen
docker volume inspect catalogue_api_postgres_data

# Eliminar volúmenes no usados
docker volume prune
```

## 🔒 Seguridad

### Variables de entorno sensibles

Las credenciales están en el archivo `.env`. **NUNCA** commitees este archivo a Git.

```bash
# .gitignore ya incluye:
.env
```

### Cambiar credenciales de producción

Para producción, cambia:
- Password de PostgreSQL
- Secret key de Django
- Credenciales de pgAdmin

## 📚 Recursos Adicionales

- [Documentación de Docker Compose](https://docs.docker.com/compose/)
- [Documentación de PostgreSQL](https://www.postgresql.org/docs/)
- [Documentación de pgAdmin](https://www.pgadmin.org/docs/)
- [Documentación de Django](https://docs.djangoproject.com/)

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `./logs`
2. Verifica que Docker esté corriendo
3. Revisa la sección de Troubleshooting
4. Contacta al equipo de desarrollo

---

**Última actualización**: 2026-01-19
