# 🚀 Pasos para Activar el Sistema de Importación Híbrido

> **Guía paso a paso para implementar el modo híbrido de importación**  
> **Fecha**: 2026-01-19

---

## ✅ Cambios Realizados

### **1. Modelo ImportFile Actualizado**

Se agregó el campo `import_mode` al modelo `ImportFile`:

```python
import_mode = models.CharField(
    max_length=20,
    choices=[
        ('update', 'Actualizar existentes y crear nuevos'),
        ('create_only', 'Solo crear nuevos (no actualizar)'),
        ('replace_all', 'Reemplazar todo (eliminar y recrear)'),
        ('soft_delete', 'Sincronizar (ocultar no incluidos)'),
    ],
    default='soft_delete',
    verbose_name='import mode'
)
```

**Ubicación**: `api/models.py` línea ~388

---

### **2. Scripts Creados**

| Script | Propósito |
|--------|-----------|
| `scripts/analyze_client_excel.py` | Analizar Excel antes de importar |
| `scripts/transform_client_excel.py` | Transformar e importar con modo híbrido |

---

### **3. Documentación Creada**

| Archivo | Contenido |
|---------|-----------|
| `FIELD_MAPPING.md` | Mapeo completo de campos |
| `IMPORT_GUIDE.md` | Guía de uso de los scripts |
| `MIGRATION_STEPS.md` | Este archivo |

---

## 🔧 Pasos de Implementación

### **Paso 1: Crear Migración de Base de Datos**

```bash
# Generar migración para el nuevo campo import_mode
docker compose exec web python manage.py makemigrations

# Deberías ver algo como:
# Migrations for 'api':
#   api/migrations/0003_importfile_import_mode.py
#     - Add field import_mode to importfile
```

---

### **Paso 2: Aplicar Migración**

```bash
# Aplicar la migración
docker compose exec web python manage.py migrate

# Deberías ver:
# Running migrations:
#   Applying api.0003_importfile_import_mode... OK
```

---

### **Paso 3: Verificar en el Admin**

```bash
# 1. Ir a: http://localhost:8050/admin/api/importfile/add/
# 2. Verificar que aparezca el campo "Import mode" con las opciones:
#    - Actualizar existentes y crear nuevos
#    - Solo crear nuevos (no actualizar)
#    - Reemplazar todo (eliminar y recrear)
#    - Sincronizar (ocultar no incluidos)
```

---

### **Paso 4: Crear Organización de Prueba**

```bash
# Entrar al shell de Django
docker compose exec web python manage.py shell

# Ejecutar:
from api.models import Organization

# Crear organización
org = Organization.objects.create(
    name="Tienda de Prueba",
    slug="tienda-prueba",
    description="Organización para pruebas de importación"
)

print(f"✅ Organización creada: {org.slug}")
exit()
```

---

### **Paso 5: Probar con Excel de Ejemplo**

```bash
# 1. Crear un Excel de prueba con estas columnas:
#    ID_SKU, NOMBRE, PRECIO, CATEGORIA, IMAGEN, DESCRIPCION, ETIQUETA

# 2. Analizar el Excel
python scripts/analyze_client_excel.py test_products.xlsx

# 3. Importar (modo soft_delete)
python scripts/transform_client_excel.py test_products.xlsx tienda-prueba --mode soft_delete

# 4. Verificar en el admin
# http://localhost:8050/admin/api/product/
```

---

## 🧪 Casos de Prueba

### **Test 1: Importación Inicial (soft_delete)**

```bash
# Excel con 5 productos
python scripts/transform_client_excel.py test1.xlsx tienda-prueba --mode soft_delete

# Resultado esperado:
# - 5 productos creados
# - 0 actualizados
# - 0 ocultos
```

---

### **Test 2: Actualización con Nuevos Productos (soft_delete)**

```bash
# Excel con 7 productos (5 existentes + 2 nuevos)
python scripts/transform_client_excel.py test2.xlsx tienda-prueba --mode soft_delete

# Resultado esperado:
# - 2 productos creados
# - 5 productos actualizados
# - 0 ocultos
```

---

### **Test 3: Sincronización (soft_delete)**

```bash
# Excel con 4 productos (falta 1 del anterior)
python scripts/transform_client_excel.py test3.xlsx tienda-prueba --mode soft_delete

# Resultado esperado:
# - 0 productos creados
# - 4 productos actualizados
# - 3 productos ocultos (is_removed=True)
```

---

### **Test 4: Solo Crear Nuevos (create_only)**

