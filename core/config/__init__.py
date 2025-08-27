"""
Core configuration package for seismic applications.
"""

from .app_config import BOLIVIA_CONFIG, PERU_CONFIG
from .constants import (
    DEFAULT_UNITS, 
    LATEX_EXTENSIONS_TO_CLEAN, 
    SEISMIC_LOAD_CASES,
    UI_DEFAULTS
)

__all__ = [
    'BOLIVIA_CONFIG',
    'PERU_CONFIG', 
    'DEFAULT_UNITS',
    'LATEX_EXTENSIONS_TO_CLEAN',
    'SEISMIC_LOAD_CASES',
    'UI_DEFAULTS'
]