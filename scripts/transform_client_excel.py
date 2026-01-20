#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para transformar el Excel del cliente al formato de importación
Soporta múltiples modos de importación (híbrido)
"""

import os
import sys
import django
import pandas as pd
import requests
from pathlib import Path
from decimal import Decimal
from io import BytesIO
import zipfile

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.files import File
from api.models import Product, Category, Brand, Images, Organization, Catalogue

# Configuración
MARCAS_CONOCIDAS = [
    'Cocinerista',
    'Destilería',
    'Cervecería',
    'Avellanera',
    'Cosmética',
    'Energizante',
    'Destilería Nacional',
    'Cocinerista Clásica',
]

def transform_and_import(excel_path, catalogue_slug, import_mode='soft_delete', download_images=True):
    """
    Transforma e importa el Excel del cliente directamente a la BD
    
    Args:
        excel_path: Ruta al archivo Excel
        catalogue_slug: Slug del catálogo
        import_mode: Modo de importación
            - 'update': Actualizar existentes y crear nuevos
            - 'create_only': Solo crear nuevos (no actualizar)
            - 'replace_all': Eliminar todo y recrear
            - 'soft_delete': Sincronizar (ocultar no incluidos)
        download_images: Si True, descarga imágenes. Si False, solo guarda URLs
    
    Returns:
        dict: Estadísticas de la importación
    """
    
    print("="*80)
    print("🚀 TRANSFORMACIÓN E IMPORTACIÓN DE PRODUCTOS")
    print("="*80)
    print(f"Archivo: {excel_path}")
    print(f"Catálogo: {catalogue_slug}")
    print(f"Modo: {import_mode}")
    print(f"Descargar imágenes: {download_images}")
    print("="*80)
    print()
    
    # 1. Obtener catálogo
    try:
        catalogue = Catalogue.objects.get(slug=catalogue_slug)
        organization = catalogue.organization
        print(f"✅ Catálogo encontrado: {catalogue.name}")
        print(f"   Organización: {organization.name}")
    except Catalogue.DoesNotExist:
        print(f"❌ Error: Catálogo '{catalogue_slug}' no encontrado")
        print("\nCatálogos disponibles:")
        for cat in Catalogue.objects.all():
            print(f"   - {cat.slug}: {cat.name} (Org: {cat.organization.name})")
        return None
    
    # 2. Leer Excel
    try:
        df = pd.read_excel(excel_path)
        print(f"✅ Excel leído: {len(df)} filas")
    except Exception as e:
        print(f"❌ Error al leer Excel: {str(e)}")
        return None
    
    # 3. Validar columnas
    columnas_requeridas = ['ID_SKU', 'NOMBRE', 'PRECIO']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        print(f"❌ Error: Columnas faltantes: {columnas_faltantes}")
        print(f"Columnas disponibles: {list(df.columns)}")
        return None
    
    print(f"✅ Columnas validadas")
    print()
    
    # 4. Obtener SKUs del Excel
    skus_en_excel = set()
    for _, row in df.iterrows():
        skus_en_excel.add(f"SKU-{row['ID_SKU']}")
    
    # 5. Aplicar modo de importación
    print(f"📋 Modo de importación: {import_mode}")
    print("-" * 80)
    
    if import_mode == 'replace_all':
        # Eliminar TODOS los productos del catálogo
        productos_existentes = Product.objects.filter(catalogue=catalogue).count()
        print(f"⚠️  MODO PELIGROSO: Se eliminarán {productos_existentes} productos del catálogo '{catalogue.name}'")
        
        confirm = input("¿Estás seguro? Escribe 'ELIMINAR TODO' para confirmar: ")
        if confirm != 'ELIMINAR TODO':
            print("❌ Operación cancelada")
            return None
        
        deleted_count = Product.objects.filter(catalogue=catalogue).delete()[0]
        print(f"🗑️  {deleted_count} productos eliminados")
        print()
    
    elif import_mode == 'soft_delete':
        # Marcar todos como eliminados (se reactivarán los del Excel)
        updated_count = Product.objects.filter(catalogue=catalogue).update(is_removed=True)
        print(f"👻 {updated_count} productos marcados como eliminados")
        print("   (Se reactivarán los que estén en el Excel)")
        print()
    
    elif import_mode == 'update':
        print("🔄 Modo actualización: Se actualizarán existentes y crearán nuevos")
        print("   (Los productos no en el Excel quedarán sin cambios)")
        print()
    
    elif import_mode == 'create_only':
        print("➕ Modo solo creación: Solo se crearán productos nuevos")
        print("   (Los productos existentes no se modificarán)")
        print()
    
    # 6. Estadísticas
    stats = {
        'total': len(df),
        'created': 0,
        'updated': 0,
        'reactivated': 0,
        'skipped': 0,
        'errors': 0,
        'error_details': []
    }
    
    # 7. Procesar cada fila
    print("📦 Procesando productos...")
    print("-" * 80)
    
    for index, row in df.iterrows():
        try:
            # SKU
            sku = f"SKU-{row['ID_SKU']}"
            
            # Verificar si existe
            producto_existente = Product.objects.filter(sku=sku, catalogue=catalogue).first()
            
            # Modo create_only: Omitir si existe
            if import_mode == 'create_only' and producto_existente:
                stats['skipped'] += 1
                print(f"⏭️  OMITIDO (ya existe): {sku}")
                continue
            
            # Preparar datos
            # Precios
            price_1 = Decimal(str(row['PRECIO']))
            price_2 = None
            
            if pd.notna(row.get('PRECIO_OFERTA')):
                price_2 = Decimal(str(row['PRECIO_OFERTA']))
            elif pd.notna(row.get('DESCUENTO_EN_%')):
                descuento_str = str(row['DESCUENTO_EN_%']).strip('%')
                descuento = float(descuento_str) / 100
                price_2 = price_1 * Decimal(str(1 - descuento))
            
            # Descripción
            descripcion = row.get('DESCRIPCION', '')
            if pd.notna(descripcion):
                short_description = descripcion[:150] + "..." if len(descripcion) > 150 else descripcion
                full_description = f"<p>{descripcion}</p>"
            else:
                short_description = row['NOMBRE']
                full_description = ""
            
            # Datos del producto
            product_data = {
                'name': row['NOMBRE'],
                'short_description': short_description,
                'description': full_description,
                'price_1': price_1,
                'price_2': price_2,
                'currency': 'CLP',
                'stock_status': 'instock',
                'stock_quantity': 100,
                'manage_stock': False,
                'state': 'publish',
                'virtual': False,
            }
            
            # Si es modo soft_delete, reactivar
            if import_mode == 'soft_delete':
                product_data['is_removed'] = False
            
            # Crear o actualizar producto
            product, created = Product.objects.update_or_create(
                sku=sku,
                catalogue=catalogue,
                defaults=product_data
            )
            
            # Estadísticas
            if created:
                stats['created'] += 1
                print(f"✅ CREADO: {sku} - {product.name}")
            else:
                if producto_existente and producto_existente.is_removed and import_mode == 'soft_delete':
                    stats['reactivated'] += 1
                    print(f"🔄 REACTIVADO: {sku} - {product.name}")
                else:
                    stats['updated'] += 1
                    print(f"🔄 ACTUALIZADO: {sku} - {product.name}")
            
            # Procesar CATEGORIA
            if pd.notna(row.get('CATEGORIA')):
                categoria_name = row['CATEGORIA']
                categoria, _ = Category.objects.get_or_create(
                    name=categoria_name,
                    organization=organization,
                    defaults={'state': 'publish'}
                )
                product.categories.add(categoria)
            
            # Procesar ETIQUETA (Brand o Categoría secundaria)
            if pd.notna(row.get('ETIQUETA')):
                etiqueta = row['ETIQUETA']
                
                # Clasificar si es marca o categoría
                if etiqueta in MARCAS_CONOCIDAS:
                    # Es una marca
                    brand, _ = Brand.objects.get_or_create(
                        name=etiqueta,
                        organization=organization,
                        defaults={'state': 'publish'}
                    )
                    product.brand = brand
                    product.save()
                else:
                    # Es una categoría secundaria
                    categoria_secundaria, _ = Category.objects.get_or_create(
                        name=etiqueta,
                        organization=organization,
                        defaults={'state': 'publish'}
                    )
                    product.categories.add(categoria_secundaria)
            
            # Procesar IMAGEN
            if download_images and pd.notna(row.get('IMAGEN')):
                image_url = row['IMAGEN']
                image_code = f"IMG-{row['ID_SKU']}"
                
                try:
                    # Descargar imagen
                    response = requests.get(image_url, timeout=15)
                    if response.status_code == 200:
                        # Detectar extensión
                        content_type = response.headers.get('content-type', '')
                        if 'jpeg' in content_type or 'jpg' in content_type:
                            ext = 'jpg'
                        elif 'png' in content_type:
                            ext = 'png'
                        elif 'webp' in content_type:
                            ext = 'webp'
                        else:
                            ext = 'jpg'  # Por defecto
                        
                        # Verificar si ya existe la imagen
                        image_obj, img_created = Images.objects.get_or_create(
                            code=image_code,
                            organization=organization,
                            defaults={
                                'name': f"{product.name} - Principal",
                                'alt': product.name,
                            }
                        )
                        
                        # Guardar archivo
                        image_obj.image.save(
                            f"{image_code}.{ext}",
                            File(BytesIO(response.content)),
                            save=True
                        )
                        
                        # Asociar al producto
                        product.images.add(image_obj)
                        
                        if img_created:
                            print(f"   📷 Imagen descargada: {image_code}.{ext}")
                        else:
                            print(f"   📷 Imagen actualizada: {image_code}.{ext}")
                    else:
                        print(f"   ⚠️  Error descargando imagen: HTTP {response.status_code}")
                
                except Exception as e:
                    print(f"   ⚠️  Error con imagen: {str(e)}")
            
        except Exception as e:
            stats['errors'] += 1
            error_msg = f"Fila {index + 2} (SKU: {row.get('ID_SKU', 'N/A')}): {str(e)}"
            stats['error_details'].append(error_msg)
            print(f"❌ ERROR: {error_msg}")
    
    print()
    
    # 8. Productos eliminados (solo en modo soft_delete)
    if import_mode == 'soft_delete':
        productos_eliminados = Product.objects.filter(
            catalogue=catalogue,
            is_removed=True
        )
        
        if productos_eliminados.exists():
            print("👻 PRODUCTOS NO EN EL EXCEL (Ocultos):")
            print("-" * 80)
            for p in productos_eliminados:
                print(f"   - {p.sku}: {p.name}")
            print()
    
    # 9. Resumen final
    print("="*80)
    print("✅ IMPORTACIÓN COMPLETADA")
    print("="*80)
    print(f"Total procesado: {stats['total']}")
    print(f"Creados: {stats['created']}")
    print(f"Actualizados: {stats['updated']}")
    
    if import_mode == 'soft_delete':
        print(f"Reactivados: {stats['reactivated']}")
        eliminados = Product.objects.filter(catalogue=catalogue, is_removed=True).count()
        print(f"Ocultos (no en Excel): {eliminados}")
    
    if import_mode == 'create_only':
        print(f"Omitidos (ya existían): {stats['skipped']}")
    
    print(f"Errores: {stats['errors']}")
    
    if stats['error_details']:
        print("\nDetalles de errores:")
        for error in stats['error_details'][:10]:
            print(f"   - {error}")
        if len(stats['error_details']) > 10:
            print(f"   ... y {len(stats['error_details']) - 10} errores más")
    
    print("="*80)
    print()
    
    return stats


def main():
    """Función principal"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Transforma e importa Excel del cliente a la base de datos'
    )
    parser.add_argument('excel_file', help='Ruta al archivo Excel')
    parser.add_argument('catalogue', help='Slug del catálogo (ej: catalogo-principal, verano-2026)')
    parser.add_argument(
        '--mode',
        choices=['update', 'create_only', 'replace_all', 'soft_delete'],
        default='soft_delete',
        help='Modo de importación (default: soft_delete)'
    )
    parser.add_argument(
        '--no-images',
        action='store_true',
        help='No descargar imágenes'
    )
    
    args = parser.parse_args()
    
    # Verificar que el archivo existe
    if not Path(args.excel_file).exists():
        print(f"❌ Error: El archivo no existe: {args.excel_file}")
        return 1
    
    # Ejecutar importación
    stats = transform_and_import(
        excel_path=args.excel_file,
        catalogue_slug=args.catalogue,
        import_mode=args.mode,
        download_images=not args.no_images
    )
    
    if stats is None:
        return 1
    
    # Código de salida basado en errores
    return 0 if stats['errors'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
