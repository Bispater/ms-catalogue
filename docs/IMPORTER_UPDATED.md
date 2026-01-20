# ✅ Importador y Views Actualizados para Catalogue

> **Resumen de actualizaciones del importador y views**  
> **Fecha**: 2026-01-20

---

## 🎉 **ACTUALIZACIONES COMPLETADAS**

---

## 📦 **Script de Importación Actualizado**

### **Archivo**: `scripts/transform_client_excel.py`

### **Cambios Realizados** ✅

#### **1. Imports Actualizados**
```python
# Antes
from api.models import Product, Category, Brand, Images, Organization

# Ahora
from api.models import Product, Category, Brand, Images, Organization, Catalogue
```

#### **2. Firma de Función Actualizada**
```python
# Antes
def transform_and_import(excel_path, organization_slug, import_mode='soft_delete', download_images=True):

# Ahora
def transform_and_import(excel_path, catalogue_slug, import_mode='soft_delete', download_images=True):
```

#### **3. Obtención de Catálogo**
```python
# Antes
organization = Organization.objects.get(slug=organization_slug)

# Ahora
catalogue = Catalogue.objects.get(slug=catalogue_slug)
organization = catalogue.organization
```

#### **4. Filtros Actualizados**
```python
# Antes
Product.objects.filter(organization=organization)

# Ahora
Product.objects.filter(catalogue=catalogue)
```

#### **5. Creación de Productos**
```python
# Antes
Product.objects.update_or_create(
    sku=sku,
    organization=organization,
    defaults=product_data
)

# Ahora
Product.objects.update_or_create(
    sku=sku,
    catalogue=catalogue,
    defaults=product_data
)
```

#### **6. Argumentos CLI Actualizados**
```python
# Antes
parser.add_argument('organization', help='Slug de la organización')

# Ahora
parser.add_argument('catalogue', help='Slug del catálogo (ej: catalogo-principal, verano-2026)')
```

---

## 🔄 **Uso Actualizado del Script**

### **Sintaxis Anterior** ❌
```bash
python scripts/transform_client_excel.py excel.xlsx organizacion-principal --mode soft_delete
```

### **Sintaxis Nueva** ✅
```bash
python scripts/transform_client_excel.py excel.xlsx catalogo-principal --mode soft_delete
```

---

## 📋 **Ejemplos de Uso**

### **1. Importar al Catálogo Principal**
```bash
python scripts/transform_client_excel.py productos.xlsx catalogo-principal --mode soft_delete
```

**Salida esperada**:
```
================================================================================
🚀 TRANSFORMACIÓN E IMPORTACIÓN DE PRODUCTOS
================================================================================
Archivo: productos.xlsx
Catálogo: catalogo-principal
Modo: soft_delete
Descargar imágenes: True
================================================================================

✅ Catálogo encontrado: Catálogo Principal
   Organización: Organización Principal
✅ Excel leído: 25 filas
✅ Columnas validadas

📋 Modo de importación: soft_delete
--------------------------------------------------------------------------------
👻 0 productos marcados como eliminados
   (Se reactivarán los que estén en el Excel)

📦 Procesando productos...
--------------------------------------------------------------------------------
✅ CREADO: SKU-12345 - Producto 1
   📷 Imagen descargada: IMG-12345.jpg
...

================================================================================
✅ IMPORTACIÓN COMPLETADA
================================================================================
Total procesado: 25
Creados: 25
Actualizados: 0
Reactivados: 0
Ocultos (no en Excel): 0
Errores: 0
================================================================================
```

---

### **2. Importar a Catálogo de Verano**
```bash
# Primero crear el catálogo
docker compose exec web python manage.py shell

from api.models import Organization, Catalogue
org = Organization.objects.get(slug='organizacion-principal')
verano = Catalogue.objects.create(
    name="Verano 2026",
    slug="verano-2026",
    organization=org,
    description="Productos de temporada verano"
)

# Luego importar
python scripts/transform_client_excel.py productos_verano.xlsx verano-2026 --mode soft_delete
```

