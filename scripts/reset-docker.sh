#!/bin/bash

# Script para resetear completamente el entorno Docker
# Autor: Catalogue API Team
# Fecha: 2026-01-19

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_danger() {
    echo -e "${RED}[PELIGRO]${NC} $1"
}

# Banner
echo -e "${RED}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║         ⚠️  RESETEAR ENTORNO DOCKER ⚠️                 ║"
echo "║              ELIMINAR TODO Y EMPEZAR DE CERO          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

print_danger "Este script eliminará TODOS los datos del entorno Docker"
echo ""
echo -e "${YELLOW}¿Qué se eliminará?${NC}"
echo ""
echo "  🗑️  Contenedores (web, db, pgadmin)"
echo "  🗑️  Volúmenes (base de datos, archivos media/static)"
echo "  🗑️  Imágenes Docker construidas"
echo "  🗑️  Redes Docker"
echo ""
print_warning "⚠️  LA BASE DE DATOS SE PERDERÁ COMPLETAMENTE ⚠️"
echo ""

# Preguntar nivel de limpieza
echo -e "${BLUE}Selecciona el nivel de limpieza:${NC}"
echo ""
echo "  ${GREEN}[1] Limpieza SUAVE${NC} - Solo detener contenedores"
echo "      └─ Mantiene: volúmenes (datos), imágenes"
echo ""
echo "  ${YELLOW}[2] Limpieza MEDIA${NC} - Detener y eliminar contenedores + volúmenes"
echo "      └─ Elimina: contenedores, volúmenes (DATOS)"
echo "      └─ Mantiene: imágenes (más rápido rebuild)"
echo ""
echo "  ${RED}[3] Limpieza COMPLETA${NC} - Eliminar TODO"
echo "      └─ Elimina: contenedores, volúmenes, imágenes, redes"
echo "      └─ Rebuild completo desde cero (más lento)"
echo ""
echo "  ${MAGENTA}[4] Limpieza NUCLEAR${NC} - Eliminar TODO de Docker (no solo este proyecto)"
echo "      └─ Elimina: TODOS los contenedores, volúmenes e imágenes de Docker"
echo "      └─ ⚠️  AFECTA OTROS PROYECTOS DOCKER ⚠️"
echo ""
echo "  [5] Cancelar"
echo ""
read -p "Selecciona una opción (1-5): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        print_message "Limpieza SUAVE - Solo deteniendo contenedores..."
        echo ""
        
        docker compose down
        
        print_success "✅ Contenedores detenidos"
        print_message "Los datos se mantienen intactos"
        print_message "Para volver a iniciar: ./start-local.sh"
        ;;
        
    2)
        print_warning "Limpieza MEDIA - Eliminando contenedores y volúmenes..."
        echo ""
        
        read -p "⚠️  ¿Estás seguro? Se perderán TODOS los datos de la base de datos (s/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_message "Operación cancelada"
            exit 0
        fi
        
        echo ""
        print_message "Deteniendo y eliminando contenedores..."
        docker compose down -v
        
        print_success "✅ Contenedores eliminados"
        print_success "✅ Volúmenes eliminados (datos borrados)"
        print_message "Las imágenes se mantienen para rebuild rápido"
        print_message "Para volver a iniciar: ./start-local.sh"
        ;;
        
    3)
        print_danger "Limpieza COMPLETA - Eliminando TODO del proyecto..."
        echo ""
        
        read -p "⚠️  ¿Estás COMPLETAMENTE seguro? (s/n): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Ss]$ ]]; then
            print_message "Operación cancelada"
            exit 0
        fi
        
        echo ""
        print_message "1/4 - Deteniendo contenedores..."
        docker compose down -v 2>/dev/null || true
        
        print_message "2/4 - Eliminando imágenes del proyecto..."
        docker images | grep catalogue | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
        
        print_message "3/4 - Eliminando redes huérfanas..."
        docker network prune -f 2>/dev/null || true
        
        print_message "4/4 - Limpiando sistema..."
        docker system prune -f 2>/dev/null || true
        
        print_success "✅ Limpieza completa finalizada"
        print_message "Todo ha sido eliminado. Rebuild será desde cero"
        print_message "Para volver a iniciar: ./start-local.sh"
        ;;
        
    4)
        print_danger "Limpieza NUCLEAR - ⚠️  ELIMINANDO TODO DE DOCKER ⚠️"
        echo ""
        print_warning "Esto afectará TODOS tus proyectos Docker, no solo este"
        echo ""
        
        read -p "⚠️  ¿Estás ABSOLUTAMENTE seguro? Escribe 'SI ELIMINAR TODO': " CONFIRM
        echo ""
        if [ "$CONFIRM" != "SI ELIMINAR TODO" ]; then
            print_message "Operación cancelada (respuesta incorrecta)"
            exit 0
        fi
        
        echo ""
        print_message "1/5 - Deteniendo TODOS los contenedores..."
        docker stop $(docker ps -aq) 2>/dev/null || true
        
        print_message "2/5 - Eliminando TODOS los contenedores..."
        docker rm $(docker ps -aq) 2>/dev/null || true
        
        print_message "3/5 - Eliminando TODOS los volúmenes..."
        docker volume rm $(docker volume ls -q) 2>/dev/null || true
        
        print_message "4/5 - Eliminando TODAS las imágenes..."
        docker rmi $(docker images -aq) -f 2>/dev/null || true
        
        print_message "5/5 - Limpieza completa del sistema..."
        docker system prune -a --volumes -f 2>/dev/null || true
        
        print_success "✅ Limpieza NUCLEAR completada"
        print_warning "Docker está completamente limpio"
        print_message "Para volver a iniciar: ./start-local.sh"
        ;;
        
    5)
        print_message "Operación cancelada"
        exit 0
        ;;
        
    *)
        print_error "Opción inválida"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║              ✨ LIMPIEZA COMPLETADA ✨                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════════════════╝${NC}"
echo ""

# Mostrar estado actual
print_message "Estado actual de Docker:"
echo ""
echo -e "${BLUE}Contenedores corriendo:${NC}"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "  Ninguno"
echo ""
echo -e "${BLUE}Volúmenes:${NC}"
docker volume ls --format "table {{.Name}}" 2>/dev/null | grep catalogue || echo "  Ninguno"
echo ""
echo -e "${BLUE}Imágenes del proyecto:${NC}"
docker images | grep catalogue || echo "  Ninguna"
echo ""

print_success "🎉 Listo para empezar de cero"
echo ""
