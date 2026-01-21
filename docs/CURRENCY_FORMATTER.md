# 💰 Currency Formatter

Sistema robusto de formateo de monedas para diferentes países y regiones.

---

## 📋 Características

✅ Soporte para 8 monedas principales  
✅ Formato automático según país  
✅ Configuración de decimales por moneda  
✅ Separadores personalizados (miles y decimales)  
✅ Símbolos de moneda opcionales  
✅ Fácil de extender con nuevas monedas  

---

## 🌍 Monedas Soportadas

| Código | Moneda | País | Decimales | Separador Miles | Separador Decimal | Ejemplo |
|--------|--------|------|-----------|-----------------|-------------------|---------|
| CLP | Peso Chileno | Chile | 0 | `.` | `,` | 1.200.000 |
| USD | Dólar | Estados Unidos | 2 | `,` | `.` | 1,200.00 |
| EUR | Euro | Unión Europea | 2 | `.` | `,` | 1.200,00 |
| ARS | Peso Argentino | Argentina | 2 | `.` | `,` | 1.200,50 |
| BRL | Real | Brasil | 2 | `.` | `,` | 1.200,50 |
| MXN | Peso Mexicano | México | 2 | `,` | `.` | 1,200.50 |
| COP | Peso Colombiano | Colombia | 0 | `.` | `,` | 1.200.000 |
| PEN | Sol | Perú | 2 | `,` | `.` | 1,200.50 |

---

## 🚀 Uso

### **Básico**

```python
from api.utils import CurrencyFormatter

# Formatear precio en CLP (sin decimales)
formatted = CurrencyFormatter.format(1200000, 'CLP')
# Resultado: "1.200.000"

# Formatear precio en USD (con decimales)
formatted = CurrencyFormatter.format(1200.50, 'USD')
# Resultado: "1,200.50"

# Formatear con símbolo
formatted = CurrencyFormatter.format(1200000, 'CLP', include_symbol=True)
# Resultado: "$ 1.200.000"
```

---

### **En Serializers (Automático)**

El `ProductSerializer` aplica el formato automáticamente según la moneda del catálogo:

```python
# Respuesta de API
{
  "id": 1,
  "name": "Producto Ejemplo",
  "sku": "PROD001",
  "price_1": "1200000.00",           # Valor original (BD)
  "price_1_formatted": "1.200.000",  # Formato CLP
  "price_2": "990000.00",            # Valor original (BD)
  "price_2_formatted": "990.000",    # Formato CLP
  "currency": "CLP",
  "currency_info": {
    "code": "CLP",
    "symbol": "$",
    "decimals": 0,
    "decimal_separator": ",",
    "thousands_separator": ".",
    "symbol_position": "prefix"
  }
}
```

---

### **Obtener Información de Moneda**

```python
# Obtener configuración de una moneda
info = CurrencyFormatter.get_currency_info('CLP')
# Resultado:
# {
#   'code': 'CLP',
#   'symbol': '$',
#   'decimals': 0,
#   'decimal_separator': ',',
#   'thousands_separator': '.',
#   'symbol_position': 'prefix'
# }

# Listar monedas disponibles
currencies = CurrencyFormatter.get_available_currencies()
# Resultado: ['CLP', 'USD', 'EUR', 'ARS', 'BRL', 'MXN', 'COP', 'PEN']
```

---

## 🔧 Agregar Nueva Moneda

Para agregar una nueva moneda, edita `api/utils/currency_formatter.py`:

```python
class CurrencyFormatter:
    CURRENCIES: Dict[str, CurrencyConfig] = {
        # ... monedas existentes ...
        
        'UYU': CurrencyConfig(
            code='UYU',
            symbol='$U',
            decimals=2,
            decimal_separator=',',
            thousands_separator='.',
            symbol_position='prefix',
            space_between=True
        ),
    }
```

---

## 📊 Ejemplos por Moneda

### **CLP (Chile)**
```python
CurrencyFormatter.format(1000, 'CLP')        # "1.000"
CurrencyFormatter.format(1200000, 'CLP')     # "1.200.000"
CurrencyFormatter.format(10990000, 'CLP')    # "10.990.000"
CurrencyFormatter.format(999, 'CLP')         # "999"
```

### **USD (Estados Unidos)**
```python
CurrencyFormatter.format(1000, 'USD')        # "1,000.00"
CurrencyFormatter.format(1200000, 'USD')     # "1,200,000.00"
CurrencyFormatter.format(999.99, 'USD')      # "999.99"
```

### **EUR (Europa)**
```python
CurrencyFormatter.format(1000, 'EUR')        # "1.000,00"
CurrencyFormatter.format(1200000, 'EUR')     # "1.200.000,00"
CurrencyFormatter.format(999.99, 'EUR')      # "999,99"
```

---

## 🎯 Ventajas

### **1. Centralizado**
- Una sola clase gestiona todos los formatos
- Fácil de mantener y actualizar

### **2. Robusto**
- Maneja diferentes tipos de entrada (int, float, Decimal)
- Retorna None si el valor es None
- Formato por defecto si la moneda no existe

### **3. Flexible**
- Fácil agregar nuevas monedas
- Configurable por país
- Opción de incluir símbolo

### **4. Retrocompatible**
- Los valores originales en BD no cambian
- Campos formateados son adicionales
- APIs existentes siguen funcionando

---

## 📝 Configuración en Modelos

### **Catalogue**
```python
class Catalogue(models.Model):
    # ... otros campos ...
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY,
        default='CLP',
        verbose_name=_('currency')
    )
```

### **ImportFile**
```python
class ImportFile(models.Model):
    # ... otros campos ...
    currency = models.CharField(
        max_length=10,
        choices=CURRENCY,
        default='CLP',
        verbose_name=_('currency')
    )
```

---

## 🧪 Testing

```python
# Test básico
from api.utils import CurrencyFormatter

# Test CLP
assert CurrencyFormatter.format(1000, 'CLP') == "1.000"
assert CurrencyFormatter.format(1200000, 'CLP') == "1.200.000"

# Test USD
assert CurrencyFormatter.format(1000, 'USD') == "1,000.00"
assert CurrencyFormatter.format(1200.50, 'USD') == "1,200.50"

# Test con símbolo
assert CurrencyFormatter.format(1000, 'CLP', include_symbol=True) == "$ 1.000"
assert CurrencyFormatter.format(1000, 'EUR', include_symbol=True) == "1.000,00 €"

# Test None
assert CurrencyFormatter.format(None, 'CLP') is None
```

---

## 📚 Referencias

- **Archivo principal**: `api/utils/currency_formatter.py`
- **Uso en serializers**: `api/serializers.py` (ProductSerializer)
- **Modelos**: `api/models.py` (Catalogue, ImportFile)

---

**Última actualización**: 2026-01-21  
**Versión**: 1.0.0
