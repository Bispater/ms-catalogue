#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para migrar datos existentes al nuevo modelo Catalogue
Crea un catálogo por defecto para cada organización
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Organization, Catalogue, Product, ImportFile, Slide, ClientConfiguration

def migrate_to_catalogues():
    """
    Crea un catálogo por defecto para cada organización
    y asocia todos los productos e import files existentes
    """
    
    print("="*80)
    print("🔄 MIGRACIÓN A MODELO CATALOGUE")
    print("="*80)
    print()
    
    # Obtener todas las organizaciones
    organizations = Organization.objects.all()
    
    if not organizations.exists():
        print("⚠️  No hay organizaciones en la base de datos")
        print("   Creando organización por defecto...")
        
        org = Organization.objects.create(
            name="Organización Principal",
            slug="organizacion-principal",
            description="Organización creada automáticamente durante la migración"
        )
        organizations = [org]
        print(f"✅ Organización creada: {org.name}")
        print()
    
    total_products = 0
    total_import_files = 0
    total_slides = 0
    total_client_configs = 0
    
    for org in organizations:
        print(f"📦 Procesando: {org.name} ({org.slug})")
        print("-" * 80)
        
        # Crear catálogo por defecto
        catalogue, created = Catalogue.objects.get_or_create(
            organization=org,
            slug='catalogo-principal',
            defaults={
                'name': 'Catálogo Principal',
                'description': 'Catálogo principal (creado automáticamente durante migración)',
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Catálogo creado: {catalogue.name}")
        else:
            print(f"   ℹ️  Catálogo ya existe: {catalogue.name}")
        
        # Migrar productos sin catálogo
        products_sin_catalogo = Product.objects.filter(catalogue__isnull=True)
        
        if products_sin_catalogo.exists():
            count = products_sin_catalogo.update(catalogue=catalogue)
            total_products += count
            print(f"   📦 {count} productos asociados al catálogo")
        else:
            print(f"   ℹ️  No hay productos sin catálogo")
        
        # Migrar import files sin catálogo
        imports_sin_catalogo = ImportFile.objects.filter(catalogue__isnull=True)
        
        if imports_sin_catalogo.exists():
            count = imports_sin_catalogo.update(catalogue=catalogue)
            total_import_files += count
            print(f"   📥 {count} archivos de importación asociados al catálogo")
        else:
            print(f"   ℹ️  No hay archivos de importación sin catálogo")
        
        # Migrar slides sin catálogo
        slides_sin_catalogo = Slide.objects.filter(catalogue__isnull=True)
        
        if slides_sin_catalogo.exists():
            count = slides_sin_catalogo.update(catalogue=catalogue)
            total_slides += count
            print(f"   🎬 {count} slides asociados al catálogo")
        else:
            print(f"   ℹ️  No hay slides sin catálogo")
        
        # Migrar client configurations sin catálogo
        configs_sin_catalogo = ClientConfiguration.objects.filter(catalogue__isnull=True)
        
        if configs_sin_catalogo.exists():
            count = configs_sin_catalogo.update(catalogue=catalogue)
            total_client_configs += count
            print(f"   ⚙️  {count} configuraciones de cliente asociadas al catálogo")
        else:
            print(f"   ℹ️  No hay configuraciones de cliente sin catálogo")
        
        print()
    
    # Resumen final
    print("="*80)
    print("✅ MIGRACIÓN COMPLETADA")
    print("="*80)
    print(f"Organizaciones procesadas: {len(organizations)}")
    print(f"Productos migrados: {total_products}")
    print(f"Archivos de importación migrados: {total_import_files}")
    print(f"Slides migrados: {total_slides}")
    print(f"Configuraciones de cliente migradas: {total_client_configs}")
    print("="*80)
    print()
    
    # Verificar que no queden registros sin catálogo
    products_sin_catalogo = Product.objects.filter(catalogue__isnull=True).count()
    imports_sin_catalogo = ImportFile.objects.filter(catalogue__isnull=True).count()
    slides_sin_catalogo = Slide.objects.filter(catalogue__isnull=True).count()
    configs_sin_catalogo = ClientConfiguration.objects.filter(catalogue__isnull=True).count()
    
    if products_sin_catalogo > 0 or imports_sin_catalogo > 0 or slides_sin_catalogo > 0 or configs_sin_catalogo > 0:
        print("⚠️  ADVERTENCIA:")
        if products_sin_catalogo > 0:
            print(f"   - {products_sin_catalogo} productos aún sin catálogo")
        if imports_sin_catalogo > 0:
            print(f"   - {imports_sin_catalogo} archivos de importación aún sin catálogo")
        if slides_sin_catalogo > 0:
            print(f"   - {slides_sin_catalogo} slides aún sin catálogo")
        if configs_sin_catalogo > 0:
            print(f"   - {configs_sin_catalogo} configuraciones de cliente aún sin catálogo")
        print()
        return False
    else:
        print("✅ Todos los registros tienen catálogo asignado")
        print()
        return True

if __name__ == "__main__":
    success = migrate_to_catalogues()
    sys.exit(0 if success else 1)
