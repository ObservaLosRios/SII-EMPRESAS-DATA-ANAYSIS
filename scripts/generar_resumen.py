"""
Script para generar un resumen de los datos de la Región de Los Ríos
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import os
from pathlib import Path

# Configuración para visualizaciones
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.family'] = 'Georgia'
plt.rcParams['figure.figsize'] = (12, 8)

# Definir rutas
BASE_DIR = Path(__file__).parents[1]
DATA_FILE = BASE_DIR / "data" / "processed" / "region_los_rios.csv"
OUTPUT_DIR = BASE_DIR / "data" / "output"

# Crear directorio de salida si no existe
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"Cargando datos: {DATA_FILE}")

# Cargar los datos procesados
df = pd.read_csv(DATA_FILE)

# Verificar datos cargados
print(f"Dimensiones del dataset: {df.shape}")
print("\nPrimeras filas:")
print(df.head())

# Convertir las columnas numéricas
numeric_columns = [
    'Año Comercial', 
    'Número de empresas',
    'Ventas anuales en UF',
    'Número de trabajadores dependientes informados',
    'Renta neta informada en UF'
]

# Convertir a formato numérico
for col in numeric_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# 1. Resumen por comuna
comunas_summary = df.groupby('Comuna del domicilio o casa matriz')['Número de empresas'].sum().sort_values(ascending=False)
print("\n--- Resumen por Comuna ---")
print(comunas_summary)

# Guardar como CSV
comunas_summary.to_csv(OUTPUT_DIR / "resumen_comunas.csv")

# 2. Evolución temporal
evolucion = df.groupby('Año Comercial').agg({
    'Número de empresas': 'sum',
    'Ventas anuales en UF': 'sum',
    'Número de trabajadores dependientes informados': 'sum'
})

print("\n--- Evolución Temporal ---")
print(evolucion)

# Guardar como CSV
evolucion.to_csv(OUTPUT_DIR / "evolucion_temporal.csv")

# 3. Resumen por rubro económico
rubros_summary = df.groupby('Rubro economico')['Número de empresas'].sum().sort_values(ascending=False)
top_rubros = rubros_summary.head(10)

print("\n--- Top 10 Rubros Económicos ---")
print(top_rubros)

# Guardar como CSV
rubros_summary.to_csv(OUTPUT_DIR / "resumen_rubros.csv")

# Crear visualizaciones con Plotly

# 1. Distribución por comuna
fig = px.bar(
    x=comunas_summary.values,
    y=comunas_summary.index,
    orientation='h',
    labels={'x': 'Número de Empresas', 'y': 'Comuna'},
    title='Número de Empresas por Comuna en la Región de Los Ríos'
)

# Aplicar estilo
fig.update_layout(
    font=dict(family='Georgia, serif', color='#1e293b'),
    title=dict(font=dict(size=18, family='Georgia, serif', color='#1e293b'), x=0.01),
    paper_bgcolor='white',
    plot_bgcolor='white'
)

# Guardar como HTML
fig.write_html(OUTPUT_DIR / "distribucion_comunas.html")
print(f"Gráfico guardado en: {OUTPUT_DIR / 'distribucion_comunas.html'}")

# 2. Evolución temporal
fig = px.line(
    evolucion.reset_index(),
    x='Año Comercial',
    y='Número de empresas',
    markers=True,
    labels={'Año Comercial': 'Año', 'Número de empresas': 'Número de Empresas'},
    title='Evolución del Número de Empresas en la Región de Los Ríos'
)

# Aplicar estilo
fig.update_layout(
    font=dict(family='Georgia, serif', color='#1e293b'),
    title=dict(font=dict(size=18, family='Georgia, serif', color='#1e293b'), x=0.01),
    paper_bgcolor='white',
    plot_bgcolor='white'
)

# Guardar como HTML
fig.write_html(OUTPUT_DIR / "evolucion_temporal.html")
print(f"Gráfico guardado en: {OUTPUT_DIR / 'evolucion_temporal.html'}")

# 3. Distribución por rubro
fig = px.pie(
    values=top_rubros.values,
    names=top_rubros.index,
    title='Top 10 Rubros Económicos en la Región de Los Ríos'
)

# Aplicar estilo
fig.update_layout(
    font=dict(family='Georgia, serif', color='#1e293b'),
    title=dict(font=dict(size=18, family='Georgia, serif', color='#1e293b'), x=0.01),
    paper_bgcolor='white',
    plot_bgcolor='white'
)

# Guardar como HTML
fig.write_html(OUTPUT_DIR / "distribucion_rubros.html")
print(f"Gráfico guardado en: {OUTPUT_DIR / 'distribucion_rubros.html'}")

print("\nResumen generado exitosamente.")
