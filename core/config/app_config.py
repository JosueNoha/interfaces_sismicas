"""
Configuraciones específicas para cada país/aplicación.
"""

BOLIVIA_CONFIG = {
    # Información de la norma
    'norma': 'CNBDS 2023',
    'titulo_norma': 'NORMA BOLIVIANA DE DISEÑO SÍSMICO (CNBDS 2023)',
    'pais': 'Bolivia',
    
    # Rutas de recursos
    'template_path': 'apps/bolivia/resources/templates/plantilla_bolivia.ltx',
    'mapa_sismico': 'MapaSismicoBolivia.png',
    'icon_path': 'shared_resources/yabar_logo.ico',
    
    # Parámetros sísmicos por defecto
    'parametros_defecto': {
        'ubicacion': 'La Paz',
        'autor': 'Yabar Ingenieros',
        'proyecto': 'Edificación de Concreto Reforzado',
        'fecha': '05/10/2025',
        'Fa': 1.86,
        'Fv': 0.63,
        'So': 2.9
    },
    
    # Configuración de ventana
    'window_title': 'Análisis Sísmico - Bolivia (CNBDS 2023)',
    
    # Configuración de espectro
    'espectro_config': {
        'archivo_datos': 'espectro_bolivia.txt',
        'formula_To': '0.15 * Fv / Fa',
        'formula_Ts': '0.5 * Fv / Fa', 
        'formula_TL': '4 * Fv / Fa',
        'formula_SDS': '2.5 * Fa * So',
        'formula_SD1': '1.25 * Fv * So'
    },
    
    # Casos de carga sísmica específicos
    'load_cases': {
        'dinamico_x': ['RSX', 'RX'],
        'dinamico_y': ['RSY', 'RY'], 
        'estatico_x': ['SDX', 'SX'],
        'estatico_y': ['SDY', 'SY']
    }
}

PERU_CONFIG = {
    # Información de la norma
    'norma': 'NTC 2023',
    'titulo_norma': 'NORMA TÉCNICA COMPLEMENTARIA PARA EL DISEÑO POR SISMO (NTC 2023)',
    'pais': 'Perú',
    
    # Rutas de recursos
    'template_path': 'apps/peru/resources/templates/plantilla_peru.ltx',
    'mapa_sismico': None,  # Perú no tiene mapa sísmico específico en el código actual
    'icon_path': 'shared_resources/yabar_logo.ico',
    
    # Parámetros sísmicos por defecto
    'parametros_defecto': {
        'ubicacion': 'Lima',
        'autor': 'Yabar Ingenieros',
        'proyecto': 'Edificación de Concreto Reforzado',
        'fecha': '05/10/2025',
        'Z': 0.25,  # Factor de zona para Lima
        'S': 1.20,  # Factor de suelo
        'categoria': 'B',  # Categoría de edificación
        'suelo': 'S1'  # Tipo de suelo
    },
    
    # Configuración de ventana
    'window_title': 'Análisis Sísmico - Perú (NTC 2023)',
    
    # Configuración de espectro (basado en E-030)
    'espectro_config': {
        'archivo_datos': 'espectro_peru.txt',
        'categorias': ['A1', 'A2', 'B', 'C', 'D'],
        'tipos_suelo': ['S0', 'S1', 'S2', 'S3']
    },
    
    # Casos de carga sísmica específicos
    'load_cases': {
        'dinamico_x': ['RSX', 'RX'],
        'dinamico_y': ['RSY', 'RY'],
        'estatico_x': ['SDX', 'SX'], 
        'estatico_y': ['SDY', 'SY']
    }
}

# Función helper para obtener configuración por país
def get_config(pais: str):
    """Obtiene la configuración para el país especificado."""
    configs = {
        'bolivia': BOLIVIA_CONFIG,
        'peru': PERU_CONFIG
    }
    return configs.get(pais.lower())

# Configuración común entre aplicaciones
COMMON_CONFIG = {
    'company_name': 'Yabar Ingenieros',
    'default_image_text': 'Sin Imagen',
    'default_description_text': 'Sin Descripción',
    'default_portada_text': 'Imagen por Defecto',
    
    # Configuración de archivos temporales
    'temp_dirs': ['images', 'out'],
    
    # Configuración de ETABS
    'etabs_connection': {
        'timeout': 30,
        'retry_attempts': 3
    }
}