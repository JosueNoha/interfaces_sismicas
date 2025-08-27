# core/__init__.py
"""
Paquete core - Funcionalidad central compartida
"""

__version__ = "1.0.0"

# core/base/__init__.py
"""
Clases base para análisis sísmico
"""

from .seismic_base import SeismicBase
from .app_base import AppBase  
from .memory_base import MemoryBase

__all__ = ['SeismicBase', 'AppBase', 'MemoryBase']

# core/config/__init__.py
"""
Configuraciones del proyecto
"""

# core/utils/__init__.py
"""
Utilidades compartidas
"""

# ui/__init__.py
"""
Interfaces de usuario
"""

# ui/generated/__init__.py
"""
Interfaces generadas desde archivos .ui
"""

# ui/widgets/__init__.py
"""
Widgets personalizados comunes
"""

# apps/__init__.py
"""
Aplicaciones específicas por país
"""

# apps/bolivia/__init__.py
"""
Aplicación para análisis sísmico Bolivia - CNBDS 2023
"""

# apps/peru/__init__.py
"""
Aplicación para análisis sísmico Perú - E.030
"""

# shared/__init__.py
"""
Componentes compartidos entre aplicaciones
"""

# shared/dialogs/__init__.py
"""
Diálogos compartidos
"""