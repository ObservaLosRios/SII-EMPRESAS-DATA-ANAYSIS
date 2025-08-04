# 📊 SII Empresas Data Analysis

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![ETL](https://img.shields.io/badge/ETL-Pipeline-orange)](https://github.com/ObservaLosRios/SII-EMPRESAS-DATA-ANAYSIS)
[![License](https://img.shields.io/badge/License-MIT-red)](LICENSE)

## 🎯 Descripción

Sistema de análisis empresarial para el procesamiento y visualización de datos del **Servicio de Impuestos Internos (SII)** de Chile, enfocado en la región Los Ríos. Incluye pipeline ETL completo, validación de datos y dashboard interactivo.

### ✨ Características

- 🔄 **Pipeline ETL**: Extracción, transformación y carga automatizada
- 📊 **Dashboard Interactivo**: Visualizaciones web con Plotly.js  
- ✅ **Validación de Datos**: Sistema de calidad y consistencia
- 📈 **Análisis Temporal**: Evolución empresarial 2005-2023
- 🗺️ **Análisis Geoespacial**: Distribución por comunas
- 📋 **Análisis Sectorial**: Composición por rubros económicos

## 📁 Estructura del Proyecto

```
sii-empresas-data-analysis/
├── src/                           # Código fuente
│   ├── etl/                       # Pipeline ETL
│   ├── data_models/               # Modelos de datos
│   ├── validators/                # Validadores
│   └── utils/                     # Utilidades
├── data/                          # Datos
│   ├── raw/                       # Datos originales SII
│   ├── processed/                 # Datos procesados
│   └── output/                    # Resultados y visualizaciones
├── docs/                          # Dashboard HTML interactivo
│   ├── index.html                 # Dashboard principal
│   ├── custom-styles.css          # Estilos personalizados
│   └── interactive.js             # Funciones JavaScript
├── notebooks/                     # Análisis exploratorio Jupyter
├── scripts/                       # Scripts de procesamiento
├── config/                        # Configuraciones YAML
├── tests/                         # Pruebas unitarias
├── logs/                          # Logs del sistema
├── main.py                        # Script principal
├── demo.py                        # Script de demostración
├── requirements.txt               # Dependencias Python
└── pyproject.toml                 # Configuración del proyecto
```

## 🚀 Instalación

### Requisitos
- Python 3.8+
- 8GB RAM recomendado

### Instalación Rápida
```bash
# Clonar repositorio
git clone https://github.com/ObservaLosRios/SII-EMPRESAS-DATA-ANAYSIS.git
cd SII-EMPRESAS-DATA-ANAYSIS

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# Instalar dependencias
pip install -r requirements.txt
```

## 💻 Uso

### Ejecución Básica
```bash
# Ejecutar pipeline completo
python main.py

# Ver opciones disponibles
python main.py --help

# Usar archivo específico
python main.py --input data/raw/mi_archivo.csv
```

### Uso Programático
```python
from src.etl import run_etl_pipeline

# Ejecutar pipeline
results = run_etl_pipeline(
    config_path="config/etl_config.yaml",
    input_file="data/raw/PUB_COMU_RUBR.csv"
)

print(f"Procesados: {results['metadata'].records_processed:,} registros")
```

### Dashboard Interactivo
Abrir `docs/index.html` en el navegador para acceder al dashboard con:
- Distribución empresarial por comuna
- Evolución temporal 2005-2023
- Análisis sectorial por rubros
- Mapas de concentración empresarial

## 🧪 Testing

```bash
# Ejecutar pruebas
pytest

# Con reporte de cobertura
pytest --cov=src --cov-report=html

# Calidad de código
black src/ tests/
flake8 src/ tests/
```

## 📦 Tecnologías

| Componente | Tecnología |
|------------|------------|
| **Lenguaje** | Python 3.8+ |
| **Datos** | Pandas, NumPy |
| **Visualización** | Plotly, Matplotlib |
| **Validación** | Pydantic, Pandera |
| **Testing** | Pytest |
| **Web** | HTML5, CSS3, JavaScript |

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**Bruno San Martín Navarro**  
*Ingeniero en Informática & Científico de Datos*  
*Proyecto Observa UACH*

[![LinkedIn](https://img.shields.io/badge/LinkedIn-sanmabruno-blue)](https://www.linkedin.com/in/sanmabruno/)
[![GitHub](https://img.shields.io/badge/GitHub-SanMaBruno-black)](https://github.com/SanMaBruno/)

---

<div align="center">

**📊 Transformando datos SII en insights estratégicos para Los Ríos**

</div>
