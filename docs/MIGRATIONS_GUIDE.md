# 📋 Guía de Migraciones Django

## 🎯 Flujo Completo: Desarrollo → Producción

---

## 1️⃣ DESARROLLO (Tu Máquina)

### A. Modificar Modelos

```python
# api/models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Agregar nuevo campo
    stock = models.IntegerField(default=0)  # ← NUEVO
```

### B. Crear Migración

```bash
cd /Users/jmarquez/MyApps/catalogue_api

# Levantar entorno local
./start

# Crear migración
docker compose exec web python manage.py makemigrations

# Salida:
# Migrations for 'api':
#   api/migrations/0002_product_stock.py
#     - Add field stock to product
```

### C. Revisar Migración Creada

```bash
# Ver el archivo generado
cat api/migrations/0002_product_stock.py

# Debe mostrar algo como:
# operations = [
#     migrations.AddField(
#         model_name='product',
#         name='stock',
#         field=models.IntegerField(default=0),
#     ),
# ]
```

### D. Aplicar Localmente (Probar)

```bash
# Aplicar migración en tu DB local
docker compose exec web python manage.py migrate

# Salida:
# Running migrations:
#   Applying api.0002_product_stock... OK

# Probar en el shell
docker compose exec web python manage.py shell
>>> from api.models import Product
>>> p = Product.objects.first()
>>> p.stock  # Debe funcionar
0
```

### E. Verificar Estado

```bash
# Ver todas las migraciones
docker compose exec web python manage.py showmigrations

# Debe mostrar:
# api
#  [X] 0001_initial
#  [X] 0002_product_stock  ← NUEVA
```

### F. Commit y Push

```bash
# Agregar archivos
git add api/models.py
git add api/migrations/0002_product_stock.py

# Commit
git commit -m "add stock field to Product model"

# Push
git push origin develop
```

---

## 2️⃣ PRODUCCIÓN (Servidor)

### A. Conectar al Servidor

```bash
ssh root@srv702740
cd /var/ms-catalogue
```

### B. Pull Cambios

```bash
git pull origin develop

# Salida:
# Updating abc123..def456
# Fast-forward
#  api/migrations/0002_product_stock.py | 18 ++++++++++++++++++
#  api/models.py                        |  1 +
#  2 files changed, 19 insertions(+)
```

### C. Deploy Automático

```bash
./quick-deploy.sh

# Qué hace automáticamente:
# 1. Git pull ✅
# 2. Docker down ✅
# 3. Docker build ✅
# 4. Docker up ✅
# 5. Espera PostgreSQL ✅
# 6. Ejecuta: python manage.py migrate --fake-initial --noinput
#    - SKIP 0001_initial (ya aplicada)
#    - APPLY 0002_product_stock (nueva)
# 7. Collectstatic ✅
# 8. Gunicorn ✅
```

### D. Verificar

```bash
# Ver estado de migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations

# Debe mostrar:
# api
#  [X] 0001_initial
#  [X] 0002_product_stock  ← APLICADA

# Probar en el admin
# https://catalogue.favric.cl/admin/
```

---

## 📊 Casos Comunes

### ✅ Agregar Campo

```python
# models.py
class Product(models.Model):
    # ... campos existentes
    new_field = models.CharField(max_length=100, blank=True)
```

```bash
# Desarrollo
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
git add . && git commit -m "add new_field" && git push

# Producción
git pull && ./quick-deploy.sh
```

---

### ✅ Modificar Campo

```python
# models.py
class Product(models.Model):
    # Antes: name = models.CharField(max_length=100)
    name = models.CharField(max_length=200)  # ← Aumentar tamaño
```

```bash
# Desarrollo
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
git add . && git commit -m "increase name max_length" && git push

# Producción
git pull && ./quick-deploy.sh
```

---

### ✅ Crear Nuevo Modelo

```python
# models.py
class NewModel(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```

```bash
# Desarrollo
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
git add . && git commit -m "add NewModel" && git push

# Producción
git pull && ./quick-deploy.sh
```

---

### ✅ Eliminar Campo

```python
# models.py
class Product(models.Model):
    name = models.CharField(max_length=200)
    # old_field = models.CharField(max_length=100)  ← ELIMINADO
```

```bash
# Desarrollo
docker compose exec web python manage.py makemigrations
# Django preguntará si quieres eliminar el campo
# Responde: yes
docker compose exec web python manage.py migrate
git add . && git commit -m "remove old_field" && git push

# Producción
git pull && ./quick-deploy.sh
```

---

## ⚠️ Casos Especiales

### 🔄 Migración con Datos

Si necesitas migrar datos (por ejemplo, renombrar campo):

```python
# migrations/0003_rename_field.py
from django.db import migrations

def migrate_data(apps, schema_editor):
    Product = apps.get_model('api', 'Product')
    for product in Product.objects.all():
        product.new_name = product.old_name
        product.save()

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0002_add_new_name'),
    ]
    
    operations = [
        migrations.RunPython(migrate_data),
        migrations.RemoveField('product', 'old_name'),
    ]
```

---

### 🚨 Si Algo Sale Mal en Producción

```bash
# Ver logs
docker compose -f docker-compose.prod.yml logs -f web

# Ver estado de migraciones
docker compose -f docker-compose.prod.yml exec web python manage.py showmigrations

# Revertir última migración
docker compose -f docker-compose.prod.yml exec web python manage.py migrate api 0001

# Volver a aplicar
docker compose -f docker-compose.prod.yml exec web python manage.py migrate
```

---

## 📝 Checklist Rápido

### Antes de Hacer Push

- [ ] Migración creada con `makemigrations`
- [ ] Migración aplicada localmente con `migrate`
- [ ] Probado en desarrollo (http://localhost:8050/admin/)
- [ ] Archivo de migración agregado a Git
- [ ] Commit con mensaje descriptivo

### En Producción

- [ ] `git pull origin develop`
- [ ] `./quick-deploy.sh`
- [ ] Verificar en https://catalogue.favric.cl/admin/
- [ ] Revisar logs si hay errores

---

## 🎯 Comandos Útiles

```bash
# Ver todas las migraciones
docker compose exec web python manage.py showmigrations

# Ver SQL de una migración (sin ejecutarla)
docker compose exec web python manage.py sqlmigrate api 0002

# Verificar problemas
docker compose exec web python manage.py check

# Crear migración vacía (para RunPython)
docker compose exec web python manage.py makemigrations --empty api

# Marcar migración como aplicada sin ejecutarla (emergencia)
docker compose exec web python manage.py migrate api 0002 --fake
```

---

## 🔒 Reglas de Oro

1. ✅ **SIEMPRE** hacer `makemigrations` en desarrollo, NUNCA en producción
2. ✅ **SIEMPRE** probar migraciones localmente antes de push
3. ✅ **SIEMPRE** hacer commit de archivos de migración
4. ✅ **NUNCA** editar migraciones ya aplicadas en producción
5. ✅ **NUNCA** borrar archivos de migración que ya están en producción
6. ✅ Usar `./quick-deploy.sh` para deploy (maneja migraciones automáticamente)

---

## 📚 Recursos

- [Django Migrations Docs](https://docs.djangoproject.com/en/4.2/topics/migrations/)
- [Django Migration Operations](https://docs.djangoproject.com/en/4.2/ref/migration-operations/)
- [Squashing Migrations](https://docs.djangoproject.com/en/4.2/topics/migrations/#squashing-migrations)

---

**Última actualización**: 2026-01-21
