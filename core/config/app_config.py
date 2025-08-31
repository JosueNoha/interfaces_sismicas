"""
Configuraciones actualizadas específicas para cada país/aplicación.
"""

BOLIVIA_CONFIG = {
    # Información de la norma
    'norma': 'CNBDS 2023',
    'titulo_norma': 'NORMA BOLIVIANA DE DISEÑO SÍSMICO (CNBDS 2023)',
    'pais': 'Bolivia',
    
    # Rutas de recursos
    'template_path': 'apps/bolivia/resources/templates/plantilla_bolivia.ltx',
    'mapa_sismico': 'mapa_sismico_bolivia.png',
    'icon_path': 'shared/resources/yabar_logo.ico',
    
    # Parámetros sísmicos por defecto
    'parametros_defecto': {
        'ubicacion': 'La Paz',
        'autor': 'Yabar Ingenieros', 
        'proyecto': 'Edificación de Concreto Reforzado',
        'fecha': '27/08/2025',
        'Fa': 1.86,  # Factor de amplificación periodo corto
        'Fv': 2.64,  # Factor de amplificación periodo largo
        'So': 2.9,   # Valor del espectro en roca
        'I': 1.0,    # Factor de importancia (Ie) - Bolivia SÍ usa I
        'R': 8.0,    # Factor de reducción - Pórticos especiales
        'categoria_suelo': 'S2',
        'categoria_edificacion': 'Tipo II - Uso habitual'
    },
    
    # Configuración de ventana
    'window_title': 'Análisis Sísmico - Bolivia (CNBDS 2023)',
    
    # Configuración de espectro según CNBDS 2023
    'espectro_config': {
        'archivo_datos': 'espectro_bolivia.txt',
        'formula_To': '0.15 * Fv / Fa',
        'formula_Ts': '0.5 * Fv / Fa', 
        'formula_TL': '4 * Fv / Fa',
        'formula_SDS': '2.5 * Fa * So',
        'formula_SD1': '1.25 * Fv * So',
        'categorias': ['A', 'B', 'C', 'D'],
        'rangos_fa': (0.8, 3.0),
        'rangos_fv': (0.6, 2.5),
        'rangos_so': (0.1, 4.0)
    },
    
    # Casos de carga sísmica específicos
    'load_cases': {
        'dinamico_x': ['RSX', 'RX'],
        'dinamico_y': ['RSY', 'RY'], 
        'estatico_x': ['SDX', 'SX'],
        'estatico_y': ['SDY', 'SY']
    },
    
    # Configuración de parámetros UI
    'parametros_ui': {
        'mostrar_mapa': True,
        'validaciones_estrictas': True,
        'precision_decimales': 2
    }
}

PERU_CONFIG = {
    # Información de la norma
    'norma': 'E.030',
    'titulo_norma': 'NORMA TÉCNICA E.030 DISEÑO SISMORRESISTENTE',
    'pais': 'Perú',
    
    # Rutas de recursos
    'template_path': 'apps/peru/resources/templates/plantilla_peru.ltx',
    'mapa_sismico': None,  # Perú no tiene mapa específico implementado
    'icon_path': 'shared/resources/yabar_logo.ico',
    
    # Parámetros sísmicos por defecto
    'parametros_defecto': {
        'ubicacion': 'Lima',
        'autor': 'Yabar Ingenieros',
        'proyecto': 'Edificación de Concreto Reforzado', 
        'fecha': '27/08/2025',
        'Z': 0.25,  # Factor de zona para Lima
        'U': 1.0,   # Factor de uso - Perú usa U, no I
        'S': 1.20,  # Factor de suelo S1
        'Tp': 0.6,  # Período que define meseta del espectro
        'Tl': 2.0,  # Período que define inicio rama descendente
        'R': 8.0,   # Factor de reducción - Pórticos especiales
        'suelo': 'S1',
        'categoria': 'C - Comunes'
    },
    
    # Configuración de ventana
    'window_title': 'Análisis Sísmico - Perú (E.030)',
    
    # Configuración de espectro según E.030
    'espectro_config': {
        'archivo_datos': 'espectro_peru.txt',
        'categorias': ['A1 - Esenciales', 'A2 - Importantes', 'B - Comunes', 'C - Menores'],
        'tipos_suelo': ['S0', 'S1', 'S2', 'S3'],
        'zonas_sismicas': {
            'Zona 1': 0.10,
            'Zona 2': 0.25,
            'Zona 3': 0.35,
            'Zona 4': 0.45
        },
        'factores_uso': {
            'A1 - Esenciales': 1.5,
            'A2 - Importantes': 1.3,
            'B - Comunes': 1.0,
            'C - Menores': 0.8
        },
        'rangos_z': (0.10, 0.45),
        'rangos_s': (0.80, 2.00),
        'rangos_tp': (0.4, 1.0),
        'rangos_tl': (1.5, 3.0)
    },
    
    # Casos de carga sísmica específicos E.030
    'load_cases': {
        'dinamico_x': ['RSX', 'RX', 'SPECX'],
        'dinamico_y': ['RSY', 'RY', 'SPECY'],
        'estatico_x': ['SDX', 'SX', 'ESTATICOX'], 
        'estatico_y': ['SDY', 'SY', 'ESTATICOY']
    },
    
    # Configuración de parámetros UI
    'parametros_ui': {
        'mostrar_zonas': True,
        'mostrar_categorias': True,
        'validaciones_estrictas': True,
        'precision_decimales': 3
    }
}

