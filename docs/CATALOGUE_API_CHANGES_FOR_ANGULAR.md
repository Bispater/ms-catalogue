# Cambios recientes en `catalogue_api` (para Frontend Angular)

## Objetivo
Este documento resume los cambios realizados recientemente en `catalogue_api` para:
- Eliminar errores de CORS desde `https://admin-catalogo-47baa.web.app`.
- Corregir/ajustar configuración para que el frontend Angular pueda consumir la API.
- Exponer endpoints que el frontend esperaba y estaban retornando `404`.

Base de producción:
- `https://catalogue.favric.cl`

---

## 1) CORS en producción (Firebase Hosting)

### Problema
Desde el frontend desplegado en Firebase Hosting:
- Origen: `https://admin-catalogo-47baa.web.app`

Se obtenía:
- `Blocked by CORS policy` al llamar, por ejemplo:
  - `POST https://catalogue.favric.cl/api/token/`

El preflight `OPTIONS` no retornaba `Access-Control-Allow-Origin`.

### Causa raíz
- En producción, `django-cors-headers` estaba permitiendo CORS para `http://localhost:4200` pero **no** para el origen de Firebase.
- Además, el contenedor en producción estaba corriendo con una versión del código donde `CORS_ALLOWED_ORIGINS` estaba hardcodeado (no leía la variable de entorno), por lo cual el cambio en `.env.prod` no se reflejaba en `settings.CORS_ALLOWED_ORIGINS`.

### Cambios aplicados
#### `.env.prod` (producción)
Agregar el origen de Firebase a las listas:
- `CORS_ALLOWED_ORIGINS`
- `CSRF_TRUSTED_ORIGINS`
- `ALLOWED_HOSTS`

Ejemplo (resumen):
```env
ALLOWED_HOSTS=... ,admin-catalogo-47baa.web.app
CSRF_TRUSTED_ORIGINS=... ,https://admin-catalogo-47baa.web.app
CORS_ALLOWED_ORIGINS=... ,https://admin-catalogo-47baa.web.app
```

#### `core/settings.py`
- Se ajustó la configuración para que `CORS_ALLOWED_ORIGINS`, `CORS_ALLOW_HEADERS`, `CORS_ALLOW_METHODS` y `CORS_ALLOW_CREDENTIALS` puedan venir desde variables de entorno (cuando están presentes).

### Despliegue requerido
Para que los cambios de CORS tomen efecto en producción:
- No basta con `restart`.
- Se requiere **rebuild** (si cambió código) y **recreate** del contenedor `web`.

Comandos (en `/var/ms-catalogue`):
```bash
git pull

docker compose -f docker-compose.prod.yml build --no-cache web
docker compose -f docker-compose.prod.yml up -d --force-recreate web
```

### Verificación sugerida (preflight)
```bash
curl -s -D - -o /dev/null -X OPTIONS \
  -H "Origin: https://admin-catalogo-47baa.web.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type,authorization" \
  https://catalogue.favric.cl/api/token/ | sed -n '1,30p'
```
Debe aparecer:
- `access-control-allow-origin: https://admin-catalogo-47baa.web.app`

---

## 2) Corrección de `client-configurations` (filter legacy)

### Problema
`GET /api/client-configurations/` fallaba por un field legacy:
- `organization_id` estaba en `filterset_fields` pero ya no existe en el modelo.

### Cambio
En `api/views.py`:
- Se eliminó `organization_id` de `filterset_fields`.

Resultado:
- `GET /api/client-configurations/` funciona.

---

## 3) Nuevos endpoints expuestos (antes retornaban 404)

> Nota: Estos endpoints se agregaron porque el frontend los estaba consumiendo con paths que no existían en el router.

### 3.1) Organizations
#### Antes
- `GET /api/organization/` -> `404`

#### Ahora
- `GET /api/organization/` -> lista organizaciones
- `GET /api/organization/{id}/` -> detalle

Implementación:
- Se agregó `OrganizationViewSet` y se registró en el router.

Uso desde Angular:
```ts
GET https://catalogue.favric.cl/api/organization/
```

### 3.2) Catalogue (list)
#### Antes
- `GET /api/catalogue/` -> `404`
- Existía solamente:
  - `GET /api/catalogue/<code>/` (catálogo completo por código)

#### Ahora
- `GET /api/catalogue/` -> listado de catálogos (respuesta liviana por defecto)
- `GET /api/catalogue/?full=true` -> listado de catálogos con relaciones (payload grande)
- Se mantiene:
  - `GET /api/catalogue/<code>/` -> catálogo completo por `code`

##### `GET /api/catalogue/` (por defecto)
Retorna campos base + `organization`.

##### `GET /api/catalogue/?full=true`
Retorna cada catálogo usando `CompleteCatalogueSerializer`, incluyendo:
- `products`
- `categories`
- `brands`
- `slides`
- `client_configuration`
- `playlists` (agrupadas por orientación)

Ejemplos:
```http
GET https://catalogue.favric.cl/api/catalogue/
GET https://catalogue.favric.cl/api/catalogue/?full=true
GET https://catalogue.favric.cl/api/catalogue/CAT001/
```

### 3.3) Playlists y Videos
#### Antes
- `GET /api/playlist/` -> `404`

#### Ahora
- `GET /api/playlist/` -> lista playlists
  - Incluye `videos` embebidos vía `PlaylistSerializer`.
- `GET /api/video/` -> lista videos (útil para administración/depuración)

Filtros disponibles (resumen):
- `GET /api/playlist/?is_active=true`
- `GET /api/video/?playlist=<playlist_id>`
- `GET /api/video/?orientation=vertical`

---

## 4) Notas sobre `GET /api/slide/` retornando lista vacía

### Estado
- `GET /api/slide/` retorna `200` pero `results` vacío.

### Interpretación
Esto no es un error de API: significa que no hay Slides que cumplan el queryset y/o que no hay data creada.

En el endpoint de catálogo completo (`GET /api/catalogue/<code>/`), los slides se filtran a:
- `virtual=False`
- `state='publish'`

Por eso puede existir la sensación de inconsistencia si se espera que `/api/slide/` siempre traiga contenido.

---

## 5) Recomendaciones para el Frontend Angular

### Auth (JWT)
- Obtener token:
  - `POST /api/token/`
- Refresh:
  - `POST /api/token/refresh/`

### Consumo recomendado de catálogo
- Para vista completa por catálogo:
  - `GET /api/catalogue/<code>/`

- Para selector/listado de catálogos:
  - `GET /api/catalogue/`

- Solo si necesitas todo (costo alto):
  - `GET /api/catalogue/?full=true`

### Playlists / Videos
- Para render de playlist con videos:
  - `GET /api/playlist/`

---

## 6) Checklist de despliegue

1. `git pull`
2. `docker compose -f docker-compose.prod.yml build --no-cache web`
3. `docker compose -f docker-compose.prod.yml up -d --force-recreate web`
4. Verificar endpoints:
   - `GET /api/organization/`
   - `GET /api/catalogue/`
   - `GET /api/catalogue/?full=true`
   - `GET /api/playlist/`
   - `GET /api/video/`
5. Verificar CORS preflight a `/api/token/` con Origin Firebase.
