#!/usr/bin/env python3
"""
Script de debug para identificar el problema de recursión
"""

import sys
import traceback
from pathlib import Path

# Configurar límite de recursión más bajo para debug
sys.setrecursionlimit(100)

# Agregar raíz del proyecto al path
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

def test_imports():
    """Probar importaciones una por una"""
    print("🔍 Probando importaciones paso a paso...")
    
    try:
        print("1. Importando PyQt5...")
        from PyQt5.QtWidgets import QApplication
        print("   ✅ PyQt5 OK")
        
        print("2. Importando core.config...")
        from core.config.app_config import PERU_CONFIG
        print("   ✅ Config OK")
        
        print("3. Importando ui.main_window...")
        from ui.main_window import Ui_MainWindow
        print("   ✅ UI OK")
        
        print("4. Importando core.base.app_base...")
        from core.base.app_base import AppBase
        print("   ✅ AppBase OK")
        
        print("5. Importando apps.peru.app...")
        from apps.peru.app import PeruSeismicApp
        print("   ✅ PeruSeismicApp OK")
        
        print("6. Creando instancia...")
        app = PeruSeismicApp()
        print("   ✅ Instancia creada OK")
        
    except RecursionError as e:
        print(f"❌ RECURSIÓN DETECTADA: {e}")
        print("\n📋 STACK TRACE:")
        traceback.print_exc()
        return False
    except ImportError as e:
        print(f"❌ ERROR DE IMPORTACIÓN: {e}")
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"❌ ERROR GENERAL: {e}")
        traceback.print_exc()
        return False
    
    return True

def check_circular_imports():
    """Verificar importaciones circulares"""
    print("\n🔄 Verificando posibles importaciones circulares...")
    
    # Mapeo de módulos y sus dependencias
    modules_to_check = {
        'core.config.app_config': [],
        'core.base.seismic_base': [],
        'core.base.app_base': ['core.base.seismic_base'],
        'ui.main_window': [],
        'ui.widgets.seismic_params_widget': [],
        'apps.peru.app': [
            'core.base.app_base', 
            'core.config.app_config', 
            'ui.main_window'
        ]
    }
    
    for module_name, dependencies in modules_to_check.items():
        try:
            print(f"  Probando {module_name}...")
            __import__(module_name)
            print(f"    ✅ {module_name} OK")
        except Exception as e:
            print(f"    ❌ {module_name} FALLÓ: {e}")

def main():
    """Función principal de debug"""
    print("🐛 INICIANDO DEBUG DE RECURSIÓN\n")
    
    # Verificar importaciones circulares
    check_circular_imports()
    
    # Probar importaciones paso a paso
    if test_imports():
        print("\n✅ Todas las importaciones funcionan correctamente")
    else:
        print("\n❌ Se encontraron problemas")

if __name__ == "__main__":
    main()