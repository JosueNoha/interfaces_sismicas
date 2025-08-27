"""
Punto de entrada principal para la aplicación de análisis sísmico de Perú
"""

import sys
from PyQt5.QtWidgets import QApplication

from apps.peru.app_peru import PeruSeismicApp


def main():
    """Función principal de la aplicación Perú"""
    app = QApplication(sys.argv)
    
    # Crear y mostrar la aplicación
    main_window = PeruSeismicApp()
    main_window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()