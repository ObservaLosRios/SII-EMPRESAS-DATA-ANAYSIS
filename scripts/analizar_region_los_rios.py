#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para analizar los datos de la Región de Los Ríos del dataset PUB_COMU_RUBR.csv
y generar gráficos y estadísticas específicas de la región.

Autor: Bruno Sanmartin
Fecha: 26 de julio de 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os
from pathlib import Path

# Definir rutas
BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_FILE = BASE_DIR / "data" / "processed" / "region_los_rios.csv"
OUTPUT_DIR = BASE_DIR / "results" / "region_los_rios"

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configurar estilo de gráficos
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_palette("viridis")
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans']

def clean_numeric_columns(df):
    """Limpia las columnas numéricas reemplazando '*' y convirtiendo formatos de números."""
    numeric_columns = df.select_dtypes(include=['object']).columns
    
    for col in numeric_columns:
        # Verificar si la columna contiene valores numéricos con formato de miles
        if df[col].dtype == 'object' and df[col].str.contains(',', na=False).any():
            # Reemplazar '*' por NaN
            df[col] = df[col].replace('*', np.nan)
            
            # Eliminar comas de números con formato de miles
            df[col] = df[col].str.replace(',', '')
            
            # Convertir a float
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

def analisis_empresas_por_comuna(df):
    """Analiza y grafica la distribución de empresas por comuna."""
    empresas_comuna = df.groupby('Comuna del domicilio o casa matriz')['Número de empresas'].sum().sort_values(ascending=False)
    
    # Gráfico de barras
    plt.figure(figsize=(14, 10))
    ax = empresas_comuna.plot(kind='bar', color=sns.color_palette("viridis", len(empresas_comuna)))
    
    plt.title('Número de Empresas por Comuna en la Región de Los Ríos', fontsize=16, fontweight='bold')
    plt.xlabel('Comuna', fontsize=14)
    plt.ylabel('Número de Empresas', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Añadir etiquetas con los valores
    for i, v in enumerate(empresas_comuna):
        ax.text(i, v + 0.5, f'{v:,.0f}', ha='center', fontsize=10)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'empresas_por_comuna.png', dpi=300, bbox_inches='tight')
    plt.close()

def analisis_rubros_economicos(df):
    """Analiza y grafica la distribución por rubros económicos."""
    # Agrupar por rubros
    rubros = df.groupby('Rubro economico')['Número de empresas'].sum().sort_values(ascending=False)
    
    # Extraer el código del rubro (primera letra) y la descripción
    rubros_clean = pd.DataFrame({
        'codigo': rubros.index.str[0],
        'descripcion': rubros.index.str[4:],
        'empresas': rubros.values
    })
    
    # Gráfico de pie chart
    plt.figure(figsize=(14, 12))
    
    # Si hay muchos rubros, mostrar solo los top 10
    if len(rubros_clean) > 10:
        top_rubros = rubros_clean.iloc[:10].copy()
        otros = pd.DataFrame({
            'codigo': [''],
            'descripcion': ['Otros rubros'],
            'empresas': [rubros_clean.iloc[10:]['empresas'].sum()]
        })
        rubros_plot = pd.concat([top_rubros, otros])
    else:
        rubros_plot = rubros_clean
    
    # Crear etiquetas para el gráfico
    labels = [f"{row['codigo']} - {row['descripcion'][:30]}..." if len(row['descripcion']) > 30 else f"{row['codigo']} - {row['descripcion']}" 
              for _, row in rubros_plot.iterrows()]
    sizes = rubros_plot['empresas']
    
    # Pie chart con porcentajes
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
            textprops={'fontsize': 12}, wedgeprops=dict(width=0.5), pctdistance=0.85)
    plt.axis('equal')
    
    plt.title('Distribución de Empresas por Rubro Económico\nen la Región de Los Ríos', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'empresas_por_rubro.png', dpi=300, bbox_inches='tight')
    plt.close()

def analisis_trabajadores(df):
    """Analiza y grafica la distribución de trabajadores por género."""
    # Filtrar filas con datos de trabajadores
    df_trab = df.copy()
    
    # Sumar trabajadores por comuna y género
    trabajadores_comuna = df_trab.groupby('Comuna del domicilio o casa matriz').agg({
        'Número de trabajadores dependientes de género femenino informados': 'sum',
        'Número de trabajadores dependientes de género masculino informados': 'sum'
    }).fillna(0)
    
    # Renombrar columnas para facilitar la manipulación
    trabajadores_comuna.columns = ['Femenino', 'Masculino']
    
    # Ordenar por total de trabajadores
    trabajadores_comuna['Total'] = trabajadores_comuna['Femenino'] + trabajadores_comuna['Masculino']
    trabajadores_comuna = trabajadores_comuna.sort_values('Total', ascending=False)
    
    # Gráfico de barras apiladas
    plt.figure(figsize=(14, 10))
    trabajadores_comuna[['Femenino', 'Masculino']].plot(kind='bar', stacked=True, 
                                                       color=['#9b59b6', '#3498db'])
    
    plt.title('Distribución de Trabajadores por Género y Comuna\nen la Región de Los Ríos', 
              fontsize=16, fontweight='bold')
    plt.xlabel('Comuna', fontsize=14)
    plt.ylabel('Número de Trabajadores', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend(fontsize=12)
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'trabajadores_por_genero_comuna.png', dpi=300, bbox_inches='tight')
    plt.close()

