"""
Punto de entrada principal para la aplicación Bolivia
Compatible con PyInstaller
"""
import sys
import os
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtGui

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from apps.bolivia.app_bolivia import BoliviaSeismicApp

def main():
    """Función principal de la aplicación Bolivia"""
    app = QApplication(sys.argv)
    
    # Configurar icono de la aplicación
    icon_path = Path(__file__).parent.parent.parent / 'shared_resources' / 'yabar_logo.ico'
    if icon_path.exists():
        app.setWindowIcon(QtGui.QIcon(str(icon_path)))
    
    window = BoliviaSeismicApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()