---

### **3. Importar Solo Nuevos Productos**
```bash
python scripts/transform_client_excel.py productos.xlsx catalogo-principal --mode create_only
```

---

### **4. Importar Sin Descargar Imágenes**
```bash
python scripts/transform_client_excel.py productos.xlsx catalogo-principal --no-images
```

---

### **5. Reemplazar Todo (Peligroso)**
```bash
python scripts/transform_client_excel.py productos.xlsx catalogo-principal --mode replace_all

# Requiere confirmación: escribir "ELIMINAR TODO"
```

---

## 🔍 **Views Actualizados**

### **Archivo**: `api/views.py`

### **Cambios Realizados** ✅

#### **1. ProductFilterByOrg** (Ya actualizado)
```python
class ProductFilterByOrg(django_filters.FilterSet):
    org_slug = CharFilter(field_name='catalogue__organization__slug')
    catalogue_slug = CharFilter(field_name='catalogue__slug')  # ← NUEVO
    
    class Meta:
        fields = ['state', 'brand', 'categories', 'catalogue', 'org_slug', 'catalogue_slug']
```

#### **2. SlideFilter** (Ya actualizado)
```python
class SlideFilter(django_filters.FilterSet):
    org_slug = CharFilter(field_name='catalogue__organization__slug')
    catalogue_slug = CharFilter(field_name='catalogue__slug')  # ← NUEVO
    
    class Meta:
        fields = ['state', 'virtual', 'catalogue', 'org_slug', 'catalogue_slug']
```

#### **3. ClientConfigurationViewSet** ✅
```python
class ClientConfigurationViewSet(viewsets.ReadOnlyModelViewSet):
    filterset_fields = ['is_active', 'catalogue', 'organization_id']  # ← catalogue agregado
```

#### **4. CategoryFilter y BrandFilter** (SIN CAMBIOS)
```python
# Estos NO cambiaron porque Category y Brand siguen usando organization
class CategoryFilter(django_filters.FilterSet):
    org_slug = CharFilter(field_name='organization__slug')  # ← Correcto
    
class BrandFilter(django_filters.FilterSet):
    org_slug = CharFilter(field_name='organization__slug')  # ← Correcto
```

---

## 🌐 **API Endpoints Actualizados**

### **Productos**

#### **Filtrar por Organización** (Sigue funcionando)
```bash
curl "http://localhost:8050/api/products/?org_slug=organizacion-principal"
```

#### **Filtrar por Catálogo** ✅ (NUEVO)
```bash
curl "http://localhost:8050/api/products/?catalogue_slug=catalogo-principal"
curl "http://localhost:8050/api/products/?catalogue_slug=verano-2026"
```

#### **Filtrar por Ambos**
```bash
curl "http://localhost:8050/api/products/?org_slug=organizacion-principal&catalogue_slug=verano-2026"
```

---

### **Slides**

#### **Filtrar por Catálogo** ✅ (NUEVO)
```bash
curl "http://localhost:8050/api/slides/?catalogue_slug=catalogo-principal"
curl "http://localhost:8050/api/slides/?catalogue_slug=verano-2026"
```

---

### **Client Configurations**

#### **Filtrar por Catálogo** ✅ (NUEVO)
```bash
curl "http://localhost:8050/api/client-config/?catalogue=1"
```

---

## 📊 **Flujo Completo de Importación**

### **Paso 1: Crear Catálogo (si no existe)**
```bash
docker compose exec web python manage.py shell
```

```python
from api.models import Organization, Catalogue

org = Organization.objects.get(slug='organizacion-principal')

catalogue = Catalogue.objects.create(
    name="Catálogo Verano 2026",
    slug="verano-2026",
    organization=org,
    description="Productos de temporada verano 2026",
    is_active=True
)

print(f"✅ Catálogo creado: {catalogue.slug}")
```

---

### **Paso 2: Analizar Excel**
```bash
python scripts/analyze_client_excel.py productos_verano.xlsx
```

---

