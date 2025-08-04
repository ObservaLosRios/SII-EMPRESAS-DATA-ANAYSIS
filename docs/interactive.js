// Funcionalidades interactivas para el análisis de la Región de Los Ríos
// JavaScript para mejorar la experiencia del usuario

document.addEventListener('DOMContentLoaded', function() {
    
    // Agregar header personalizado
    addCustomHeader();
    
    // Agregar controles interactivos
    addInteractiveControls();
    
    // Mejorar las visualizaciones de Plotly
    enhancePlotlyGraphs();
    
    // Agregar funcionalidad de smooth scroll
    addSmoothScrolling();
    
    // Agregar footer personalizado
    addCustomFooter();
    
    // Inicializar efectos visuales
    initializeVisualEffects();
    
    console.log('✅ Análisis de Los Ríos cargado exitosamente');
});

function addCustomHeader() {
    const header = document.createElement('div');
    header.className = 'custom-header';
    header.innerHTML = `
        <h1>📊 Análisis de Empresas SII</h1>
        <p>Región de Los Ríos - Chile</p>
    `;
    
    // Insertar al inicio del documento
    const firstCell = document.querySelector('.jp-Cell');
    if (firstCell) {
        firstCell.parentNode.insertBefore(header, firstCell);
    }
}

function addInteractiveControls() {
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'interactive-controls';
    controlsDiv.innerHTML = `
        <h3>🎛️ Controles Interactivos</h3>
        <button class="btn" onclick="toggleAllGraphs()">👁️ Mostrar/Ocultar Gráficos</button>
        <button class="btn" onclick="exportData()">💾 Exportar Datos</button>
        <button class="btn" onclick="generateReport()">📋 Generar Reporte</button>
        <button class="btn" onclick="scrollToTop()">⬆️ Ir al Inicio</button>
    `;
    
    // Insertar después del header
    const header = document.querySelector('.custom-header');
    if (header) {
        header.parentNode.insertBefore(controlsDiv, header.nextSibling);
    }
}

function enhancePlotlyGraphs() {
    // Mejorar todos los gráficos de Plotly
    const plotlyDivs = document.querySelectorAll('.plotly-graph-div');
    
    plotlyDivs.forEach((div, index) => {
        // Agregar título descriptivo si no existe
        if (!div.previousElementSibling || !div.previousElementSibling.classList.contains('graph-title')) {
            const title = document.createElement('div');
            title.className = 'graph-title';
            title.style.cssText = `
                text-align: center;
                font-size: 1.2rem;
                font-weight: bold;
                margin: 20px 0 10px 0;
                color: var(--primary-color);
                border-bottom: 2px solid var(--accent-color);
                padding-bottom: 10px;
            `;
            
            const titles = [
                '🏢 Distribución de Empresas por Comuna',
                '📈 Evolución Temporal del Número de Empresas', 
                '🥧 Distribución por Rubro Económico',
                '🔥 Mapa de Calor: Comunas vs Rubros',
                '📊 Composición Porcentual por Comuna'
            ];
            
            title.textContent = titles[index] || `Gráfico ${index + 1}`;
            div.parentNode.insertBefore(title, div);
        }
        
        // Agregar funcionalidad de descarga
        const downloadBtn = document.createElement('button');
        downloadBtn.className = 'btn';
        downloadBtn.style.cssText = 'margin: 10px; font-size: 12px;';
        downloadBtn.innerHTML = '📸 Descargar Gráfico';
        downloadBtn.onclick = () => downloadPlotlyGraph(div, index);
        
        div.parentNode.insertBefore(downloadBtn, div.nextSibling);
    });
}

