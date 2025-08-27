"""
Configuración específica para Bolivia - CNBDS 2023
Redirige a la configuración centralizada
"""

# Importar configuración centralizada
from core.config.app_config import BOLIVIA_CONFIG

# Re-exportar para compatibilidad (si es necesario)
__all__ = ['BOLIVIA_CONFIG']

# Si hay constantes específicas de Bolivia que no están en la config central,
# se pueden agregar aquí:

# Constantes auxiliares específicas de Bolivia (si son necesarias)
BOLIVIA_SEISMIC_ZONES = {
    1: {"Z": 0.2, "description": "Zona de baja sismicidad"},
    2: {"Z": 0.25, "description": "Zona de moderada sismicidad"}, 
    3: {"Z": 0.3, "description": "Zona de alta sismicidad"},
    4: {"Z": 0.4, "description": "Zona de muy alta sismicidad"}
}

# Factores de suelo específicos de Bolivia (si no están en config central)
BOLIVIA_SOIL_FACTORS = {
    'S1': {'Fa_min': 1.0, 'Fa_max': 1.2, 'Fv_min': 1.0, 'Fv_max': 1.5},
    'S2': {'Fa_min': 1.2, 'Fa_max': 1.4, 'Fv_min': 1.1, 'Fv_max': 1.8},
    'S3': {'Fa_min': 1.8, 'Fa_max': 2.5, 'Fv_min': 1.8, 'Fv_max': 2.4}
}