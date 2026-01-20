# 🛍️ Catalogue API

> **API REST para gestión de catálogos de productos con arquitectura multi-catálogo**

[![Django](https://img.shields.io/badge/Django-4.2.7-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue.svg)](https://www.postgresql.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

---

## 🎯 **Descripción**

Sistema de gestión de catálogos de productos con soporte para **múltiples catálogos por organización**, importación de datos desde Excel, gestión de categorías, marcas, imágenes y configuraciones personalizadas.

### **Características Principales**

✅ **Sistema Multi-Catálogo** - Una organización puede tener múltiples catálogos  
✅ **Importación desde Excel** - Importa productos masivamente con 4 modos diferentes  
✅ **API REST Completa** - Endpoints para productos, catálogos, categorías, marcas  
✅ **Admin de Django** - Interfaz administrativa completa  
✅ **Gestión de Imágenes** - Descarga y asociación automática de imágenes  
✅ **Configuraciones por Catálogo** - Personalización visual por catálogo  
✅ **Slides Personalizados** - Banners y slides por catálogo  

---

## 🚀 **Inicio Rápido**

### **1. Clonar el Repositorio**
```bash
git clone <repository-url>
cd catalogue_api
```

### **2. Configurar Variables de Entorno**
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

### **3. Iniciar con Docker**
```bash
docker compose up -d
```

### **4. Crear Superusuario**
```bash
docker compose exec web python manage.py createsuperuser
```

### **5. Acceder**
- **Admin**: http://localhost:8050/admin/
- **API**: http://localhost:8050/api/

---

## 📚 **Documentación**

Toda la documentación está organizada en el directorio [`docs/`](docs/):

### **📖 Inicio Rápido**
- [QUICK_START.md](docs/QUICK_START.md) - Guía rápida de inicio
- [DOCKER_README.md](docs/DOCKER_README.md) - Configuración con Docker
- [PRODUCTION_README.md](docs/PRODUCTION_README.md) - Despliegue en producción

### **🏗️ Arquitectura** ⭐
- [FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) - Resumen ejecutivo del proyecto
- [CATALOGUE_ARCHITECTURE.md](docs/CATALOGUE_ARCHITECTURE.md) - Arquitectura de catálogos
- [CATALOGUE_COMPLETE.md](docs/CATALOGUE_COMPLETE.md) - Implementación completa

### **📥 Importación**
- [IMPORTER_UPDATED.md](docs/IMPORTER_UPDATED.md) - Guía del importador actualizado
- [IMPORT_GUIDE.md](docs/IMPORT_GUIDE.md) - Guía completa de importación
- [FIELD_MAPPING.md](docs/FIELD_MAPPING.md) - Mapeo de campos Excel → Modelo

### **🔄 Migración**
- [CATALOGUE_MIGRATION_STEPS.md](docs/CATALOGUE_MIGRATION_STEPS.md) - Migración a catálogos
- [MIGRATION_COMPLETED.md](docs/MIGRATION_COMPLETED.md) - Resumen de migración

### **📑 Índice Completo**
- [docs/README.md](docs/README.md) - Índice completo de documentación

---

## 🏗️ **Arquitectura**

### **Modelo de Datos**

```
Organization (1) ──→ (N) Catalogue (1) ──→ (N) Product
                           ↓
                      ImportFile
                           ↓
                        Slide
                           ↓
                  ClientConfiguration

Organization (1) ──→ (N) Category (compartidas)
Organization (1) ──→ (N) Brand (compartidas)
Organization (1) ──→ (N) Images (compartidas)
```

### **Casos de Uso**

#### **1. Catálogos por Temporada**
```python
verano = Catalogue.objects.create(name="Verano 2026", slug="verano-2026", organization=org)
invierno = Catalogue.objects.create(name="Invierno 2026", slug="invierno-2026", organization=org)
```

#### **2. Catálogos por Canal**
```python
b2b = Catalogue.objects.create(name="Mayorista", slug="b2b", organization=org)
b2c = Catalogue.objects.create(name="Retail", slug="b2c", organization=org)
```

---

## 📥 **Importación de Productos**

### **Sintaxis**
```bash
python scripts/transform_client_excel.py <excel_file> <catalogue_slug> [--mode MODE] [--no-images]
```

### **Modos de Importación**
- `soft_delete` - Sincroniza (oculta no incluidos) ⭐ Recomendado
- `update` - Actualiza existentes y crea nuevos
- `create_only` - Solo crea nuevos
- `replace_all` - Elimina todo y recrea ⚠️ Peligroso

### **Ejemplo**
```bash
python scripts/transform_client_excel.py productos.xlsx catalogo-principal --mode soft_delete
```

---

## 🌐 **API Endpoints**

### **Productos**
```bash
# Listar todos
GET /api/products/

# Filtrar por catálogo
GET /api/products/?catalogue_slug=verano-2026

# Filtrar por organización
GET /api/products/?org_slug=mi-organizacion

# Obtener uno
GET /api/products/{id}/
```

### **Catálogos**
```bash
# Listar todos
GET /api/catalogues/

# Obtener uno
GET /api/catalogues/{id}/
```

### **Categorías y Marcas**
```bash
GET /api/categories/
GET /api/brands/
```

---

## 🛠️ **Tecnologías**

### **Backend**
- Django 4.2.7
- Django REST Framework
- PostgreSQL 13
- Celery (opcional)

### **Frontend Admin**
- Django Admin
- CKEditor para contenido rico

### **Infraestructura**
- Docker & Docker Compose
- Nginx (producción)
- Gunicorn (producción)

---

## 📊 **Estructura del Proyecto**

```
catalogue_api/
├── api/                    # App principal
│   ├── models.py          # Modelos (Catalogue, Product, etc.)
│   ├── views.py           # Vistas y ViewSets
│   ├── serializers.py     # Serializers de DRF
│   ├── admin.py           # Admin de Django
│   └── migrations/        # Migraciones
│
├── core/                   # Configuración del proyecto
│   ├── settings.py        # Configuración
│   └── urls.py            # URLs principales
│
├── scripts/                # Scripts de utilidad
│   ├── transform_client_excel.py  # Importador
│   ├── analyze_client_excel.py    # Analizador
│   ├── migrate_to_catalogues.py   # Migración
│   └── test_import.py             # Pruebas
│
├── docs/                   # Documentación completa
│   ├── README.md          # Índice de documentación
│   ├── FINAL_SUMMARY.md   # Resumen ejecutivo
│   └── ...                # Más documentos
│
├── docker-compose.yml      # Configuración Docker
├── Dockerfile             # Imagen Docker
├── requirements.txt       # Dependencias Python
└── README.md              # Este archivo
```

---

## 🧪 **Testing**

### **Probar el Sistema**
```bash
docker compose exec web python scripts/test_import.py
```

### **Crear Datos de Prueba**
```bash
docker compose exec web python manage.py shell

from api.models import Organization, Catalogue, Product

org = Organization.objects.first()
catalogue = Catalogue.objects.create(
    name="Test Catalogue",
    slug="test-catalogue",
    organization=org
)

Product.objects.create(
    catalogue=catalogue,
    sku="TEST-001",
    name="Producto de Prueba",
    price_1=10000,
    currency="CLP"
)
```

---

## 🔧 **Comandos Útiles**

### **Docker**
```bash
# Iniciar servicios
docker compose up -d

# Ver logs
docker compose logs -f web

# Reiniciar
docker compose restart web

# Detener
docker compose down
```

### **Django**
```bash
# Shell
docker compose exec web python manage.py shell

# Migraciones
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Crear superusuario
docker compose exec web python manage.py createsuperuser

# Colectar estáticos
docker compose exec web python manage.py collectstatic
```

---

## 📈 **Estado del Proyecto**

- ✅ **Sistema de Catálogos**: Implementado y funcionando
- ✅ **Importador**: Actualizado y probado
- ✅ **Migraciones**: Aplicadas exitosamente
- ✅ **Admin**: Completamente funcional
- ✅ **API**: Endpoints funcionando
- ✅ **Documentación**: Completa y actualizada

**Estado**: 🟢 **Producción Ready**

---

## 📞 **Soporte**

### **Documentación**
Ver el directorio [`docs/`](docs/) para documentación completa.

### **Documentos Clave**
- [FINAL_SUMMARY.md](docs/FINAL_SUMMARY.md) - Resumen ejecutivo
- [CATALOGUE_ARCHITECTURE.md](docs/CATALOGUE_ARCHITECTURE.md) - Arquitectura
- [IMPORTER_UPDATED.md](docs/IMPORTER_UPDATED.md) - Importador

---

## 📝 **Licencia**

[Especificar licencia]

---

## 👥 **Contribuidores**

[Lista de contribuidores]

---

**Última actualización**: 2026-01-20  
**Versión**: 2.0.0 (Sistema Multi-Catálogo)
