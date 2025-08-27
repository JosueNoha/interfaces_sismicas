"""
Configuración específica para la aplicación de análisis sísmico de Perú
"""

PERU_CONFIG = {
    'norma': 'E.030',
    'titulo_norma': 'NORMA TÉCNICA COMPLEMENTARIA PARA EL DISEÑO POR SISMO (E.030 2018)',
    'template_path': 'apps/peru/resources/templates/plantilla_peru.ltx',
    'ubicacion_defecto': 'Lima',
    'autor_defecto': 'Yabar Ingenieros',
    'parametros_defecto': {
        'Z': 0.25,  # Zona 2
        'U': 1.00,  # Categoría C
        'S': 1.20,  # Suelo S1
        'Tp': 0.60,
        'Tl': 2.00,
        'fecha': '05/10/2025',
        'proyecto': 'Edificación de Concreto Reforzado'
    },
    'zonas_sismicas': {
        '1': {'Z': 0.10},
        '2': {'Z': 0.25},
        '3': {'Z': 0.35},
        '4': {'Z': 0.45}
    },
    'tipos_suelo': {
        'S0': {'S_zona_1': 0.80, 'S_zona_2': 0.80, 'S_zona_3': 0.80, 'S_zona_4': 0.80,
               'Tp': 0.30, 'Tl': 3.00},
        'S1': {'S_zona_1': 1.00, 'S_zona_2': 1.00, 'S_zona_3': 1.00, 'S_zona_4': 1.00,
               'Tp': 0.40, 'Tl': 2.50},
        'S2': {'S_zona_1': 1.60, 'S_zona_2': 1.20, 'S_zona_3': 1.15, 'S_zona_4': 1.05,
               'Tp': 0.60, 'Tl': 2.00},
        'S3': {'S_zona_1': 2.00, 'S_zona_2': 1.40, 'S_zona_3': 1.20, 'S_zona_4': 1.10,
               'Tp': 1.00, 'Tl': 1.60}
    },
    'categorias': {
        'A1': {'U': 1.50},
        'A2': {'U': 1.30}, 
        'B': {'U': 1.30},
        'C': {'U': 1.00},
        'D': {'U': 1.00}
    }
}