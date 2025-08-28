#!/usr/bin/env python3
"""
Punto de entrada unificado para aplicaciones sísmicas
Reemplaza main_bolivia.py y main_peru.py eliminando duplicación
"""

import sys
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon

# Agregar raíz del proyecto al path de forma segura
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def parse_arguments():
    """Parsear argumentos de línea de comandos"""
    parser = argparse.ArgumentParser(
        description="Aplicaciones de Análisis Sísmico Unificadas",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main_app.py bolivia    # Ejecutar aplicación Bolivia (CNBDS 2023)
  python main_app.py peru      # Ejecutar aplicación Perú (E.030)
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
    countries = {
        'bolivia': 'Bolivia - CNBDS 2023 (Norma Boliviana de Diseño Sísmico)',
        'peru': 'Perú - E.030 (Norma Técnica de Diseño Sismorresistente)'
    }
    
    print("🌎 Países disponibles para análisis sísmico:")
    print("=" * 50)
    for code, description in countries.items():
        print(f"  {code:<8} : {description}")


def create_app(country: str, debug: bool = False):
    """
    Crear aplicación específica del país
    
    Args:
        country: País ('bolivia' o 'peru')
        debug: Modo debug habilitado
    """
    try:
        # Crear aplicación Qt
        app = QApplication(sys.argv)
        app.setApplicationName("Análisis Sísmico")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("Yabar Ingenieros")
        
        # Configurar icono si está disponible
        icon_path = ROOT_DIR / 'shared_resources' / 'yabar_logo.ico'
        if icon_path.exists():
            app.setWindowIcon(QIcon(str(icon_path)))
        
        # Importar dinámicamente la aplicación correspondiente
        if country == 'bolivia':
            from apps.bolivia.app import BoliviaSeismicApp
            window = BoliviaSeismicApp()
        elif country == 'peru':
            from apps.peru.app import PeruSeismicApp
            window = PeruSeismicApp()
        else:
            raise ValueError(f"País no soportado: {country}")
        
        # Configurar título específico
        country_titles = {
            'bolivia': 'Análisis Sísmico - Bolivia (CNBDS 2023)',
            'peru': 'Análisis Sísmico - Perú (E.030)'
        }
        window.setWindowTitle(country_titles[country])
        
        # Mostrar aplicación
        window.show()
        
        if debug:
            print(f"✅ Aplicación {country.upper()} iniciada en modo debug")
        
        return app.exec_()
        
    except ImportError as e:
        print(f"❌ Error importando módulos para {country}: {e}")
        print("💡 Verifique que todos los archivos estén en su lugar correcto")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if debug:
            import traceback
            traceback.print_exc()
        return 1


def main():
    """Función principal"""
    args = parse_arguments()
    
    # Mostrar países disponibles
    if args.list:
        show_available_countries()
        return 0
    
    # Mensaje de inicio
    print(f"🚀 Iniciando aplicación de análisis sísmico para {args.pais.upper()}")
    
    # Crear y ejecutar aplicación
    exit_code = create_app(args.pais, args.debug)
    
    print(f"📋 Aplicación finalizada con código: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())