```bash
# Excel con 6 productos (4 existentes + 2 nuevos)
python scripts/transform_client_excel.py test4.xlsx tienda-prueba --mode create_only

# Resultado esperado:
# - 2 productos creados
# - 0 productos actualizados
# - 4 productos omitidos
```

---

### **Test 5: Actualizar sin Eliminar (update)**

```bash
# Excel con 5 productos (3 existentes + 2 nuevos)
python scripts/transform_client_excel.py test5.xlsx tienda-prueba --mode update

# Resultado esperado:
# - 2 productos creados
# - 3 productos actualizados
# - Productos no en Excel quedan sin cambios
```

---

## 🔍 Verificación Post-Migración

### **1. Verificar Campo en BD**

```bash
docker compose exec web python manage.py dbshell

# Ejecutar:
\d api_importfile

# Deberías ver la columna: import_mode | character varying(20)
```

---

### **2. Verificar Productos Ocultos**

```bash
docker compose exec web python manage.py shell

from api.models import Product, Organization

org = Organization.objects.get(slug='tienda-prueba')

# Ver productos activos
activos = Product.objects.filter(organization=org, is_removed=False).count()
print(f"Productos activos: {activos}")

# Ver productos ocultos
ocultos = Product.objects.filter(organization=org, is_removed=True).count()
print(f"Productos ocultos: {ocultos}")
```

---

### **3. Verificar en el Admin**

```
1. Ir a: http://localhost:8050/admin/api/product/
2. Agregar filtro: "Organization" = "Tienda de Prueba"
3. Agregar filtro: "Is removed" = "Yes"
4. Verificar que se muestran los productos ocultos
```

---

## 🎯 Checklist de Implementación

- [ ] Cambio en `api/models.py` aplicado (campo `import_mode`)
- [ ] Migración creada (`makemigrations`)
- [ ] Migración aplicada (`migrate`)
- [ ] Scripts creados y ejecutables
- [ ] Organización de prueba creada
- [ ] Test 1: Importación inicial ✅
- [ ] Test 2: Actualización con nuevos ✅
- [ ] Test 3: Sincronización ✅
- [ ] Test 4: Solo crear nuevos ✅
- [ ] Test 5: Actualizar sin eliminar ✅
- [ ] Verificación en admin ✅
- [ ] Documentación revisada ✅

---

## 🚨 Rollback (Si algo sale mal)

### **Revertir Migración**

```bash
# Ver migraciones aplicadas
docker compose exec web python manage.py showmigrations api

# Revertir a la migración anterior
docker compose exec web python manage.py migrate api 0002_previous_migration

# Eliminar archivo de migración
rm api/migrations/0003_importfile_import_mode.py
```

---

### **Restaurar Backup**

```bash
# Si hiciste backup antes
docker compose exec -T db psql -U postgres ms_catalogue_db < backup_20260119.sql
```

---

## 📊 Monitoreo

### **Ver Logs de Importación**

```bash
# Si usas el script directamente
python scripts/transform_client_excel.py excel.xlsx org --mode soft_delete 2>&1 | tee import_log.txt
```

---

### **Estadísticas de Productos**

```bash
docker compose exec web python manage.py shell

from api.models import Product, Organization
from django.db.models import Count

# Por organización
stats = Product.objects.values('organization__name').annotate(
    total=Count('id'),
    activos=Count('id', filter=Q(is_removed=False)),
    ocultos=Count('id', filter=Q(is_removed=True))
)

for stat in stats:
    print(f"{stat['organization__name']}:")
    print(f"  Total: {stat['total']}")
    print(f"  Activos: {stat['activos']}")
    print(f"  Ocultos: {stat['ocultos']}")
```

---

## 🎉 Próximos Pasos

Una vez completada la implementación:

1. ✅ Probar con Excel real del cliente
2. ✅ Ajustar lista de `MARCAS_CONOCIDAS` si es necesario
3. ✅ Documentar casos especiales del cliente
4. ✅ Entrenar al equipo en el uso de los scripts
5. ✅ Configurar backups automáticos antes de importaciones

---

## 📚 Referencias

- **Guía de Importación**: `IMPORT_GUIDE.md`
- **Mapeo de Campos**: `FIELD_MAPPING.md`
- **Script de Análisis**: `scripts/analyze_client_excel.py`
- **Script de Transformación**: `scripts/transform_client_excel.py`

---

**Fin de los pasos de migración**  
**Estado**: ✅ Listo para implementar
