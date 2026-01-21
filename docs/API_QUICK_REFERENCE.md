# 🚀 API Quick Reference - Para Desarrollo Angular

## 📍 URLs Base

- **Producción**: `https://catalogue.favric.cl/api/`
- **Local**: `http://localhost:8050/api/`

## 📥 Probar con Insomnia

**[📦 Descargar Colección de Insomnia](../Insomnia_Catalogue_API.json)** - Todos los endpoints listos para probar

---

## 🎯 Endpoints Principales

### **Productos**
```
GET    /api/products/                    # Listar
GET    /api/products/{id}/               # Obtener uno
POST   /api/products/                    # Crear
PATCH  /api/products/{id}/               # Actualizar
DELETE /api/products/{id}/               # Eliminar
```

### **Categorías**
```
GET    /api/categories/
GET    /api/categories/{id}/
POST   /api/categories/
PATCH  /api/categories/{id}/
DELETE /api/categories/{id}/
```

### **Marcas**
```
GET    /api/brands/
GET    /api/brands/{id}/
POST   /api/brands/
PATCH  /api/brands/{id}/
DELETE /api/brands/{id}/
```

### **Slides/Banners**
```
GET    /api/slides/
GET    /api/slides/{id}/
POST   /api/slides/
PATCH  /api/slides/{id}/
DELETE /api/slides/{id}/
```

### **Configuración de Cliente**
```
GET    /api/client-config/{name}/              # Por nombre
GET    /api/client-config-by-domain/{domain}/  # Por dominio
GET    /api/client-configurations/             # Listar todas
```

### **Catálogo Completo** ⭐
```
GET    /api/catalogue/{code}/  # Retorna TODO en una llamada
```

---

## 🔍 Filtros Comunes

### **Productos**
```
?search=vino                    # Buscar
?catalogue__code=CAT2024        # Por código de catálogo
?categories=1                   # Por categoría ID
?brand=1                        # Por marca ID
?ordering=-price_1              # Ordenar por precio desc
?page=2&page_size=50           # Paginación
```

### **Categorías**
```
?org_slug=favric               # Por organización
?parent=1                      # Subcategorías
?state=publish                 # Por estado
```

### **Marcas**
```
?org_slug=favric               # Por organización
?state=publish                 # Por estado
```

---

## 📦 Interfaces TypeScript Esenciales

```typescript
// Product
interface Product {
  id: number;
  name: string;
  sku?: string;
  price_1?: string;
  price_1_formatted?: string;  // "$5.500"
  price_2?: string;
  price_2_formatted?: string;
  currency: string;
  stock_quantity: number;
  stock_status: 'instock' | 'outofstock';
  tags?: string;
  tags_list?: string[];
  brand?: Brand;
  categories?: Category[];
  images?: Image[];
}

// Category
interface Category {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
  parent?: number;
}

// Brand
interface Brand {
  id: number;
  name: string;
  slug: string;
  description?: string;
  image?: string;
}

// ClientConfiguration
interface ClientConfiguration {
  id: number;
  name: string;
  domain: string;
  primary_color: string;    // "#FF5733"
  secondary_color: string;
  accent_color?: string;
  logo?: string;
  favicon?: string;
}

// Respuesta Paginada
interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}
```

---

## 💡 Ejemplos de Uso

### **Obtener productos de un catálogo**
```typescript
this.http.get<PaginatedResponse<Product>>(
  'https://catalogue.favric.cl/api/products/',
  {
    params: {
      catalogue__code: 'CAT2024',
      ordering: '-created'
    }
  }
).subscribe(response => {
  this.products = response.results;
});
```

### **Buscar productos por tags**
```typescript
this.http.get<PaginatedResponse<Product>>(
  'https://catalogue.favric.cl/api/products/',
  {
    params: {
      search: 'vino tinto'
    }
  }
).subscribe(response => {
  this.products = response.results;
});
```

### **Obtener catálogo completo**
```typescript
this.http.get<CompleteCatalogue>(
  'https://catalogue.favric.cl/api/catalogue/CAT2024/'
).subscribe(data => {
  this.products = data.products;
  this.categories = data.categories;
  this.brands = data.brands;
  this.slides = data.slides;
  this.config = data.client_configuration;
});
```

### **Obtener configuración por dominio**
```typescript
const domain = window.location.hostname;
this.http.get<ClientConfiguration>(
  `https://catalogue.favric.cl/api/client-config-by-domain/${domain}/`
).subscribe(config => {
  // Aplicar colores
  document.documentElement.style.setProperty('--primary-color', config.primary_color);
  document.documentElement.style.setProperty('--secondary-color', config.secondary_color);
});
```

### **Crear producto**
```typescript
const newProduct = {
  catalogue: 1,
  name: 'Nuevo Producto',
  sku: 'PROD001',
  price_1: '10000.00',
  stock_quantity: 100,
  manage_stock: true
};

this.http.post<Product>(
  'https://catalogue.favric.cl/api/products/',
  newProduct
).subscribe(product => {
  console.log('Producto creado:', product);
});
```

### **Actualizar stock**
```typescript
this.http.patch<Product>(
  `https://catalogue.favric.cl/api/products/${productId}/`,
  { stock_quantity: 50 }
).subscribe(product => {
  console.log('Stock actualizado:', product.stock_quantity);
  console.log('Estado:', product.stock_status); // 'instock' o 'outofstock'
});
```

---

## 🎨 Características Especiales

### **Formato de Moneda Automático**
Los productos incluyen precios formateados según la moneda del catálogo:

```json
{
  "price_1": "15000.00",
  "price_1_formatted": "$15.000",  // ← Listo para mostrar
  "currency": "CLP",
  "currency_info": {
    "symbol": "$",
    "decimals": 0,
    "thousands_separator": "."
  }
}
```

### **Tags Automáticas**
Los productos tienen tags generadas automáticamente:

```json
{
  "name": "Fernet con Cola",
  "tags": "fernet, cola, destilado",
  "tags_list": ["fernet", "cola", "destilado"]  // ← Para chips/badges
}
```

### **Stock Automático**
El estado de stock se actualiza automáticamente:

```typescript
// Al actualizar stock_quantity a 0
product.stock_status // Cambia automáticamente a 'outofstock'

// Al actualizar stock_quantity > 0
product.stock_status // Cambia automáticamente a 'instock'
```

---

## ⚠️ Notas Importantes

1. **Paginación**: Todos los listados están paginados (20 por página)
2. **CORS**: Configurado para permitir peticiones desde Angular
3. **Autenticación**: Actualmente no requerida (AllowAny)
4. **Formato de Fechas**: ISO 8601 (`2024-01-21T15:30:00Z`)
5. **Trailing Slash**: Siempre incluir `/` al final de las URLs

---

## 🔗 Documentación Completa

Ver `API_DOCUMENTATION.md` para:
- Interfaces TypeScript completas
- Ejemplos de servicios Angular
- Todos los modelos y campos
- Configuración de environment
- Manejo de errores

---

**Última actualización**: 2026-01-21
