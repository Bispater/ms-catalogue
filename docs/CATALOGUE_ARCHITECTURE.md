# 🏗️ Nueva Arquitectura: Modelo Catalogue

> **Cambio arquitectónico importante: Introducción del modelo Catalogue**  
> **Fecha**: 2026-01-19

---

## 📊 Arquitectura Anterior vs Nueva

### **Antes** (Arquitectura Plana)

```
Organization (1) ──→ (N) Product
Organization (1) ──→ (N) Category
Organization (1) ──→ (N) Brand
Organization (1) ──→ (N) Images
Organization (1) ──→ (N) ImportFile
```

**Problema**: Una organización solo podía tener un catálogo implícito.

---

### **Ahora** (Arquitectura con Catálogos)

```
Organization (1) ──→ (N) Catalogue (1) ──→ (N) Product
                           ↑
                           │
                      ImportFile

Organization (1) ──→ (N) Category  (compartidas)
Organization (1) ──→ (N) Brand     (compartidas)
Organization (1) ──→ (N) Images    (compartidas)
```

**Ventaja**: Una organización puede tener **múltiples catálogos**.

---

## 🎯 Casos de Uso

### **Caso 1: Catálogos por Temporada**

```
Organization: "Tienda ABC"
  ├── Catalogue: "Verano 2026"
  │   ├── Product: Traje de baño
  │   ├── Product: Sandalias
  │   └── Product: Lentes de sol
  │
  └── Catalogue: "Invierno 2026"
      ├── Product: Abrigo
      ├── Product: Botas
      └── Product: Bufanda
```

---

### **Caso 2: Catálogos por Canal**

```
Organization: "Distribuidora XYZ"
  ├── Catalogue: "B2B - Mayorista"
  │   ├── Product: Producto A (precio mayorista)
  │   └── Product: Producto B (precio mayorista)
  │
  └── Catalogue: "B2C - Retail"
      ├── Product: Producto A (precio retail)
      └── Product: Producto B (precio retail)
```

---

### **Caso 3: Catálogos por Región**

```
Organization: "Empresa Internacional"
  ├── Catalogue: "Chile"
  │   ├── Product: iPhone 15 (CLP)
  │   └── Product: Samsung S24 (CLP)
  │
  └── Catalogue: "Perú"
      ├── Product: iPhone 15 (PEN)
      └── Product: Samsung S24 (PEN)
```

---

## 📋 Modelo Catalogue

### **Definición**

```python
class Catalogue(models.Model):
    name = CharField(max_length=255)
    slug = SlugField(max_length=255)
    description = TextField(blank=True, null=True)
    organization = ForeignKey(Organization, related_name='catalogues')
    is_active = BooleanField(default=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['slug', 'organization']]
```

### **Campos**

| Campo | Tipo | Descripción |
|-------|------|-------------|
| `name` | CharField | Nombre del catálogo |
| `slug` | SlugField | Slug único por organización |
| `description` | TextField | Descripción del catálogo |
| `organization` | ForeignKey | Organización dueña |
| `is_active` | BooleanField | ¿Catálogo activo? |
| `created_at` | DateTimeField | Fecha de creación |
| `updated_at` | DateTimeField | Última actualización |

### **Constraints**

- `unique_together = [['slug', 'organization']]`: El slug es único **por organización**

---

## 🔄 Cambios en Modelos Existentes

### **Product**

**Antes**:
```python
class Product(..., OrganizationRelatedModel):
    # organization heredado de OrganizationRelatedModel
```

**Ahora**:
```python
class Product(...):  # Ya NO hereda de OrganizationRelatedModel
    catalogue = ForeignKey('Catalogue', related_name='products')
```

**Acceso a Organization**:
```python
# Antes
product.organization

# Ahora
product.catalogue.organization
```

---

### **ImportFile**

**Antes**:
```python
class ImportFile(..., OrganizationRelatedModel):
    # organization heredado de OrganizationRelatedModel
```

**Ahora**:
```python
class ImportFile(...):  # Ya NO hereda de OrganizationRelatedModel
    catalogue = ForeignKey('Catalogue', related_name='import_files')
```

**Acceso a Organization**:
```python
# Antes
import_file.organization

# Ahora
import_file.catalogue.organization
```

---

### **Modelos que NO cambiaron**

Estos modelos **siguen** asociados a **Organization**:

- ✅ `Category` - Compartidas entre catálogos
- ✅ `Brand` - Compartidas entre catálogos
- ✅ `Images` - Compartidas entre catálogos
- ✅ `Slide` - A nivel de organización
- ✅ `ClientConfiguration` - A nivel de organización

