#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para procesar, filtrar y analizar los datos de la Región de Los Ríos
del dataset PUB_COMU_RUBR.csv.

Este script ejecuta de forma secuencial los scripts de filtrado y análisis.

Autor: Bruno Sanmartin
Fecha: 26 de julio de 2025
"""

import os
import sys
import subprocess
from pathlib import Path

# Definir rutas
BASE_DIR = Path(__file__).resolve().parent
SCRIPTS_DIR = BASE_DIR
FILTER_SCRIPT = SCRIPTS_DIR / "filtrar_region_los_rios.py"
ANALYSIS_SCRIPT = SCRIPTS_DIR / "analizar_region_los_rios.py"

def ejecutar_script(script_path):
    """Ejecuta un script de Python e imprime su salida en tiempo real."""
    print(f"\n{'=' * 80}")
    print(f"Ejecutando: {script_path}")
    print(f"{'=' * 80}\n")
    
    # Ejecutar el script y capturar la salida en tiempo real
    try:
        process = subprocess.Popen(
            [sys.executable, str(script_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        
        # Mostrar la salida en tiempo real
        for line in process.stdout:
            print(line, end='')
            
        # Esperar a que el proceso termine y obtener el código de salida
        exit_code = process.wait()
        
        if exit_code != 0:
            print(f"Error: El script {script_path} finalizó con código {exit_code}")
            return False
            
        return True
        
    except Exception as e:
        print(f"Error al ejecutar {script_path}: {e}")
        return False

def main():
    print("\n" + "=" * 80)
    print("PROCESAMIENTO DE DATOS DE LA REGIÓN DE LOS RÍOS")
    print("=" * 80)
    
    # Paso 1: Verificar que los scripts existen
    if not os.path.exists(FILTER_SCRIPT):
        print(f"Error: No se encontró el script de filtrado: {FILTER_SCRIPT}")
        return
        
    if not os.path.exists(ANALYSIS_SCRIPT):
        print(f"Error: No se encontró el script de análisis: {ANALYSIS_SCRIPT}")
        return
    
    # Paso 2: Ejecutar el script de filtrado
    print("\nPaso 1: Filtrado de datos para la Región de Los Ríos")
    if not ejecutar_script(FILTER_SCRIPT):
        print("Error en el proceso de filtrado. Abortando.")
        return
    
    # Paso 3: Ejecutar el script de análisis
    print("\nPaso 2: Análisis de datos de la Región de Los Ríos")
    if not ejecutar_script(ANALYSIS_SCRIPT):
        print("Error en el proceso de análisis.")
        return
    
    print("\n" + "=" * 80)
    print("PROCESAMIENTO COMPLETADO EXITOSAMENTE")
    print("=" * 80)
    
    # Mostrar ubicación de los resultados
    processed_data = Path(BASE_DIR).parent / "data" / "processed" / "region_los_rios.csv"
    results_dir = Path(BASE_DIR).parent / "results" / "region_los_rios"
    
    print(f"\nArchivo de datos filtrado: {processed_data}")
    print(f"Directorio de resultados: {results_dir}")
    
    # Mostrar archivos generados
    if os.path.exists(results_dir):
        print("\nArchivos generados:")
        for file in os.listdir(results_dir):
            print(f"- {file}")

if __name__ == "__main__":
    main()
