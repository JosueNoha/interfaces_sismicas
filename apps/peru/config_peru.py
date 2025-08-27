"""
Configuración específica para Perú - E.030
Redirige a la configuración centralizada
"""

# Importar configuración centralizada
from core.config.app_config import PERU_CONFIG

# Re-exportar para compatibilidad
__all__ = ['PERU_CONFIG']