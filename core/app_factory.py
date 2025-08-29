"""
Factory centralizado para crear aplicaciones sísmicas
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QApplication

from core.base.app_base import AppBase
from ui.main_window import Ui_MainWindow
from core.config.app_config import BOLIVIA_CONFIG, PERU_CONFIG


class SeismicAppFactory:
    """Factory para crear aplicaciones sísmicas específicas por país"""
    
    @staticmethod
    def create_app(country: str) -> AppBase:
        """
        Crear aplicación sísmica
        
        Args:
            country: 'bolivia' o 'peru'
        Returns:
            Instancia de aplicación configurada
        """
        if country.lower() == 'bolivia':
            from apps.bolivia.app import BoliviaSeismicApp
            return BoliviaSeismicApp()
            
        elif country.lower() == 'peru':
            from apps.peru.app import PeruSeismicApp  
            return PeruSeismicApp()
            
        else:
            raise ValueError(f"País no soportado: {country}. Use 'bolivia' o 'peru'")

    @staticmethod
    def get_available_countries():
        """Países disponibles"""
        return ['bolivia', 'peru']