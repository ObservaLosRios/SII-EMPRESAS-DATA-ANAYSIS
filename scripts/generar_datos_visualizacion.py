#!/usr/bin/env python3
"""
Script para generar datos en formato JSON para las visualizaciones interactivas
"""

import pandas as pd
import json
from pathlib import Path

def limpiar_texto(texto):
    """Limpia caracteres especiales en el texto"""
    if pd.isna(texto):
        return ""
    texto = str(texto)
    replacements = {
        'Ã³': 'ó', 'Ã¡': 'á', 'Ã­': 'í', 'Ã©': 'é', 'Ãº': 'ú',
        'Ã±': 'ñ', 'Ã‰': 'É', 'Ã': 'Á', 'Ã"': 'Ó', 'Ãš': 'Ú',
        'ï»¿AÃ±o': 'Año', 'NÃºmero': 'Número'
    }
    for old, new in replacements.items():
        texto = texto.replace(old, new)
    return texto

def corregir_ventas_uf(valor):
    """Corrige valores extremos en ventas anuales UF"""
    import math
    
    if pd.isna(valor) or valor == 0:
        return valor
    
    if valor > 1000000:
        valor_corregido = math.log10(valor) * 50000
        return min(valor_corregido, 500000)
    elif valor > 100000:
        return valor * 0.7
    else:
        return valor

