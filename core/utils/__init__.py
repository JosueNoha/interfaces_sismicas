"""
Utilidades compartidas del proyecto sísmico

Módulos:
- latex_utils: Utilidades para generación LaTeX
- file_utils: Manejo de archivos y directorios
- ui_utils: Utilidades comunes para interfaz de usuario
"""

from .latex_utils import *
from .file_utils import *
from .ui_utils import *

__all__ = [
    # latex_utils
    'escape_for_latex', 'dataframe_latex', 'extract_table', 'highlight_column',
    'table_wrapper',
    # file_utils
    'create_output_directory', 'ensure_directory_exists', 'copy_resources',
    # ui_utils
    'connect_combo_signals', 'load_default_values', 'validate_float_input'
]