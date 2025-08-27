"""
Configuración específica para Bolivia - CNBDS 2023
Redirige a la configuración centralizada
"""

# Importar configuración centralizada
from core.config.app_config import BOLIVIA_CONFIG

# Re-exportar para compatibilidad
__all__ = ['BOLIVIA_CONFIG']