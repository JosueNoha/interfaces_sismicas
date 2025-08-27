# -*- mode: python ; coding: utf-8 -*-

import os
from pathlib import Path
from PyInstaller.building.build_main import Analysis
from PyInstaller.building.datastruct import PYZ
from PyInstaller.building.api import EXE, COLLECT

# Obtener rutas del proyecto
project_root = Path().resolve()
bolivia_app_path = project_root / 'apps' / 'bolivia' / 'main_bolivia.py'

block_cipher = None

a = Analysis(
    [str(bolivia_app_path)],
    pathex=[str(project_root)],
    binaries=[],
    datas=[
        # Carpeta core completa
        (str(project_root / 'core'), 'core'),
        # Carpeta ui completa
        (str(project_root / 'ui'), 'ui'),
        # Carpeta shared completa
        (str(project_root / 'shared'), 'shared'),
        # Recursos específicos de Bolivia
        (str(project_root / 'apps' / 'bolivia' / 'resources'), 'apps/bolivia/resources'),
        # Icono compartido
        (str(project_root / 'shared_resources'), 'shared_resources'),
    ],
    hiddenimports=[
        'PyQt5.QtCore',
        'PyQt5.QtGui', 
        'PyQt5.QtWidgets',
        'PyQt5.QtPrintSupport',
        'matplotlib.backends.backend_qt5agg',
        'matplotlib.figure',
        'numpy',
        'pandas',
        'scipy',
        'jinja2',
        'importlib.resources',
        'pathlib',
        # Módulos específicos del proyecto
        'core.base.seismic_base',
        'core.base.app_base',
        'core.base.memory_base',
        'core.config.app_config',
        'core.config.constants',
        'ui.generated.ui_bolivia',
        'ui.generated.ui_descriptions',
        'apps.bolivia.app_bolivia',
        'apps.bolivia.config_bolivia',
        'shared.dialogs.descriptions_dialog'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',
        'test',
        'unittest',
        'distutils',
        'setuptools',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='AnalisisSismicoBolivia',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_root / 'shared_resources' / 'yabar_logo.ico'),
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='AnalisisSismicoBolivia',
)