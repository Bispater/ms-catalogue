# 🗺️ Mapeo de Campos - Excel Cliente → Modelo Product

> **Referencia completa de campos del modelo Product y mapeo desde Excel del cliente**  
> **Fecha**: 2026-01-19

---

## 📊 Campos del Modelo Product

### **Campos Propios**

```python
class Product(BaseModel, TimeStampedModel, SoftDeletableModel, 
              Dimensions, OrganizationRelatedModel):
    
    # Identificación
    sku = CharField(max_length=250, unique=True, blank=True, null=True)
    
    # Descripciones
    short_description = TextField(blank=True, null=True)
    
    # Precios
    price_1 = DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    price_2 = DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    currency = CharField(max_length=10, choices=CURRENCY, blank=True, null=True)
    
    # Stock
    manage_stock = BooleanField(default=False)
    stock_quantity = IntegerField(default=0, blank=True, null=True)
    stock_status = CharField(max_length=20, choices=STOCK_STATUS, default='instock')
    
    # Dimensiones
    weight = DecimalField(max_digits=12, decimal_places=1, blank=True, null=True)
    # length, width, height heredados de Dimensions
    
    # Relaciones
    parent = ForeignKey('self', related_name='variations', blank=True, null=True)
    brand = ForeignKey(Brand, related_name='products', blank=True, null=True)
    categories = ManyToManyField(Category, related_name='products', blank=True)
    
    # Otros
    virtual = BooleanField(default=False)
```

### **Campos Heredados de BaseModel**

```python
name = CharField(max_length=250)
slug = SlugField()
description = TextField(blank=True, null=True)
image = ImageField(blank=True, null=True)
images = ManyToManyField(Images, blank=True)
icon = CharField(max_length=100, blank=True, null=True)
style = CharField(max_length=255, blank=True, null=True)
state = CharField(max_length=20, choices=OBJECT_STATUS, default='publish')
```

### **Campos Heredados de Dimensions**

```python
length = DecimalField(max_digits=12, decimal_places=1, blank=True, null=True)
width = DecimalField(max_digits=12, decimal_places=1, blank=True, null=True)
height = DecimalField(max_digits=12, decimal_places=1, blank=True, null=True)
```

### **Campos Heredados de OrganizationRelatedModel**

```python
organization = ForeignKey(Organization, on_delete=CASCADE)
```

### **Campos Heredados de TimeStampedModel**

```python
created = DateTimeField(auto_now_add=True)
modified = DateTimeField(auto_now=True)
```

### **Campos Heredados de SoftDeletableModel**

```python
is_removed = BooleanField(default=False)
```

---

## 🎯 Mapeo: Excel Cliente → Modelo Product

### **Mapeo Directo**

| Excel Cliente | Modelo Product | Tipo | Notas |
|---------------|----------------|------|-------|
| `ID_SKU` | `sku` | CharField | Agregar prefijo "SKU-" |
| `NOMBRE` | `name` | CharField | Directo |
| `PRECIO` | `price_1` | DecimalField | Precio principal |
| `PRECIO_OFERTA` | `price_2` | DecimalField | Precio de oferta |
| `DESCRIPCION` | `description` | TextField | Convertir a HTML |
| - | `short_description` | TextField | Primeros 150 chars de DESCRIPCION |
| - | `currency` | CharField | Valor fijo: "CLP" |
| - | `stock_status` | CharField | Valor fijo: "instock" |
| - | `stock_quantity` | IntegerField | Valor fijo: 100 |
| - | `manage_stock` | BooleanField | Valor fijo: False |
| - | `state` | CharField | Valor fijo: "publish" |
| - | `virtual` | BooleanField | Valor fijo: False |

### **Mapeo con Transformación**

| Excel Cliente | Modelo Product | Transformación |
|---------------|----------------|----------------|
| `DESCUENTO_EN_%` | `price_2` | Si no existe PRECIO_OFERTA: `price_1 * (1 - descuento/100)` |
| `IMAGEN` | `images` | Descargar imagen, crear objeto Images, asociar |
| `CATEGORIA` | `categories` | Crear/obtener Category, asociar ManyToMany |
| `ETIQUETA` | `brand` o `categories` | Clasificar si es marca o categoría |

### **Campos sin Mapeo (valores por defecto)**

| Modelo Product | Valor por Defecto |
|----------------|-------------------|
| `weight` | `None` |
| `length` | `None` |
| `width` | `None` |
| `height` | `None` |
| `parent` | `None` |
| `icon` | `None` |
| `style` | `None` |
| `image` | `None` (usar images ManyToMany) |

---

## 📝 Constantes

### **CURRENCY**

```python
CURRENCY = (
    ('CLP', 'Peso Chileno'),
    ('PEN', 'Sol Peruano'),
)
```

### **STOCK_STATUS**

```python
STOCK_STATUS = (
    ('instock', 'En Stock'),
    ('outofstock', 'Agotado'),
    ('onbackorder', 'En Pedido'),
)
```

### **OBJECT_STATUS**

```python
OBJECT_STATUS = (
    ('publish', 'Publicado'),
    ('pending', 'Pendiente'),
    ('private', 'Privado'),
    ('draft', 'Borrador'),
)
```

---

## 🔄 Lógica de Transformación

### **1. SKU**

```python
# Excel: ID_SKU = 12345048
# Modelo: sku = "SKU-12345048"

sku = f"SKU-{row['ID_SKU']}"
```

### **2. Precios**

