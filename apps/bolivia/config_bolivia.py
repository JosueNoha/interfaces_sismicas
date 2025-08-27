"""
Configuración específica para Bolivia - CNBDS 2023
"""
from pathlib import Path

# Ruta base de la aplicación Bolivia
BASE_DIR = Path(__file__).parent

BOLIVIA_CONFIG = {
    'pais': 'bolivia',
    'norma': 'CNBDS 2023',
    'titulo_norma': 'CÓDIGO NACIONAL BOLIVIANO DE DISEÑO SÍSMICO (CNBDS 2023)',
    'template_path': str(BASE_DIR / 'resources' / 'templates' / 'plantilla_bolivia.ltx'),
    'mapa_sismico': 'MapaSismicoBolivia.png',
    
    # Parámetros sísmicos por defecto para Bolivia
    'parametros_defecto': {
        'ubicacion': 'La Paz',
        'autor': 'Yabar Ingenieros',
        'Fa': 1.86,
        'Fv': 0.63,
        'So': 2.9,
        'Z': 0.3,  # Zona sísmica 3 por defecto
        'U': 1.0,  # Factor de uso normal
        'S': 1.2   # Suelo intermedio por defecto
    },
    
    # Sistemas estructurales disponibles en Bolivia
    'sistemas_estructurales': {
        'Acero': {
            'Pórticos Especiales de Acero Resistentes a Momento (SMF)': {
                'descripcion': 'Pórticos Especiales Resistentes a Momento (SMF)',
                'Ro': 8
            },
            'Pórticos Intermedios de Acero Resistentes a Momento (IMF)': {
                'descripcion': 'Pórticos Intermedios Resistentes a Momento (IMF)', 
                'Ro': 4.5
            },
            'Pórticos Ordinarios de Acero Resistentes a Momento (OMF)': {
                'descripcion': 'Pórticos Ordinarios Resistentes a Momento (OMF)',
                'Ro': 4
            },
            'Pórticos Especiales de Acero Concénticamente Arriostrados': {
                'descripcion': 'Pórticos Especiales Concentricamente Arriostrados (SCBF)',
                'Ro': 7
            },
            'Pórticos Ordinarios de Acero Concénticamente Arriostrados': {
                'descripcion': 'Pórticos Ordinarios Concentricamente Arriostrados (OCBF)',
                'Ro': 4
            },
            'Pórticos Acero Excéntricamente Arriostrados': {
                'descripcion': 'Pórticos Excéntricamente Arriostrados (EBF)',
                'Ro': 8
            }
        },
        'Concreto': {
            'Pórticos de Concreto Armado': {
                'descripcion': 'Pórticos',
                'Ro': 8
            },
            'Dual de Concreto Armado': {
                'descripcion': 'Dual',
                'Ro': 7
            },
            'De Muros Estructurales de Concreto Armado': {
                'descripcion': 'De muros estructurales',
                'Ro': 6
            },
            'Muros de Ductilidad Limita de Concreto Armado': {
                'descripcion': 'Muros de ductilidad limitada',
                'Ro': 4
            }
        },
        'Albañilería Armada o Confinada': {
            'descripcion': r'\textbf{Albañilería Armada o Confinada}',
            'Ro': 3
        },
        'Madera': {
            'descripcion': r'\textbf{Madera}',
            'Ro': 7
        }
    },
    
    # Factores de zona sísmica Bolivia
    'zonas_sismicas': {
        'Zona 1': 0.2,
        'Zona 2': 0.25,
        'Zona 3': 0.3,
        'Zona 4': 0.4
    },
    
    # Factores de uso
    'factores_uso': {
        'Categoría I - Edificaciones esenciales': 1.5,
        'Categoría II - Edificaciones importantes': 1.25,
        'Categoría III - Edificaciones comunes': 1.0,
        'Categoría IV - Edificaciones menores': 1.0
    }
}