---

## 🚀 Migración de Datos

### **Problema**: Los productos existentes no tienen `catalogue`

**Solución**: Crear un catálogo por defecto para cada organización.

### **Script de Migración**

```python
# En la migración de Django
from django.db import migrations

def create_default_catalogues(apps, schema_editor):
    """
    Crea un catálogo por defecto para cada organización
    y asocia todos los productos existentes a ese catálogo
    """
    Organization = apps.get_model('api', 'Organization')
    Catalogue = apps.get_model('api', 'Catalogue')
    Product = apps.get_model('api', 'Product')
    ImportFile = apps.get_model('api', 'ImportFile')
    
    for org in Organization.objects.all():
        # Crear catálogo por defecto
        catalogue, created = Catalogue.objects.get_or_create(
            organization=org,
            slug='catalogo-principal',
            defaults={
                'name': 'Catálogo Principal',
                'description': 'Catálogo principal (migración automática)',
                'is_active': True
            }
        )
        
        # Asociar productos existentes
        # Nota: Esto requiere que el campo catalogue ya exista pero sea nullable
        Product.objects.filter(organization=org).update(catalogue=catalogue)
        
        # Asociar import files existentes
        ImportFile.objects.filter(organization=org).update(catalogue=catalogue)
        
        print(f"✅ Organización '{org.name}': {catalogue.products.count()} productos migrados")

class Migration(migrations.Migration):
    dependencies = [
        ('api', '0005_importfile_import_mode'),
    ]
    
    operations = [
        # 1. Crear modelo Catalogue
        migrations.CreateModel(...),
        
        # 2. Agregar campo catalogue a Product (nullable temporalmente)
        migrations.AddField(
            model_name='product',
            name='catalogue',
            field=models.ForeignKey(
                null=True,  # Temporal
                on_delete=models.CASCADE,
                related_name='products',
                to='api.catalogue'
            ),
        ),
        
        # 3. Agregar campo catalogue a ImportFile (nullable temporalmente)
        migrations.AddField(
            model_name='importfile',
            name='catalogue',
            field=models.ForeignKey(
                null=True,  # Temporal
                on_delete=models.CASCADE,
                related_name='import_files',
                to='api.catalogue'
            ),
        ),
        
        # 4. Migrar datos
        migrations.RunPython(create_default_catalogues),
        
        # 5. Hacer catalogue NOT NULL
        migrations.AlterField(
            model_name='product',
            name='catalogue',
            field=models.ForeignKey(
                null=False,  # Ahora obligatorio
                on_delete=models.CASCADE,
                related_name='products',
                to='api.catalogue'
            ),
        ),
        
        migrations.AlterField(
            model_name='importfile',
            name='catalogue',
            field=models.ForeignKey(
                null=False,  # Ahora obligatorio
                on_delete=models.CASCADE,
                related_name='import_files',
                to='api.catalogue'
            ),
        ),
        
        # 6. Eliminar campo organization de Product
        migrations.RemoveField(
            model_name='product',
            name='organization',
        ),
        
        # 7. Eliminar campo organization de ImportFile
        migrations.RemoveField(
            model_name='importfile',
            name='organization',
        ),
    ]
```

---

## 📝 Uso del Nuevo Modelo

### **Crear Catálogo**

```python
from api.models import Organization, Catalogue

org = Organization.objects.get(slug='tienda-abc')

catalogue = Catalogue.objects.create(
    name="Verano 2026",
    slug="verano-2026",
    organization=org,
    description="Catálogo de productos de verano",
    is_active=True
)
```

---

### **Crear Producto en Catálogo**

```python
from api.models import Catalogue, Product

catalogue = Catalogue.objects.get(slug='verano-2026')

product = Product.objects.create(
    catalogue=catalogue,  # ← Ahora es catalogue, no organization
    sku="SKU-001",
    name="Traje de baño",
    price_1=29990,
    currency="CLP"
)
```

---

### **Importar a Catálogo Específico**

```python
# Actualizar script de transformación
def transform_and_import(excel_path, catalogue_slug):
    # Obtener catálogo
    catalogue = Catalogue.objects.get(slug=catalogue_slug)
    organization = catalogue.organization
    
    # Procesar Excel
    for _, row in df.iterrows():
        product, created = Product.objects.update_or_create(
            sku=sku,
            catalogue=catalogue,  # ← Ahora es catalogue
            defaults={...}
        )
```

---

### **Consultas**

