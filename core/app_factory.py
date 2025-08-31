"""
Factory centralizado mejorado para crear aplicaciones sísmicas
Elimina duplicación y centraliza configuración común
"""
from PyQt5.QtWidgets import QApplication
import sys
from pathlib import Path

def create_qt_application():
    """Crear aplicación Qt reutilizable"""
    if not QApplication.instance():
        app = QApplication(sys.argv)
        app.setStyle('Fusion')  # Estilo consistente
        return app
    return QApplication.instance()

class SeismicAppFactory:
    """Factory para crear aplicaciones sísmicas centralizadas"""
    
    @staticmethod
    def create_app(country: str):
        """
        Crear aplicación sísmica según país usando las clases reales
        
        Args:
            country: 'bolivia' o 'peru'
            
        Returns:
            Instancia de BoliviaSeismicApp o PeruSeismicApp
        """
        if country.lower() == 'bolivia':
            from apps.bolivia.app import BoliviaSeismicApp
            return BoliviaSeismicApp()
        elif country.lower() == 'peru':
            from apps.peru.app import PeruSeismicApp
            return PeruSeismicApp()
        else:
            raise ValueError(f"País no soportado: {country}")

def main(country='bolivia'):
    """Función main centralizada usando clases reales"""
    try:
        # Crear aplicación Qt
        qt_app = create_qt_application()
        
        # Crear aplicación sísmica usando las clases reales
        seismic_app = SeismicAppFactory.create_app(country)
        
        # Configurar título
        titles = {
            'bolivia': 'Análisis Sísmico - Bolivia (CNBDS 2023)',
            'peru': 'Análisis Sísmico - Perú (E.030)'
        }
        seismic_app.setWindowTitle(titles[country])
        
        # Mostrar aplicación
        seismic_app.show()
        
        return qt_app.exec_()
        
    except Exception as e:
        print(f"Error: {e}")
        return 1

