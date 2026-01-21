# 🎉 Deployment Issues - RESUELTO

**Fecha**: 2026-01-21  
**Estado**: ✅ COMPLETADO

---

## 🚨 Problemas Encontrados y Solucionados

### **1. Django usaba SQLite en lugar de PostgreSQL**

**Problema**:
- Django siempre usaba SQLite (`/app/db.sqlite3`) en producción
- Los datos se perdían en cada deploy

**Causa Raíz**:
- `settings.py` requería `DOCKER_ENV=true` para usar PostgreSQL
- Esta variable NO existía en `.env.prod`

**Solución**:
```bash
# Agregado a .env.prod
DOCKER_ENV=true
```

---

### **2. PostgreSQL no creaba el usuario `catalogue_user`**

**Problema**:
```
FATAL: role "catalogue_user" does not exist
```

**Causa Raíz**:
- `docker-compose.prod.yml` usaba variables con expansión `${POSTGRES_USER}`
- Docker Compose no expandía las variables correctamente
- PostgreSQL recibía valores por defecto (`postgres`)

**Solución**:
```yaml
# ANTES (no funcionaba):
db:
  environment:
    POSTGRES_DB: ${POSTGRES_DB}
    POSTGRES_USER: ${POSTGRES_USER}
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}

# DESPUÉS (funciona):
db:
  env_file:
    - .env.prod
  # Sin environment, usa directamente las variables de .env.prod
```

---

### **3. quick-deploy.sh ejecutaba migraciones automáticamente**

**Problema**:
- `quick-deploy.sh` ejecutaba `migrate --fake-initial`
- Esto podía causar problemas con migraciones conflictivas

**Solución**:
- Removido `migrate` automático de `quick-deploy.sh`
- Migraciones se ejecutan **manualmente** solo cuando sea necesario

---

## ✅ Configuración Final

### **Archivos Modificados**

1. **`.env.prod`**
   - Agregado `DOCKER_ENV=true`

2. **`docker-compose.prod.yml`**
   - Agregado `env_file: - .env.prod` a servicios `db` y `db-backup`
   - Removido `environment` con expansión de variables
   - Fijado healthcheck con usuario correcto

3. **`quick-deploy.sh`**
   - Removido `migrate` automático
   - Agregado mensaje indicando que migraciones son manuales

---

## 🚀 Flujo de Deploy Correcto

### **Primera Vez (Setup)**

```bash
# 1. Limpiar todo
./reset

# 2. Iniciar servicios
./start-prod

# 3. Aplicar migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Crear superuser
./scripts/create-superuser.sh

# 5. Acceder
https://catalogue.favric.cl/admin/
```

---

### **Deploy Normal (Código sin cambios de modelos)**

```bash
# 1. Pull cambios
git pull origin develop

# 2. Deploy
./quick-deploy.sh

# 3. Listo ✅
# NO ejecuta migraciones
# Datos se mantienen intactos
```

---

### **Deploy con Cambios de Modelos**

```bash
# En desarrollo:
docker compose exec web python manage.py makemigrations
git add api/migrations/
git commit -m "add migration"
git push origin develop

# En producción:
git pull origin develop
./quick-deploy.sh

# Aplicar migraciones MANUALMENTE
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---

## 📊 Verificación

### **Verificar que usa PostgreSQL**

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from django.conf import settings
>>> print("DB Engine:", settings.DATABASES['default']['ENGINE'])
DB Engine: django.db.backends.postgresql
>>> print("DB Name:", settings.DATABASES['default']['NAME'])
DB Name: catalogue_favric_prod
>>> exit()
```

### **Verificar usuario de PostgreSQL**

```bash
docker compose -f docker-compose.prod.yml exec db env | grep POSTGRES
# Debe mostrar:
# POSTGRES_USER=catalogue_user
# POSTGRES_PASSWORD=357357@Favric
# POSTGRES_DB=catalogue_favric_prod
```

### **Verificar tablas**

```bash
docker compose -f docker-compose.prod.yml exec db psql -U catalogue_user -d catalogue_favric_prod -c "\dt"
# Debe mostrar las tablas: auth_user, api_product, etc.
```

---

## 🎯 Resultado Final

✅ Django usa PostgreSQL correctamente  
✅ PostgreSQL tiene el usuario `catalogue_user`  
✅ Datos persisten entre deploys  
✅ `quick-deploy.sh` es seguro (no ejecuta migraciones)  
✅ Migraciones se aplican manualmente con control total  
✅ Sistema funcionando en producción: https://catalogue.favric.cl/admin/  

---

## 📝 Lecciones Aprendidas

1. **Variables de entorno**: Usar `env_file` directamente es más confiable que expansión de variables
2. **PostgreSQL**: El usuario solo se crea en la primera inicialización del volumen
3. **Migraciones**: Mejor control manual que automático en producción
4. **Debug**: Verificar siempre qué base de datos está usando Django con `settings.DATABASES`

---

**Problema resuelto**: 2026-01-21  
**Tiempo total**: ~3 horas  
**Estado**: ✅ PRODUCCIÓN FUNCIONANDO
