#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para analizar el Excel del cliente antes de transformarlo
Verifica estructura, datos y genera reporte
"""

import pandas as pd
import sys
from pathlib import Path

def analyze_client_excel(excel_path):
    """
    Analiza el Excel del cliente y genera reporte
    
    Args:
        excel_path: Ruta al archivo Excel
    """
    
    print("="*80)
    print("📊 ANÁLISIS DEL EXCEL DEL CLIENTE")
    print("="*80)
    print(f"\nArchivo: {excel_path}\n")
    
    try:
        # Leer Excel
        df = pd.read_excel(excel_path)
        
        # 1. INFORMACIÓN GENERAL
        print("1️⃣  INFORMACIÓN GENERAL")
        print("-" * 80)
        print(f"   Total de filas: {len(df)}")
        print(f"   Total de columnas: {len(df.columns)}")
        print(f"   Columnas: {', '.join(df.columns)}")
        print()
        
        # 2. COLUMNAS ESPERADAS
        print("2️⃣  VALIDACIÓN DE COLUMNAS")
        print("-" * 80)
        
        columnas_esperadas = {
            'ID_SKU': 'Identificador único del producto',
            'NOMBRE': 'Nombre del producto',
            'PRECIO': 'Precio principal (price_1)',
            'CATEGORIA': 'Categoría del producto',
            'IMAGEN': 'URL de la imagen',
            'DESCRIPCION': 'Descripción del producto',
            'ETIQUETA': 'Marca o categoría secundaria',
            'PRECIO_OFERTA': 'Precio de oferta (price_2)',
            'DESCUENTO_EN_%': 'Porcentaje de descuento'
        }
        
        for col, desc in columnas_esperadas.items():
            if col in df.columns:
                print(f"   ✅ {col:20} - {desc}")
            else:
                print(f"   ❌ {col:20} - FALTANTE - {desc}")
        print()
        
        # 3. ANÁLISIS DE DATOS
        print("3️⃣  ANÁLISIS DE DATOS")
        print("-" * 80)
        
        # ID_SKU
        if 'ID_SKU' in df.columns:
            print(f"   ID_SKU:")
            print(f"      - Únicos: {df['ID_SKU'].nunique()}")
            print(f"      - Duplicados: {df['ID_SKU'].duplicated().sum()}")
            print(f"      - Nulos: {df['ID_SKU'].isna().sum()}")
            if df['ID_SKU'].duplicated().any():
                print(f"      ⚠️  IDs duplicados: {df[df['ID_SKU'].duplicated()]['ID_SKU'].tolist()}")
        
        # NOMBRE
        if 'NOMBRE' in df.columns:
            print(f"\n   NOMBRE:")
            print(f"      - Nulos: {df['NOMBRE'].isna().sum()}")
            print(f"      - Longitud promedio: {df['NOMBRE'].str.len().mean():.0f} caracteres")
            print(f"      - Longitud máxima: {df['NOMBRE'].str.len().max():.0f} caracteres")
        
        # PRECIO
        if 'PRECIO' in df.columns:
            print(f"\n   PRECIO:")
            print(f"      - Nulos: {df['PRECIO'].isna().sum()}")
            print(f"      - Mínimo: ${df['PRECIO'].min():,.0f}")
            print(f"      - Máximo: ${df['PRECIO'].max():,.0f}")
            print(f"      - Promedio: ${df['PRECIO'].mean():,.0f}")
        
        # PRECIO_OFERTA
        if 'PRECIO_OFERTA' in df.columns:
            print(f"\n   PRECIO_OFERTA:")
            print(f"      - Con oferta: {df['PRECIO_OFERTA'].notna().sum()}")
            print(f"      - Sin oferta: {df['PRECIO_OFERTA'].isna().sum()}")
            if df['PRECIO_OFERTA'].notna().any():
                print(f"      - Mínimo: ${df['PRECIO_OFERTA'].min():,.0f}")
                print(f"      - Máximo: ${df['PRECIO_OFERTA'].max():,.0f}")
        
        # DESCUENTO_EN_%
        if 'DESCUENTO_EN_%' in df.columns:
            print(f"\n   DESCUENTO_EN_%:")
            print(f"      - Con descuento: {df['DESCUENTO_EN_%'].notna().sum()}")
            print(f"      - Sin descuento: {df['DESCUENTO_EN_%'].isna().sum()}")
            if df['DESCUENTO_EN_%'].notna().any():
                # Limpiar porcentajes
                descuentos = df['DESCUENTO_EN_%'].dropna().astype(str).str.strip('%').astype(float)
                print(f"      - Mínimo: {descuentos.min():.0f}%")
                print(f"      - Máximo: {descuentos.max():.0f}%")
                print(f"      - Promedio: {descuentos.mean():.0f}%")
        
        # CATEGORIA
        if 'CATEGORIA' in df.columns:
            print(f"\n   CATEGORIA:")
            print(f"      - Únicas: {df['CATEGORIA'].nunique()}")
            print(f"      - Categorías:")
            for cat, count in df['CATEGORIA'].value_counts().items():
                print(f"         • {cat}: {count} productos")
        
        # ETIQUETA
        if 'ETIQUETA' in df.columns:
            print(f"\n   ETIQUETA:")
            print(f"      - Únicas: {df['ETIQUETA'].nunique()}")
            print(f"      - Etiquetas:")
            for etiq, count in df['ETIQUETA'].value_counts().items():
                print(f"         • {etiq}: {count} productos")
        
        # IMAGEN
        if 'IMAGEN' in df.columns:
            print(f"\n   IMAGEN:")
            print(f"      - Con imagen: {df['IMAGEN'].notna().sum()}")
            print(f"      - Sin imagen: {df['IMAGEN'].isna().sum()}")
            if df['IMAGEN'].notna().any():
                # Analizar URLs
                urls = df['IMAGEN'].dropna()
                print(f"      - Dominios:")
                dominios = urls.str.extract(r'https?://([^/]+)')[0].value_counts()
                for dominio, count in dominios.items():
                    print(f"         • {dominio}: {count} imágenes")
        
        # DESCRIPCION
        if 'DESCRIPCION' in df.columns:
            print(f"\n   DESCRIPCION:")
            print(f"      - Con descripción: {df['DESCRIPCION'].notna().sum()}")
            print(f"      - Sin descripción: {df['DESCRIPCION'].isna().sum()}")
            if df['DESCRIPCION'].notna().any():
                longitudes = df['DESCRIPCION'].dropna().str.len()
                print(f"      - Longitud promedio: {longitudes.mean():.0f} caracteres")
                print(f"      - Longitud máxima: {longitudes.max():.0f} caracteres")
        
        print()
        
        # 4. MUESTRA DE DATOS
        print("4️⃣  MUESTRA DE DATOS (Primeras 3 filas)")
        print("-" * 80)
        print(df.head(3).to_string())
        print()
        
        # 5. MAPEO A MODELO PRODUCT
        print("5️⃣  MAPEO A MODELO PRODUCT")
        print("-" * 80)
        print(f"   Excel del Cliente          →  Modelo Product")
        print(f"   {'─'*25}    {'─'*30}")
        print(f"   ID_SKU                     →  sku")
        print(f"   NOMBRE                     →  name")
        print(f"   PRECIO                     →  price_1 (precio principal)")
        print(f"   PRECIO_OFERTA              →  price_2 (precio oferta)")
        print(f"   DESCUENTO_EN_%             →  (calcular price_2 si no existe)")
        print(f"   CATEGORIA                  →  categories (ManyToMany)")
        print(f"   ETIQUETA                   →  brand o categories")
        print(f"   IMAGEN                     →  images (ManyToMany, descargar)")
        print(f"   DESCRIPCION                →  description")
        print(f"   (ninguno)                  →  currency = 'CLP'")
        print(f"   (ninguno)                  →  stock_status = 'instock'")
        print(f"   (ninguno)                  →  stock_quantity = 100")
        print(f"   (ninguno)                  →  state = 'publish'")
        print()
        
        # 6. RECOMENDACIONES
        print("6️⃣  RECOMENDACIONES")
        print("-" * 80)
        
        recomendaciones = []
        
        # Verificar duplicados
        if 'ID_SKU' in df.columns and df['ID_SKU'].duplicated().any():
            recomendaciones.append("⚠️  Hay IDs duplicados. Deben ser únicos.")
        
        # Verificar precios
        if 'PRECIO' in df.columns and df['PRECIO'].isna().any():
            recomendaciones.append("⚠️  Hay productos sin precio. Se deben completar.")
        
        # Verificar nombres
        if 'NOMBRE' in df.columns and df['NOMBRE'].isna().any():
            recomendaciones.append("⚠️  Hay productos sin nombre. Se deben completar.")
        
        # Verificar imágenes
        if 'IMAGEN' in df.columns:
            sin_imagen = df['IMAGEN'].isna().sum()
            if sin_imagen > 0:
                recomendaciones.append(f"ℹ️  {sin_imagen} productos sin imagen. Se crearán sin imagen.")
        
        # Verificar consistencia de precios
        if 'PRECIO' in df.columns and 'PRECIO_OFERTA' in df.columns and 'DESCUENTO_EN_%' in df.columns:
            # Verificar que precio_oferta = precio * (1 - descuento)
            df_temp = df[df['PRECIO_OFERTA'].notna() & df['DESCUENTO_EN_%'].notna()].copy()
            if len(df_temp) > 0:
                df_temp['descuento_num'] = df_temp['DESCUENTO_EN_%'].astype(str).str.strip('%').astype(float) / 100
                df_temp['precio_calculado'] = df_temp['PRECIO'] * (1 - df_temp['descuento_num'])
                df_temp['diferencia'] = abs(df_temp['PRECIO_OFERTA'] - df_temp['precio_calculado'])
                inconsistentes = (df_temp['diferencia'] > 1).sum()
                if inconsistentes > 0:
                    recomendaciones.append(f"⚠️  {inconsistentes} productos con inconsistencia entre PRECIO_OFERTA y DESCUENTO_EN_%")
        
        if recomendaciones:
            for rec in recomendaciones:
                print(f"   {rec}")
        else:
            print("   ✅ Todo se ve bien. Listo para transformar.")
        
        print()
        print("="*80)
        print("✅ ANÁLISIS COMPLETADO")
        print("="*80)
        print()
        print("Próximo paso: Ejecutar transform_client_excel.py para transformar los datos")
        print()
        
        return True
        
    except FileNotFoundError:
        print(f"❌ Error: Archivo no encontrado: {excel_path}")
        return False
    except Exception as e:
        print(f"❌ Error al analizar: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_client_excel.py <archivo_excel>")
        print("\nEjemplo:")
        print("  python analyze_client_excel.py excel_cliente.xlsx")
        sys.exit(1)
    
    excel_path = sys.argv[1]
    
    if not Path(excel_path).exists():
        print(f"❌ Error: El archivo no existe: {excel_path}")
        sys.exit(1)
    
    success = analyze_client_excel(excel_path)
    sys.exit(0 if success else 1)
