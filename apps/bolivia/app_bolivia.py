"""
Aplicación específica para análisis sísmico Bolivia
Hereda de AppBase y usa configuración específica de Bolivia
"""
from pathlib import Path
from PyQt5.QtWidgets import QMainWindow

from core.base.app_base import AppBase
from apps.bolivia.config_bolivia import BOLIVIA_CONFIG
from ui.generated.ui_bolivia import Ui_MainWindow

class BoliviaSeismicApp(AppBase):
    """Aplicación principal para análisis sísmico Bolivia"""
    
    def __init__(self):
        super().__init__(
            config=BOLIVIA_CONFIG,
            ui_class=Ui_MainWindow,
            window_title="Análisis Sísmico Bolivia - CNBDS 2023"
        )
        
    def setup_specific_connections(self):
        """Configurar conexiones específicas de Bolivia"""
        # Conectar signals específicos de la UI Bolivia
        self.ui.pushButton_mapa.clicked.connect(self.mostrar_mapa_bolivia)
        
        # Configurar valores por defecto específicos de Bolivia
        self.ui.lineEdit_ubicacion.setText(self.config['parametros_defecto']['ubicacion'])
        self.ui.lineEdit_autor.setText(self.config['parametros_defecto']['autor'])
        self.ui.doubleSpinBox_Fa.setValue(self.config['parametros_defecto']['Fa'])
        self.ui.doubleSpinBox_Fv.setValue(self.config['parametros_defecto']['Fv'])
        self.ui.doubleSpinBox_So.setValue(self.config['parametros_defecto']['So'])
        
    def mostrar_mapa_bolivia(self):
        """Mostrar mapa sísmico específico de Bolivia"""
        mapa_path = Path(__file__).parent / 'resources' / 'images' / self.config['mapa_sismico']
        self.mostrar_imagen(str(mapa_path), "Mapa Sísmico de Bolivia")
        
    def crear_instancia_sismica(self):
        """Crear instancia específica para análisis sísmico Bolivia"""
        from core.base.seismic_base import SeismicBase
        
        # Obtener parámetros de la interfaz
        params = self.obtener_parametros_interfaz()
        
        # Crear instancia con configuración de Bolivia
        seismic_instance = SeismicBase(
            pais='bolivia',
            norma=self.config['norma'],
            **params
        )
        
        return seismic_instance
        
    def obtener_parametros_interfaz(self):
        """Obtener parámetros específicos de la interfaz Bolivia"""
        params = super().obtener_parametros_interfaz()
        
        # Parámetros específicos de Bolivia
        params.update({
            'Fa': self.ui.doubleSpinBox_Fa.value(),
            'Fv': self.ui.doubleSpinBox_Fv.value(), 
            'So': self.ui.doubleSpinBox_So.value()
        })
        
        return params