def main():
    # Definir rutas
    BASE_DIR = Path(__file__).parent.parent
    INPUT_FILE = BASE_DIR / "data" / "processed" / "region_los_rios.csv"
    OUTPUT_DIR = BASE_DIR / "visualizations"
    
    # Crear directorio de salida si no existe
    OUTPUT_DIR.mkdir(exist_ok=True)
    
    print(f"Cargando datos desde: {INPUT_FILE}")
    
    # Cargar datos
    df = pd.read_csv(INPUT_FILE, encoding='utf-8')
    
    # Limpiar nombres de columnas
    df.columns = [limpiar_texto(col) for col in df.columns]
    
    # Limpiar datos específicos
    df['Comuna'] = df['Comuna del domicilio o casa matriz'].apply(limpiar_texto)
    df['Rubro_limpio'] = df['Rubro economico'].apply(limpiar_texto)
    df['Descripcion_rubro'] = df['Rubro_limpio'].str.split(' - ').str[1:].apply(lambda x: ' - '.join(x) if isinstance(x, list) else '')
    
    # Convertir columnas numéricas
    numeric_cols = ['Año Comercial', 'Número de empresas', 'Ventas anuales en UF', 'Número de trabajadores dependientes informados']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Corregir ventas
    if 'Ventas anuales en UF' in df.columns:
        df['Ventas anuales en UF'] = df['Ventas anuales en UF'].apply(corregir_ventas_uf)
    
    # Datos para visualizaciones
    data_viz = {}
    
    # 1. Empresas por comuna
    empresas_por_comuna = df.groupby('Comuna')['Número de empresas'].sum().sort_values(ascending=False)
    total_empresas = empresas_por_comuna.sum()
    
    data_viz['empresas_por_comuna'] = {
        'comunas': empresas_por_comuna.index.tolist(),
        'valores': empresas_por_comuna.values.tolist(),
        'porcentajes': (empresas_por_comuna.values / total_empresas * 100).tolist(),
        'total': int(total_empresas)
    }
    
    # 2. Evolución temporal
    evolucion_temporal = df.groupby('Año Comercial')['Número de empresas'].sum().reset_index()
    evolucion_temporal = evolucion_temporal.sort_values('Año Comercial')
    
    data_viz['evolucion_temporal'] = {
        'años': evolucion_temporal['Año Comercial'].astype(int).tolist(),
        'empresas': evolucion_temporal['Número de empresas'].astype(int).tolist()
    }
    
    # 3. Distribución por rubros
    def abreviar_descripcion(descripcion):
        abreviaciones = {
            'Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas': 'Comercio y reparación automotriz',
            'Agricultura, ganadería, silvicultura y pesca': 'Agricultura y ganadería',
            'Transporte y almacenamiento': 'Transporte y almacenamiento',
            'Actividades de servicios administrativos y de apoyo': 'Servicios administrativos',
            'Construcción': 'Construcción',
            'Actividades inmobiliarias': 'Inmobiliarias',
            'Alojamiento y servicios de comida': 'Hotelería y restaurantes',
            'Industrias manufactureras': 'Industria manufacturera',
            'Información y comunicaciones': 'Información y comunicaciones',
            'Actividades profesionales, científicas y técnicas': 'Servicios profesionales',
            'Enseñanza': 'Enseñanza',
            'Actividades de atención de la salud humana y de asistencia social': 'Atención de salud y asistencia social',
            'Otros servicios': 'Otros servicios'
        }
        return abreviaciones.get(descripcion, descripcion)
    
    rubros_empresas = df.groupby('Descripcion_rubro')['Número de empresas'].sum().sort_values(ascending=False)
    total_empresas_rubros = rubros_empresas.sum()
    
    # Top 10 rubros más "Otros"
    top_10_rubros = rubros_empresas.head(10)
    otros_valor = rubros_empresas.iloc[10:].sum() if len(rubros_empresas) > 10 else 0
    
    rubros_labels = [abreviar_descripcion(rubro) for rubro in top_10_rubros.index]
    rubros_valores = top_10_rubros.values.tolist()
    rubros_porcentajes = (top_10_rubros.values / total_empresas_rubros * 100).tolist()
    
    if otros_valor > 0:
        rubros_labels.append('Otros rubros')
        rubros_valores.append(int(otros_valor))
        rubros_porcentajes.append(otros_valor / total_empresas_rubros * 100)
    
    data_viz['rubros_empresas'] = {
        'labels': rubros_labels,
        'valores': [int(v) for v in rubros_valores],
        'porcentajes': rubros_porcentajes
    }
    
    # 4. Top 15 rubros (barras)
    top_15_rubros = rubros_empresas.head(15)
    data_viz['top_15_rubros'] = {
        'rubros': [abreviar_descripcion(rubro) for rubro in top_15_rubros.index],
        'valores': top_15_rubros.values.astype(int).tolist(),
        'porcentajes': (top_15_rubros.values / total_empresas_rubros * 100).tolist()
    }
    
    # 5. Mapa de calor (top 5 comunas y top 5 rubros)
    top_5_comunas = empresas_por_comuna.head(5).index.tolist()
    top_5_rubros_desc = rubros_empresas.head(5).index.tolist()
    
    # Filtrar datos para mapa de calor
    df_heatmap = df[df['Comuna'].isin(top_5_comunas) & 
                    df['Descripcion_rubro'].isin(top_5_rubros_desc)]
    
    pivot_data = df_heatmap.pivot_table(
        index='Comuna',
        columns='Descripcion_rubro',
        values='Número de empresas',
        aggfunc='sum',
        fill_value=0
    )
    
    # Abreviar nombres para el mapa de calor
    def abreviar_rubro_heatmap(descripcion):
        abreviaciones_heatmap = {
            'Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas': 'Comercio y Reparación Automotriz',
            'Agricultura, ganadería, silvicultura y pesca': 'Agricultura y Ganadería',
            'Transporte y almacenamiento': 'Transporte y Almacenamiento',
            'Actividades de servicios administrativos y de apoyo': 'Servicios Administrativos',
            'Construcción': 'Construcción'
        }
        return abreviaciones_heatmap.get(descripcion, descripcion)
    
    data_viz['mapa_calor'] = {
        'comunas': pivot_data.index.tolist(),
        'rubros': [abreviar_rubro_heatmap(col) for col in pivot_data.columns],
        'valores': pivot_data.values.astype(int).tolist()
    }
    
    # 6. Barras apiladas (composición por comuna)
    df_stacked = df_heatmap.groupby(['Comuna', 'Descripcion_rubro'])['Número de empresas'].sum().unstack(fill_value=0)
    df_stacked_pct = df_stacked.div(df_stacked.sum(axis=1), axis=0) * 100
    
    data_viz['barras_apiladas'] = {
        'comunas': df_stacked_pct.index.tolist(),
        'rubros': [abreviar_rubro_heatmap(col) for col in df_stacked_pct.columns],
        'porcentajes': df_stacked_pct.values.tolist()
    }
    
    # 7. Gráfico de radar (top 3 comunas)
    top_3_comunas = empresas_por_comuna.head(3).index.tolist()
    
    radar_data = df[df['Comuna'].isin(top_3_comunas)].groupby('Comuna').agg({
        'Número de empresas': 'sum',
        'Ventas anuales en UF': lambda x: pd.to_numeric(x, errors='coerce').sum(),
        'Número de trabajadores dependientes informados': lambda x: pd.to_numeric(x, errors='coerce').sum(),
    }).reset_index()
    
    # Normalizar datos
    radar_data_norm = radar_data.set_index('Comuna')
    for col in radar_data_norm.columns:
        radar_data_norm[col] = radar_data_norm[col] / radar_data_norm[col].max()
    
    data_viz['radar'] = {
        'comunas': radar_data_norm.index.tolist(),
        'indicadores': ['Número de empresas', 'Ventas anuales (UF)', 'Número de trabajadores'],
        'valores': radar_data_norm.values.tolist()
    }
    
    # 8. Tendencias temporales múltiples
    tendencias_anuales = df.groupby('Año Comercial').agg({
        'Número de empresas': 'sum',
        'Ventas anuales en UF': 'sum',
        'Número de trabajadores dependientes informados': 'sum'
    }).reset_index()
    
    data_viz['tendencias_multiples'] = {
        'años': tendencias_anuales['Año Comercial'].astype(int).tolist(),
        'empresas': tendencias_anuales['Número de empresas'].astype(int).tolist(),
        'ventas': tendencias_anuales['Ventas anuales en UF'].fillna(0).astype(int).tolist(),
        'trabajadores': tendencias_anuales['Número de trabajadores dependientes informados'].fillna(0).astype(int).tolist()
    }
    
    # Estadísticas adicionales
    data_viz['estadisticas'] = {
        'total_empresas': int(total_empresas),
        'total_comunas': len(empresas_por_comuna),
        'total_rubros': len(rubros_empresas),
        'periodo': {
            'inicio': int(df['Año Comercial'].min()),
            'fin': int(df['Año Comercial'].max())
        }
    }
    
    # Guardar datos en JSON
    output_file = OUTPUT_DIR / "datos_visualizacion.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data_viz, f, ensure_ascii=False, indent=2)
    
    print(f"Datos generados y guardados en: {output_file}")
    print(f"Total de empresas: {total_empresas:,.0f}")
    print(f"Comunas analizadas: {len(empresas_por_comuna)}")
    print(f"Período: {int(df['Año Comercial'].min())}-{int(df['Año Comercial'].max())}")

if __name__ == "__main__":
    main()
