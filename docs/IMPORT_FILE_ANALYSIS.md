# 📥 Análisis de ImportFile - Sistema de Importación Masiva

> **Análisis completo del modelo ImportFile y su funcionalidad**  
> **Estado actual**: ⚠️ **INCOMPLETO** - Solo marca como subido, no procesa datos  
> **Fecha**: 2026-01-19

---

## 📋 Tabla de Contenidos

1. [Estado Actual](#estado-actual)
2. [Modelo ImportFile](#modelo-importfile)
3. [Signal handle_import_file](#signal-handle_import_file)
4. [Flujo Actual](#flujo-actual)
5. [Problemas Identificados](#problemas-identificados)
6. [Implementación Propuesta](#implementación-propuesta)
7. [Formato de Archivo CSV](#formato-de-archivo-csv)
8. [Código de Implementación](#código-de-implementación)

---

## ⚠️ Estado Actual

### Funcionalidad Implementada

```python
✅ Modelo ImportFile definido
✅ Signal post_save configurado
✅ Admin de Django configurado
✅ Validación de extensión .zip para imágenes
❌ NO procesa archivos CSV
❌ NO extrae imágenes del ZIP
❌ NO crea productos
❌ NO hay tarea Celery
```

### Código Actual

```python
@receiver(post_save, sender=ImportFile)
@prevent_recursion
def handle_import_file(sender, instance=None, created=False, **kwargs):
    """
    Maneja la importación de archivos
    """
    if created and not instance.uploaded:
        # Aquí iría la lógica para procesar el archivo de importación
        # Por ahora, solo marcamos como subido
        instance.uploaded = True
        instance.save(update_fields=['uploaded'])
        # En producción, aquí podrías llamar a una tarea Celery
        # from .tasks import process_import_file
        # process_import_file.delay(instance.id)
```

**Análisis**: 
- ✅ Detecta cuando se crea un nuevo ImportFile
- ✅ Marca como `uploaded=True`
- ❌ **NO hace nada más**
- ❌ El comentario indica que falta implementación

---

## 📊 Modelo ImportFile

### Definición Completa

```python
class ImportFile(TimeStampedModel, SoftDeletableModel, OrganizationRelatedModel):
    # Archivos
    file = FileField(
        upload_to='imports/',
        verbose_name='file'
    )
    
    images_zip = FileField(
        upload_to='imports/zips/',
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['zip'])],
        verbose_name='images zip'
    )
    
    # Configuración
    currency = CharField(
        max_length=10,
        choices=CURRENCY,  # CLP o PEN
        blank=True,
        null=True,
        verbose_name='currency'
    )
    
    description = TextField(
        blank=True,
        null=True,
        verbose_name='description'
    )
    
    # Estado
    uploaded = BooleanField(
        default=False,
        verbose_name='uploaded'
    )
    
    remove_all = BooleanField(
        default=False,
        verbose_name='remove all'
    )
    
    # Auditoría
    user_created = ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name='imported_files',
        verbose_name='user created'
    )
    
    # Heredados de TimeStampedModel:
    # - created: DateTimeField (auto_now_add=True)
    # - modified: DateTimeField (auto_now=True)
    
    # Heredados de SoftDeletableModel:
    # - is_removed: BooleanField (default=False)
    
    # Heredados de OrganizationRelatedModel:
    # - organization: ForeignKey(Organization)
```

### Campos Explicados

| Campo | Tipo | Propósito | Obligatorio |
|-------|------|-----------|-------------|
| `file` | FileField | Archivo CSV/Excel con productos | ✅ Sí |
| `images_zip` | FileField | ZIP con imágenes de productos | ❌ No |
| `currency` | CharField | Moneda por defecto (CLP/PEN) | ❌ No |
| `description` | TextField | Descripción de la importación | ❌ No |
| `uploaded` | BooleanField | ¿Se procesó el archivo? | Auto |
| `remove_all` | BooleanField | ¿Eliminar productos antes? | ❌ No |
| `user_created` | ForeignKey | Usuario que importó | Auto |
| `organization` | ForeignKey | Organización destino | ✅ Sí |

---

## 🔄 Signal handle_import_file

### Decoradores

```python
@receiver(post_save, sender=ImportFile)
@prevent_recursion
```

**Explicación**:
- `@receiver(post_save, sender=ImportFile)`: Se ejecuta después de guardar un ImportFile
- `@prevent_recursion`: Evita bucles infinitos (si el signal llama a `save()` de nuevo)

### Lógica Actual

```python
def handle_import_file(sender, instance=None, created=False, **kwargs):
    if created and not instance.uploaded:
        # Solo se ejecuta si:
        # 1. Es un registro NUEVO (created=True)
        # 2. NO ha sido procesado (uploaded=False)
        
        instance.uploaded = True
        instance.save(update_fields=['uploaded'])
```

**Problema**: Solo marca como procesado, pero no procesa nada.

---

## 🔄 Flujo Actual

```
Usuario sube archivo en Admin
         ↓
ImportFile.save() se ejecuta
         ↓
Signal post_save se dispara
         ↓
handle_import_file() se ejecuta
         ↓
uploaded = True
         ↓
FIN (no hace nada más)
```

**Resultado**: El archivo queda guardado pero no se procesa.

---

## ❌ Problemas Identificados

### 1. **No hay procesamiento de archivos**
```python
# Actual:
instance.uploaded = True  # Solo marca como procesado

# Debería:
# - Leer CSV
# - Validar datos
# - Crear/actualizar productos
# - Extraer imágenes del ZIP
# - Asociar imágenes a productos
```

### 2. **No hay tarea Celery**
```python
# Comentario en el código:
# from .tasks import process_import_file
# process_import_file.delay(instance.id)

# Problema: El archivo tasks.py NO EXISTE
```

### 3. **No hay validación de formato CSV**
- No se valida que el CSV tenga las columnas correctas
- No se valida que los datos sean válidos
- No se manejan errores

### 4. **No hay feedback al usuario**
- No se reportan errores
- No se muestra progreso
- No se indica cuántos productos se crearon/actualizaron

### 5. **Campo `remove_all` no se usa**
```python
remove_all = BooleanField(default=False)
# Este campo existe pero no se usa en ningún lado
```

### 6. **Procesamiento síncrono**
- Si se implementa en el signal, bloqueará la request
- Para archivos grandes (1000+ productos), puede tardar minutos
- Puede causar timeouts

---

## ✅ Implementación Propuesta

### Arquitectura Recomendada

```
Usuario sube archivo
         ↓
ImportFile.save()
         ↓
Signal post_save
         ↓
Crear tarea Celery (async)
         ↓
Tarea procesa en background
         ↓
Actualizar estado y resultados
```

### Ventajas de Celery

1. ✅ **Asíncrono**: No bloquea la request
2. ✅ **Escalable**: Múltiples workers
3. ✅ **Reintentos**: Si falla, reintenta automáticamente
4. ✅ **Monitoreo**: Flower para ver estado
5. ✅ **Timeout**: Configurable por tarea

---

## 📄 Formato de Archivo CSV

### Columnas Requeridas

```csv
sku,name,short_description,description,regular_price,sale_price,currency,stock_status,stock_quantity,weight,length,width,height,brand_name,category_names,image_codes,meta_title,meta_description,meta_keywords,state
```

### Ejemplo de CSV

```csv
sku,name,short_description,description,regular_price,sale_price,currency,stock_status,stock_quantity,weight,length,width,height,brand_name,category_names,image_codes,meta_title,meta_description,meta_keywords,state
IPH15-256,iPhone 15 Pro 256GB,El iPhone más avanzado,"<p>iPhone 15 Pro con chip A17 Pro</p>",1299000,1199000,CLP,instock,50,0.221,14.67,7.15,0.83,Apple,"Electrónica|Celulares|Smartphones","IPH15-1|IPH15-2|IPH15-3",iPhone 15 Pro - Compra Online,Compra el iPhone 15 Pro con 256GB de almacenamiento,iphone 15 pro apple smartphone,publish
SAM-S24,Samsung Galaxy S24,"Smartphone premium de Samsung","<p>Galaxy S24 con cámara de 50MP</p>",899000,849000,CLP,instock,30,0.168,14.6,7.06,0.76,Samsung,"Electrónica|Celulares|Smartphones","SAM24-1|SAM24-2",Samsung Galaxy S24 - Tienda Online,Compra el Samsung Galaxy S24,samsung galaxy s24 smartphone,publish
```

### Formato de Categorías

```
"Electrónica|Celulares|Smartphones"
```
- Separadas por `|`
- Se crean automáticamente si no existen
- Se respeta la jerarquía

### Formato de Imágenes

```
"IPH15-1|IPH15-2|IPH15-3"
```
- Separadas por `|`
- Deben existir en el ZIP como: `IPH15-1.jpg`, `IPH15-2.jpg`, etc.

### Estructura del ZIP de Imágenes

```
images.zip
├── IPH15-1.jpg
├── IPH15-2.jpg
├── IPH15-3.jpg
├── SAM24-1.jpg
└── SAM24-2.jpg
```

---

## 💻 Código de Implementación

### 1. Crear `api/tasks.py`

```python
from celery import shared_task
from django.core.files import File
from django.db import transaction
import pandas as pd
import zipfile
import os
import logging
from decimal import Decimal

from .models import ImportFile, Product, Brand, Category, Images, Organization

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_import_file(self, import_file_id):
    """
    Procesa un archivo de importación de productos
    
    Args:
        import_file_id: ID del ImportFile a procesar
    
    Returns:
        dict: Resultado del procesamiento
    """
    try:
        import_file = ImportFile.objects.get(id=import_file_id)
        organization = import_file.organization
        
        logger.info(f"Iniciando procesamiento de ImportFile {import_file_id}")
        
        # Estadísticas
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        # 1. Leer CSV
        try:
            df = pd.read_csv(import_file.file.path)
            stats['total'] = len(df)
            logger.info(f"CSV leído: {stats['total']} filas")
        except Exception as e:
            logger.error(f"Error al leer CSV: {str(e)}")
            import_file.description = f"Error al leer CSV: {str(e)}"
            import_file.save()
            return stats
        
        # 2. Extraer imágenes del ZIP (si existe)
        images_dir = None
        if import_file.images_zip:
            try:
                images_dir = f'/tmp/import_{import_file_id}_images/'
                os.makedirs(images_dir, exist_ok=True)
                
                with zipfile.ZipFile(import_file.images_zip.path, 'r') as zip_ref:
                    zip_ref.extractall(images_dir)
                
                logger.info(f"ZIP extraído en {images_dir}")
            except Exception as e:
                logger.error(f"Error al extraer ZIP: {str(e)}")
                stats['error_details'].append(f"Error en ZIP: {str(e)}")
        
        # 3. Eliminar productos existentes si remove_all=True
        if import_file.remove_all:
            deleted_count = Product.objects.filter(
                organization=organization
            ).delete()[0]
            logger.info(f"Eliminados {deleted_count} productos existentes")
        
        # 4. Procesar cada fila
        for index, row in df.iterrows():
            try:
                with transaction.atomic():
                    # Obtener o crear marca
                    brand = None
                    if pd.notna(row.get('brand_name')):
                        brand, _ = Brand.objects.get_or_create(
                            name=row['brand_name'],
                            organization=organization,
                            defaults={'state': 'publish'}
                        )
                    
                    # Procesar categorías jerárquicas
                    categories = []
                    if pd.notna(row.get('category_names')):
                        category_path = row['category_names'].split('|')
                        parent = None
                        
                        for cat_name in category_path:
                            cat_name = cat_name.strip()
                            category, _ = Category.objects.get_or_create(
                                name=cat_name,
                                parent=parent,
                                organization=organization,
                                defaults={'state': 'publish'}
                            )
                            categories.append(category)
                            parent = category
                    
                    # Preparar datos del producto
                    product_data = {
                        'name': row['name'],
                        'short_description': row.get('short_description', ''),
                        'description': row.get('description', ''),
                        'regular_price': Decimal(str(row['regular_price'])),
                        'currency': row.get('currency', import_file.currency or 'CLP'),
                        'stock_status': row.get('stock_status', 'instock'),
                        'stock_quantity': int(row.get('stock_quantity', 0)),
                        'brand': brand,
                        'organization': organization,
                        'state': row.get('state', 'publish'),
                    }
                    
                    # Campos opcionales
                    if pd.notna(row.get('sale_price')):
                        product_data['sale_price'] = Decimal(str(row['sale_price']))
                    
                    if pd.notna(row.get('weight')):
                        product_data['weight'] = Decimal(str(row['weight']))
                    
                    if pd.notna(row.get('length')):
                        product_data['length'] = Decimal(str(row['length']))
                    
                    if pd.notna(row.get('width')):
                        product_data['width'] = Decimal(str(row['width']))
                    
                    if pd.notna(row.get('height')):
                        product_data['height'] = Decimal(str(row['height']))
                    
                    # SEO
                    if pd.notna(row.get('meta_title')):
                        product_data['meta_title'] = row['meta_title']
                    
                    if pd.notna(row.get('meta_description')):
                        product_data['meta_description'] = row['meta_description']
                    
                    if pd.notna(row.get('meta_keywords')):
                        product_data['meta_keywords'] = row['meta_keywords']
                    
                    # Crear o actualizar producto
                    product, created = Product.objects.update_or_create(
                        sku=row['sku'],
                        organization=organization,
                        defaults=product_data
                    )
                    
                    # Asociar categorías
                    if categories:
                        product.categories.set(categories)
                    
                    # Procesar imágenes
                    if images_dir and pd.notna(row.get('image_codes')):
                        image_codes = row['image_codes'].split('|')
                        
                        for code in image_codes:
                            code = code.strip()
                            
                            # Buscar archivo de imagen
                            for ext in ['.jpg', '.jpeg', '.png', '.webp']:
                                image_path = os.path.join(images_dir, f"{code}{ext}")
                                
                                if os.path.exists(image_path):
                                    # Crear objeto Images
                                    image_obj = Images.objects.create(
                                        name=f"{product.name} - {code}",
                                        alt=f"{product.name}",
                                        code=code,
                                        organization=organization
                                    )
                                    
                                    # Guardar archivo
                                    with open(image_path, 'rb') as f:
                                        image_obj.image.save(
                                            f"{code}{ext}",
                                            File(f),
                                            save=True
                                        )
                                    
                                    # Asociar a producto
                                    product.images.add(image_obj)
                                    break
                    
                    # Actualizar estadísticas
                    if created:
                        stats['created'] += 1
                    else:
                        stats['updated'] += 1
                    
                    logger.info(f"Producto {row['sku']}: {'creado' if created else 'actualizado'}")
                    
            except Exception as e:
                stats['errors'] += 1
                error_msg = f"Fila {index + 2}: {str(e)}"
                stats['error_details'].append(error_msg)
                logger.error(error_msg)
        
        # 5. Limpiar archivos temporales
        if images_dir and os.path.exists(images_dir):
            import shutil
            shutil.rmtree(images_dir)
            logger.info(f"Directorio temporal eliminado: {images_dir}")
        
        # 6. Actualizar ImportFile con resultados
        result_description = f"""
Importación completada:
- Total: {stats['total']}
- Creados: {stats['created']}
- Actualizados: {stats['updated']}
- Errores: {stats['errors']}
"""
        
        if stats['error_details']:
            result_description += "\n\nErrores:\n" + "\n".join(stats['error_details'][:10])
            if len(stats['error_details']) > 10:
                result_description += f"\n... y {len(stats['error_details']) - 10} errores más"
        
        import_file.description = result_description
        import_file.uploaded = True
        import_file.save()
        
        logger.info(f"Procesamiento completado: {stats}")
        return stats
        
    except ImportFile.DoesNotExist:
        logger.error(f"ImportFile {import_file_id} no encontrado")
        return {'error': 'ImportFile no encontrado'}
    
    except Exception as e:
        logger.error(f"Error inesperado: {str(e)}")
        
        # Reintentar si es posible
        if self.request.retries < self.max_retries:
            raise self.retry(exc=e, countdown=60)  # Reintentar en 60 segundos
        
        return {'error': str(e)}
```

### 2. Actualizar Signal en `api/models.py`

```python
@receiver(post_save, sender=ImportFile)
@prevent_recursion
def handle_import_file(sender, instance=None, created=False, **kwargs):
    """
    Maneja la importación de archivos
    """
    if created and not instance.uploaded:
        # Llamar a tarea Celery para procesamiento asíncrono
        from .tasks import process_import_file
        process_import_file.delay(instance.id)
```

### 3. Configurar Celery en `core/celery.py`

```python
import os
from celery import Celery

# Configurar Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

app = Celery('catalogue_api')

# Configuración desde Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-descubrir tareas en todas las apps
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
```

### 4. Actualizar `core/__init__.py`

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 5. Agregar a `requirements.txt`

```txt
pandas==2.1.0
openpyxl==3.1.2  # Para leer Excel
```

### 6. Actualizar `docker-compose.yml`

```yaml
services:
  # ... servicios existentes ...
  
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
  
  celery:
    build: .
    command: celery -A core worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    environment:
      - DOCKER_ENV=true
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/0

volumes:
  redis_data:
```

### 7. Actualizar Admin para mostrar resultados

```python
@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_filter = ['uploaded', 'created']
    search_fields = ['description']
    list_display = ['id', 'created', 'modified', 'description_short', 'file', 'uploaded', 'user_created']
    readonly_fields = ('created', 'modified', 'description')
    
    def description_short(self, obj):
        if obj.description:
            return obj.description[:100] + '...' if len(obj.description) > 100 else obj.description
        return '-'
    description_short.short_description = 'Resultado'
```

---

## 🧪 Pruebas

### 1. Crear CSV de prueba

```csv
sku,name,short_description,description,regular_price,sale_price,currency,stock_status,stock_quantity,weight,brand_name,category_names,image_codes,state
TEST-001,Producto de Prueba 1,Descripción corta,<p>Descripción larga</p>,10000,9000,CLP,instock,100,0.5,Marca Test,Categoría Test,TEST-001-1|TEST-001-2,publish
TEST-002,Producto de Prueba 2,Descripción corta 2,<p>Descripción larga 2</p>,20000,,CLP,instock,50,1.0,Marca Test,Categoría Test,TEST-002-1,publish
```

### 2. Crear ZIP con imágenes de prueba

```
test_images.zip
├── TEST-001-1.jpg
├── TEST-001-2.jpg
└── TEST-002-1.jpg
```

### 3. Subir en el Admin

1. Ir a `/admin/api/importfile/add/`
2. Subir CSV y ZIP
3. Seleccionar organización
4. Guardar
5. Ver logs de Celery para seguimiento

---

## 📊 Monitoreo

### Ver logs de Celery

```bash
# En desarrollo
docker compose logs -f celery

# Ver tareas en ejecución
docker compose exec celery celery -A core inspect active

# Ver tareas completadas
docker compose exec celery celery -A core inspect stats
```

### Instalar Flower (opcional)

```bash
# Agregar a requirements.txt
flower==2.0.1

# Agregar servicio en docker-compose.yml
flower:
  build: .
  command: celery -A core flower
  ports:
    - "5555:5555"
  depends_on:
    - redis
    - celery

# Acceder a: http://localhost:5555
```

---

## ✅ Checklist de Implementación

- [ ] Crear `api/tasks.py` con la tarea `process_import_file`
- [ ] Actualizar signal `handle_import_file` en `api/models.py`
- [ ] Crear `core/celery.py`
- [ ] Actualizar `core/__init__.py`
- [ ] Agregar `pandas` y `openpyxl` a `requirements.txt`
- [ ] Actualizar `docker-compose.yml` con Redis y Celery
- [ ] Actualizar `ImportFileAdmin` en `api/admin.py`
- [ ] Reconstruir contenedores: `./reset` (opción 3) y `./start`
- [ ] Probar con CSV y ZIP de prueba
- [ ] Verificar logs de Celery
- [ ] Verificar productos creados en el admin

---

## 🎯 Resumen

### Estado Actual
- ⚠️ **INCOMPLETO**: Solo marca como `uploaded=True`, no procesa nada

### Implementación Propuesta
- ✅ Tarea Celery asíncrona
- ✅ Procesamiento de CSV con pandas
- ✅ Extracción de imágenes del ZIP
- ✅ Creación/actualización de productos
- ✅ Manejo de errores y reintentos
- ✅ Feedback detallado al usuario
- ✅ Estadísticas de importación

### Beneficios
- 🚀 **Asíncrono**: No bloquea la interfaz
- 📊 **Escalable**: Múltiples importaciones simultáneas
- 🔄 **Robusto**: Reintentos automáticos
- 📝 **Trazable**: Logs detallados
- 👤 **User-friendly**: Feedback claro

---

**Fin del análisis**  
**Próximo paso**: Implementar la tarea Celery