def analisis_evolucion_temporal(df):
    """Analiza y grafica la evolución temporal de las empresas por año."""
    # Agrupar por año
    evolucion = df.groupby('Año Comercial').agg({
        'Número de empresas': 'sum',
        'Número de trabajadores dependientes informados': 'sum'
    }).fillna(0)
    
    # Graficar evolución temporal
    fig, ax1 = plt.subplots(figsize=(14, 8))
    
    # Línea para empresas (eje izquierdo)
    color = '#2980b9'
    ax1.set_xlabel('Año', fontsize=14)
    ax1.set_ylabel('Número de Empresas', fontsize=14, color=color)
    ax1.plot(evolucion.index, evolucion['Número de empresas'], marker='o', 
             linewidth=3, markersize=8, color=color, label='Empresas')
    ax1.tick_params(axis='y', labelcolor=color)
    
    # Línea para trabajadores (eje derecho)
    ax2 = ax1.twinx()
    color = '#e74c3c'
    ax2.set_ylabel('Número de Trabajadores', fontsize=14, color=color)
    ax2.plot(evolucion.index, evolucion['Número de trabajadores dependientes informados'], 
             marker='s', linewidth=3, markersize=8, color=color, label='Trabajadores')
    ax2.tick_params(axis='y', labelcolor=color)
    
    # Título y leyenda
    plt.title('Evolución Temporal de Empresas y Trabajadores\nen la Región de Los Ríos', 
              fontsize=16, fontweight='bold')
    
    # Añadir leyendas combinadas
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='upper left', fontsize=12)
    
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / 'evolucion_temporal.png', dpi=300, bbox_inches='tight')
    plt.close()

def generar_reporte_estadisticas(df):
    """Genera un reporte con estadísticas clave de la región."""
    # Calcular estadísticas generales
    total_empresas = df['Número de empresas'].sum()
    total_trabajadores = df['Número de trabajadores dependientes informados'].sum()
    total_comunas = df['Comuna del domicilio o casa matriz'].nunique()
    total_rubros = df['Rubro economico'].nunique()
    
    # Empresas por provincia
    empresas_provincia = df.groupby('Provincia del domicilio o casa matriz')['Número de empresas'].sum()
    
    # Crear un reporte HTML
    html_report = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Reporte Estadístico - Región de Los Ríos</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
            h1 {{ color: #2c3e50; text-align: center; margin-bottom: 30px; }}
            h2 {{ color: #3498db; border-bottom: 1px solid #eee; padding-bottom: 10px; }}
            .stats-container {{ display: flex; flex-wrap: wrap; justify-content: space-between; margin: 30px 0; }}
            .stat-box {{ width: 48%; background-color: #f9f9f9; border-radius: 8px; padding: 20px; 
                      margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 24px; font-weight: bold; color: #2c3e50; }}
            .stat-label {{ font-size: 16px; color: #7f8c8d; }}
            table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
            th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
            th {{ background-color: #3498db; color: white; }}
            tr:nth-child(even) {{ background-color: #f2f2f2; }}
            .footer {{ margin-top: 50px; text-align: center; color: #7f8c8d; font-size: 14px; }}
        </style>
    </head>
    <body>
        <h1>Reporte Estadístico - Región de Los Ríos</h1>
        
        <h2>Estadísticas Generales</h2>
        <div class="stats-container">
            <div class="stat-box">
                <div class="stat-value">{total_empresas:,.0f}</div>
                <div class="stat-label">Total de Empresas</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_trabajadores:,.0f}</div>
                <div class="stat-label">Total de Trabajadores</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_comunas}</div>
                <div class="stat-label">Comunas</div>
            </div>
            <div class="stat-box">
                <div class="stat-value">{total_rubros}</div>
                <div class="stat-label">Rubros Económicos</div>
            </div>
        </div>
        
        <h2>Distribución por Provincia</h2>
        <table>
            <tr>
                <th>Provincia</th>
                <th>Número de Empresas</th>
                <th>Porcentaje</th>
            </tr>
    """
    
    # Añadir filas de la tabla de provincias
    for provincia, empresas in empresas_provincia.items():
        porcentaje = (empresas / total_empresas) * 100
        html_report += f"""
            <tr>
                <td>{provincia}</td>
                <td>{empresas:,.0f}</td>
                <td>{porcentaje:.1f}%</td>
            </tr>
        """
    
    # Completar el HTML
    html_report += """
        </table>
        
        <div class="footer">
            <p>Generado automáticamente a partir del dataset PUB_COMU_RUBR.csv</p>
            <p>Fecha: 26 de julio de 2025</p>
        </div>
    </body>
    </html>
    """
    
    # Guardar el reporte
    with open(OUTPUT_DIR / 'reporte_estadistico.html', 'w', encoding='utf-8') as f:
        f.write(html_report)

def main():
    print(f"Leyendo archivo procesado de la Región de Los Ríos: {INPUT_FILE}")
    
    # Verificar si el archivo existe
    if not os.path.exists(INPUT_FILE):
        print(f"Error: El archivo {INPUT_FILE} no existe.")
        print("Primero ejecute el script filtrar_region_los_rios.py")
        return
    
    # Leer el archivo CSV procesado
    df = pd.read_csv(INPUT_FILE)
    
    # Limpiar columnas numéricas
    df = clean_numeric_columns(df)
    
    print(f"Dimensiones del dataset filtrado: {df.shape}")
    
    # Realizar análisis
    print("Generando análisis de empresas por comuna...")
    analisis_empresas_por_comuna(df)
    
    print("Generando análisis de rubros económicos...")
    analisis_rubros_economicos(df)
    
    print("Generando análisis de trabajadores por género...")
    analisis_trabajadores(df)
    
    print("Generando análisis de evolución temporal...")
    analisis_evolucion_temporal(df)
    
    print("Generando reporte estadístico...")
    generar_reporte_estadisticas(df)
    
    print(f"Análisis completado. Los resultados se guardaron en: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
