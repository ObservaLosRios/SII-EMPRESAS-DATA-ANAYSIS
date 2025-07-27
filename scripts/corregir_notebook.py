"""
Script para arreglar el notebook analisis_region_los_rios.ipynb
Este script crea una copia del notebook original con las rutas corregidas
"""
import json
import os
from pathlib import Path

# Ruta al notebook original y al nuevo notebook
BASE_DIR = Path(__file__).parents[1]
NOTEBOOK_PATH = BASE_DIR / "notebooks" / "analisis_region_los_rios.ipynb"
NEW_NOTEBOOK_PATH = BASE_DIR / "notebooks" / "analisis_region_los_rios_corregido.ipynb"

print(f"Leyendo notebook: {NOTEBOOK_PATH}")

# Leer el contenido del notebook
with open(NOTEBOOK_PATH, 'r', encoding='utf-8') as file:
    notebook_data = json.load(file)

# Modificar las celdas problemáticas
for cell in notebook_data['cells']:
    if cell['cell_type'] == 'code':
        # Convertimos el contenido de la celda a string para buscar y reemplazar
        cell_content = ''.join(cell['source'])
        
        # Reemplazar rutas para cargar el archivo CSV (ya existente)
        if 'INPUT_FILE = BASE_DIR / "data" / "raw" / "PUB_COMU_RUBR.csv"' in cell_content:
            # La ruta al archivo CSV ya es correcta, se generó con el script procesar_xlsb.py
            pass
        
        # Si hay una referencia a df['Region del domicilio o casa matriz'] == "Región de Los Ríos"
        # reemplazarla por el nombre correcto identificado en el procesamiento
        if 'region_los_rios = df[df["Region del domicilio o casa matriz"] == "Región de Los Ríos"]' in cell_content:
            # Actualizar el nombre correcto de la región
            cell['source'] = [line.replace('"Región de Los Ríos"', '"Región de Los Ríos"') 
                             for line in cell['source']]
        
        # Si hay una celda que busca la región con nombre "RegiÃ³n de Los RÃ­os"
        if 'region_name = "RegiÃ³n de Los RÃ­os"' in cell_content:
            for i, line in enumerate(cell['source']):
                if 'region_name = "RegiÃ³n de Los RÃ­os"' in line:
                    # Reemplazar por el nombre correcto
                    cell['source'][i] = 'region_name = "Región de Los Ríos"\n'

# Guardar el notebook modificado
with open(NEW_NOTEBOOK_PATH, 'w', encoding='utf-8') as file:
    json.dump(notebook_data, file, indent=1)

print(f"Notebook corregido guardado como: {NEW_NOTEBOOK_PATH}")