# Configuración común para ambos países
COMMON_CONFIG = {
    # Configuración de reporte
    'reporte_config': {
        'formato_fecha': '%d/%m/%Y',
        'incluir_graficos': True,
        'incluir_tablas': True,
        'incluir_imagenes': True,
        'latex_compiler': 'pdflatex',
        'ejecutar_dos_veces': True
    },
    
    # Configuración de ETABS
    'etabs_config': {
        'unidades_fuerza': ['N', 'kN', 'tonf', 'kgf'],
        'unidades_longitud': ['mm', 'cm', 'm'],
        'precision_modal': 4,
        'precision_fuerzas': 2,
        'precision_desplazamientos': 4
    },
    
    # Configuración de validaciones
    'validaciones': {
        'verificar_masa_participativa': True,
        'minimo_masa_participativa': 90.0,
        'verificar_periodo_fundamental': True,
        'verificar_cortante_minima': True
    }
}


def get_config(pais: str):
    """
    Obtiene la configuración para el país especificado.
    
    Args:
        pais: 'bolivia' o 'peru'
        
    Returns:
        Diccionario con la configuración completa
    """
    pais_lower = pais.lower()
    
    if pais_lower == 'bolivia':
        config = BOLIVIA_CONFIG.copy()
    elif pais_lower == 'peru':
        config = PERU_CONFIG.copy()
    else:
        raise ValueError(f"País no soportado: {pais}. Use 'bolivia' o 'peru'")
    
    # Agregar configuración común
    config['common'] = COMMON_CONFIG
    
    return config


def get_seismic_parameters_template(pais: str):
    """
    Obtiene plantilla de parámetros sísmicos para el país.
    
    Args:
        pais: 'bolivia' o 'peru'
        
    Returns:
        Diccionario con parámetros sísmicos
    """
    config = get_config(pais)
    return config.get('parametros_defecto', {})


def validate_config(config: dict) -> bool:
    """
    Valida que la configuración tenga los campos requeridos.
    
    Args:
        config: Diccionario de configuración
        
    Returns:
        True si la configuración es válida
    """
    required_fields = [
        'norma', 'titulo_norma', 'pais', 'window_title',
        'parametros_defecto', 'espectro_config', 'load_cases'
    ]
    
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Campo requerido '{field}' no encontrado en configuración")
    
    return True


def get_available_countries():
    """
    Obtiene lista de países disponibles.
    
    Returns:
        Lista de países soportados
    """
    return ['bolivia', 'peru']


def get_country_info(pais: str):
    """
    Obtiene información básica del país.
    
    Args:
        pais: Código del país
        
    Returns:
        Diccionario con información básica
    """
    configs = {
        'bolivia': {
            'nombre': 'Bolivia',
            'norma': 'CNBDS 2023',
            'descripcion': 'Norma Boliviana de Diseño Sísmico'
        },
        'peru': {
            'nombre': 'Perú', 
            'norma': 'E.030',
            'descripcion': 'Norma Técnica E.030 Diseño Sismorresistente'
        }
    }
    
    return configs.get(pais.lower(), {})