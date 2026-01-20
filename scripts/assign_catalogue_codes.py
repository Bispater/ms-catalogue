#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para asignar códigos a catálogos existentes
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
sys.path.append(str(Path(__file__).parent.parent))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Catalogue
from django.utils.text import slugify

def assign_codes():
    """
    Asigna códigos únicos a catálogos que no tienen código
    """
    
    print("="*80)
    print("🔢 ASIGNACIÓN DE CÓDIGOS A CATÁLOGOS")
    print("="*80)
    print()
    
    # Obtener catálogos sin código
    catalogues_without_code = Catalogue.objects.filter(code__isnull=True) | Catalogue.objects.filter(code='')
    
    if not catalogues_without_code.exists():
        print("✅ Todos los catálogos ya tienen código asignado")
        print()
        return
    
    print(f"📋 Encontrados {catalogues_without_code.count()} catálogos sin código")
    print()
    
    updated_count = 0
    
    for catalogue in catalogues_without_code:
        # Generar código basado en el slug
        # Ejemplo: "catalogo-principal" -> "CAT-PRINCIPAL"
        # Ejemplo: "verano-2026" -> "VERANO-2026"
        
        base_code = catalogue.slug.upper().replace('-', '_')
        
        # Si el código es muy largo, usar las primeras letras + número
        if len(base_code) > 20:
            # Tomar primeras 3 letras de cada palabra
            words = catalogue.slug.split('-')
            short_code = ''.join([w[:3].upper() for w in words[:3]])
            base_code = short_code
        
        # Verificar unicidad
        code = base_code
        counter = 1
        while Catalogue.objects.filter(code=code, organization=catalogue.organization).exists():
            code = f"{base_code}_{counter}"
            counter += 1
        
        # Asignar código
        catalogue.code = code
        catalogue.save()
        
        print(f"✅ {catalogue.name} ({catalogue.organization.name})")
        print(f"   Código asignado: {code}")
        print()
        
        updated_count += 1
    
    print("="*80)
    print("✅ ASIGNACIÓN COMPLETADA")
    print("="*80)
    print(f"Total de catálogos actualizados: {updated_count}")
    print()
    
    # Mostrar todos los catálogos con sus códigos
    print("📋 CATÁLOGOS CON CÓDIGOS:")
    print("-"*80)
    for cat in Catalogue.objects.all().order_by('organization', 'code'):
        print(f"  {cat.code:20} | {cat.name:30} | {cat.organization.name}")
    print()

if __name__ == "__main__":
    try:
        assign_codes()
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
