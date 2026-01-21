# 🔧 TODO: Solucionar Problema de Migraciones

**Fecha**: 2026-01-21  
**Problema**: `quick-deploy.sh` está borrando la base de datos cada vez que se ejecuta

---

## 🚨 **PROBLEMA IDENTIFICADO**

1. ✅ Volúmenes de Docker están bien (no se borran)
2. ❌ El problema es la migración `0001_initial.py`
3. ❌ Django intenta ejecutarla y recrea las tablas
4. ❌ Resultado: Se pierden todos los datos

---

## ✅ **SOLUCIONES A PROBAR MAÑANA**

### **Solución 1: Quitar Migrate Automático** ⭐ (Recomendada)

**Archivo**: `quick-deploy.sh`

**Cambio**:
```bash
# COMENTAR estas líneas (líneas 46-50):
# # 6. Aplicar solo migraciones nuevas (no recrea tablas existentes)
# echo -e "${YELLOW}🔄 Aplicando migraciones nuevas...${NC}"
# docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --fake-initial --noinput || {
#     echo -e "${YELLOW}⚠️  No hay migraciones nuevas o error${NC}"
# }
```

**Resultado**: 
- `quick-deploy.sh` NO ejecutará migraciones automáticamente
- Ejecutar migraciones MANUALMENTE solo cuando sea necesario
- Más control, menos riesgo

---

### **Solución 2: Marcar Migración como Fake**

**En el servidor**, ejecutar UNA VEZ:

```bash
# 1. Levantar servicios
docker compose -f docker-compose.prod.yml up -d

# 2. Marcar 0001_initial como aplicada SIN ejecutarla
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --fake

# 3. Verificar
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations

# Debe mostrar:
# api
#  [X] 0001_initial  ← Marcada como aplicada
```

**Luego**, `quick-deploy.sh` no intentará aplicarla de nuevo.

---

### **Solución 3: Fijar Nombre de Volumen**

**Archivo**: `docker-compose.prod.yml`

**Cambio**:
```yaml
volumes:
  postgres_data:
    name: catalogue_postgres_data_prod  # ← Nombre fijo, no cambia
  static_volume:
  media_volume:
```

**Resultado**: Docker siempre usará el mismo volumen, no creará uno nuevo.

---

## 📋 **PASOS PARA MAÑANA**

### **Paso 1: Diagnóstico**

```bash
# En el servidor
cd /var/ms-catalogue

# Ver qué volumen se está usando
docker volume ls | grep postgres
docker inspect ms-catalogue-db-1 | grep -A 5 "Mounts"

# Ver estado de migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations
```

---

### **Paso 2: Aplicar Solución 1** (Recomendada)

```bash
# En tu máquina
cd /Users/jmarquez/MyApps/catalogue_api

# Editar quick-deploy.sh
# Comentar líneas 46-50 (el bloque de migrate)

# Commit
git add quick-deploy.sh
git commit -m "remove auto-migrate from quick-deploy for safety"
git push origin develop
```

---

### **Paso 3: En el Servidor**

```bash
# Pull cambios
cd /var/ms-catalogue
git pull origin develop

# Aplicar migraciones MANUALMENTE (una vez)
docker compose -f docker-compose.prod.yml exec web python manage.py migrate --fake

# Crear superuser
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Probar deploy (ahora NO debe borrar datos)
./quick-deploy.sh
```

---

### **Paso 4: Verificar**

```bash
# Acceder al admin
https://catalogue.favric.cl/admin/

# Verificar que el superuser sigue existiendo
# Verificar que los datos NO se borraron
```

---

## 🔄 **FLUJO FUTURO (Después del Fix)**

### **Para Cambios de Código Normal**

```bash
# En el servidor
git pull origin develop
./quick-deploy.sh  # ✅ Seguro, NO ejecuta migraciones
```

### **Para Cambios de Modelos (con migraciones)**

```bash
# En tu máquina
docker compose exec web python manage.py makemigrations
git add api/migrations/
git commit -m "add migration"
git push origin develop

# En el servidor
git pull origin develop
./quick-deploy.sh  # ✅ NO ejecuta migraciones automáticamente

# Ejecutar migración MANUALMENTE
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---

## 📝 **NOTAS IMPORTANTES**

1. ✅ El problema NO son los volúmenes (están bien)
2. ✅ El problema es que Django ejecuta `0001_initial.py` y recrea tablas
3. ✅ `--fake-initial` NO funciona porque la migración es diferente a las viejas
4. ✅ Solución: NO ejecutar migraciones automáticamente en `quick-deploy.sh`
5. ✅ Ejecutar migraciones MANUALMENTE solo cuando sea necesario

---

## 🎯 **OBJETIVO**

- ✅ `quick-deploy.sh` debe ser SEGURO (no borrar datos)
- ✅ Migraciones se ejecutan MANUALMENTE con control total
- ✅ Datos en producción están PROTEGIDOS

---

## 📞 **ESTADO ACTUAL**

- ✅ Nginx funcionando en el host
- ✅ Django funcionando en Docker
- ✅ Google Cloud Storage configurado
- ✅ Scripts de deploy creados
- ✅ Documentación completa
- ❌ **PENDIENTE**: Solucionar problema de migraciones

---

**Próxima sesión**: Aplicar Solución 1 y verificar que funciona

---

**Buenas noches! 😴🌙**
