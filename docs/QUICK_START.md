# 🚀 Quick Start - Catalogue API

Guía rápida para comenzar a desarrollar en menos de 2 minutos.

## ⚡ Inicio Ultra Rápido

```bash
# 1. Iniciar entorno
./start

# 2. Acceder a la aplicación
# Django API: http://localhost:8050
# pgAdmin: http://localhost:5050
```

¡Eso es todo! 🎉

---

## 📋 Comandos Principales

| Comando | Descripción |
|---------|-------------|
| `./start` | Iniciar entorno completo |
| `./stop` | Detener entorno |
| `./logs` | Ver logs de servicios |
| `./reset` | Resetear todo desde cero |

---

## 🎯 Flujo de Trabajo Diario

### Iniciar el día

```bash
./start
```

### Durante el desarrollo

```bash
# Ver logs en tiempo real
./logs

# Crear migraciones
docker compose exec web python manage.py makemigrations

# Aplicar migraciones
docker compose exec web python manage.py migrate

# Acceder al shell de Django
docker compose exec web python manage.py shell
```

### Terminar el día

```bash
./stop
```

---

## 🌐 URLs de Acceso

| Servicio | URL | Credenciales |
|----------|-----|--------------|
| **Django API** | http://localhost:8050 | - |
| **Django Admin** | http://localhost:8050/admin | Crear con `./scripts/create-superuser.sh` |
| **pgAdmin** | http://localhost:5050 | `admin@admin.com` / `admin` |
| **PostgreSQL** | `localhost:5333` | `postgres` / `postgres` / `ms_catalogue_db` |

---

## 🔧 Tareas Comunes

### Crear superusuario

```bash
./scripts/create-superuser.sh
# Seleccionar opción 2 para valores predefinidos (admin/admin)
```

### Resetear base de datos

```bash
./reset
# Seleccionar opción 2 (MEDIA)
./start
```

### Ver logs de un servicio específico

```bash
# Django
docker compose logs -f web

# PostgreSQL
docker compose logs -f db

# pgAdmin
docker compose logs -f pgadmin
```

### Ejecutar tests

```bash
docker compose exec web python manage.py test
```

### Acceder al contenedor

```bash
docker compose exec web bash
```

---

## 📚 Documentación Completa

- [DOCKER_README.md](DOCKER_README.md) - Guía completa de Docker
- [scripts/README.md](scripts/README.md) - Documentación de scripts
- [PRODUCTION_README.md](PRODUCTION_README.md) - Guía de producción

---

## 🆘 Problemas Comunes

### Docker no está corriendo

```bash
# Abrir Docker Desktop y esperar a que inicie
```

### Puerto ya en uso

```bash
# Ver qué proceso usa el puerto 8050
lsof -i :8050

# Matar el proceso
kill -9 <PID>
```

### Base de datos corrupta

```bash
./reset  # Opción 2
./start
```

### Cambios en código no se reflejan

```bash
# Reiniciar servicio web
docker compose restart web
```

---

## ✨ Tips

- Los cambios en el código Python se reflejan automáticamente (hot reload)
- Los archivos media y static persisten entre reinicios
- La base de datos persiste hasta que ejecutes `./reset`
- Usa `./logs` para debugging en tiempo real

---

**¿Necesitas más ayuda?** Lee [DOCKER_README.md](DOCKER_README.md)