function addSmoothScrolling() {
    // Agregar navegación por secciones
    const navDiv = document.createElement('div');
    navDiv.id = 'section-nav';
    navDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        z-index: 1000;
        max-width: 200px;
    `;
    
    navDiv.innerHTML = `
        <h4 style="margin: 0 0 10px 0; color: var(--primary-color);">📑 Navegación</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <li><a href="#comunas" class="nav-link">🏢 Por Comunas</a></li>
            <li><a href="#temporal" class="nav-link">📈 Evolución</a></li>
            <li><a href="#rubros" class="nav-link">🥧 Por Rubros</a></li>
            <li><a href="#heatmap" class="nav-link">🔥 Mapa Calor</a></li>
            <li><a href="#composicion" class="nav-link">📊 Composición</a></li>
        </ul>
    `;
    
    document.body.appendChild(navDiv);
    
    // Agregar IDs a las secciones
    const graphs = document.querySelectorAll('.plotly-graph-div');
    const ids = ['comunas', 'temporal', 'rubros', 'heatmap', 'composicion'];
    graphs.forEach((graph, index) => {
        if (ids[index]) {
            graph.id = ids[index];
        }
    });
    
    // Estilo para los links de navegación
    const style = document.createElement('style');
    style.textContent = `
        .nav-link {
            display: block;
            padding: 5px 0;
            color: var(--primary-color);
            text-decoration: none;
            font-size: 14px;
            transition: color 0.3s ease;
        }
        .nav-link:hover {
            color: var(--accent-color);
            text-decoration: underline;
        }
    `;
    document.head.appendChild(style);
}

function addCustomFooter() {
    const footer = document.createElement('div');
    footer.className = 'custom-footer';
    footer.innerHTML = `
        <p>📊 Análisis desarrollado con datos del Servicio de Impuestos Internos (SII) de Chile</p>
        <p>🌊 Región de Los Ríos - ${new Date().getFullYear()}</p>
        <p style="margin-top: 15px; font-size: 12px;">
            Generado automáticamente desde Jupyter Notebook con nbconvert
        </p>
    `;
    document.body.appendChild(footer);
}

function initializeVisualEffects() {
    // Efecto de aparición progresiva para las celdas
    const cells = document.querySelectorAll('.jp-Cell');
    cells.forEach((cell, index) => {
        cell.style.opacity = '0';
        cell.style.transform = 'translateY(20px)';
        cell.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        
        setTimeout(() => {
            cell.style.opacity = '1';
            cell.style.transform = 'translateY(0)';
        }, index * 200);
    });
}

// Funciones interactivas
function toggleAllGraphs() {
    const graphs = document.querySelectorAll('.plotly-graph-div');
    const isHidden = graphs[0] && graphs[0].style.display === 'none';
    
    graphs.forEach(graph => {
        graph.style.display = isHidden ? 'block' : 'none';
    });
    
    showNotification(isHidden ? '👁️ Gráficos mostrados' : '🙈 Gráficos ocultados');
}

function exportData() {
    // Simular exportación de datos
    showLoading('Exportando datos...');
    
    setTimeout(() => {
        const dataText = `
Datos de Empresas - Región de Los Ríos
=====================================
Fecha de exportación: ${new Date().toLocaleDateString()}

Este archivo contendría los datos procesados del análisis.
En una implementación real, aquí se exportarían los datos
en formato CSV, JSON o Excel.
        `;
        
        downloadTextFile(dataText, 'datos_region_los_rios.txt');
        hideLoading();
        showNotification('💾 Datos exportados exitosamente');
    }, 2000);
}

function generateReport() {
    showLoading('Generando reporte...');
    
    setTimeout(() => {
        const reportHTML = `
<!DOCTYPE html>
<html>
<head>
    <title>Reporte - Análisis Región de Los Ríos</title>
    <style>
        body { font-family: Georgia, serif; margin: 40px; line-height: 1.6; }
        h1 { color: #1B4F72; border-bottom: 3px solid #DC143C; padding-bottom: 10px; }
        .summary { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; }
    </style>
</head>
<body>
    <h1>📊 Reporte de Análisis - Región de Los Ríos</h1>
    <div class="summary">
        <h2>📋 Resumen Ejecutivo</h2>
        <p><strong>Fecha:</strong> ${new Date().toLocaleDateString()}</p>
        <p><strong>Fuente:</strong> Servicio de Impuestos Internos (SII)</p>
        <p><strong>Alcance:</strong> Análisis de empresas registradas en la Región de Los Ríos</p>
        
        <h3>🎯 Hallazgos Principales</h3>
        <ul>
            <li>Valdivia concentra la mayor cantidad de empresas de la región</li>
            <li>El sector comercio y reparación automotriz es predominante</li>
            <li>Se observa crecimiento en el número de empresas registradas</li>
            <li>Diversificación sectorial equilibrada en las principales comunas</li>
        </ul>
        
        <h3>💡 Recomendaciones</h3>
        <ul>
            <li>Fomentar el desarrollo empresarial en comunas con menor concentración</li>
            <li>Diversificar la matriz productiva regional</li>
            <li>Implementar programas de apoyo a PYMES</li>
        </ul>
    </div>
</body>
</html>
        `;
        
        downloadTextFile(reportHTML, 'reporte_los_rios.html');
        hideLoading();
        showNotification('📋 Reporte generado exitosamente');
    }, 3000);
}

function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
    showNotification('⬆️ Volviendo al inicio');
}

function downloadPlotlyGraph(graphDiv, index) {
    showNotification('📸 Preparando descarga del gráfico...');
    
    // En una implementación real, aquí se usaría Plotly.downloadImage()
    // Por ahora, mostramos una notificación
    setTimeout(() => {
        showNotification(`📸 Gráfico ${index + 1} descargado (simulado)`);
    }, 1500);
}

// Funciones de utilidad
function showNotification(message) {
    // Remover notificación anterior si existe
    const existingNotification = document.querySelector('.notification');
    if (existingNotification) {
        existingNotification.remove();
    }
    
    const notification = document.createElement('div');
    notification.className = 'notification';
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--primary-color);
        color: white;
        padding: 15px 30px;
        border-radius: 25px;
        z-index: 2000;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        font-family: var(--font-family);
        animation: slideDown 0.3s ease;
    `;
    notification.textContent = message;
    
    // Agregar animación CSS
    if (!document.querySelector('#notification-styles')) {
        const style = document.createElement('style');
        style.id = 'notification-styles';
        style.textContent = `
            @keyframes slideDown {
                from { transform: translateX(-50%) translateY(-100%); opacity: 0; }
                to { transform: translateX(-50%) translateY(0); opacity: 1; }
            }
        `;
        document.head.appendChild(style);
    }
    
    document.body.appendChild(notification);
    
    // Remover después de 3 segundos
    setTimeout(() => {
        notification.style.animation = 'slideDown 0.3s ease reverse';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

function showLoading(message) {
    const loading = document.createElement('div');
    loading.id = 'loading-overlay';
    loading.className = 'loading';
    loading.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        z-index: 3000;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    `;
    loading.innerHTML = `
        <div class="spinner"></div>
        <p style="margin-top: 20px; font-size: 1.1rem;">${message}</p>
    `;
    document.body.appendChild(loading);
}

function hideLoading() {
    const loading = document.querySelector('#loading-overlay');
    if (loading) {
        loading.remove();
    }
}

function downloadTextFile(content, filename) {
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(content));
    element.setAttribute('download', filename);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
}

// Mejorar la accesibilidad
document.addEventListener('keydown', function(e) {
    // Atajos de teclado
    if (e.ctrlKey || e.metaKey) {
        switch(e.key) {
            case 'h':
                e.preventDefault();
                toggleAllGraphs();
                break;
            case 'e':
                e.preventDefault();
                exportData();
                break;
            case 'r':
                e.preventDefault();
                generateReport();
                break;
        }
    }
    
    // Escape para ir al inicio
    if (e.key === 'Escape') {
        scrollToTop();
    }
});

// Mostrar atajos de teclado
setTimeout(() => {
    showNotification('💡 Atajos: Ctrl+H (gráficos), Ctrl+E (exportar), Ctrl+R (reporte), Esc (inicio)');
}, 5000);
