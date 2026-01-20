# 📜 Scripts de Automatización - Catalogue API

Este directorio contiene todos los scripts de automatización para el desarrollo local con Docker.

## 📋 Scripts Disponibles

### 🚀 **start-local.sh**
Levanta el entorno completo de desarrollo (PostgreSQL, Django, pgAdmin).

**Uso:**
```bash
./scripts/start-local.sh
# o desde la raíz:
./start
```

**Funciones:**
- ✅ Verifica que Docker esté corriendo
- ✅ Verifica/crea archivo `.env`
- ✅ Construye imágenes Docker
- ✅ Levanta todos los servicios
- ✅ Espera a que PostgreSQL esté listo
- ✅ Opción para crear superusuario
- ✅ Opción para ver logs en tiempo real

---

### 🛑 **stop-local.sh**
Detiene el entorno de desarrollo.

**Uso:**
```bash
./scripts/stop-local.sh
# o desde la raíz:
./stop
```

**Opciones:**
- **Opción 1:** Detener contenedores (mantiene datos) - RECOMENDADO
- **Opción 2:** Detener y eliminar volúmenes (borra DB)

---

### 📋 **logs.sh**
Muestra logs de los servicios Docker.

**Uso:**
```bash
./scripts/logs.sh
# o desde la raíz:
./logs
```

**Opciones:**
- Ver logs de todos los servicios
- Ver logs solo de Django (web)
- Ver logs solo de PostgreSQL (db)
- Ver logs solo de pgAdmin

---

### 🔄 **reset-docker.sh**
Resetea completamente el entorno Docker.

**Uso:**
```bash
./scripts/reset-docker.sh
# o desde la raíz:
./reset
```

**Niveles de limpieza:**
1. **SUAVE:** Solo detener contenedores
2. **MEDIA:** Eliminar contenedores + datos (RECOMENDADO)
3. **COMPLETA:** Eliminar todo del proyecto
4. **NUCLEAR:** Eliminar TODO de Docker (⚠️ afecta otros proyectos)

---

### 👤 **create-superuser.sh**
Crea un superusuario de Django.

**Uso:**
```bash
./scripts/create-superuser.sh
```

**Opciones:**
- **Opción 1:** Interactivo (tú eliges usuario/password)
- **Opción 2:** Predefinido (admin/admin@admin.com/admin)

---

### 🔀 **switch-env.sh**
Cambia entre entornos de desarrollo y producción.

**Uso:**
```bash
./scripts/switch-env.sh
```

**Opciones:**
- **Opción 1:** Desarrollo (local con Docker)
- **Opción 2:** Producción (desde `.env.prod`)
- **Opción 3:** Personalizado (desde `.env.example`)

---

## 🎯 Comandos Rápidos desde la Raíz

Para facilitar el uso, hay wrappers en la raíz del proyecto:

```bash
# Iniciar entorno
./start

# Detener entorno
./stop

# Ver logs
./logs

# Resetear todo
./reset
```

---

## 📂 Estructura

```
catalogue_api/
├── scripts/                    # Scripts de automatización
│   ├── start-local.sh         # Iniciar entorno
│   ├── stop-local.sh          # Detener entorno
│   ├── logs.sh                # Ver logs
│   ├── reset-docker.sh        # Resetear entorno
│   ├── create-superuser.sh    # Crear superusuario
│   ├── switch-env.sh          # Cambiar entorno
│   └── README.md              # Esta documentación
├── start                       # Wrapper para start-local.sh
├── stop                        # Wrapper para stop-local.sh
├── logs                        # Wrapper para logs.sh
└── reset                       # Wrapper para reset-docker.sh
```

---

## 🔧 Desarrollo de Scripts

### Agregar un nuevo script

1. Crear el script en `scripts/`:
   ```bash
   touch scripts/mi-script.sh
   chmod +x scripts/mi-script.sh
   ```

2. (Opcional) Crear wrapper en la raíz:
   ```bash
   echo '#!/bin/bash' > mi-comando
   echo './scripts/mi-script.sh "$@"' >> mi-comando
   chmod +x mi-comando
   ```

### Convenciones

- Usar `#!/bin/bash` como shebang
- Usar `set -e` para detener en errores
- Usar colores para mensajes (ver scripts existentes)
- Documentar funciones y parámetros
- Hacer scripts idempotentes cuando sea posible

---

## 📚 Recursos

- [DOCKER_README.md](../DOCKER_README.md) - Guía completa de Docker
- [PRODUCTION_README.md](../PRODUCTION_README.md) - Guía de producción
- [README.md](../README.md) - README principal del proyecto

---

**Última actualización:** 2026-01-19
