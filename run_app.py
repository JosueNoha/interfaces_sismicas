#!/usr/bin/env python3
"""
Launcher principal para las aplicaciones sísmicas
Permite ejecutar Bolivia o Perú desde un único punto de entrada
"""

import sys
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication

# Agregar el directorio raíz al path
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from core.app_factory import SeismicAppFactory


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Aplicación de Análisis Sísmico Unificada",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run_app.py bolivia           # Ejecutar aplicación Bolivia
  python run_app.py peru             # Ejecutar aplicación Perú
  python run_app.py --list           # Listar países disponibles
        """
    )
    
    parser.add_argument(
        'pais',
        nargs='?',
        choices=['bolivia', 'peru'],
        default='bolivia',
        help='País para el análisis sísmico (default: bolivia)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Listar países disponibles y salir'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Ejecutar en modo debug'
    )
    
    return parser.parse_args()


def list_available_countries():
    """Listar países disponibles"""
    countries = {
        'bolivia': 'Bolivia - CNBDS 2023',
        'peru': 'Perú - E.030'
    }
    
    print("Países disponibles:")
    for code, description in countries.items():
        print(f"  {code:<10} : {description}")


def main():
    """Función principal"""
    args = parse_arguments()
    
    # Mostrar lista si se solicita
    if args.list:
        list_available_countries()
        return 0
    
    # Configurar modo debug
    if args.debug:
        print(f"Ejecutando en modo debug para: {args.pais}")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Análisis Sísmico")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Yabar Ingenieros")
    
    try:
        # Crear aplicación sísmica
        print(f"Iniciando aplicación para {args.pais.upper()}...")
        seismic_app = SeismicAppFactory.create_app(args.pais)
        
        # Mostrar ventana
        seismic_app.show()
        
        print("Aplicación iniciada correctamente")
        
        # Ejecutar aplicación
        return app.exec_()
        
    except ValueError as e:
        print(f"Error de configuración: {e}")
        return 1
    except ImportError as e:
        print(f"Error de importación: {e}")
        print("Verifique que todas las dependencias estén instaladas")
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())