```python
# Obtener todos los catálogos de una organización
org = Organization.objects.get(slug='tienda-abc')
catalogues = org.catalogues.all()

# Obtener todos los productos de un catálogo
catalogue = Catalogue.objects.get(slug='verano-2026')
products = catalogue.products.all()

# Obtener organización desde un producto
product = Product.objects.get(sku='SKU-001')
organization = product.catalogue.organization

# Filtrar productos por organización (a través de catálogo)
products = Product.objects.filter(
    catalogue__organization__slug='tienda-abc'
)

# Filtrar productos activos de catálogos activos
products = Product.objects.filter(
    catalogue__is_active=True,
    state='publish'
)
```

---

## 🔧 Actualizar Scripts de Importación

### **Antes**

```bash
python scripts/transform_client_excel.py excel.xlsx tienda-abc --mode soft_delete
```

### **Ahora**

```bash
python scripts/transform_client_excel.py excel.xlsx catalogo-verano-2026 --mode soft_delete
```

**Cambio**: El segundo argumento ahora es el **slug del catálogo**, no de la organización.

---

## 📊 Admin de Django

### **Nuevo Admin: Catalogue**

```
http://localhost:8050/admin/api/catalogue/

Campos visibles:
- name
- organization
- slug
- is_active
- created_at

Filtros:
- organization
- is_active
- created_at
```

### **Product Admin Actualizado**

```
Filtros agregados:
- catalogue
- catalogue__organization

List display:
- name
- catalogue  ← NUEVO
- brand
- currency
- ...
```

### **ImportFile Admin Actualizado**

```
Filtros agregados:
- catalogue
- catalogue__organization
- import_mode

List display:
- id
- catalogue  ← NUEVO
- import_mode
- ...
```

---

## ✅ Ventajas de la Nueva Arquitectura

### **1. Múltiples Catálogos por Organización**
```python
org.catalogues.all()
# [<Catalogue: Verano 2026>, <Catalogue: Invierno 2026>]
```

### **2. Aislamiento de Productos**
```python
# Productos de verano
catalogue_verano.products.all()

# Productos de invierno
catalogue_invierno.products.all()

# Completamente separados
```

### **3. Importaciones Dirigidas**
```python
# Importar solo al catálogo de verano
ImportFile.objects.create(
    catalogue=catalogue_verano,
    file=excel_verano,
    import_mode='soft_delete'
)
```

### **4. Activación/Desactivación de Catálogos**
```python
# Desactivar catálogo de invierno
catalogue_invierno.is_active = False
catalogue_invierno.save()

# Productos siguen existiendo pero el catálogo está inactivo
```

### **5. Categorías y Marcas Compartidas**
```python
# Las categorías y marcas son compartidas entre catálogos
category = Category.objects.get(name='Ropa')

# Usada en ambos catálogos
catalogue_verano.products.filter(categories=category)
catalogue_invierno.products.filter(categories=category)
```

---

## 🎯 Próximos Pasos

### **1. Generar Migración**

```bash
docker compose exec web python manage.py makemigrations
```

### **2. Revisar Migración**

```bash
# Ver el archivo generado
cat api/migrations/0006_catalogue_and_more.py
```

### **3. Aplicar Migración**

```bash
docker compose exec web python manage.py migrate
```

### **4. Verificar en Admin**

```
http://localhost:8050/admin/api/catalogue/
```

### **5. Actualizar Scripts de Importación**

- Modificar `transform_client_excel.py` para usar `catalogue` en lugar de `organization`

---

## ⚠️ Consideraciones Importantes

### **1. Migración de Datos Existentes**

Todos los productos y archivos de importación existentes se asociarán automáticamente a un catálogo por defecto llamado "Catálogo Principal".

### **2. SKU Único Global**

El campo `sku` sigue siendo único a nivel global. Si quieres SKUs únicos por catálogo:

```python
class Product(models.Model):
    sku = CharField(max_length=250)  # Quitar unique=True
    
    class Meta:
        unique_together = [['sku', 'catalogue']]
```

### **3. Queries Existentes**

Queries que usaban `organization` deben actualizarse:

```python
# Antes
Product.objects.filter(organization=org)

# Ahora
Product.objects.filter(catalogue__organization=org)
```

---

## 📚 Resumen

| Aspecto | Antes | Ahora |
|---------|-------|-------|
| **Estructura** | Organization → Product | Organization → Catalogue → Product |
| **Catálogos por Org** | 1 (implícito) | N (explícitos) |
| **Product.organization** | Directo | A través de catalogue |
| **ImportFile.organization** | Directo | A través de catalogue |
| **Category/Brand** | Por organization | Por organization (compartidas) |
| **Flexibilidad** | Baja | Alta |

---

**Fin de la documentación**  
**Próximo paso**: Generar y aplicar la migración
