#!/usr/bin/env python3
"""
Script para procesar el archivo PUB_COMU_RUBR.xlsb y generar un CSV con datos de la Región de Los Ríos.
Este script convierte los datos del archivo XLSB a formato CSV y corrige problemas de codificación.
"""

import pandas as pd
from pyxlsb import open_workbook
import os
import numpy as np
from pathlib import Path

# Definir rutas
BASE_DIR = Path(__file__).parents[1]
INPUT_FILE = BASE_DIR / "PUB_COMU_RUBR.xlsb"
OUTPUT_DIR = BASE_DIR / "data" / "raw"
OUTPUT_FILE_CSV = OUTPUT_DIR / "PUB_COMU_RUBR.csv"

print(f"Procesando archivo: {INPUT_FILE}")
print(f"Base dir: {BASE_DIR}")

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Determinar qué hojas hay en el archivo XLSB
sheets = []
with open_workbook(INPUT_FILE) as wb:
    for sheet in wb.sheets:
        sheets.append(sheet)
    
print(f"Hojas encontradas en el archivo XLSB: {sheets}")

# Leer la primera hoja (o la especificada)
target_sheet = sheets[0] if sheets else None

if target_sheet:
    print(f"Leyendo hoja: {target_sheet}")
    
    # Leer el archivo XLSB
    df = pd.read_excel(INPUT_FILE, engine='pyxlsb', sheet_name=target_sheet)
    
    # Mostrar las primeras filas para verificar
    print("\nPrimeras filas del dataset original:")
    print(df.head())
    
    # Mostrar información sobre el DataFrame
    print("\nInformación del DataFrame original:")
    print(f"Columnas: {df.columns.tolist()}")
    print(f"Dimensiones: {df.shape}")
    
    # Determinar la fila que contiene los nombres de columnas
    for i, row in df.iterrows():
        if 'Año Comercial' in str(row.values):
            header_row_idx = i
            break
    
    # Extraer los nombres de las columnas de la fila correspondiente
    column_names = df.iloc[header_row_idx].values
    
    # Crear un nuevo DataFrame empezando desde la fila después de las cabeceras
    new_df = df.iloc[header_row_idx+1:].copy()
    
    # Asignar los nombres de columnas
    new_df.columns = column_names
    
    # Resetear los índices
    new_df = new_df.reset_index(drop=True)
    
    print("\nPrimeras filas del dataset con nombres de columnas corregidos:")
    print(new_df.head())
    
    print("\nColumnas en el nuevo DataFrame:")
    for col in new_df.columns:
        print(f"- {col}")
    
    # Buscar y listar todas las regiones disponibles
    region_column = [col for col in new_df.columns if 'Region' in str(col) or 'región' in str(col).lower()]
    
    if region_column:
        region_col = region_column[0]
        print(f"\nColumna de región encontrada: {region_col}")
        regiones = new_df[region_col].dropna().unique()
        print("\nRegiones disponibles en el dataset:")
        for region in sorted(regiones):
            print(f"- {region}")
        
        # Filtrar datos para la Región de Los Ríos
        # Busca cualquier variante de "Los Ríos" en el nombre de la región
        region_los_rios = None
        for region in regiones:
            if isinstance(region, str) and ('rio' in region.lower() or 'río' in region.lower()):
                region_los_rios = new_df[new_df[region_col] == region].copy()
                print(f"\nEncontrada la Región de Los Ríos como: '{region}'")
                break
        
        if region_los_rios is not None:
            # Guardar los datos filtrados de Los Ríos
            region_output_file = BASE_DIR / "data" / "processed" / "region_los_rios.csv"
            os.makedirs(os.path.dirname(region_output_file), exist_ok=True)
            region_los_rios.to_csv(region_output_file, index=False, encoding='utf-8')
            print(f"Datos de la Región de Los Ríos guardados en: {region_output_file}")
            print(f"Número de registros: {len(region_los_rios)}")
        else:
            print("\nNo se pudo encontrar la Región de Los Ríos en el dataset")
    else:
        print("No se pudo encontrar la columna de región en el dataset")
    
    # Guardar el dataset completo con nombres corregidos
    new_df.to_csv(OUTPUT_FILE_CSV, index=False, encoding='utf-8')
    print(f"\nArchivo CSV completo guardado en: {OUTPUT_FILE_CSV}")
    
else:
    print("No se encontraron hojas en el archivo XLSB")
