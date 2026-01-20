# 📥 Guía de Importación de Productos - Modo Híbrido

> **Guía completa para importar productos desde Excel del cliente**  
> **Fecha**: 2026-01-19

---

## 🎯 Modos de Importación Disponibles

### **1. Soft Delete (Sincronización)** ⭐ **RECOMENDADO**

```bash
python scripts/transform_client_excel.py excel_cliente.xlsx mi-organizacion --mode soft_delete
```

**Comportamiento**:
- ✅ Actualiza productos existentes
- ✅ Crea productos nuevos
- ✅ **Oculta** productos no en el Excel (`is_removed=True`)
- ✅ Recuperable (no elimina físicamente)

**Resultado**:
```
Planilla:
- SKU-001: iPhone 15, $1.100.000
- SKU-002: Samsung S24, $900.000
- SKU-004: Google Pixel, $800.000

Base de Datos:
- SKU-001: ACTUALIZADO
- SKU-002: ACTUALIZADO
- SKU-003: OCULTO (is_removed=True) ← No está en el Excel
- SKU-004: CREADO
```

**Cuándo usar**: 
- ✅ Actualizaciones regulares del catálogo
- ✅ Cliente envía catálogo completo
- ✅ Quieres mantener historial

---

### **2. Update (Actualizar y Crear)**

```bash
python scripts/transform_client_excel.py excel_cliente.xlsx mi-organizacion --mode update
```

**Comportamiento**:
- ✅ Actualiza productos existentes
- ✅ Crea productos nuevos
- ⚠️ **NO toca** productos no en el Excel

**Resultado**:
```
Planilla:
- SKU-001: iPhone 15, $1.100.000
- SKU-004: Google Pixel, $800.000

Base de Datos:
- SKU-001: ACTUALIZADO
- SKU-002: SIN CAMBIOS ← No está en el Excel
- SKU-003: SIN CAMBIOS ← No está en el Excel
- SKU-004: CREADO
```

**Cuándo usar**:
- ✅ Actualizaciones parciales
- ✅ Cliente solo envía productos modificados
- ✅ No quieres afectar productos existentes

---

### **3. Create Only (Solo Crear)**

```bash
python scripts/transform_client_excel.py excel_cliente.xlsx mi-organizacion --mode create_only
```

**Comportamiento**:
- ❌ NO actualiza productos existentes
- ✅ Solo crea productos nuevos
- ⚠️ Omite productos que ya existen

**Resultado**:
```
Planilla:
- SKU-001: iPhone 15, $1.100.000 (existe)
- SKU-004: Google Pixel, $800.000 (nuevo)

Base de Datos:
- SKU-001: OMITIDO (ya existe)
- SKU-002: SIN CAMBIOS
- SKU-003: SIN CAMBIOS
- SKU-004: CREADO
```

**Cuándo usar**:
- ✅ Solo agregar productos nuevos
- ✅ No quieres modificar existentes
- ✅ Importación inicial

---

### **4. Replace All (Reemplazar Todo)** ⚠️ **PELIGROSO**

```bash
python scripts/transform_client_excel.py excel_cliente.xlsx mi-organizacion --mode replace_all
```

**Comportamiento**:
- 🗑️ **ELIMINA TODOS** los productos existentes
- ✅ Crea todos desde cero
- ❌ **NO recuperable**

**Resultado**:
```
Planilla:
- SKU-001: iPhone 15, $1.100.000
- SKU-004: Google Pixel, $800.000

Base de Datos:
- SKU-001: CREADO (desde cero)
- SKU-002: ELIMINADO ← Borrado físicamente
- SKU-003: ELIMINADO ← Borrado físicamente
- SKU-004: CREADO
```

**Cuándo usar**:
- ⚠️ Solo si estás 100% seguro
- ⚠️ Catálogo completamente nuevo
- ⚠️ Requiere confirmación: escribir "ELIMINAR TODO"

