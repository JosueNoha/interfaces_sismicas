"""
Aplicación para análisis sísmico Bolivia - CNBDS 2023
"""

from .bolivia_app import BoliviaSeismicApp
from .memory_bolivia import BoliviaMemoryGenerator
from .config_bolivia import BOLIVIA_CONFIG

__version__ = "1.0.0"
__all__ = ['BoliviaSeismicApp', 'BoliviaMemoryGenerator', 'BOLIVIA_CONFIG']