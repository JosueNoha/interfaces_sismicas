"""
Factory centralizado y corregido para crear aplicaciones sísmicas
Elimina importaciones circulares y rutas incorrectas
"""

import sys
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QApplication

from core.base.app_base import AppBase
from ui.main_window import Ui_MainWindow  # ✅ Ruta corregida
from ui.widgets.seismic_params_widget import SeismicParamsWidget


class SeismicAppFactory:
    """Factory centralizado para crear aplicaciones sísmicas"""
    
    @staticmethod
    def create_app(pais: str, config: Optional[Dict[str, Any]] = None):
        """
        Crear aplicación sísmica para el país especificado
        
        Args:
            pais: País ('bolivia' o 'peru')
            config: Configuración personalizada opcional
            
        Returns:
            Instancia de aplicación configurada
        """
        # Importar configuraciones de forma segura
        try:
            from core.config.app_config import get_config
            country_config = get_config(pais)
        except ValueError:
            raise ValueError(f"País no soportado: {pais}. Use 'bolivia' o 'peru'")
        
        # Sobrescribir con config personalizada si se proporciona
        if config:
            country_config.update(config)
        
        # Crear aplicación específica según el país
        # ✅ Rutas corregidas eliminando importaciones circulares
        if pais.lower() == 'bolivia':
            from apps.bolivia.app import BoliviaSeismicApp  # ✅ Ruta correcta
            app = BoliviaSeismicApp(country_config)
        elif pais.lower() == 'peru':
            from apps.peru.app import PeruSeismicApp  # ✅ Ruta correcta  
            app = PeruSeismicApp(country_config)
        else:
            # Fallback a aplicación unificada
            app = UnifiedSeismicApp(country_config)
        
        return app

    @staticmethod
    def get_available_countries():
        """Obtener lista de países disponibles"""
        return ['bolivia', 'peru']

    @staticmethod  
    def validate_country(country: str) -> bool:
        """Validar que el país esté soportado"""
        return country.lower() in SeismicAppFactory.get_available_countries()


