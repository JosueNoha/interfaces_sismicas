#!/usr/bin/env python3
"""
Launcher principal simplificado usando el factory centralizado
"""

import sys
import argparse
from pathlib import Path

# Agregar raíz del proyecto al path
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Aplicaciones de Análisis Sísmico Centralizadas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main_app.py bolivia    # Bolivia (CNBDS 2023)
  python main_app.py peru      # Perú (E.030)
  python main_app.py --list    # Mostrar países disponibles
        """
    )
    
    parser.add_argument(
        'pais',
        nargs='?',
        choices=['bolivia', 'peru'],
        default='bolivia',
        help='País para análisis sísmico (default: bolivia)'
    )
    
    parser.add_argument(
        '--list',
        action='store_true',
        help='Mostrar países disponibles'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true', 
        help='Ejecutar en modo debug'
    )
    
    return parser.parse_args()


def show_available_countries():
    """Mostrar países disponibles"""
    print("🌎 Países disponibles:")
    print("  bolivia  : Bolivia - CNBDS 2023")
    print("  peru     : Perú - E.030")


def main():
    """Función principal usando factory centralizado corregido"""
    args = parse_arguments()
    
    if args.list:
        show_available_countries()
        return 0
    
    try:
        # ✅ USAR FACTORY CON CLASES REALES
        from core.app_factory import create_qt_application, SeismicAppFactory
        
        print(f"🚀 Iniciando aplicación {args.pais.upper()}...")
        
        # Crear aplicación Qt
        qt_app = create_qt_application()
        
        # Crear aplicación usando clases reales BoliviaSeismicApp/PeruSeismicApp
        seismic_app = SeismicAppFactory.create_app(args.pais)
        
        # Configurar título específico
        titles = {
            'bolivia': 'Análisis Sísmico - Bolivia (CNBDS 2023)',
            'peru': 'Análisis Sísmico - Perú (E.030)'
        }
        seismic_app.setWindowTitle(titles[args.pais])
        
        # Mostrar aplicación
        seismic_app.show()
        
        if args.debug:
            print(f"✅ Aplicación {args.pais.upper()} iniciada correctamente")
        
        return qt_app.exec_()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())