---

## 📋 Uso del Script

### **Sintaxis Básica**

```bash
python scripts/transform_client_excel.py <archivo_excel> <organizacion> [opciones]
```

### **Argumentos**

| Argumento | Descripción | Requerido |
|-----------|-------------|-----------|
| `archivo_excel` | Ruta al Excel del cliente | ✅ Sí |
| `organizacion` | Slug de la organización | ✅ Sí |
| `--mode` | Modo de importación | ❌ No (default: soft_delete) |
| `--no-images` | No descargar imágenes | ❌ No |

### **Ejemplos**

```bash
# 1. Importación con sincronización (recomendado)
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc

# 2. Importación con modo específico
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc --mode update

# 3. Importación sin descargar imágenes
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc --no-images

# 4. Solo crear nuevos productos
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc --mode create_only

# 5. Reemplazar todo (peligroso)
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc --mode replace_all
```

---

## 🔄 Flujo de Trabajo Recomendado

### **Paso 1: Analizar el Excel**

```bash
python scripts/analyze_client_excel.py excel_cliente.xlsx
```

**Verifica**:
- ✅ Columnas correctas
- ✅ Datos válidos
- ✅ Sin duplicados
- ✅ Precios consistentes

---

### **Paso 2: Crear Organización (si no existe)**

```bash
# Entrar al shell de Django
docker compose exec web python manage.py shell

# Crear organización
from api.models import Organization
org = Organization.objects.create(
    name="Tienda ABC",
    slug="tienda-abc",
    description="Tienda de productos varios"
)
print(f"Organización creada: {org.slug}")
```

---

### **Paso 3: Importar con Modo Apropiado**

```bash
# Primera importación: soft_delete (recomendado)
python scripts/transform_client_excel.py excel_cliente.xlsx tienda-abc --mode soft_delete
```

---

### **Paso 4: Verificar en el Admin**

```
1. Ir a: http://localhost:8050/admin/api/product/
2. Filtrar por organización
3. Verificar productos creados/actualizados
4. Verificar productos ocultos (is_removed=True)
```

---

## 📊 Salida del Script

### **Ejemplo de Ejecución Exitosa**

```
================================================================================
🚀 TRANSFORMACIÓN E IMPORTACIÓN DE PRODUCTOS
================================================================================
Archivo: excel_cliente.xlsx
Organización: tienda-abc
Modo: soft_delete
Descargar imágenes: True
================================================================================

✅ Organización encontrada: Tienda ABC
✅ Excel leído: 25 filas
✅ Columnas validadas

📋 Modo de importación: soft_delete
--------------------------------------------------------------------------------
👻 25 productos marcados como eliminados
   (Se reactivarán los que estén en el Excel)

📦 Procesando productos...
--------------------------------------------------------------------------------
✅ CREADO: SKU-12345048 - Pisco Sour
   📷 Imagen descargada: IMG-12345048.jpg
✅ CREADO: SKU-27443331 - Amaretto Disaronno
   📷 Imagen descargada: IMG-27443331.jpg
🔄 ACTUALIZADO: SKU-86471103 - Ramazotti Violetto
   📷 Imagen actualizada: IMG-86471103.jpg
...

👻 PRODUCTOS NO EN EL EXCEL (Ocultos):
--------------------------------------------------------------------------------
   - SKU-999999: Producto Antiguo

================================================================================
✅ IMPORTACIÓN COMPLETADA
================================================================================
Total procesado: 25
Creados: 20
Actualizados: 3
Reactivados: 2
Ocultos (no en Excel): 1
Errores: 0
================================================================================
```

---

## ⚠️ Manejo de Errores

### **Error: Organización no encontrada**

```
❌ Error: Organización 'tienda-xyz' no encontrada

Organizaciones disponibles:
   - tienda-abc: Tienda ABC
   - tienda-def: Tienda DEF
```

