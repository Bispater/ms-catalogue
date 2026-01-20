# 🚀 Pasos para Migrar a la Arquitectura con Catalogue

> **Guía paso a paso para aplicar la nueva arquitectura con catálogos**  
> **Fecha**: 2026-01-19

---

## ✅ Cambios Realizados

### **1. Nuevo Modelo: Catalogue**
- ✅ Creado modelo `Catalogue` con relación a `Organization`
- ✅ Campos: name, slug, description, organization, is_active
- ✅ Constraint: `unique_together = [['slug', 'organization']]`

### **2. Product Actualizado**
- ✅ Eliminada herencia de `OrganizationRelatedModel`
- ✅ Agregado campo `catalogue` (ForeignKey a Catalogue)
- ✅ Acceso a organization ahora es: `product.catalogue.organization`

### **3. ImportFile Actualizado**
- ✅ Eliminada herencia de `OrganizationRelatedModel`
- ✅ Agregado campo `catalogue` (ForeignKey a Catalogue)
- ✅ Acceso a organization ahora es: `import_file.catalogue.organization`

### **4. Admin Actualizado**
- ✅ Creado `CatalogueAdmin`
- ✅ Actualizado `ProductAdmin` (filtros por catalogue)
- ✅ Actualizado `ImportFileAdmin` (filtros por catalogue)

### **5. Views/Filters Actualizados**
- ✅ `ProductFilterByOrg` actualizado para usar `catalogue__organization__slug`
- ✅ Agregado filtro `catalogue_slug`

### **6. Migración Generada**
- ✅ `api/migrations/0006_remove_importfile_organization_and_more.py`

### **7. Script de Migración de Datos**
- ✅ `scripts/migrate_to_catalogues.py`

---

## 📋 Pasos de Migración

### **Paso 1: Aplicar Migración de Base de Datos**

```bash
# Aplicar la migración
docker compose exec web python manage.py migrate
```

**Resultado esperado**:
```
Running migrations:
  Applying api.0006_remove_importfile_organization_and_more... OK
```

---

### **Paso 2: Ejecutar Script de Migración de Datos**

```bash
# Ejecutar script para crear catálogos por defecto
docker compose exec web python scripts/migrate_to_catalogues.py
```

**Resultado esperado**:
```
================================================================================
🔄 MIGRACIÓN A MODELO CATALOGUE
================================================================================

📦 Procesando: Organización Principal (organizacion-principal)
--------------------------------------------------------------------------------
   ✅ Catálogo creado: Catálogo Principal
   📦 25 productos asociados al catálogo
   📥 3 archivos de importación asociados al catálogo

================================================================================
✅ MIGRACIÓN COMPLETADA
================================================================================
Organizaciones procesadas: 1
Productos migrados: 25
Archivos de importación migrados: 3
================================================================================

✅ Todos los registros tienen catálogo asignado
```

---

### **Paso 3: Verificar en el Admin**

```bash
# Abrir en el navegador
http://localhost:8050/admin/
```

**Verificar**:
1. ✅ Ir a `/admin/api/catalogue/`
2. ✅ Ver catálogos creados
3. ✅ Ir a `/admin/api/product/`
4. ✅ Ver productos con catálogo asignado
5. ✅ Filtrar por catálogo

---

### **Paso 4: Hacer Catalogue Obligatorio (Opcional)**

Una vez que todos los datos estén migrados, puedes hacer el campo `catalogue` obligatorio:

#### **4.1. Editar models.py**

```python
# En Product
catalogue = models.ForeignKey(
    'Catalogue',
    on_delete=models.CASCADE,
    related_name='products',
    # null=True,  # ← Eliminar esta línea
    # blank=True,  # ← Eliminar esta línea
    verbose_name=_('catalogue')
)

# En ImportFile
catalogue = models.ForeignKey(
    'Catalogue',
    on_delete=models.CASCADE,
    related_name='import_files',
    # null=True,  # ← Eliminar esta línea
    # blank=True,  # ← Eliminar esta línea
    verbose_name=_('catalogue')
)
```

#### **4.2. Generar y Aplicar Migración**

```bash
# Generar migración
docker compose exec web python manage.py makemigrations

# Aplicar migración
docker compose exec web python manage.py migrate
```

---

## 🧪 Pruebas

### **Test 1: Crear Catálogo**

```bash
docker compose exec web python manage.py shell
```

```python
from api.models import Organization, Catalogue

# Obtener organización
org = Organization.objects.first()

# Crear catálogo
catalogue = Catalogue.objects.create(
    name="Catálogo de Verano 2026",
    slug="verano-2026",
    organization=org,
    description="Productos de temporada verano",
    is_active=True
)

print(f"✅ Catálogo creado: {catalogue}")
```

---

### **Test 2: Crear Producto en Catálogo**

```python
from api.models import Catalogue, Product

# Obtener catálogo
catalogue = Catalogue.objects.get(slug='verano-2026')

# Crear producto
product = Product.objects.create(
    catalogue=catalogue,
    sku="SKU-VERANO-001",
    name="Traje de Baño",
    price_1=29990,
    currency="CLP",
    state="publish"
)

print(f"✅ Producto creado: {product.name}")
print(f"   Catálogo: {product.catalogue.name}")
print(f"   Organización: {product.catalogue.organization.name}")
```

