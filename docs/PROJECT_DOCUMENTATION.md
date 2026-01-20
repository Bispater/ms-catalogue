# 📚 Catalogue API - Documentación Completa del Proyecto

> **Documentación técnica completa para desarrolladores e IA**  
> **Versión:** 1.0  
> **Última actualización:** 2026-01-19

---

## 📋 Tabla de Contenidos

1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Arquitectura del Sistema](#arquitectura-del-sistema)
3. [Modelos de Datos](#modelos-de-datos)
4. [API y Endpoints](#api-y-endpoints)
5. [Configuración y Entorno](#configuración-y-entorno)
6. [Flujos de Negocio](#flujos-de-negocio)
7. [Seguridad y Permisos](#seguridad-y-permisos)
8. [Despliegue](#despliegue)

---

## 🎯 Resumen Ejecutivo

### ¿Qué es Catalogue API?

**Catalogue API** es una **plataforma de gestión de catálogos de productos multi-tenant (multi-organización)** construida con Django y Django REST Framework. Permite a múltiples organizaciones gestionar sus propios catálogos de productos de forma aislada en una única instancia de la aplicación.

### Características Principales

- ✅ **Multi-Tenancy**: Soporte para múltiples organizaciones con datos aislados
- ✅ **Gestión de Productos**: CRUD completo de productos con variaciones
- ✅ **Categorías Jerárquicas**: Categorías anidadas ilimitadas
- ✅ **Gestión de Marcas**: Organización por marcas con jerarquías
- ✅ **Galería de Imágenes**: Múltiples imágenes por producto
- ✅ **Importación Masiva**: Carga de productos desde CSV/Excel
- ✅ **SEO-Friendly**: Slugs automáticos y meta tags
- ✅ **Soft Delete**: Borrado lógico de registros
- ✅ **API RESTful**: Endpoints completos con documentación Swagger
- ✅ **White-Label**: Personalización por cliente (colores, logos, dominios)
- ✅ **Multi-Moneda**: Soporte para CLP y PEN
- ✅ **Editor WYSIWYG**: CKEditor integrado para descripciones ricas

### Casos de Uso

1. **E-commerce Multi-Tenant**: Múltiples tiendas en una plataforma
2. **Marketplace**: Múltiples vendedores con catálogos independientes
3. **Catálogo Corporativo**: Múltiples sucursales/regiones
4. **Distribuidores**: Gestión de productos por cliente/distribuidor

---

## 🏗️ Arquitectura del Sistema

### Stack Tecnológico

```yaml
Backend:
  Framework: Django 4.2.7
  API: Django REST Framework 3.14.0
  Base de Datos: PostgreSQL 13
  Cache: Redis 7
  Task Queue: Celery 5.3.1
  
Frontend Integration:
  CORS: django-cors-headers
  API Docs: drf-yasg (Swagger/OpenAPI)
  
Storage:
  Local: Sistema de archivos
  Cloud: Google Cloud Storage
  
Development:
  Containerization: Docker + Docker Compose
  Web Server: Gunicorn
  Reverse Proxy: Nginx (producción)
```

### Estructura del Proyecto

```
catalogue_api/
├── api/                          # Aplicación principal
│   ├── models.py                 # Modelos de datos (568 líneas)
│   ├── serializers.py            # Serializadores DRF
│   ├── views.py                  # Vistas y ViewSets
│   ├── urls.py                   # Rutas de la API
│   ├── admin.py                  # Configuración del admin
│   ├── forms.py                  # Formularios personalizados
│   └── migrations/               # Migraciones de BD
│
├── core/                         # Configuración del proyecto
│   ├── settings.py               # Configuración Django
│   ├── urls.py                   # URLs principales
│   ├── wsgi.py                   # WSGI application
│   └── asgi.py                   # ASGI application
│
├── config/                       # Configuraciones externas
│   └── postgres/                 # Configuración PostgreSQL
│       ├── postgresql.conf
│       └── pg_hba.conf
│
├── scripts/                      # Scripts de automatización
│   ├── start-local.sh           # Iniciar entorno
│   ├── stop-local.sh            # Detener entorno
│   ├── reset-docker.sh          # Resetear Docker
│   ├── create-superuser.sh      # Crear superusuario
│   ├── switch-env.sh            # Cambiar entorno
│   └── update-dependencies.sh   # Actualizar dependencias
│
├── static/                       # Archivos estáticos
├── staticfiles/                  # Archivos estáticos recolectados
├── media/                        # Archivos subidos por usuarios
│
├── docker-compose.yml            # Docker Compose (desarrollo)
├── docker-compose.prod.yml       # Docker Compose (producción)
├── Dockerfile                    # Imagen Docker
├── requirements.txt              # Dependencias Python
├── manage.py                     # CLI de Django
│
├── .env                          # Variables de entorno (desarrollo)
├── .env.prod                     # Variables de entorno (producción)
├── .env.example                  # Template de variables
│
└── [Documentación]
    ├── README.md                 # README principal
    ├── DOCKER_README.md          # Guía de Docker
    ├── PRODUCTION_README.md      # Guía de producción
    ├── QUICK_START.md            # Inicio rápido
    ├── SECURITY_UPDATE.md        # Actualizaciones de seguridad
    └── PROJECT_DOCUMENTATION.md  # Este archivo
```

### Flujo de Datos

```
┌─────────────┐
│   Cliente   │ (Angular/React/Mobile)
└──────┬──────┘
       │ HTTP/HTTPS
       ↓
┌─────────────┐
│    Nginx    │ (Reverse Proxy - Producción)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Gunicorn   │ (WSGI Server)
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Django    │ (Application Server)
│  + DRF API  │
└──────┬──────┘
       │
       ├──────→ ┌──────────────┐
       │        │  PostgreSQL  │ (Base de Datos)
       │        └──────────────┘
       │
       ├──────→ ┌──────────────┐
       │        │    Redis     │ (Cache + Celery)
       │        └──────────────┘
       │
       └──────→ ┌──────────────┐
                │  GCS / Local │ (Almacenamiento)
                └──────────────┘
```

---

## 📊 Modelos de Datos

### Diagrama de Relaciones

```
Organization (1) ←──────────────────────────────┐
    │                                           │
    │ (1:N)                                     │
    ├─→ Category (N)                            │
    │   ├─→ parent (self, recursive)            │
    │   └─→ products (M:N)                      │
    │                                           │
    ├─→ Brand (N)                               │
    │   ├─→ parent (self, recursive)            │
    │   └─→ products (1:N)                      │
    │                                           │
    ├─→ Product (N) ←──────────────────────┐   │
    │   ├─→ parent (self, variations)      │   │
    │   ├─→ brand (N:1)                    │   │
    │   ├─→ categories (M:N)                │   │
    │   ├─→ images (M:N) ──────────────────┤   │
    │   └─→ metadata (1:1)                 │   │
    │                                      │   │
    ├─→ Images (N) ←─────────────────────┘   │
    │                                         │
    ├─→ MetaData (N)                          │
    │   └─→ product (1:1)                     │
    │                                         │
    ├─→ ImportFile (N)                        │
    │   └─→ user_created (N:1)                │
    │                                         │
    └─→ Slide (N)                             │
        └─→ parent (self, recursive)          │
                                              │
ClientConfiguration (1) ──────────────────────┘
    └─→ organization_id (reference)
```

### Modelos Detallados

#### 1. **Organization** (Organización)

**Propósito**: Entidad principal para multi-tenancy. Cada organización tiene sus propios datos aislados.

```python
class Organization(models.Model):
    name = CharField(max_length=255)           # Nombre de la organización
    slug = SlugField(unique=True)              # Slug único (ej: "tienda-abc")
    description = TextField(blank=True)        # Descripción
    created_at = DateTimeField(auto_now_add)   # Fecha de creación
    updated_at = DateTimeField(auto_now)       # Última actualización
```

**Relaciones**:
- Padre de: Category, Brand, Product, Images, MetaData, ImportFile, Slide

**Uso**:
```python
# Crear organización
org = Organization.objects.create(
    name="Tienda ABC",
    slug="tienda-abc",
    description="Tienda de electrónica"
)

# Filtrar productos por organización
products = Product.objects.filter(organization=org)
```

---

#### 2. **Category** (Categoría)

**Propósito**: Categorías jerárquicas para organizar productos. Soporta anidación ilimitada.

```python
class Category(BaseModel, MetaModel, OrganizationRelatedModel):
    parent = ForeignKey('self', null=True)     # Categoría padre (jerárquica)
    icon_file = ImageField()                   # Ícono de la categoría
    order = IntegerField(default=0)            # Orden de visualización
    virtual = BooleanField(default=False)      # Categoría virtual (no física)
    
    # Heredados de BaseModel:
    # - name, slug, description, image, images
    # - icon, style, state (publish/draft/pending/private)
    
    # Heredados de MetaModel:
    # - meta_title, meta_description, meta_keywords
```

**Jerarquía**:
```
Electrónica (parent=None)
├── Celulares (parent=Electrónica)
│   ├── Smartphones (parent=Celulares)
│   └── Básicos (parent=Celulares)
└── Computadoras (parent=Electrónica)
    ├── Laptops (parent=Computadoras)
    └── Desktops (parent=Computadoras)
```

**Uso**:
```python
# Crear categoría raíz
electronica = Category.objects.create(
    name="Electrónica",
    organization=org,
    state="publish"
)

# Crear subcategoría
celulares = Category.objects.create(
    name="Celulares",
    parent=electronica,
    organization=org
)

# Obtener hijos
hijos = electronica.children.all()

# Obtener productos de una categoría
productos = category.products.all()
```

---

#### 3. **Brand** (Marca)

**Propósito**: Marcas de productos con soporte para jerarquías (ej: marcas y sub-marcas).

```python
class Brand(BaseModel, MetaModel, OrganizationRelatedModel):
    parent = ForeignKey('self', null=True)     # Marca padre
    order = IntegerField(default=0)            # Orden
    virtual = BooleanField(default=False)      # Marca virtual
    
    # Heredados de BaseModel:
    # - name, slug, description, image, images, icon, style, state
```

**Uso**:
```python
# Crear marca
apple = Brand.objects.create(
    name="Apple",
    organization=org,
    state="publish"
)

# Productos de una marca
productos_apple = Product.objects.filter(brand=apple)
```

---

#### 4. **Product** (Producto)

**Propósito**: Modelo principal de productos con soporte para variaciones, precios, stock, dimensiones y SEO.

```python
class Product(BaseModel, MetaModel, Dimensions, 
              TimeStampedModel, SoftDeletableModel, 
              OrganizationRelatedModel):
    
    # Identificación
    sku = CharField(max_length=250, unique=True)   # SKU único
    
    # Descripciones
    short_description = TextField()                 # Descripción corta
    # description heredado de BaseModel
    
    # Precios
    regular_price = DecimalField(max_digits=12, decimal_places=2)
    sale_price = DecimalField(max_digits=12, decimal_places=2, null=True)
    currency = CharField(choices=CURRENCY)          # CLP o PEN
    
    # Stock
    stock_status = CharField(choices=STOCK_STATUS)  # instock/outofstock/onbackorder
    stock_quantity = IntegerField(default=0)        # Cantidad en stock
    
    # Dimensiones (heredado de Dimensions)
    # - length, width, height
    weight = DecimalField(max_digits=12, decimal_places=2)
    
    # Relaciones
    brand = ForeignKey(Brand, null=True)            # Marca del producto
    parent = ForeignKey('self', null=True)          # Producto padre (variaciones)
    categories = ManyToManyField(Category)          # Categorías
    
    # Otros
    virtual = BooleanField(default=False)           # Producto virtual (digital)
    
    # Timestamps automáticos (TimeStampedModel):
    # - created, modified
    
    # Soft delete (SoftDeletableModel):
    # - is_removed
```

**Constantes**:
```python
STOCK_STATUS = (
    ('instock', 'En Stock'),
    ('outofstock', 'Agotado'),
    ('onbackorder', 'En Pedido'),
)

OBJECT_STATUS = (
    ('publish', 'Publicado'),
    ('pending', 'Pendiente'),
    ('private', 'Privado'),
    ('draft', 'Borrador'),
)

CURRENCY = (
    ('CLP', 'Peso Chileno'),
    ('PEN', 'Sol Peruano'),
)
```

**Variaciones de Productos**:
```python
# Producto padre (Camiseta)
camiseta = Product.objects.create(
    name="Camiseta Básica",
    sku="CAM-001",
    regular_price=15000,
    currency="CLP",
    organization=org
)

# Variaciones (Tallas)
camiseta_s = Product.objects.create(
    name="Camiseta Básica - Talla S",
    sku="CAM-001-S",
    parent=camiseta,  # ← Referencia al padre
    regular_price=15000,
    stock_quantity=10,
    organization=org
)

camiseta_m = Product.objects.create(
    name="Camiseta Básica - Talla M",
    sku="CAM-001-M",
    parent=camiseta,
    regular_price=15000,
    stock_quantity=15,
    organization=org
)

# Verificar si es variación
camiseta_s.is_variation()  # True
camiseta.is_variation()    # False
```

**Uso Completo**:
```python
# Crear producto completo
producto = Product.objects.create(
    name="iPhone 15 Pro",
    slug="iphone-15-pro",
    sku="IPH-15-PRO-256",
    short_description="El iPhone más avanzado",
    description="<p>Descripción completa con HTML</p>",
    regular_price=1299000,
    sale_price=1199000,
    currency="CLP",
    stock_status="instock",
    stock_quantity=50,
    weight=0.221,  # kg
    length=14.67,  # cm
    width=7.15,
    height=0.83,
    brand=apple,
    organization=org,
    state="publish",
    # SEO
    meta_title="iPhone 15 Pro - Compra Online",
    meta_description="Compra el iPhone 15 Pro...",
    meta_keywords="iphone, apple, smartphone"
)

# Agregar categorías
producto.categories.add(smartphones, celulares)

# Agregar imágenes
producto.images.add(imagen1, imagen2, imagen3)
```

---

#### 5. **Images** (Imágenes)

**Propósito**: Galería de imágenes reutilizables para productos y otros modelos.

```python
class Images(TimeStampedModel, SoftDeletableModel, OrganizationRelatedModel):
    name = CharField(max_length=255)           # Nombre de la imagen
    alt = CharField(max_length=255)            # Texto alternativo (SEO)
    code = CharField(max_length=100)           # Código/referencia
    image = ImageField(upload_to=get_organization_image_path)
    
    # Path dinámico: {org_slug}/images/{filename}
```

**Uso**:
```python
# Crear imagen
imagen = Images.objects.create(
    name="iPhone 15 Pro - Frontal",
    alt="iPhone 15 Pro vista frontal",
    code="IPH15-FRONT",
    image=archivo_imagen,
    organization=org
)

# Asociar a producto
producto.images.add(imagen)

# Path generado automáticamente:
# tienda-abc/images/iphone-15-pro-frontal.jpg
```

---

#### 6. **MetaData** (Metadatos SEO)

**Propósito**: Metadatos SEO específicos por producto (relación 1:1).

```python
class MetaData(MetaModel, OrganizationRelatedModel):
    product = OneToOneField(Product)           # Producto asociado
    
    # Heredados de MetaModel:
    # - meta_title, meta_description, meta_keywords
```

**Uso**:
```python
# Crear metadatos
metadata = MetaData.objects.create(
    product=producto,
    meta_title="iPhone 15 Pro | Tienda ABC",
    meta_description="Compra el iPhone 15 Pro...",
    meta_keywords="iphone 15 pro, apple, smartphone",
    organization=org
)

# Acceder desde producto
producto.metadata.meta_title
```

---

#### 7. **ImportFile** (Importación Masiva)

**Propósito**: Importar productos masivamente desde archivos CSV/Excel con imágenes en ZIP.

```python
class ImportFile(TimeStampedModel, SoftDeletableModel, OrganizationRelatedModel):
    file = FileField(upload_to='imports/')              # Archivo CSV/Excel
    images_zip = FileField(upload_to='imports/zips/')   # ZIP con imágenes
    uploaded = BooleanField(default=False)              # Estado de carga
    user_created = ForeignKey(User)                     # Usuario que importó
```

**Flujo de Importación**:
```
1. Usuario sube archivo CSV + ZIP de imágenes
2. Signal post_save se dispara automáticamente
3. (TODO) Tarea Celery procesa el archivo
4. Productos se crean/actualizan masivamente
5. Imágenes se extraen y asocian a productos
```

**Formato CSV Esperado**:
```csv
sku,name,description,regular_price,sale_price,currency,stock_quantity,brand,categories,image_codes
IPH15-256,iPhone 15 Pro,Descripción...,1299000,1199000,CLP,50,Apple,"Celulares,Smartphones","IPH15-1,IPH15-2"
```

---

#### 8. **Slide** (Carrusel/Banners)

**Propósito**: Slides para homepage, banners promocionales, carruseles.

```python
class Slide(BaseModel, OrganizationRelatedModel):
    parent = ForeignKey('self', null=True)     # Slide padre (grupos)
    order = IntegerField(default=0)            # Orden de visualización
    virtual = BooleanField(default=False)      # Slide virtual
    
    # Heredados de BaseModel:
    # - name, slug, description, image, images, icon, style, state
```

**Uso**:
```python
# Crear slide promocional
slide = Slide.objects.create(
    name="Promoción Black Friday",
    description="Descuentos hasta 50%",
    image=imagen_banner,
    order=1,
    state="publish",
    organization=org
)
```

---

#### 9. **ClientConfiguration** (Configuración White-Label)

**Propósito**: Personalización por cliente (colores, logos, dominios) para white-label.

```python
class ClientConfiguration(TimeStampedModel, SoftDeletableModel):
    name = CharField(max_length=100, unique=True)          # Nombre del cliente
    organization_id = IntegerField(unique=True)            # ID de organización
    
    # Colores (hexadecimal)
    primary_color = CharField(max_length=7, default="#FFFFFF")
    secondary_color = CharField(max_length=7, default="#000000")
    accent_color = CharField(max_length=7, default="#007BFF")
    
    # Branding
    logo = ImageField(upload_to='client_configs/logos/')
    favicon = ImageField(upload_to='client_configs/favicons/')
    
    # Dominio
    domain = CharField(max_length=255, unique=True)        # ej: cliente.dominio.com
    
    # Otros
    description = TextField(blank=True)
    is_active = BooleanField(default=True)
```

**Uso**:
```python
# Configurar cliente
config = ClientConfiguration.objects.create(
    name="Tienda ABC",
    organization_id=org.id,
    primary_color="#FF5733",
    secondary_color="#333333",
    accent_color="#FFC300",
    logo=logo_file,
    favicon=favicon_file,
    domain="tienda-abc.midominio.com",
    is_active=True
)

# Obtener configuración por dominio
config = ClientConfiguration.objects.get(domain=request.get_host())
```

---

### Modelos Base (Abstract)

#### **OrganizationRelatedModel**
```python
class OrganizationRelatedModel(models.Model):
    organization = ForeignKey(Organization)
    
    class Meta:
        abstract = True
```
**Propósito**: Todos los modelos que heredan de este tienen relación con una organización.

#### **MetaModel**
```python
class MetaModel(models.Model):
    meta_title = CharField(max_length=255)
    meta_description = TextField()
    meta_keywords = TextField()
    
    class Meta:
        abstract = True
```
**Propósito**: SEO metadata para cualquier modelo.

#### **BaseModel**
```python
class BaseModel(models.Model):
    name = CharField(max_length=250)
    slug = SlugField()
    description = TextField()
    image = ImageField()
    images = ManyToManyField(Images)
    icon = CharField(max_length=100)
    style = CharField(max_length=255)
    state = CharField(choices=OBJECT_STATUS)
    
    class Meta:
        abstract = True
```
**Propósito**: Campos comunes para Category, Brand, Slide.

#### **Dimensions**
```python
class Dimensions(models.Model):
    length = DecimalField()
    width = DecimalField()
    height = DecimalField()
    
    class Meta:
        abstract = True
```
**Propósito**: Dimensiones físicas para productos.

---

## 🔌 API y Endpoints

### Base URL

```
Desarrollo: http://localhost:8050/api/
Producción: https://api.tudominio.com/api/
```

### Documentación Interactiva

```
Swagger UI: /swagger/
ReDoc: /redoc/
```

### Endpoints Principales

#### **Productos**

```http
GET    /api/products/              # Listar productos
POST   /api/products/              # Crear producto
GET    /api/products/{id}/         # Detalle de producto
PUT    /api/products/{id}/         # Actualizar producto
PATCH  /api/products/{id}/         # Actualización parcial
DELETE /api/products/{id}/         # Eliminar producto (soft delete)

# Filtros
GET /api/products/?organization=1
GET /api/products/?brand=2
GET /api/products/?category=3
GET /api/products/?state=publish
GET /api/products/?stock_status=instock
GET /api/products/?search=iphone

# Variaciones
GET /api/products/{id}/variations/  # Obtener variaciones de un producto
```

#### **Categorías**

```http
GET    /api/categories/            # Listar categorías
POST   /api/categories/            # Crear categoría
GET    /api/categories/{id}/       # Detalle de categoría
PUT    /api/categories/{id}/       # Actualizar categoría
DELETE /api/categories/{id}/       # Eliminar categoría

# Jerarquía
GET /api/categories/{id}/children/  # Obtener hijos
GET /api/categories/{id}/products/  # Productos de la categoría
```

#### **Marcas**

```http
GET    /api/brands/                # Listar marcas
POST   /api/brands/                # Crear marca
GET    /api/brands/{id}/           # Detalle de marca
PUT    /api/brands/{id}/           # Actualizar marca
DELETE /api/brands/{id}/           # Eliminar marca

GET /api/brands/{id}/products/     # Productos de la marca
```

#### **Imágenes**

```http
GET    /api/images/                # Listar imágenes
POST   /api/images/                # Subir imagen
GET    /api/images/{id}/           # Detalle de imagen
DELETE /api/images/{id}/           # Eliminar imagen
```

#### **Organizaciones**

```http
GET    /api/organizations/         # Listar organizaciones
POST   /api/organizations/         # Crear organización
GET    /api/organizations/{id}/    # Detalle de organización
PUT    /api/organizations/{id}/    # Actualizar organización
```

#### **Importación**

```http
POST   /api/import/                # Importar productos
GET    /api/import/{id}/           # Estado de importación
```

### Ejemplos de Requests

#### Crear Producto

```http
POST /api/products/
Content-Type: application/json

{
  "name": "iPhone 15 Pro",
  "slug": "iphone-15-pro",
  "sku": "IPH-15-PRO-256",
  "short_description": "El iPhone más avanzado",
  "description": "<p>Descripción completa</p>",
  "regular_price": "1299000.00",
  "sale_price": "1199000.00",
  "currency": "CLP",
  "stock_status": "instock",
  "stock_quantity": 50,
  "weight": "0.221",
  "length": "14.67",
  "width": "7.15",
  "height": "0.83",
  "brand": 1,
  "organization": 1,
  "categories": [1, 2],
  "state": "publish",
  "meta_title": "iPhone 15 Pro - Compra Online",
  "meta_description": "Compra el iPhone 15 Pro...",
  "meta_keywords": "iphone, apple, smartphone"
}
```

#### Respuesta

```json
{
  "id": 1,
  "name": "iPhone 15 Pro",
  "slug": "iphone-15-pro",
  "sku": "IPH-15-PRO-256",
  "short_description": "El iPhone más avanzado",
  "description": "<p>Descripción completa</p>",
  "regular_price": "1299000.00",
  "sale_price": "1199000.00",
  "currency": "CLP",
  "stock_status": "instock",
  "stock_quantity": 50,
  "weight": "0.221",
  "length": "14.67",
  "width": "7.15",
  "height": "0.83",
  "brand": {
    "id": 1,
    "name": "Apple",
    "slug": "apple"
  },
  "organization": {
    "id": 1,
    "name": "Tienda ABC",
    "slug": "tienda-abc"
  },
  "categories": [
    {
      "id": 1,
      "name": "Celulares",
      "slug": "celulares"
    },
    {
      "id": 2,
      "name": "Smartphones",
      "slug": "smartphones"
    }
  ],
  "images": [],
  "state": "publish",
  "created": "2026-01-19T21:00:00Z",
  "modified": "2026-01-19T21:00:00Z",
  "is_variation": false
}
```

---

## ⚙️ Configuración y Entorno

### Variables de Entorno

#### Desarrollo (`.env`)

```bash
# Django
DEBUG=True
SECRET_KEY=dev-secret-key-change-in-production
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Base de Datos
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ms_catalogue_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432

# Docker
DOCKER_ENV=true

# Redis
REDIS_URL=redis://redis:6379/0

# Email (Console backend para desarrollo)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Storage
USE_S3=False
MEDIA_URL=/media/
STATIC_URL=/static/

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:8050,http://localhost:3000
```

#### Producción (`.env.prod`)

```bash
# Django
DEBUG=False
SECRET_KEY=<GENERAR_CLAVE_SEGURA>
ALLOWED_HOSTS=.tudominio.com,tudominio.com

# Base de Datos
DB_NAME=ms_catalogue_prod
DB_USER=catalogue_user
DB_PASSWORD=<CONTRASEÑA_SEGURA>
DB_HOST=<HOST_RDS_O_SERVIDOR>
DB_PORT=5432

# Redis
REDIS_URL=redis://:password@redis:6379/0

# Email (SMTP real)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=<EMAIL>
EMAIL_HOST_PASSWORD=<APP_PASSWORD>

# Google Cloud Storage
USE_S3=False
GS_BUCKET_NAME=ms-catalogue-prod
GS_PROJECT_ID=tu-proyecto
GS_LOCATION=ms_catalogue
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Seguridad
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Docker Compose

#### Desarrollo (`docker-compose.yml`)

```yaml
services:
  web:
    build: .
    command: >
      sh -c "python manage.py migrate &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    ports:
      - "8050:8000"
    environment:
      - DOCKER_ENV=true
      - DJANGO_DEBUG=True
    depends_on:
      - db
    
  db:
    image: postgres:13
    environment:
      POSTGRES_DB: ms_catalogue_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5333:5432"
  
  pgadmin:
    image: dpage/pgadmin4
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@admin.com
      PGADMIN_DEFAULT_PASSWORD: admin
    ports:
      - "5050:80"
    volumes:
      - pgadmin_data:/var/lib/pgadmin

volumes:
  postgres_data:
  pgadmin_data:
  static_volume:
  media_volume:
```

---

## 🔄 Flujos de Negocio

### 1. Crear Producto Completo

```python
# 1. Crear organización (si no existe)
org = Organization.objects.get(slug="tienda-abc")

# 2. Crear/obtener marca
brand, _ = Brand.objects.get_or_create(
    name="Apple",
    organization=org,
    defaults={'state': 'publish'}
)

# 3. Crear/obtener categorías
categoria_padre, _ = Category.objects.get_or_create(
    name="Electrónica",
    organization=org,
    defaults={'state': 'publish'}
)

categoria_hija, _ = Category.objects.get_or_create(
    name="Smartphones",
    parent=categoria_padre,
    organization=org,
    defaults={'state': 'publish'}
)

# 4. Subir imágenes
imagen1 = Images.objects.create(
    name="iPhone 15 Pro - Frontal",
    alt="iPhone 15 Pro vista frontal",
    image=archivo1,
    organization=org
)

imagen2 = Images.objects.create(
    name="iPhone 15 Pro - Trasera",
    alt="iPhone 15 Pro vista trasera",
    image=archivo2,
    organization=org
)

# 5. Crear producto
producto = Product.objects.create(
    name="iPhone 15 Pro 256GB",
    slug="iphone-15-pro-256gb",
    sku="IPH-15-PRO-256",
    short_description="El iPhone más avanzado con chip A17 Pro",
    description="<h2>iPhone 15 Pro</h2><p>Descripción completa...</p>",
    regular_price=Decimal("1299000.00"),
    sale_price=Decimal("1199000.00"),
    currency="CLP",
    stock_status="instock",
    stock_quantity=50,
    weight=Decimal("0.221"),
    length=Decimal("14.67"),
    width=Decimal("7.15"),
    height=Decimal("0.83"),
    brand=brand,
    organization=org,
    state="publish"
)

# 6. Asociar categorías
producto.categories.add(categoria_padre, categoria_hija)

# 7. Asociar imágenes
producto.images.add(imagen1, imagen2)

# 8. Crear metadatos SEO
MetaData.objects.create(
    product=producto,
    meta_title="iPhone 15 Pro 256GB | Tienda ABC",
    meta_description="Compra el iPhone 15 Pro con 256GB...",
    meta_keywords="iphone 15 pro, apple, smartphone, 256gb",
    organization=org
)

# 9. Crear variaciones (colores)
for color in ["Titanio Natural", "Titanio Azul", "Titanio Blanco", "Titanio Negro"]:
    Product.objects.create(
        name=f"iPhone 15 Pro 256GB - {color}",
        sku=f"IPH-15-PRO-256-{color[:3].upper()}",
        parent=producto,  # ← Variación del producto padre
        regular_price=producto.regular_price,
        sale_price=producto.sale_price,
        currency=producto.currency,
        stock_status="instock",
        stock_quantity=10,
        brand=brand,
        organization=org,
        state="publish"
    )
```

### 2. Importación Masiva

```python
# 1. Usuario sube archivo en el admin
import_file = ImportFile.objects.create(
    file=csv_file,
    images_zip=zip_file,
    organization=org,
    user_created=request.user
)

# 2. Signal post_save se dispara automáticamente
# (Ver api/models.py línea 554)

# 3. TODO: Implementar tarea Celery
@shared_task
def process_import_file(import_file_id):
    import_file = ImportFile.objects.get(id=import_file_id)
    
    # Leer CSV
    df = pd.read_csv(import_file.file.path)
    
    # Extraer ZIP de imágenes
    with zipfile.ZipFile(import_file.images_zip.path) as zip_ref:
        zip_ref.extractall('/tmp/images/')
    
    # Procesar cada fila
    for _, row in df.iterrows():
        # Crear/actualizar producto
        product, created = Product.objects.update_or_create(
            sku=row['sku'],
            organization=import_file.organization,
            defaults={
                'name': row['name'],
                'description': row['description'],
                'regular_price': row['regular_price'],
                # ... más campos
            }
        )
        
        # Asociar imágenes
        image_codes = row['image_codes'].split(',')
        for code in image_codes:
            image_path = f'/tmp/images/{code}.jpg'
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image = Images.objects.create(
                        name=f"{product.name} - {code}",
                        code=code,
                        organization=import_file.organization
                    )
                    image.image.save(f'{code}.jpg', File(f))
                    product.images.add(image)
    
    # Marcar como procesado
    import_file.uploaded = True
    import_file.save()
```

### 3. White-Label por Dominio

```python
# Middleware o vista para obtener configuración
def get_client_config(request):
    domain = request.get_host()
    
    try:
        config = ClientConfiguration.objects.get(
            domain=domain,
            is_active=True
        )
        
        # Aplicar configuración
        context = {
            'primary_color': config.primary_color,
            'secondary_color': config.secondary_color,
            'accent_color': config.accent_color,
            'logo_url': config.logo.url if config.logo else None,
            'favicon_url': config.favicon.url if config.favicon else None,
        }
        
        # Filtrar productos por organización
        organization = Organization.objects.get(id=config.organization_id)
        products = Product.objects.filter(
            organization=organization,
            state='publish'
        )
        
        return context, products
        
    except ClientConfiguration.DoesNotExist:
        # Configuración por defecto
        return default_config, Product.objects.filter(state='publish')
```

---

## 🔒 Seguridad y Permisos

### Autenticación

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
        # TODO: Agregar JWT
        # 'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}
```

### Permisos

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # Desarrollo
        # Producción:
        # 'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### CORS

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:4200",  # Angular
    "http://localhost:3000",  # React/Next.js
]

# Producción
CORS_ALLOWED_ORIGINS = [
    "https://app.tudominio.com",
    "https://www.tudominio.com",
]
```

### Aislamiento Multi-Tenant

```python
# Filtrar siempre por organización
class ProductViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        user_organization = self.request.user.organization
        return Product.objects.filter(organization=user_organization)
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)
```

---

## 🚀 Despliegue

### Desarrollo Local

```bash
# 1. Clonar repositorio
git clone https://github.com/tu-usuario/catalogue_api.git
cd catalogue_api

# 2. Iniciar entorno
./start

# 3. Acceder
# Django API: http://localhost:8050
# Django Admin: http://localhost:8050/admin
# pgAdmin: http://localhost:5050
# Swagger: http://localhost:8050/swagger/
```

### Producción

Ver `PRODUCTION_README.md` para guía completa.

**Resumen**:
```bash
# 1. Configurar .env.prod
cp .env.prod .env
nano .env  # Editar valores

# 2. Desplegar con Docker
docker-compose -f docker-compose.prod.yml up -d --build

# 3. Migraciones
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# 4. Archivos estáticos
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 5. Crear superusuario
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## 📝 Notas para IA

### Contexto Importante

1. **Multi-Tenancy**: SIEMPRE filtrar por `organization` en queries
2. **Soft Delete**: Los registros eliminados tienen `is_removed=True`, no se borran físicamente
3. **Slugs**: Se generan automáticamente con signal `save_category`
4. **Paths de Imágenes**: Dinámicos por organización: `{org_slug}/images/{filename}`
5. **Variaciones**: Productos con `parent != None` son variaciones
6. **Estados**: Solo mostrar productos con `state='publish'` en frontend
7. **Stock**: Verificar `stock_status` y `stock_quantity` antes de vender
8. **Precios**: Usar `sale_price` si existe, sino `regular_price`
9. **SEO**: Siempre incluir `meta_title`, `meta_description`, `meta_keywords`
10. **Importación**: Implementar con Celery para evitar timeouts

### Patrones Comunes

```python
# Obtener productos publicados de una organización
products = Product.objects.filter(
    organization=org,
    state='publish',
    is_removed=False
)

# Obtener categorías raíz
root_categories = Category.objects.filter(
    organization=org,
    parent=None,
    state='publish'
)

# Obtener variaciones de un producto
variations = Product.objects.filter(parent=product)

# Precio efectivo
price = product.sale_price if product.sale_price else product.regular_price

# Verificar stock
in_stock = product.stock_status == 'instock' and product.stock_quantity > 0
```

---

## 📚 Referencias

- **Django**: https://docs.djangoproject.com/
- **Django REST Framework**: https://www.django-rest-framework.org/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Docker**: https://docs.docker.com/
- **Celery**: https://docs.celeryproject.org/

---

**Fin de la documentación**  
**Versión**: 1.0  
**Fecha**: 2026-01-19  
**Mantenedor**: Catalogue API Team