```python
# Opción A: Si existe PRECIO_OFERTA
price_1 = float(row['PRECIO'])
price_2 = float(row['PRECIO_OFERTA']) if pd.notna(row['PRECIO_OFERTA']) else None

# Opción B: Si existe DESCUENTO_EN_% pero no PRECIO_OFERTA
if pd.notna(row['DESCUENTO_EN_%']) and pd.isna(row['PRECIO_OFERTA']):
    descuento = float(row['DESCUENTO_EN_%'].strip('%')) / 100
    price_2 = price_1 * (1 - descuento)
```

### **3. Descripción**

```python
# Short description: primeros 150 caracteres
short_description = row['DESCRIPCION'][:150] + "..." if len(row['DESCRIPCION']) > 150 else row['DESCRIPCION']

# Full description: convertir a HTML
description = f"<p>{row['DESCRIPCION']}</p>"
```

### **4. Categorías**

```python
# Crear/obtener categoría
categoria_name = row['CATEGORIA']
categoria, created = Category.objects.get_or_create(
    name=categoria_name,
    organization=organization,
    defaults={'state': 'publish'}
)

# Asociar al producto
product.categories.add(categoria)
```

### **5. Marca vs Categoría (ETIQUETA)**

```python
# Clasificar ETIQUETA
marcas_conocidas = [
    'Cocinerista',
    'Destilería',
    'Cervecería',
    'Avellanera',
    'Cosmética',
    'Energizante'
]

etiqueta = row['ETIQUETA']

if etiqueta in marcas_conocidas:
    # Es una marca
    brand, created = Brand.objects.get_or_create(
        name=etiqueta,
        organization=organization,
        defaults={'state': 'publish'}
    )
    product.brand = brand
else:
    # Es una categoría secundaria
    categoria_secundaria, created = Category.objects.get_or_create(
        name=etiqueta,
        organization=organization,
        defaults={'state': 'publish'}
    )
    product.categories.add(categoria_secundaria)
```

### **6. Imágenes**

```python
import requests
from django.core.files import File

# Descargar imagen
image_url = row['IMAGEN']
image_code = f"IMG-{row['ID_SKU']}"

response = requests.get(image_url, timeout=15)
if response.status_code == 200:
    # Crear objeto Images
    image_obj = Images.objects.create(
        name=f"{product.name} - Principal",
        alt=product.name,
        code=image_code,
        organization=organization
    )
    
    # Guardar archivo
    from io import BytesIO
    image_obj.image.save(
        f"{image_code}.jpg",
        File(BytesIO(response.content)),
        save=True
    )
    
    # Asociar al producto
    product.images.add(image_obj)
```

---

## ✅ Ejemplo Completo

### **Fila del Excel**

```
ID_SKU: 12345048
NOMBRE: Pisco Sour
PRECIO: 8.900
CATEGORIA: Cocinerista
IMAGEN: https://grupocomerlife.com/wp-content/uploads/2021/02/PISCO-SOUR-CHILENO.png
DESCRIPCION: Copa de pisco sour chileno con abundante espuma y aroma...
ETIQUETA: Cocinerista
PRECIO_OFERTA: 5.100
DESCUENTO_EN_%: 40%
```

### **Producto Creado**

```python
Product.objects.create(
    # Campos propios
    sku="SKU-12345048",
    short_description="Copa de pisco sour chileno con abundante espuma y aroma...",
    price_1=Decimal("8900.00"),
    price_2=Decimal("5100.00"),
    currency="CLP",
    manage_stock=False,
    stock_quantity=100,
    stock_status="instock",
    weight=None,
    parent=None,
    brand=brand_cocinerista,  # ForeignKey
    virtual=False,
    
    # Campos heredados de BaseModel
    name="Pisco Sour",
    slug="pisco-sour",  # Auto-generado
    description="<p>Copa de pisco sour chileno con abundante espuma y aroma...</p>",
    image=None,
    icon=None,
    style=None,
    state="publish",
    
    # Campos heredados de Dimensions
    length=None,
    width=None,
    height=None,
    
    # Campos heredados de OrganizationRelatedModel
    organization=organization,
    
    # Campos heredados de TimeStampedModel
    # created, modified (auto)
    
    # Campos heredados de SoftDeletableModel
    is_removed=False
)

# Asociar categorías (ManyToMany)
product.categories.add(categoria_cocinerista)

# Asociar imágenes (ManyToMany)
product.images.add(image_obj)
```

---

## 🎯 Resumen del Mapeo

### **Campos Mapeados: 9/9**

✅ ID_SKU → sku  
✅ NOMBRE → name  
✅ PRECIO → price_1  
✅ PRECIO_OFERTA → price_2  
✅ DESCUENTO_EN_% → (calcular price_2)  
✅ CATEGORIA → categories  
✅ ETIQUETA → brand o categories  
✅ IMAGEN → images  
✅ DESCRIPCION → description + short_description  

### **Campos con Valores por Defecto: 7**

✅ currency = "CLP"  
✅ stock_status = "instock"  
✅ stock_quantity = 100  
✅ manage_stock = False  
✅ state = "publish"  
✅ virtual = False  
✅ organization = (del contexto)  

### **Campos sin Datos: 8**

❌ weight, length, width, height (dimensiones)  
❌ parent (variaciones)  
❌ icon, style (estilo)  
❌ image (imagen principal, usar images ManyToMany)  

---

## 📚 Referencias

- Modelo Product: `api/models.py` líneas 252-340
- Modelo BaseModel: `api/models.py` líneas 78-108
- Modelo Dimensions: `api/models.py` líneas 222-249
- Constantes: `api/models.py` líneas 18-37

---

**Fin del mapeo**  
**Próximo paso**: Ejecutar `analyze_client_excel.py` para validar los datos
