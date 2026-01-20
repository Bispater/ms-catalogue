# 📥 Guía de Importación por Admin

> **Cómo importar productos desde Excel usando el Admin de Django**  
> **Fecha**: 2026-01-20

---

## 🎯 **Pasos para Importar Productos**

### **1. Acceder al Admin**

```
http://localhost:8050/admin/
# o en producción:
https://catalogue.favric.cl/admin/
```

Iniciar sesión con tu usuario administrador.

---

### **2. Ir a Import Files**

```
Admin → API → Import files
```

---

### **3. Crear Nuevo Import File**

Click en **"Add Import File"** (Agregar Import File)

#### **Campos a Completar**:

| Campo | Descripción | Ejemplo |
|-------|-------------|---------|
| **Catalogue** | Catálogo destino | Catálogo Principal |
| **File** | Archivo Excel | productos.xlsx |
| **Import mode** | Modo de importación | soft_delete |
| **Description** | Descripción opcional | Importación enero 2026 |

#### **Modos de Importación**:

- **soft_delete** ⭐ (Recomendado)
  - Sincroniza productos
  - Oculta los que no están en el Excel
  - No elimina datos

- **update**
  - Actualiza existentes
  - Crea nuevos
  - No afecta productos no incluidos

- **create_only**
  - Solo crea nuevos
  - No actualiza existentes

- **replace_all** ⚠️ (Peligroso)
  - Elimina todos los productos del catálogo
  - Crea desde cero

---

### **4. Guardar**

Click en **"Save"** (Guardar)

El archivo se guardará pero **NO se procesará automáticamente**.

---

### **5. Procesar la Importación**

#### **Opción A: Desde la Lista**

1. Ir a **Admin → API → Import files**
2. Seleccionar el/los archivo(s) a procesar (checkbox)
3. En el menú desplegable "Action", seleccionar **"🚀 Procesar importación de productos"**
4. Click en **"Go"**

#### **Opción B: Desde el Detalle**

1. Abrir el Import File
2. En la parte superior, seleccionar la acción **"🚀 Procesar importación de productos"**
3. Click en **"Go"**

---

### **6. Ver Resultados**

Después de procesar, verás mensajes como:

```
✅ ImportFile 1 procesado: 25 creados, 10 actualizados, 0 errores
✅ 1 archivo(s) procesado(s) exitosamente
```

O si hay errores:

```
❌ Error en ImportFile 1: Faltan columnas: ['PRECIO']
⚠️ 1 archivo(s) con errores
```

---

## 📊 **Formato del Excel**

### **Columnas Requeridas** (Mínimo):

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `ID_SKU` | Texto/Número | ID único del producto | 12345 |
| `NOMBRE` | Texto | Nombre del producto | Polera Negra |
| `PRECIO` | Número | Precio normal | 10000 |

### **Columnas Opcionales**:

| Columna | Tipo | Descripción | Ejemplo |
|---------|------|-------------|---------|
| `PRECIO_OFERTA` | Número | Precio en oferta | 8000 |
| `DESCUENTO_EN_%` | Número | Descuento porcentual | 20 |
| `DESCRIPCION` | Texto | Descripción del producto | Polera 100% algodón |
| `CATEGORIA` | Texto | Categoría | Ropa |
| `MARCA` | Texto | Marca | Nike |
| `IMAGEN_1` | URL | URL de imagen | https://... |

### **Ejemplo de Excel**:

| ID_SKU | NOMBRE | PRECIO | PRECIO_OFERTA | DESCRIPCION |
|--------|--------|--------|---------------|-------------|
| 001 | Polera Negra | 10000 | 8000 | Polera 100% algodón |
| 002 | Pantalón Azul | 25000 | | Pantalón de mezclilla |
| 003 | Zapatillas Rojas | 35000 | 28000 | Zapatillas deportivas |

---

## ✅ **Verificar Importación**

### **1. Ver Productos Importados**

```
Admin → API → Products
```

Filtrar por:
- **Catalogue**: Tu catálogo
- **State**: publish

### **2. Ver en la API**

