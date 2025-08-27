"""
Constantes globales del proyecto.
"""

# Unidades por defecto (basado en unit_tool.Units)
DEFAULT_UNITS = {
    'mm': 'mm',
    'm': 'm', 
    'cm': 'cm',
    'pies': 'ft',
    'pulg': 'inch',
    'tonf': 'tonf',
    'kN': 'kN',
    'kip': 'kip'  # 4.4482*kN
}

# Extensiones de archivos temporales de LaTeX a limpiar
LATEX_EXTENSIONS_TO_CLEAN = (
    '.log', '.aux', '.fdb_latexmk', '.fls', '.toc', 
    '.out', '.synctex.gz', '.fls', '.figlist', '.makefile'
)

# Casos de carga sísmica comunes
SEISMIC_LOAD_CASES = {
    'dinamico': ['RSX', 'RSY', 'RX', 'RY'],
    'estatico': ['SDX', 'SDY', 'SX', 'SY']
}

# Configuración de UI por defecto
UI_DEFAULTS = {
    'window_size': (1200, 800),
    'icon_size': (24, 24),
    'table_row_height': 25,
    'image_preview_size': (200, 150),
    'font_family': 'Arial',
    'font_size': 9
}

# Validadores numéricos comunes
NUMERIC_VALIDATORS = {
    'double_positive': {'bottom': 0.0, 'top': 999999.99, 'decimals': 3},
    'double_general': {'bottom': -999999.99, 'top': 999999.99, 'decimals': 3},
    'integer_positive': {'bottom': 1, 'top': 99999},
    'percentage': {'bottom': 0.0, 'top': 100.0, 'decimals': 2}
}

# Configuración de gráficos matplotlib
PLOT_CONFIG = {
    'backend': 'Agg',
    'dpi': 100,
    'figure_size': (10, 6),
    'colors': {
        'primary': '#1f77b4',
        'secondary': '#ff7f0e', 
        'grid': 'gray',
        'text': 'black'
    }
}

# Configuración de archivos de salida
OUTPUT_CONFIG = {
    'pdf_name': 'memoria_calculo.pdf',
    'tex_name': 'memoria_calculo.tex',
    'images_folder': 'images',
    'output_folder': 'out'
}

# Mensajes de error comunes
ERROR_MESSAGES = {
    'etabs_connection': 'Error conectando con ETABS. Verifique que el programa esté abierto.',
    'file_not_found': 'Archivo no encontrado: {}',
    'invalid_data': 'Datos inválidos en campo: {}',
    'latex_compilation': 'Error en compilación LaTeX. Verifique la instalación.',
    'image_load': 'Error cargando imagen: {}',
    'pdf_generation': 'Error generando PDF. Verifique permisos de escritura.'
}

# Configuración de logging
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file_name': 'seismic_app.log',
    'max_bytes': 10485760,  # 10MB
    'backup_count': 3
}

# Configuración de PyQt5
PYQT_CONFIG = {
    'style_sheet': """
        QMainWindow {
            background-color: #f0f0f0;
        }
        QTabWidget::pane {
            border: 1px solid #c0c0c0;
        }
        QGroupBox {
            font-weight: bold;
            border: 2px solid #cccccc;
            border-radius: 5px;
            margin-top: 1ex;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
        }
    """
}

# Configuración de PyInstaller
PYINSTALLER_CONFIG = {
    'hidden_imports': [
        'PyQt5',
        'matplotlib', 
        'numpy',
        'pandas',
        'scipy',
        'jinja2',
        'importlib.resources'
    ],
    'collect_data': [
        'matplotlib',
        'scipy'
    ],
    'exclude_modules': [
        'tkinter',
        'test',
        'unittest',
        'distutils'
    ]
}