**Solución**: Usar el slug correcto o crear la organización.

---

### **Error: Columnas faltantes**

```
❌ Error: Columnas faltantes: ['NOMBRE', 'PRECIO']
Columnas disponibles: ['ID', 'PRODUCTO', 'VALOR', ...]
```

**Solución**: Verificar que el Excel tenga las columnas correctas.

---

### **Error al descargar imagen**

```
✅ CREADO: SKU-12345 - Producto X
   ⚠️  Error descargando imagen: HTTP 404
```

**Solución**: La imagen no existe en la URL. El producto se crea sin imagen.

---

## 🔍 Verificar Productos Ocultos

### **En el Admin de Django**

```
1. Ir a: http://localhost:8050/admin/api/product/
2. Agregar filtro: "is removed" = "Yes"
3. Ver productos ocultos
```

### **En el Shell de Django**

```python
from api.models import Product, Organization

# Obtener organización
org = Organization.objects.get(slug='tienda-abc')

# Ver productos ocultos
ocultos = Product.objects.filter(organization=org, is_removed=True)
print(f"Productos ocultos: {ocultos.count()}")

for p in ocultos:
    print(f"- {p.sku}: {p.name}")

# Reactivar un producto
producto = Product.objects.get(sku='SKU-999999')
producto.is_removed = False
producto.save()
print(f"Producto reactivado: {producto.name}")
```

---

## 📝 Formato del Excel

### **Columnas Requeridas**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `ID_SKU` | Número | Identificador único |
| `NOMBRE` | Texto | Nombre del producto |
| `PRECIO` | Número | Precio principal |

### **Columnas Opcionales**

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `CATEGORIA` | Texto | Categoría del producto |
| `ETIQUETA` | Texto | Marca o categoría secundaria |
| `IMAGEN` | URL | URL de la imagen |
| `DESCRIPCION` | Texto | Descripción del producto |
| `PRECIO_OFERTA` | Número | Precio de oferta |
| `DESCUENTO_EN_%` | Texto | Porcentaje de descuento (ej: "40%") |

---

## 🎯 Mejores Prácticas

### **1. Siempre analizar primero**

```bash
# SIEMPRE ejecutar esto primero
python scripts/analyze_client_excel.py excel_cliente.xlsx
```

### **2. Usar soft_delete por defecto**

```bash
# Modo más seguro y flexible
python scripts/transform_client_excel.py excel_cliente.xlsx org --mode soft_delete
```

### **3. Hacer backup antes de replace_all**

```bash
# Backup de la base de datos
docker compose exec db pg_dump -U postgres ms_catalogue_db > backup_$(date +%Y%m%d).sql

# Luego sí, replace_all
python scripts/transform_client_excel.py excel_cliente.xlsx org --mode replace_all
```

### **4. Verificar después de importar**

```bash
# Entrar al admin y verificar
# http://localhost:8050/admin/api/product/
```

---

## 🔧 Troubleshooting

### **Problema: Script no encuentra Django**

```bash
# Asegurarse de estar en el entorno correcto
docker compose exec web python scripts/transform_client_excel.py ...
```

### **Problema: Imágenes no se descargan**

```bash
# Verificar conectividad
curl -I https://url-de-la-imagen.com/imagen.jpg

# Importar sin imágenes
python scripts/transform_client_excel.py excel.xlsx org --no-images
```

### **Problema: Errores de memoria con muchos productos**

```bash
# Procesar en lotes (dividir el Excel)
# O aumentar memoria de Docker
```

---

## 📚 Referencias

- **Análisis de Excel**: `scripts/analyze_client_excel.py`
- **Transformación**: `scripts/transform_client_excel.py`
- **Mapeo de campos**: `FIELD_MAPPING.md`
- **Modelo Product**: `api/models.py` líneas 252-340

---

**Fin de la guía**  
**Próximo paso**: Ejecutar el análisis y luego la importación
