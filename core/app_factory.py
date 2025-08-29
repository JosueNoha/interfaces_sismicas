"""
Factory centralizado mejorado para crear aplicaciones sísmicas
Elimina duplicación y centraliza configuración común
"""

import sys
from typing import Dict, Any
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon
from pathlib import Path

from core.config.app_config import get_config
from ui.main_window import Ui_MainWindow
from ui.widgets.seismic_params_widget import SeismicParamsWidget


class SeismicAppFactory:
    """Factory centralizado para crear aplicaciones sísmicas"""
    
    @staticmethod
    def create_app(country: str, config: Dict[str, Any] = None):
        """
        Crear aplicación sísmica unificada
        
        Args:
            country: País ('bolivia' o 'peru')
            config: Configuración personalizada opcional
        """
        # Obtener configuración del país
        try:
            country_config = get_config(country)
        except ValueError:
            raise ValueError(f"País no soportado: {country}")
        
        # Sobrescribir con config personalizada
        if config:
            country_config.update(config)
        
        # Crear aplicación unificada con configuración específica
        return UnifiedSeismicApp(country_config, country)


class UnifiedSeismicApp:
    """Aplicación sísmica unificada que se adapta según el país"""
    
    def __init__(self, config: Dict[str, Any], country: str):
        self.config = config
        self.country = country.lower()
        
        # Importar módulos específicos del país
        self._import_country_modules()
        
        # Crear aplicación base con funcionalidad común
        from core.base.app_base import AppBase
        
        # Crear instancia heredando de AppBase
        self.app = self._create_country_app(config)
    
    def _import_country_modules(self):
        """Importar módulos específicos según el país"""
        if self.country == 'bolivia':
            from apps.bolivia.memory import BoliviaMemoryGenerator
            self.memory_generator_class = BoliviaMemoryGenerator
        elif self.country == 'peru':
            from apps.peru.memory import PeruMemoryGenerator
            self.memory_generator_class = PeruMemoryGenerator
    
    def _create_country_app(self, config):
        """Crear aplicación específica del país"""
        if self.country == 'bolivia':
            from apps.bolivia.app import BoliviaSeismicApp
            return BoliviaSeismicApp(config)
        elif self.country == 'peru':
            from apps.peru.app import PeruSeismicApp
            return PeruSeismicApp(config)
        else:
            raise ValueError(f"País no implementado: {self.country}")
    
    def show(self):
        """Mostrar la aplicación"""
        self.app.show()
    
    def __getattr__(self, name):
        """Delegar atributos no encontrados a la aplicación interna"""
        return getattr(self.app, name)


def create_qt_application():
    """Crear aplicación Qt con configuración común"""
    app = QApplication(sys.argv)
    app.setApplicationName("Análisis Sísmico")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Yabar Ingenieros")
    
    # Configurar icono común
    icon_path = Path(__file__).parent.parent / 'shared_resources' / 'yabar_logo.ico'
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    return app


def main(country: str = None):
    """Función principal simplificada"""
    if not country:
        country = sys.argv[1] if len(sys.argv) > 1 else 'bolivia'
    
    try:
        # Crear aplicación Qt
        qt_app = create_qt_application()
        
        # Crear aplicación sísmica
        seismic_app = SeismicAppFactory.create_app(country)
        seismic_app.show()
        
        return qt_app.exec_()
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())