```bash
# Por catálogo
curl "http://localhost:8050/api/products/?catalogue_code=TU_CODIGO"

# Por organización
curl "http://localhost:8050/api/products/?org_slug=tu-org"
```

---

## 🔍 **Columna "Estado"**

En la lista de Import Files verás:

| Estado | Significado |
|--------|-------------|
| ⏳ Pendiente | Archivo subido, no procesado |
| ✅ Procesado | Importación completada |

---

## ⚠️ **Errores Comunes**

### **Error: "No tiene catálogo asignado"**

**Solución**: Editar el Import File y seleccionar un catálogo.

### **Error: "Faltan columnas: ['PRECIO']"**

**Solución**: Tu Excel no tiene las columnas requeridas. Agregar:
- ID_SKU
- NOMBRE
- PRECIO

### **Error: "could not convert string to float"**

**Solución**: Verificar que los precios sean números, no texto.

### **Error: "File does not exist"**

**Solución**: Volver a subir el archivo Excel.

---

## 🎯 **Ejemplo Completo**

### **Paso a Paso**:

1. **Preparar Excel**
   ```
   ID_SKU | NOMBRE        | PRECIO
   001    | Producto 1    | 10000
   002    | Producto 2    | 20000
   003    | Producto 3    | 30000
   ```

2. **Crear Catálogo** (si no existe)
   ```
   Admin → API → Catalogues → Add
   Name: Mi Catálogo
   Code: MICAT001
   Organization: Mi Organización
   ```

3. **Subir Import File**
   ```
   Admin → API → Import files → Add
   Catalogue: Mi Catálogo
   File: [Seleccionar productos.xlsx]
   Import mode: soft_delete
   Description: Importación de prueba
   Save
   ```

4. **Procesar**
   ```
   Seleccionar el archivo
   Action: 🚀 Procesar importación de productos
   Go
   ```

5. **Verificar**
   ```
   Admin → API → Products
   Filtrar por Catalogue: Mi Catálogo
   ```

---

## 📋 **Modos de Importación Detallados**

### **soft_delete** (Sincronización) ⭐

```
Antes:  A, B, C, D
Excel:  B, C, E
Después: B, C, E (A y D ocultos, no eliminados)
```

**Uso**: Actualización regular del catálogo

### **update** (Actualización)

```
Antes:  A, B, C
Excel:  B, C, D
Después: A, B (actualizado), C (actualizado), D (nuevo)
```

**Uso**: Agregar productos sin afectar existentes

### **create_only** (Solo Nuevos)

```
Antes:  A, B
Excel:  B, C
Después: A, B (sin cambios), C (nuevo)
```

**Uso**: Solo agregar productos nuevos

### **replace_all** (Reemplazo Total) ⚠️

```
Antes:  A, B, C
Excel:  D, E
Después: D, E (A, B, C eliminados permanentemente)
```

**Uso**: Reiniciar catálogo desde cero

---

## 🚀 **Tips y Mejores Prácticas**

### **1. Siempre Usar soft_delete**
Es el modo más seguro. No elimina datos permanentemente.

### **2. Probar con Pocos Productos Primero**
Crear un Excel con 5-10 productos para probar.

### **3. Verificar Columnas**
Asegurarse que el Excel tenga al menos: ID_SKU, NOMBRE, PRECIO

### **4. Usar Descripciones**
Agregar descripción al Import File para saber qué contiene.

### **5. Revisar Resultados**
Siempre verificar los mensajes de éxito/error.

---

## 📞 **Soporte**

### **Documentación Relacionada**:
- [FIELD_MAPPING.md](FIELD_MAPPING.md) - Mapeo de columnas
- [IMPORT_GUIDE.md](IMPORT_GUIDE.md) - Guía completa de importación
- [IMPORTER_UPDATED.md](IMPORTER_UPDATED.md) - Importador por línea de comandos

### **Problemas Comunes**:
Ver sección "Errores Comunes" arriba.

---

**Última actualización**: 2026-01-20  
**Versión**: 1.0

---

**Fin del documento**