class UnifiedSeismicApp(AppBase):
    """Aplicación sísmica unificada como fallback"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, Ui_MainWindow)
        
        # Configurar título específico del país
        self.setWindowTitle(config.get('window_title', 'Análisis Sísmico'))
        
        # Configurar widget de parámetros sísmicos dinámico
        self._setup_seismic_params_widget()
        
        # Conectar señales específicas
        self._connect_specific_signals()
        
        # Aplicar valores por defecto
        self._apply_default_values()

    def _setup_seismic_params_widget(self):
        """Configurar widget de parámetros sísmicos dinámico"""
        # Crear widget de parámetros específico para el país
        self.seismic_params_widget = SeismicParamsWidget(self.config)
        
        # Agregar al grupo de parámetros sísmicos en la UI
        self.ui.seismic_params_layout.addWidget(self.seismic_params_widget)
        
        # Conectar cambios de parámetros
        self.seismic_params_widget.connect_param_changed(self._on_seismic_params_changed)

    def _connect_specific_signals(self):
        """Conectar señales específicas"""
        # Botón de actualizar datos
        if hasattr(self.ui, 'b_actualizar'):
            self.ui.b_actualizar.clicked.connect(self.update_seismic_data)
        
        # Análisis modal
        if hasattr(self.ui, 'b_modal'):
            self.ui.b_modal.clicked.connect(self.show_modal_analysis)
        
        # Análisis de cortantes
        if hasattr(self.ui, 'b_cortantes'):
            self.ui.b_cortantes.clicked.connect(self.calculate_shear_forces)
        
        # Análisis de desplazamientos
        if hasattr(self.ui, 'b_desplazamiento'):
            self.ui.b_desplazamiento.clicked.connect(self.calculate_displacements)
        if hasattr(self.ui, 'b_derivas'):
            self.ui.b_derivas.clicked.connect(self.calculate_drifts)

    def _apply_default_values(self):
        """Aplicar valores por defecto según configuración"""
        defaults = self.config.get('parametros_defecto', {})
        
        # Datos del proyecto
        project_fields = {
            'ubicacion': 'le_ubicacion',
            'autor': 'le_autor', 
            'proyecto': 'le_proyecto',
            'fecha': 'le_fecha'
        }
        
        for key, ui_element in project_fields.items():
            if key in defaults and hasattr(self.ui, ui_element):
                getattr(self.ui, ui_element).setText(str(defaults[key]))
        
        # Parámetros sísmicos
        seismic_defaults = {k: v for k, v in defaults.items() 
                           if k not in project_fields.keys()}
        if seismic_defaults and hasattr(self, 'seismic_params_widget'):
            self.seismic_params_widget.set_parameters(seismic_defaults)

    def _on_seismic_params_changed(self):
        """Callback cuando cambian parámetros sísmicos"""
        if hasattr(self, 'seismic_params_widget'):
            params = self.seismic_params_widget.get_parameters()
            self.update_sismo_parameters(params)

    def update_seismic_data(self):
        """Actualizar datos sísmicos desde la interfaz"""
        # Obtener datos del proyecto
        project_data = self.get_project_data()
        for key, value in project_data.items():
            setattr(self.sismo, key, value)
        
        # Obtener parámetros sísmicos
        if hasattr(self, 'seismic_params_widget'):
            seismic_params = self.seismic_params_widget.get_parameters()
            self.update_sismo_parameters(seismic_params)
        
        self.show_info("Datos actualizados correctamente")

    def update_sismo_parameters(self, params: Dict[str, Any]):
        """Actualizar parámetros del modelo sísmico"""
        for key, value in params.items():
            setattr(self.sismo, key, value)

    # Métodos de análisis con manejo de errores mejorado
    def show_modal_analysis(self):
        """Mostrar análisis modal"""
        try:
            modal_data = self.sismo.get_modal_analysis()
            if modal_data:
                # Actualizar campos en la interfaz
                if hasattr(self.ui, 'le_tx'):
                    self.ui.le_tx.setText(f"{modal_data.get('Tx', 0):.4f}")
                if hasattr(self.ui, 'le_ty'):
                    self.ui.le_ty.setText(f"{modal_data.get('Ty', 0):.4f}")
                
                self.show_info("Análisis modal completado")
            else:
                self.show_warning("No se pudieron obtener datos modales. Verifique conexión con ETABS.")
        except Exception as e:
            self.show_error(f"Error en análisis modal: {str(e)}")

    def calculate_shear_forces(self):
        """Calcular fuerzas cortantes"""
        try:
            shear_data = self.sismo.calculate_shear_forces()
            if shear_data:
                if hasattr(self.ui, 'le_vestx'):
                    self.ui.le_vestx.setText(f"{shear_data.get('Vx', 0):.2f}")
                if hasattr(self.ui, 'le_vesty'):
                    self.ui.le_vesty.setText(f"{shear_data.get('Vy', 0):.2f}")
                
                self.show_info("Fuerzas cortantes calculadas")
            else:
                self.show_warning("No se pudieron calcular las fuerzas cortantes")
        except Exception as e:
            self.show_error(f"Error calculando cortantes: {str(e)}")

    def calculate_displacements(self):
        """Calcular desplazamientos"""
        try:
            displacement_data = self.sismo.calculate_displacements()
            if displacement_data:
                self.show_info("Desplazamientos calculados correctamente")
            else:
                self.show_warning("No se pudieron calcular los desplazamientos")
        except Exception as e:
            self.show_error(f"Error calculando desplazamientos: {str(e)}")

    def calculate_drifts(self):
        """Calcular derivas"""
        try:
            drift_data = self.sismo.calculate_drifts()
            if drift_data:
                self.show_info("Derivas calculadas correctamente")
            else:
                self.show_warning("No se pudieron calcular las derivas")
        except Exception as e:
            self.show_error(f"Error calculando derivas: {str(e)}")

    def generate_report(self):
        """Generar reporte base - implementado en clases específicas"""
        self.show_warning(
            "Función de reporte debe ser implementada en la aplicación específica.\n"
            "Use las aplicaciones de Bolivia o Perú para generar reportes."
        )


# Funciones de conveniencia para compatibilidad
def create_application(country: str = None):
    """
    Función de conveniencia para crear aplicación desde línea de comandos
    ⚠️ DEPRECATED: Usar main_app.py en su lugar
    """
    print("⚠️  create_application() está deprecated. Use main_app.py")
    
    if not country:
        if len(sys.argv) > 1:
            country = sys.argv[1].lower()
        else:
            country = 'bolivia'
    
    # Crear aplicación Qt
    qt_app = QApplication(sys.argv)
    
    # Crear aplicación sísmica
    seismic_app = SeismicAppFactory.create_app(country)
    
    return qt_app, seismic_app


def main():
    """
    Función principal del factory
    ⚠️ DEPRECATED: Usar main_app.py en su lugar
    """
    print("⚠️  Usando factory deprecated. Use main_app.py para mejor experiencia")
    
    try:
        qt_app, seismic_app = create_application()
        seismic_app.show()
        sys.exit(qt_app.exec_())
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()