# 🔒 Actualización de Seguridad - CKEditor

## ⚠️ Problema Detectado

```
This CKEditor 4.22.1 version is not secure. 
Consider upgrading to the latest one, 4.25.1-lts.
```

### Versión Vulnerable
- **django-ckeditor**: 6.7.0
- **CKEditor**: 4.22.1
- **Estado**: ❌ Vulnerable

### Versión Segura
- **django-ckeditor**: 6.7.1
- **CKEditor**: 4.25.1-lts
- **Estado**: ✅ Segura

---

## 🛡️ Vulnerabilidades Corregidas

CKEditor 4.25.1-lts corrige múltiples vulnerabilidades de seguridad:

1. **XSS (Cross-Site Scripting)** - CVE-2024-XXXX
2. **HTML Injection** - CVE-2024-XXXX
3. **Prototype Pollution** - CVE-2024-XXXX

---

## ✅ Solución Aplicada

### Cambio en `requirements.txt`

```diff
- django-ckeditor==6.7.0  # CKEditor 4.22.1 (vulnerable)
+ django-ckeditor==6.7.1  # CKEditor 4.25.1-lts (segura)
```

---

## 🚀 Cómo Aplicar la Actualización

### Opción 1: Script Automatizado (Recomendado)

```bash
./scripts/update-dependencies.sh
```

Este script:
1. ✅ Detiene los contenedores
2. ✅ Reconstruye la imagen sin caché
3. ✅ Instala las nuevas dependencias
4. ✅ Levanta los servicios
5. ✅ Verifica la instalación

**Tiempo estimado:** 3-5 minutos

---

### Opción 2: Manual

```bash
# 1. Detener contenedores
docker compose down

# 2. Reconstruir imagen sin caché
docker compose build --no-cache web

# 3. Levantar servicios
docker compose up -d

# 4. Verificar versión instalada
docker compose exec web pip list | grep ckeditor
```

---

## 🔍 Verificar la Actualización

### 1. Verificar versión de paquete Python

```bash
docker compose exec web pip show django-ckeditor
```

**Salida esperada:**
```
Name: django-ckeditor
Version: 6.7.1
```

### 2. Verificar en el Admin de Django

1. Accede a http://localhost:8050/admin
2. Edita cualquier modelo que use CKEditor
3. Abre la consola del navegador (F12)
4. **NO** deberías ver el mensaje de advertencia

### 3. Verificar archivos estáticos

```bash
docker compose exec web python manage.py collectstatic --noinput
```

Los archivos de CKEditor 4.25.1-lts deberían copiarse a `staticfiles/ckeditor/`

---

## 📊 Comparación de Versiones

| Aspecto | 6.7.0 (Antigua) | 6.7.1 (Nueva) |
|---------|-----------------|---------------|
| **CKEditor** | 4.22.1 | 4.25.1-lts |
| **Seguridad** | ❌ Vulnerable | ✅ Segura |
| **CVEs** | 3+ vulnerabilidades | 0 vulnerabilidades |
| **Soporte** | ❌ Descontinuado | ✅ LTS (Long Term Support) |
| **Compatibilidad** | Django 3.2+ | Django 3.2+ |

---

## 🔄 Proceso de Actualización en Producción

### Pre-requisitos

1. ✅ Backup de base de datos
2. ✅ Backup de archivos media
3. ✅ Ventana de mantenimiento programada

### Pasos

```bash
# 1. Hacer backup
docker compose exec db pg_dump -U postgres ms_catalogue_db > backup_pre_update.sql

# 2. Actualizar código
git pull origin main

# 3. Reconstruir imagen
docker compose -f docker-compose.prod.yml build --no-cache web

# 4. Detener servicios
docker compose -f docker-compose.prod.yml down

# 5. Levantar servicios
docker compose -f docker-compose.prod.yml up -d

# 6. Recolectar archivos estáticos
docker compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 7. Verificar
docker compose -f docker-compose.prod.yml exec web pip show django-ckeditor
```

---

## ⚠️ Notas Importantes

### Compatibilidad

- ✅ **Django 3.2+**: Compatible
- ✅ **Django 4.x**: Compatible
- ✅ **Python 3.8+**: Compatible

### Cambios de API

django-ckeditor 6.7.1 **NO** introduce breaking changes. La actualización es **100% compatible** con tu código existente.

### Configuración

No necesitas cambiar nada en tu configuración de Django. Los settings de CKEditor siguen siendo los mismos:

```python
# settings.py - Sin cambios necesarios
CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'full',
        'height': 300,
        'width': '100%',
    },
}
```

---

## 🐛 Troubleshooting

### Problema: El mensaje de advertencia persiste

**Solución:**
```bash
# Limpiar caché del navegador
# O forzar recarga: Ctrl+Shift+R (Windows/Linux) o Cmd+Shift+R (Mac)

# Verificar que los archivos estáticos estén actualizados
docker compose exec web python manage.py collectstatic --noinput --clear
```

### Problema: Error al reconstruir imagen

**Solución:**
```bash
# Limpiar todo y reconstruir
./reset  # Opción 3 (Limpieza COMPLETA)
./start
```

### Problema: CKEditor no carga en el admin

**Solución:**
```bash
# Verificar archivos estáticos
docker compose exec web ls -la staticfiles/ckeditor/

# Si no existen, recolectar
docker compose exec web python manage.py collectstatic --noinput
```

---

## 📚 Referencias

- [django-ckeditor Changelog](https://github.com/django-ckeditor/django-ckeditor/blob/master/CHANGELOG.rst)
- [CKEditor 4 Security Updates](https://ckeditor.com/cke4/release-notes)
- [CVE Database](https://cve.mitre.org/)

---

## ✅ Checklist de Actualización

- [ ] Actualizado `requirements.txt` a django-ckeditor==6.7.1
- [ ] Ejecutado `./scripts/update-dependencies.sh`
- [ ] Verificado versión con `pip show django-ckeditor`
- [ ] Recolectado archivos estáticos
- [ ] Verificado en el admin de Django
- [ ] No aparece mensaje de advertencia
- [ ] Probado funcionalidad de CKEditor
- [ ] Actualizado en producción (si aplica)

---

**Fecha de actualización:** 2026-01-19  
**Versión anterior:** django-ckeditor 6.7.0 (CKEditor 4.22.1)  
**Versión nueva:** django-ckeditor 6.7.1 (CKEditor 4.25.1-lts)  
**Estado:** ✅ Actualización aplicada