---

### **Test 3: Filtrar Productos por Catálogo**

```python
from api.models import Catalogue, Product

# Por catálogo
catalogue = Catalogue.objects.get(slug='verano-2026')
products = catalogue.products.all()
print(f"Productos en {catalogue.name}: {products.count()}")

# Por organización (a través de catálogo)
org = Organization.objects.first()
products = Product.objects.filter(catalogue__organization=org)
print(f"Productos de {org.name}: {products.count()}")
```

---

### **Test 4: API Endpoints**

```bash
# Filtrar por organización
curl "http://localhost:8050/api/products/?org_slug=organizacion-principal"

# Filtrar por catálogo
curl "http://localhost:8050/api/products/?catalogue_slug=verano-2026"

# Ambos filtros
curl "http://localhost:8050/api/products/?org_slug=organizacion-principal&catalogue_slug=verano-2026"
```

---

## 🔄 Actualizar Scripts de Importación

### **Antes**

```python
def transform_and_import(excel_path, organization_slug, import_mode='soft_delete'):
    organization = Organization.objects.get(slug=organization_slug)
    
    product, created = Product.objects.update_or_create(
        sku=sku,
        organization=organization,  # ← Antiguo
        defaults={...}
    )
```

### **Ahora**

```python
def transform_and_import(excel_path, catalogue_slug, import_mode='soft_delete'):
    catalogue = Catalogue.objects.get(slug=catalogue_slug)
    organization = catalogue.organization
    
    product, created = Product.objects.update_or_create(
        sku=sku,
        catalogue=catalogue,  # ← Nuevo
        defaults={...}
    )
```

### **Uso**

```bash
# Antes
python scripts/transform_client_excel.py excel.xlsx tienda-abc --mode soft_delete

# Ahora
python scripts/transform_client_excel.py excel.xlsx catalogo-principal --mode soft_delete
```

---

## ⚠️ Consideraciones Importantes

### **1. Queries Existentes**

Actualizar queries que usaban `organization`:

```python
# Antes
Product.objects.filter(organization=org)
Category.objects.filter(organization=org)

# Ahora
Product.objects.filter(catalogue__organization=org)
Category.objects.filter(organization=org)  # ← Category NO cambió
```

### **2. Serializers**

Si tienes serializers personalizados, actualizar:

```python
# Antes
class ProductSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='organization.name')

# Ahora
class ProductSerializer(serializers.ModelSerializer):
    organization_name = serializers.CharField(source='catalogue.organization.name')
    catalogue_name = serializers.CharField(source='catalogue.name')
```

### **3. Permisos**

Actualizar lógica de permisos si filtraban por organization:

```python
# Antes
def has_permission(self, request, view):
    return request.user.organization == obj.organization

# Ahora
def has_permission(self, request, view):
    return request.user.organization == obj.catalogue.organization
```

---

## 📊 Verificación Post-Migración

### **Checklist**

- [ ] Migración de BD aplicada (`0006_remove_importfile_organization_and_more`)
- [ ] Script de migración de datos ejecutado
- [ ] Todos los productos tienen catálogo asignado
- [ ] Todos los import files tienen catálogo asignado
- [ ] Admin muestra catálogos correctamente
- [ ] Admin muestra productos con catálogo
- [ ] Filtros en admin funcionan
- [ ] API endpoints funcionan con nuevos filtros
- [ ] Scripts de importación actualizados
- [ ] Tests actualizados (si existen)

### **Comandos de Verificación**

```bash
# Verificar que no hay productos sin catálogo
docker compose exec web python manage.py shell -c "
from api.models import Product
count = Product.objects.filter(catalogue__isnull=True).count()
print(f'Productos sin catálogo: {count}')
"

# Verificar que no hay import files sin catálogo
docker compose exec web python manage.py shell -c "
from api.models import ImportFile
count = ImportFile.objects.filter(catalogue__isnull=True).count()
print(f'Import files sin catálogo: {count}')
"

# Ver estadísticas
docker compose exec web python manage.py shell -c "
from api.models import Organization, Catalogue, Product
for org in Organization.objects.all():
    catalogues = org.catalogues.count()
    products = Product.objects.filter(catalogue__organization=org).count()
    print(f'{org.name}: {catalogues} catálogos, {products} productos')
"
```

---

## 🎯 Próximos Pasos

1. ✅ Aplicar migración
2. ✅ Ejecutar script de migración de datos
3. ✅ Verificar en admin
4. ⏳ Actualizar scripts de importación
5. ⏳ Actualizar documentación de API
6. ⏳ Actualizar tests (si existen)
7. ⏳ Hacer catalogue obligatorio (opcional)

---

## 📚 Documentación Relacionada

- **Arquitectura**: `CATALOGUE_ARCHITECTURE.md`
- **Modelo Catalogue**: `api/models.py` línea ~449
- **Admin**: `api/admin.py`
- **Script de migración**: `scripts/migrate_to_catalogues.py`

---

**Fin de la guía de migración**  
**Estado**: ✅ Listo para aplicar
