# Guía Completa de API para Frontend con IA
## Catalogue API - Documentación para Administrador de Usuario

Esta documentación está diseñada para que un frontend con IA pueda generar un administrador completo que permita realizar todas las operaciones disponibles en el Django Admin, pero con una interfaz enfocada al usuario.

---

## 📋 Tabla de Contenidos

1. [Información General](#información-general)
2. [Autenticación](#autenticación)
3. [Modelos de Datos](#modelos-de-datos)
4. [Endpoints Disponibles](#endpoints-disponibles)
5. [Ejemplos de Uso](#ejemplos-de-uso)
6. [Filtros y Búsqueda](#filtros-y-búsqueda)
7. [Gestión de Archivos](#gestión-de-archivos)
8. [Casos de Uso Comunes](#casos-de-uso-comunes)

---

## 🌐 Información General

### Base URL
```
Desarrollo: http://localhost:8050
Producción: https://catalogue.favric.cl
```

### Swagger/OpenAPI
Documentación interactiva disponible en:
- Swagger UI: `http://localhost:8050/swagger/`
- ReDoc: `http://localhost:8050/redoc/`
- JSON Schema: `http://localhost:8050/swagger.json`

### Formato de Respuesta
Todas las respuestas son en formato JSON.

### Headers Requeridos
```http
Content-Type: application/json
Authorization: Bearer {token}  # Para endpoints protegidos
```

---

## 🔐 Autenticación

### Obtener Token JWT

**Endpoint:** `POST /api/token/`

**Body:**
```json
{
  "username": "usuario",
  "password": "contraseña"
}
```

**Respuesta:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Uso del Token:**
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

### Refrescar Token

**Endpoint:** `POST /api/token/refresh/`

**Body:**
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### Verificar Token

**Endpoint:** `POST /api/token/verify/`

**Body:**
```json
{
  "token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

## 📊 Modelos de Datos

### 1. Organization (Organización)

Representa una organización que agrupa catálogos.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre de la organización
- `slug` (string, auto-generated): Slug único para URLs
- `description` (string, optional): Descripción
- `created_at` (datetime, read-only): Fecha de creación
- `updated_at` (datetime, read-only): Fecha de actualización

**Relaciones:**
- Tiene múltiples `Catalogue`
- Tiene múltiples `Category`
- Tiene múltiples `Brand`
- Tiene múltiples `Playlist`

---

### 2. Catalogue (Catálogo)

Representa un catálogo de productos.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre del catálogo
- `code` (string, required, unique): Código único (ej: "CAT001")
- `slug` (string, auto-generated): Slug único
- `description` (string, optional): Descripción
- `organization` (integer, required): ID de la organización
- `is_active` (boolean, default: true): Estado activo/inactivo
- `currency` (string, default: "CLP"): Moneda del catálogo
  - Opciones: CLP, USD, EUR, ARS, BRL, MXN, COP, PEN
- `created_at` (datetime, read-only): Fecha de creación
- `updated_at` (datetime, read-only): Fecha de actualización

**Relaciones:**
- Pertenece a una `Organization`
- Tiene múltiples `Product`
- Tiene múltiples `Slide`
- Tiene múltiples `ImportFile`
- Tiene múltiples `ClientConfiguration`
- Tiene múltiples `CataloguePlaylist`

**Constraints:**
- `code` + `organization` deben ser únicos
- `slug` + `organization` deben ser únicos

---

### 3. Category (Categoría)

Categorías jerárquicas para productos.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre de la categoría
- `slug` (string, auto-generated): Slug único
- `description` (string, optional): Descripción
- `image` (file, optional): Imagen principal
- `icon_file` (file, optional): Archivo de ícono
- `parent` (integer, optional): ID de categoría padre
- `organization` (integer, required): ID de la organización
- `order` (integer, default: 0): Orden de visualización
- `style` (string, optional): Estilos CSS personalizados
- `tags` (string, optional): Etiquetas separadas por comas
- `state` (string, default: "publish"): Estado de publicación
  - Opciones: publish, pending, private, draft
- `virtual` (boolean, default: false): Si es virtual (oculto)

**Relaciones:**
- Pertenece a una `Organization`
- Puede tener una `Category` padre
- Puede tener múltiples categorías hijas (`children`)
- Tiene múltiples `Product` (many-to-many)
- Tiene múltiples `Images` (many-to-many)

---

### 4. Brand (Marca)

Marcas de productos.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre de la marca
- `slug` (string, auto-generated): Slug único
- `description` (string, optional): Descripción
- `image` (file, optional): Imagen/logo de la marca
- `parent` (integer, optional): ID de marca padre
- `organization` (integer, required): ID de la organización
- `order` (integer, default: 0): Orden de visualización
- `style` (string, optional): Estilos CSS personalizados
- `tags` (string, optional): Etiquetas separadas por comas
- `state` (string, default: "publish"): Estado de publicación
  - Opciones: publish, pending, private, draft
- `virtual` (boolean, default: false): Si es virtual (oculto)

**Relaciones:**
- Pertenece a una `Organization`
- Puede tener una `Brand` padre
- Tiene múltiples `Product`
- Tiene múltiples `Images` (many-to-many)

---

### 5. Product (Producto)

Productos del catálogo.

**Campos Básicos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre del producto
- `slug` (string, auto-generated): Slug único
- `sku` (string, optional): Código SKU único por catálogo
- `description` (string, optional): Descripción completa (HTML)
- `short_description` (string, optional): Descripción corta
- `image` (file, optional): Imagen principal

**Campos de Precio:**
- `currency` (string, optional): Moneda del producto
- `price_1` (decimal, optional): Precio regular
- `price_2` (decimal, optional): Precio oferta/descuento
- `price_1_formatted` (string, read-only): Precio formateado
- `price_2_formatted` (string, read-only): Precio oferta formateado

**Campos de Stock:**
- `manage_stock` (boolean, default: false): Gestionar inventario
- `stock_quantity` (integer, default: 0): Cantidad en stock
- `stock_status` (string, default: "instock"): Estado del stock
  - Opciones: instock, outofstock, onbackorder

**Campos de Dimensiones:**
- `length` (decimal, optional): Largo
- `width` (decimal, optional): Ancho
- `height` (decimal, optional): Alto
- `weight` (decimal, optional): Peso

**Campos de Organización:**
- `catalogue` (integer, required): ID del catálogo
- `brand` (integer, optional): ID de la marca
- `categories` (array[integer], optional): IDs de categorías
- `parent` (integer, optional): ID de producto padre (para variaciones)
- `order` (integer, default: 0): Orden de visualización
- `style` (string, optional): Estilos CSS personalizados
- `tags` (string, optional): Etiquetas separadas por comas
- `tags_list` (array[string], read-only): Tags como array
- `state` (string, default: "publish"): Estado de publicación
- `virtual` (boolean, default: false): Si es virtual (oculto)

**Campos de Auditoría:**
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación
- `is_removed` (boolean, default: false): Soft delete

**Relaciones:**
- Pertenece a un `Catalogue`
- Pertenece a una `Brand` (opcional)
- Tiene múltiples `Category` (many-to-many)
- Tiene múltiples `Images` (many-to-many)
- Puede tener un `Product` padre
- Puede tener múltiples variaciones (`variations`)
- Tiene un `MetaData` (one-to-one)

**Constraints:**
- `sku` + `catalogue` deben ser únicos

---

### 6. Images (Imágenes)

Imágenes reutilizables.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, optional): Nombre de la imagen
- `alt` (string, optional): Texto alternativo
- `code` (string, optional): Código identificador
- `image` (file, required): Archivo de imagen
- `organization` (integer, optional): ID de la organización
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a una `Organization` (opcional)
- Puede estar asociada a múltiples `Product`, `Category`, `Brand`

---

### 7. Slide (Carrusel/Banner)

Slides para carruseles o banners.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre del slide
- `slug` (string, auto-generated): Slug único
- `description` (string, optional): Descripción
- `image` (file, optional): Imagen del slide
- `catalogue` (integer, required): ID del catálogo
- `parent` (integer, optional): ID de slide padre
- `order` (integer, default: 0): Orden de visualización
- `style` (string, optional): Estilos CSS personalizados
- `tags` (string, optional): Etiquetas separadas por comas
- `state` (string, default: "publish"): Estado de publicación
- `virtual` (boolean, default: false): Si es virtual (oculto)

**Relaciones:**
- Pertenece a un `Catalogue`
- Puede tener un `Slide` padre
- Tiene múltiples `Images` (many-to-many)

---

### 8. ClientConfiguration (Configuración de Cliente)

Configuración de branding para clientes.

**Campos:**
- `id` (integer, read-only): ID único
- `catalogue` (integer, required): ID del catálogo
- `name` (string, required, unique): Nombre del cliente
- `domain` (string, required, unique): Dominio (ej: "cliente.dominio.com")
- `description` (string, optional): Descripción
- `primary_color` (string, default: "#FFFFFF"): Color primario (hex)
- `secondary_color` (string, default: "#000000"): Color secundario (hex)
- `accent_color` (string, optional): Color de acento (hex)
- `logo` (file, optional): Logo del cliente
- `logo_url` (string, read-only): URL completa del logo
- `favicon` (file, optional): Favicon del cliente
- `favicon_url` (string, read-only): URL completa del favicon
- `metadata` (json, optional): Metadata adicional
- `is_active` (boolean, default: true): Estado activo/inactivo
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a un `Catalogue`

---

### 9. Playlist (Lista de Reproducción)

Playlists de videos.

**Campos:**
- `id` (integer, read-only): ID único
- `name` (string, required): Nombre de la playlist
- `slug` (string, auto-generated): Slug único
- `description` (string, optional): Descripción
- `image` (file, optional): Imagen de la playlist
- `organization` (integer, required): ID de la organización
- `duration` (integer, default: 0): Duración total en segundos
- `style` (string, optional): Estilos CSS personalizados
- `tags` (string, optional): Etiquetas separadas por comas
- `state` (string, default: "publish"): Estado de publicación
- `is_active` (boolean, default: true): Estado activo/inactivo
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a una `Organization`
- Tiene múltiples `Video`
- Tiene múltiples `CataloguePlaylist`
- Tiene múltiples `Images` (many-to-many)

---

### 10. Video

Videos en playlists.

**Campos:**
- `id` (integer, read-only): ID único
- `playlist` (integer, required): ID de la playlist
- `name` (string, optional): Nombre del video (auto-generado del archivo)
- `description` (string, optional): Descripción
- `file` (file, required): Archivo de video
  - Formatos: mp4, avi, mov, wmv, flv, mkv, webm, m4v
- `file_url` (string, read-only): URL completa del video
- `thumbnail` (file, optional): Miniatura (auto-generada)
- `thumbnail_url` (string, read-only): URL completa de la miniatura
- `orientation` (string, default: "horizontal"): Orientación
  - Opciones: horizontal, vertical
- `duration` (integer, default: 0): Duración en segundos (auto-calculada)
- `order` (integer, default: 0): Orden en la playlist
- `organization` (integer, auto): ID de la organización (heredado)
- `is_active` (boolean, default: true): Estado activo/inactivo
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a una `Playlist`
- Pertenece a una `Organization` (heredado de playlist)

**Nota:** Al subir un video, se extraen automáticamente:
- Duración
- Orientación (basada en dimensiones)
- Thumbnail del primer frame

---

### 11. CataloguePlaylist (Asociación Catálogo-Playlist)

Asocia playlists a catálogos con fechas de vigencia.

**Campos:**
- `id` (integer, read-only): ID único
- `catalogue` (integer, required): ID del catálogo
- `playlist` (integer, required): ID de la playlist
- `start_date` (datetime, optional): Fecha de inicio de vigencia
- `end_date` (datetime, optional): Fecha de fin de vigencia
- `order` (integer, default: 0): Orden de reproducción
- `is_active` (boolean, default: true): Estado activo/inactivo
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a un `Catalogue`
- Pertenece a una `Playlist`

**Constraints:**
- `catalogue` + `playlist` + `start_date` deben ser únicos
- `end_date` debe ser posterior a `start_date`

**Lógica de Vigencia:**
- Sin `start_date`: vigente desde siempre
- Con `start_date`: vigente desde esa fecha
- Sin `end_date`: vigente indefinidamente
- Con `end_date`: vigente hasta esa fecha

---

### 12. ImportFile (Importación de Archivos)

Gestión de importaciones masivas de productos desde Excel.

**Campos:**
- `id` (integer, read-only): ID único
- `catalogue` (integer, required): ID del catálogo
- `file` (file, required): Archivo Excel (.xlsx, .xls)
- `images_zip` (file, optional): ZIP con imágenes
- `currency` (string, default: "CLP"): Moneda para productos
- `description` (string, optional): Descripción de la importación
- `uploaded` (boolean, default: false): Estado de procesamiento
- `import_mode` (string, default: "update"): Modo de importación
  - `update`: Actualizar existentes y crear nuevos
  - `create_only`: Solo crear nuevos (no actualizar)
  - `replace_all`: Reemplazar todo (eliminar y recrear)
  - `soft_delete`: Sincronizar (ocultar no incluidos)
- `user_created` (integer, optional): ID del usuario que creó
- `created` (datetime, read-only): Fecha de creación
- `modified` (datetime, read-only): Fecha de modificación

**Relaciones:**
- Pertenece a un `Catalogue`
- Pertenece a un `User` (opcional)

**Formato del Excel:**

Columnas requeridas:
- `SKU` o primera columna: Código único del producto
- `NOMBRE`: Nombre del producto
- `PRECIO`: Precio regular

Columnas opcionales:
- `DESCRIPCIÓN` o `DESCRIPCION`: Descripción del producto
- `PRECIO_OFERTA` o `PRECIO OFERTA`: Precio con descuento
- `DESCUENTO_EN_%` o `DESCUENTO`: Porcentaje de descuento
- `STOCK`: Cantidad en inventario
- `CATEGORÍA` o `CATEGORIA`: Nombre de la categoría
- `MARCA`: Nombre de la marca
- `IMAGEN`: URL de la imagen principal
- `IMAGES`: URLs de imágenes adicionales (separadas por |)

**Proceso Automático:**
1. Al guardar el archivo, se procesa automáticamente
2. Crea/actualiza productos según el modo
3. Crea categorías y marcas si no existen
4. Descarga imágenes desde URLs
5. Genera tags automáticamente
6. Marca como `uploaded=true` al finalizar

---

### 13. MetaData

Metadatos SEO para productos.

**Campos:**
- `id` (integer, read-only): ID único
- `product` (integer, required): ID del producto
- `meta_title` (string, optional): Título SEO
- `meta_description` (string, optional): Descripción SEO
- `meta_keywords` (string, optional): Palabras clave SEO

**Relaciones:**
- Pertenece a un `Product` (one-to-one)

---

## 🔌 Endpoints Disponibles

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/token/` | Obtener token JWT |
| POST | `/api/token/refresh/` | Refrescar token |
| POST | `/api/token/verify/` | Verificar token |

---

### Categories (Categorías)

**Base URL:** `/api/category/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/category/` | Listar todas las categorías | No |
| POST | `/api/category/` | Crear categoría | Sí |
| GET | `/api/category/{id}/` | Obtener categoría específica | No |
| PUT | `/api/category/{id}/` | Actualizar categoría completa | Sí |
| PATCH | `/api/category/{id}/` | Actualizar categoría parcial | Sí |
| DELETE | `/api/category/{id}/` | Eliminar categoría | Sí |

**Filtros disponibles:**
- `state`: Estado de publicación (publish, pending, private, draft)
- `parent`: ID de categoría padre
- `organization`: ID de organización
- `org_slug`: Slug de organización

**Búsqueda:**
- `search`: Buscar en name, description, style, state

**Ordenamiento:**
- `ordering`: order, name, created (usar `-` para descendente)

**Ejemplo GET:**
```http
GET /api/category/?org_slug=favric&state=publish&ordering=order
```

**Ejemplo POST:**
```json
{
  "name": "Bebidas",
  "description": "Categoría de bebidas",
  "organization": 1,
  "parent": null,
  "order": 1,
  "state": "publish",
  "virtual": false
}
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Bebidas",
  "slug": "bebidas",
  "description": "Categoría de bebidas",
  "image": null,
  "icon_file": null,
  "images": [],
  "style": "",
  "tags": null,
  "state": "publish",
  "organization": 1,
  "parent": null,
  "childs": [],
  "order": 1,
  "virtual": false
}
```

---

### Products (Productos)

**Base URL:** `/api/product_view/` (ViewSet) o `/api/product/` (ListView)

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/product_view/` | Listar productos | No |
| POST | `/api/product_view/` | Crear producto | Sí |
| GET | `/api/product_view/{id}/` | Obtener producto específico | No |
| PUT | `/api/product_view/{id}/` | Actualizar producto completo | Sí |
| PATCH | `/api/product_view/{id}/` | Actualizar producto parcial | Sí |
| DELETE | `/api/product_view/{id}/` | Eliminar producto | Sí |

**Filtros disponibles:**
- `state`: Estado de publicación
- `brand`: ID de marca
- `categories`: ID de categoría
- `catalogue`: ID de catálogo
- `org_slug`: Slug de organización
- `catalogue_slug`: Slug de catálogo
- `catalogue_code`: Código de catálogo
- `id_in`: Lista de IDs (ej: `1,2,3`)
- `categories__name`: Nombre de categoría
- `categories__id`: ID de categoría
- `brand__name`: Nombre de marca
- `brand__id`: ID de marca

**Búsqueda:**
- `search`: Buscar en name, sku, description, short_description

**Ordenamiento:**
- `ordering`: name, price_1, created

**Ejemplo GET con filtros:**
```http
GET /api/product_view/?catalogue_code=CAT001&state=publish&brand__name=Coca-Cola&ordering=-created
```

**Ejemplo POST:**
```json
{
  "catalogue": 1,
  "name": "Coca-Cola 500ml",
  "sku": "CC500",
  "short_description": "Bebida gaseosa",
  "description": "<p>Coca-Cola 500ml</p>",
  "price_1": "1500.00",
  "price_2": "1200.00",
  "currency": "CLP",
  "brand": 1,
  "categories": [1, 2],
  "stock_quantity": 100,
  "manage_stock": true,
  "stock_status": "instock",
  "state": "publish",
  "tags": "bebida, gaseosa, coca-cola"
}
```

**Respuesta incluye:**
```json
{
  "id": 1,
  "name": "Coca-Cola 500ml",
  "slug": "coca-cola-500ml",
  "sku": "CC500",
  "description": "<p>Coca-Cola 500ml</p>",
  "short_description": "Bebida gaseosa",
  "image": "https://storage.googleapis.com/...",
  "images": [
    {
      "id": 1,
      "name": "Imagen 1",
      "image": "https://storage.googleapis.com/...",
      "alt": "Coca-Cola"
    }
  ],
  "price_1": "1500.00",
  "price_1_formatted": "$1.500",
  "price_2": "1200.00",
  "price_2_formatted": "$1.200",
  "currency": "CLP",
  "currency_info": {
    "code": "CLP",
    "symbol": "$",
    "name": "Peso Chileno"
  },
  "brand": {
    "id": 1,
    "name": "Coca-Cola",
    "slug": "coca-cola",
    "image": "https://..."
  },
  "categories": [
    {
      "id": 1,
      "name": "Bebidas",
      "slug": "bebidas"
    }
  ],
  "tags": "bebida, gaseosa, coca-cola",
  "tags_list": ["bebida", "gaseosa", "coca-cola"],
  "stock_quantity": 100,
  "stock_status": "instock",
  "manage_stock": true,
  "state": "publish",
  "variations": [],
  "created": "2026-03-03T17:00:00Z",
  "modified": "2026-03-03T17:00:00Z"
}
```

---

### Brands (Marcas)

**Base URL:** `/api/brand/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/brand/` | Listar marcas | No |
| POST | `/api/brand/` | Crear marca | Sí |
| GET | `/api/brand/{id}/` | Obtener marca específica | No |
| PUT | `/api/brand/{id}/` | Actualizar marca completa | Sí |
| PATCH | `/api/brand/{id}/` | Actualizar marca parcial | Sí |
| DELETE | `/api/brand/{id}/` | Eliminar marca | Sí |

**Filtros:**
- `state`: Estado de publicación
- `organization`: ID de organización
- `org_slug`: Slug de organización

**Búsqueda:**
- `search`: Buscar en name, description

**Ordenamiento:**
- `ordering`: order, name

**Ejemplo POST:**
```json
{
  "name": "Coca-Cola",
  "description": "The Coca-Cola Company",
  "organization": 1,
  "order": 1,
  "state": "publish"
}
```

---

### Slides (Carruseles/Banners)

**Base URL:** `/api/slide/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/slide/` | Listar slides | No |
| POST | `/api/slide/` | Crear slide | Sí |
| GET | `/api/slide/{id}/` | Obtener slide específico | No |
| PUT | `/api/slide/{id}/` | Actualizar slide completo | Sí |
| PATCH | `/api/slide/{id}/` | Actualizar slide parcial | Sí |
| DELETE | `/api/slide/{id}/` | Eliminar slide | Sí |

**Filtros:**
- `state`: Estado de publicación
- `virtual`: Booleano
- `catalogue`: ID de catálogo
- `org_slug`: Slug de organización
- `catalogue_slug`: Slug de catálogo
- `catalogue_code`: Código de catálogo

**Búsqueda:**
- `search`: Buscar en name, description

**Ordenamiento:**
- `ordering`: order, name, created

**Ejemplo POST:**
```json
{
  "catalogue": 1,
  "name": "Banner Principal",
  "description": "Banner de promoción",
  "order": 1,
  "state": "publish"
}
```

---

### Client Configurations (Configuraciones de Cliente)

**Base URL:** `/api/client-configurations/`

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| GET | `/api/client-configurations/` | Listar configuraciones | No |
| POST | `/api/client-configurations/` | Crear configuración | Sí |
| GET | `/api/client-configurations/{id}/` | Obtener por ID | No |
| GET | `/api/client-configurations/{name}/` | Obtener por nombre | No |
| PUT | `/api/client-configurations/{id}/` | Actualizar completa | Sí |
| PATCH | `/api/client-configurations/{id}/` | Actualizar parcial | Sí |
| DELETE | `/api/client-configurations/{id}/` | Eliminar | Sí |

**Endpoints adicionales:**
- `GET /api/client-config/{client_name}/` - Obtener por nombre
- `GET /api/client-config-by-domain/{domain}/` - Obtener por dominio

**Filtros:**
- `is_active`: Booleano
- `catalogue`: ID de catálogo

**Búsqueda:**
- `search`: Buscar en name, domain, description

**Ejemplo POST:**
```json
{
  "catalogue": 1,
  "name": "cliente-demo",
  "domain": "demo.favric.cl",
  "description": "Cliente de demostración",
  "primary_color": "#FF5733",
  "secondary_color": "#000000",
  "accent_color": "#007BFF",
  "is_active": true,
  "metadata": {
    "custom_field": "value"
  }
}
```

**Respuesta:**
```json
{
  "id": 1,
  "catalogue": 1,
  "name": "cliente-demo",
  "primary_color": "#FF5733",
  "secondary_color": "#000000",
  "accent_color": "#007BFF",
  "logo": null,
  "favicon": null,
  "logo_url": null,
  "favicon_url": null,
  "domain": "demo.favric.cl",
  "description": "Cliente de demostración",
  "metadata": {
    "custom_field": "value"
  },
  "is_active": true,
  "created": "2026-03-03T17:00:00Z",
  "modified": "2026-03-03T17:00:00Z"
}
```

---

### Complete Catalogue (Catálogo Completo)

**Endpoint:** `GET /api/catalogue/{code}/`

Obtiene toda la información de un catálogo en una sola llamada.

**Parámetros:**
- `code` (string): Código del catálogo

**Respuesta incluye:**
- Información del catálogo
- Información de la organización
- Todos los productos (con imágenes, categorías, marcas)
- Todas las categorías de la organización
- Todas las marcas de la organización
- Todos los slides del catálogo
- Configuración del cliente
- Playlists vigentes (agrupadas por orientación)

**Ejemplo:**
```http
GET /api/catalogue/CAT001/
```

**Respuesta:**
```json
{
  "id": 1,
  "name": "Catálogo Principal",
  "code": "CAT001",
  "slug": "catalogo-principal",
  "description": "Catálogo principal de productos",
  "is_active": true,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-03-03T17:00:00Z",
  "organization": {
    "id": 1,
    "name": "Favric",
    "slug": "favric",
    "description": "Organización Favric",
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-03-03T17:00:00Z"
  },
  "products": [
    {
      "id": 1,
      "name": "Producto 1",
      "price_1": "1000.00",
      "price_1_formatted": "$1.000",
      ...
    }
  ],
  "categories": [
    {
      "id": 1,
      "name": "Categoría 1",
      ...
    }
  ],
  "brands": [
    {
      "id": 1,
      "name": "Marca 1",
      ...
    }
  ],
  "slides": [
    {
      "id": 1,
      "name": "Slide 1",
      ...
    }
  ],
  "client_configuration": {
    "id": 1,
    "name": "cliente-demo",
    "primary_color": "#FF5733",
    ...
  },
  "playlists": {
    "vertical": [
      {
        "id": 1,
        "name": "Playlist Vertical 1",
        "videos": [
          {
            "id": 1,
            "name": "Video 1",
            "file_url": "https://...",
            "thumbnail_url": "https://...",
            "duration": 30,
            "orientation": "vertical"
          }
        ]
      }
    ],
    "horizontal": [
      {
        "id": 2,
        "name": "Playlist Horizontal 1",
        "videos": [...]
      }
    ]
  }
}
```

---

## 📤 Gestión de Archivos

### Subir Imágenes

Para subir imágenes, usa `multipart/form-data`:

**Ejemplo con Product:**
```http
POST /api/product_view/
Content-Type: multipart/form-data

name: Producto Test
catalogue: 1
price_1: 1000
image: [archivo]
```

**Ejemplo con JavaScript:**
```javascript
const formData = new FormData();
formData.append('name', 'Producto Test');
formData.append('catalogue', 1);
formData.append('price_1', 1000);
formData.append('image', fileInput.files[0]);

fetch('/api/product_view/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});
```

### Importación Masiva de Productos

**Endpoint:** `POST /api/admin/` (Django Admin) o crear ImportFile via API

**Proceso:**
1. Preparar archivo Excel con las columnas requeridas
2. Subir archivo a través del admin o API
3. El sistema procesa automáticamente
4. Verifica el campo `uploaded` para confirmar

**Formato Excel mínimo:**
```
SKU     | NOMBRE           | PRECIO
--------|------------------|--------
CC500   | Coca-Cola 500ml  | 1500
PP500   | Pepsi 500ml      | 1400
```

**Formato Excel completo:**
```
SKU   | NOMBRE          | PRECIO | PRECIO_OFERTA | DESCRIPCIÓN      | CATEGORÍA | MARCA     | STOCK | IMAGEN
------|-----------------|--------|---------------|------------------|-----------|-----------|-------|--------
CC500 | Coca-Cola 500ml | 1500   | 1200          | Bebida gaseosa   | Bebidas   | Coca-Cola | 100   | https://...
```

---

## 🔍 Filtros y Búsqueda

### Búsqueda de Texto

Usa el parámetro `search`:

```http
GET /api/product_view/?search=coca-cola
```

### Filtros Múltiples

Combina múltiples filtros:

```http
GET /api/product_view/?catalogue_code=CAT001&state=publish&brand__name=Coca-Cola&categories__id=1
```

### Filtros IN (múltiples valores)

Usa `id_in` para filtrar por múltiples IDs:

```http
GET /api/product_view/?id_in=1,2,3,4,5
```

### Ordenamiento

Usa `ordering` (prefijo `-` para descendente):

```http
GET /api/product_view/?ordering=-created
GET /api/product_view/?ordering=price_1
GET /api/category/?ordering=order,name
```

### Paginación

Por defecto, las respuestas están paginadas:

```json
{
  "count": 100,
  "next": "http://localhost:8000/api/product_view/?page=2",
  "previous": null,
  "results": [...]
}
```

---

## 💡 Casos de Uso Comunes

### 1. Crear un Producto Completo

```javascript
// 1. Crear categoría si no existe
const category = await fetch('/api/category/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Bebidas',
    organization: 1,
    state: 'publish'
  })
}).then(r => r.json());

// 2. Crear marca si no existe
const brand = await fetch('/api/brand/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Coca-Cola',
    organization: 1,
    state: 'publish'
  })
}).then(r => r.json());

// 3. Crear producto con imagen
const formData = new FormData();
formData.append('catalogue', 1);
formData.append('name', 'Coca-Cola 500ml');
formData.append('sku', 'CC500');
formData.append('price_1', 1500);
formData.append('price_2', 1200);
formData.append('currency', 'CLP');
formData.append('brand', brand.id);
formData.append('categories', category.id);
formData.append('stock_quantity', 100);
formData.append('manage_stock', true);
formData.append('state', 'publish');
formData.append('image', imageFile);

const product = await fetch('/api/product_view/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
}).then(r => r.json());
```

### 2. Actualizar Stock de un Producto

```javascript
const response = await fetch(`/api/product_view/${productId}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    stock_quantity: 50
  })
});
```

### 3. Obtener Productos de una Categoría

```javascript
const products = await fetch(
  '/api/product_view/?categories__id=1&state=publish'
).then(r => r.json());
```

### 4. Buscar Productos por Texto

```javascript
const results = await fetch(
  '/api/product_view/?search=coca&state=publish'
).then(r => r.json());
```

### 5. Crear Configuración de Cliente

```javascript
const config = await fetch('/api/client-configurations/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    catalogue: 1,
    name: 'mi-cliente',
    domain: 'cliente.dominio.com',
    primary_color: '#FF5733',
    secondary_color: '#000000',
    is_active: true
  })
}).then(r => r.json());
```

### 6. Obtener Catálogo Completo para Frontend

```javascript
const catalogue = await fetch('/api/catalogue/CAT001/')
  .then(r => r.json());

// Ahora tienes:
// - catalogue.products (todos los productos)
// - catalogue.categories (todas las categorías)
// - catalogue.brands (todas las marcas)
// - catalogue.slides (todos los slides)
// - catalogue.client_configuration (configuración)
// - catalogue.playlists (videos agrupados por orientación)
```

### 7. Filtrar Productos por Marca y Categoría

```javascript
const products = await fetch(
  '/api/product_view/?brand__name=Coca-Cola&categories__name=Bebidas&state=publish'
).then(r => r.json());
```

### 8. Crear Playlist con Videos

```javascript
// 1. Crear playlist
const playlist = await fetch('/api/playlist/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'Playlist Principal',
    organization: 1,
    is_active: true
  })
}).then(r => r.json());

// 2. Subir video
const videoFormData = new FormData();
videoFormData.append('playlist', playlist.id);
videoFormData.append('file', videoFile);
videoFormData.append('orientation', 'vertical');
videoFormData.append('order', 1);

const video = await fetch('/api/video/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: videoFormData
}).then(r => r.json());

// 3. Asociar playlist a catálogo
const cataloguePlaylist = await fetch('/api/catalogue-playlist/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    catalogue: 1,
    playlist: playlist.id,
    order: 1,
    is_active: true
  })
}).then(r => r.json());
```

---

## 🎯 Recomendaciones para el Frontend

### 1. Gestión de Estado

Mantén un estado global con:
- Token de autenticación
- Información del usuario
- Catálogo actual
- Filtros activos

### 2. Caché de Datos

Cachea respuestas de:
- Categorías (cambian poco)
- Marcas (cambian poco)
- Configuración de cliente (cambia poco)

### 3. Optimización de Imágenes

- Usa lazy loading para imágenes
- Implementa placeholders mientras cargan
- Considera usar thumbnails para listados

### 4. Manejo de Errores

```javascript
try {
  const response = await fetch('/api/product_view/', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(productData)
  });

  if (!response.ok) {
    const error = await response.json();
    console.error('Error:', error);
    // Mostrar mensaje al usuario
  }

  const product = await response.json();
  // Éxito
} catch (error) {
  console.error('Network error:', error);
  // Mostrar mensaje de error de red
}
```

### 5. Refresh de Token

```javascript
async function refreshToken() {
  const response = await fetch('/api/token/refresh/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      refresh: localStorage.getItem('refresh_token')
    })
  });

  if (response.ok) {
    const data = await response.json();
    localStorage.setItem('access_token', data.access);
    return data.access;
  } else {
    // Redirigir a login
    window.location.href = '/login';
  }
}
```

### 6. Interceptor para Tokens Expirados

```javascript
async function fetchWithAuth(url, options = {}) {
  let token = localStorage.getItem('access_token');

  options.headers = {
    ...options.headers,
    'Authorization': `Bearer ${token}`
  };

  let response = await fetch(url, options);

  // Si el token expiró, refrescar y reintentar
  if (response.status === 401) {
    token = await refreshToken();
    options.headers['Authorization'] = `Bearer ${token}`;
    response = await fetch(url, options);
  }

  return response;
}
```

---

## 📝 Notas Importantes

### Soft Delete

Los modelos con `is_removed` no se eliminan físicamente:
- `Product`
- `Images`
- `ClientConfiguration`
- `Playlist`
- `Video`
- `CataloguePlaylist`

Para "eliminar", usa:
```javascript
await fetch(`/api/product_view/${id}/`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    is_removed: true
  })
});
```

### Slugs Automáticos

Los campos `slug` se generan automáticamente desde `name`. No es necesario enviarlos en POST/PUT.

### Tags

Las tags se almacenan como string separado por comas:
```json
{
  "tags": "bebida, gaseosa, coca-cola"
}
```

Se retornan también como array en `tags_list`:
```json
{
  "tags": "bebida, gaseosa, coca-cola",
  "tags_list": ["bebida", "gaseosa", "coca-cola"]
}
```

### Precios Formateados

Los precios se retornan en dos formatos:
- `price_1`: Valor decimal (1500.00)
- `price_1_formatted`: Valor formateado según moneda ($1.500)

### Monedas Soportadas

- CLP: Peso Chileno ($)
- USD: Dólar Estadounidense ($)
- EUR: Euro (€)
- ARS: Peso Argentino ($)
- BRL: Real Brasileño (R$)
- MXN: Peso Mexicano ($)
- COP: Peso Colombiano ($)
- PEN: Sol Peruano (S/)

### Variaciones de Productos

Para crear variaciones:
```json
{
  "parent": 1,
  "name": "Coca-Cola 500ml - Sabor Limón",
  "sku": "CC500-LIMON",
  ...
}
```

Las variaciones se retornan en el campo `variations` del producto padre.

---

## 🚀 Swagger/OpenAPI

Documentación interactiva disponible en:
- Swagger UI: `http://localhost:8050/swagger/`
- ReDoc: `http://localhost:8050/redoc/`
- JSON Schema: `http://localhost:8050/swagger.json`

---

## 📞 Soporte

Para más información, consulta:
- `/docs/API_DOCUMENTATION.md`
- `/docs/PROJECT_DOCUMENTATION.md`
- `/docs/IMPORT_GUIDE.md`

---

**Última actualización:** 6 de Marzo, 2026
