#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de prueba para verificar la importación con Catalogue
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Organization, Catalogue, Product, Category, Brand

def test_catalogue_system():
    """
    Prueba completa del sistema de catálogos
    """
    
    print("="*80)
    print("🧪 PRUEBA DEL SISTEMA DE CATÁLOGOS")
    print("="*80)
    print()
    
    # 1. Verificar organización
    print("1️⃣  Verificando organización...")
    org = Organization.objects.first()
    if not org:
        print("   ❌ No hay organizaciones. Creando una...")
        org = Organization.objects.create(
            name="Organización de Prueba",
            slug="org-prueba",
            description="Organización para pruebas"
        )
        print(f"   ✅ Organización creada: {org.name}")
    else:
        print(f"   ✅ Organización encontrada: {org.name} ({org.slug})")
    print()
    
    # 2. Verificar catálogo principal
    print("2️⃣  Verificando catálogo principal...")
    catalogue = Catalogue.objects.filter(slug='catalogo-principal').first()
    if not catalogue:
        print("   ❌ Catálogo principal no existe. Creando...")
        catalogue = Catalogue.objects.create(
            name="Catálogo Principal",
            slug="catalogo-principal",
            organization=org,
            description="Catálogo principal de prueba",
            is_active=True
        )
        print(f"   ✅ Catálogo creado: {catalogue.name}")
    else:
        print(f"   ✅ Catálogo encontrado: {catalogue.name} ({catalogue.slug})")
    print()
    
    # 3. Crear catálogo de verano
    print("3️⃣  Creando catálogo de verano...")
    verano, created = Catalogue.objects.get_or_create(
        slug='verano-2026',
        organization=org,
        defaults={
            'name': 'Verano 2026',
            'description': 'Productos de temporada verano 2026',
            'is_active': True
        }
    )
    if created:
        print(f"   ✅ Catálogo creado: {verano.name}")
    else:
        print(f"   ℹ️  Catálogo ya existe: {verano.name}")
    print()
    
    # 4. Crear categoría de prueba
    print("4️⃣  Creando categoría de prueba...")
    categoria, created = Category.objects.get_or_create(
        slug='ropa',
        organization=org,
        defaults={
            'name': 'Ropa',
            'description': 'Categoría de ropa',
            'state': 'publish'
        }
    )
    if created:
        print(f"   ✅ Categoría creada: {categoria.name}")
    else:
        print(f"   ℹ️  Categoría ya existe: {categoria.name}")
    print()
    
    # 5. Crear marca de prueba
    print("5️⃣  Creando marca de prueba...")
    marca, created = Brand.objects.get_or_create(
        slug='marca-test',
        organization=org,
        defaults={
            'name': 'Marca Test',
            'description': 'Marca de prueba',
            'state': 'publish'
        }
    )
    if created:
        print(f"   ✅ Marca creada: {marca.name}")
    else:
        print(f"   ℹ️  Marca ya existe: {marca.name}")
    print()
    
    # 6. Crear productos de prueba en catálogo principal
    print("6️⃣  Creando productos en catálogo principal...")
    productos_principal = [
        {
            'sku': 'TEST-001',
            'name': 'Producto Test 1',
            'price_1': 10000,
            'description': '<p>Descripción del producto test 1</p>',
        },
        {
            'sku': 'TEST-002',
            'name': 'Producto Test 2',
            'price_1': 20000,
            'description': '<p>Descripción del producto test 2</p>',
        },
        {
            'sku': 'TEST-003',
            'name': 'Producto Test 3',
            'price_1': 30000,
            'description': '<p>Descripción del producto test 3</p>',
        },
    ]
    
    for prod_data in productos_principal:
        product, created = Product.objects.update_or_create(
            sku=prod_data['sku'],
            catalogue=catalogue,
            defaults={
                'name': prod_data['name'],
                'price_1': prod_data['price_1'],
                'description': prod_data['description'],
                'short_description': prod_data['name'],
                'currency': 'CLP',
                'stock_status': 'instock',
                'stock_quantity': 100,
                'state': 'publish',
                'brand': marca,
            }
        )
        
        if created:
            product.categories.add(categoria)
            print(f"   ✅ Creado: {product.sku} - {product.name}")
        else:
            print(f"   🔄 Actualizado: {product.sku} - {product.name}")
    print()
    
    # 7. Crear productos de prueba en catálogo de verano
    print("7️⃣  Creando productos en catálogo de verano...")
    productos_verano = [
        {
            'sku': 'VERANO-001',
            'name': 'Traje de Baño',
            'price_1': 25000,
            'description': '<p>Traje de baño para verano</p>',
        },
        {
            'sku': 'VERANO-002',
            'name': 'Sandalias',
            'price_1': 15000,
            'description': '<p>Sandalias cómodas</p>',
        },
    ]
    
    for prod_data in productos_verano:
        product, created = Product.objects.update_or_create(
            sku=prod_data['sku'],
            catalogue=verano,
            defaults={
                'name': prod_data['name'],
                'price_1': prod_data['price_1'],
                'description': prod_data['description'],
                'short_description': prod_data['name'],
                'currency': 'CLP',
                'stock_status': 'instock',
                'stock_quantity': 50,
                'state': 'publish',
                'brand': marca,
            }
        )
        
        if created:
            product.categories.add(categoria)
            print(f"   ✅ Creado: {product.sku} - {product.name}")
        else:
            print(f"   🔄 Actualizado: {product.sku} - {product.name}")
    print()
    
    # 8. Estadísticas finales
    print("="*80)
    print("📊 ESTADÍSTICAS")
    print("="*80)
    
    total_catalogues = Catalogue.objects.count()
    total_products = Product.objects.count()
    
    print(f"Total de organizaciones: {Organization.objects.count()}")
    print(f"Total de catálogos: {total_catalogues}")
    print(f"Total de productos: {total_products}")
    print()
    
    print("Por catálogo:")
    for cat in Catalogue.objects.all():
        count = cat.products.count()
        print(f"   - {cat.name} ({cat.slug}): {count} productos")
    print()
    
    print("Por organización (a través de catálogos):")
    for org_item in Organization.objects.all():
        count = Product.objects.filter(catalogue__organization=org_item).count()
        print(f"   - {org_item.name}: {count} productos")
    print()
    
    # 9. Verificar relaciones
    print("="*80)
    print("🔗 VERIFICACIÓN DE RELACIONES")
    print("="*80)
    
    # Producto → Catálogo → Organización
    producto = Product.objects.first()
    if producto:
        print(f"Producto: {producto.name}")
        print(f"   └── Catálogo: {producto.catalogue.name}")
        print(f"       └── Organización: {producto.catalogue.organization.name}")
    print()
    
    # Catálogo → Productos
    print(f"Catálogo '{catalogue.name}' tiene:")
    for p in catalogue.products.all()[:3]:
        print(f"   - {p.sku}: {p.name}")
    print()
    
    # Organización → Catálogos → Productos
    print(f"Organización '{org.name}' tiene:")
    for cat in org.catalogues.all():
        print(f"   - Catálogo '{cat.name}': {cat.products.count()} productos")
    print()
    
    print("="*80)
    print("✅ PRUEBA COMPLETADA")
    print("="*80)
    print()
    
    return {
        'organization': org,
        'catalogues': Catalogue.objects.count(),
        'products': Product.objects.count(),
    }

if __name__ == "__main__":
    try:
        result = test_catalogue_system()
        print("✅ Sistema de catálogos funcionando correctamente")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
