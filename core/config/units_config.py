# core/config/units_config.py
"""
Sistema de unidades centralizado para el proyecto
"""

UNITS_CONFIG = {
    'alturas': {
        'opciones': ['m', 'pies'],
        'defecto': 'm',
        'factores_conversion': {
            'm': 1.0,
            'pies': 3.28084  # m a pies
        }
    },
    'desplazamientos': {
        'opciones': ['mm', 'cm', 'pulg'],
        'defecto': 'mm',
        'factores_conversion': {
            'mm': 1.0,
            'cm': 0.1,
            'pulg': 0.0393701  # mm a pulg
        }
    },
    'fuerzas': {
        'opciones': ['tonf', 'kN', 'kip'],
        'defecto': 'tonf',
        'factores_conversion': {
            'tonf': 1.0,
            'kN': 9.80665,  # tonf a kN
            'kip': 2.20462  # tonf a kip
        }
    }
}

def get_unit_options(categoria):
    """Obtener opciones de unidades para una categoría"""
    return UNITS_CONFIG.get(categoria, {}).get('opciones', [])

def get_default_unit(categoria):
    """Obtener unidad por defecto para una categoría"""
    return UNITS_CONFIG.get(categoria, {}).get('defecto', '')

def convert_value(valor, unidad_origen, unidad_destino, categoria):
    """Convertir valor entre unidades de la misma categoría"""
    if unidad_origen == unidad_destino:
        return valor
    
    config = UNITS_CONFIG.get(categoria, {})
    factores = config.get('factores_conversion', {})
    
    # Convertir a unidad base (primer elemento)
    factor_origen = factores.get(unidad_origen, 1.0)
    factor_destino = factores.get(unidad_destino, 1.0)
    
    return valor * factor_destino / factor_origen