### **Paso 3: Importar**
```bash
python scripts/transform_client_excel.py productos_verano.xlsx verano-2026 --mode soft_delete
```

---

### **Paso 4: Verificar en Admin**
```
http://localhost:8050/admin/api/product/

Filtrar por:
- Catalogue: Catálogo Verano 2026
```

---

## 🎯 **Modos de Importación**

| Modo | Descripción | Uso |
|------|-------------|-----|
| `soft_delete` | Sincroniza: actualiza, crea y oculta no incluidos | ⭐ Recomendado |
| `update` | Actualiza existentes y crea nuevos | Actualizaciones parciales |
| `create_only` | Solo crea nuevos, no actualiza | Agregar productos |
| `replace_all` | Elimina todo y recrea | ⚠️ Peligroso |

---

## ✅ **Checklist de Actualización**

### **Script de Importación**
- [x] Imports actualizados (Catalogue agregado)
- [x] Firma de función actualizada (catalogue_slug)
- [x] Obtención de catálogo implementada
- [x] Filtros actualizados (catalogue en lugar de organization)
- [x] Creación de productos actualizada
- [x] Argumentos CLI actualizados
- [x] Mensajes de error actualizados

### **Views**
- [x] ProductFilterByOrg actualizado
- [x] SlideFilter actualizado
- [x] ClientConfigurationViewSet actualizado
- [x] CategoryFilter sin cambios (correcto)
- [x] BrandFilter sin cambios (correcto)

### **Documentación**
- [x] Guía de uso actualizada
- [x] Ejemplos actualizados
- [x] API endpoints documentados

---

## 🚀 **Próximos Pasos**

### **1. Probar Importación**
```bash
# Crear catálogo de prueba
docker compose exec web python manage.py shell

from api.models import Organization, Catalogue
org = Organization.objects.first()
cat = Catalogue.objects.create(
    name="Test Catalogue",
    slug="test-catalogue",
    organization=org
)

# Importar datos de prueba
python scripts/transform_client_excel.py test_products.xlsx test-catalogue --mode soft_delete
```

---

### **2. Actualizar Documentación de Usuario**
- Actualizar `IMPORT_GUIDE.md` con nuevos ejemplos
- Actualizar `README.md` con sintaxis nueva

---

### **3. Crear Catálogos Adicionales (Opcional)**
```python
# Catálogos por temporada
verano = Catalogue.objects.create(name="Verano 2026", slug="verano-2026", organization=org)
invierno = Catalogue.objects.create(name="Invierno 2026", slug="invierno-2026", organization=org)

# Catálogos por canal
b2b = Catalogue.objects.create(name="Mayorista", slug="b2b", organization=org)
b2c = Catalogue.objects.create(name="Retail", slug="b2c", organization=org)
```

---

## 📚 **Documentación Relacionada**

| Archivo | Contenido |
|---------|-----------|
| `CATALOGUE_COMPLETE.md` | Resumen completo de migración |
| `CATALOGUE_ARCHITECTURE.md` | Arquitectura y casos de uso |
| `IMPORT_GUIDE.md` | Guía de importación (actualizar) |
| `FIELD_MAPPING.md` | Mapeo de campos Excel → Modelo |
| `IMPORTER_UPDATED.md` | Este archivo |

---

## ✅ **Resumen**

### **Completado**:
- ✅ Script de importación actualizado para usar Catalogue
- ✅ Todos los filtros de Product actualizados
- ✅ Todos los filtros de Slide actualizados
- ✅ ClientConfiguration filtros actualizados
- ✅ Argumentos CLI actualizados
- ✅ Mensajes y documentación actualizados

### **Sintaxis Nueva**:
```bash
# Antes
python scripts/transform_client_excel.py excel.xlsx organizacion-principal

# Ahora
python scripts/transform_client_excel.py excel.xlsx catalogo-principal
```

---

**Estado**: ✅ **IMPORTADOR 100% ACTUALIZADO**  
**Próximo paso**: Probar importación con datos reales

---

**Fin del documento**
