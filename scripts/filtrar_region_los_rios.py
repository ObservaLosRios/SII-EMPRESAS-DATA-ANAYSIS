#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para filtrar el dataset PUB_COMU_RUBR.csv y obtener solo los datos 
de la Región de Los Ríos.

Autor: Bruno Sanmartin
Fecha: 26 de julio de 2025
"""

import pandas as pd
import os
from pathlib import Path

# Definir rutas
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "raw" / "PUB_COMU_RUBR.csv"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "region_los_rios.csv"

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

def main():
    print(f"Leyendo archivo: {INPUT_FILE}")
    
    # Leer el archivo CSV
    # Nota: Usamos encoding='latin1' para manejar caracteres especiales del español
    df = pd.read_csv(INPUT_FILE, encoding='latin1')
    
    # Verificar columnas y datos iniciales
    print(f"Dimensiones originales: {df.shape}")
    print(f"Columnas disponibles: {df.columns.tolist()}")
    
    # Filtrar solo los registros de la Región de Los Ríos
    region_los_rios = df[df["Region del domicilio o casa matriz"] == "Región de Los Ríos"]
    
    # Verificar cuántos registros se obtuvieron
    print(f"Registros filtrados: {region_los_rios.shape[0]} (de {df.shape[0]} originales)")
    
    # Guardar en un nuevo archivo CSV
    region_los_rios.to_csv(OUTPUT_FILE, index=False, encoding='utf-8')
    
    print(f"Archivo guardado exitosamente en: {OUTPUT_FILE}")
    
    # Mostrar estadísticas básicas
    print("\nEstadísticas básicas de la Región de Los Ríos:")
    print(f"Total de comunas: {region_los_rios['Comuna del domicilio o casa matriz'].nunique()}")
    print(f"Años disponibles: {sorted(region_los_rios['Año Comercial'].unique())}")
    print(f"Rubros económicos: {region_los_rios['Rubro economico'].nunique()}")
    
    # Mostrar las comunas de la región
    print("\nComunas de la Región de Los Ríos:")
    comunas = region_los_rios['Comuna del domicilio o casa matriz'].unique()
    for comuna in sorted(comunas):
        print(f"- {comuna}")

if __name__ == "__main__":
    main()
