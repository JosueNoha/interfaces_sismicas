"""
Factory actualizado para crear aplicaciones sísmicas centralizadas
"""

import sys
from typing import Dict, Any, Optional
from PyQt5.QtWidgets import QApplication

from core.base.app_base import AppBase
# CORREGIDO: Usar interfaz real en lugar de generated
from ui.main_window import Ui_MainWindow
from ui.widgets.seismic_params_widget import SeismicParamsWidget


class SeismicAppFactory:
    """Factory para crear aplicaciones sísmicas"""
    
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
        # Importar configuraciones
        from core.config.app_config import get_config
        
        try:
            country_config = get_config(pais)
        except ValueError as e:
            raise ValueError(f"País no soportado: {pais}. Use 'bolivia' o 'peru'")
        
        # Sobrescribir con config personalizada si se proporciona
        if config:
            country_config.update(config)
        
        # Crear aplicación específica según el país
        if pais.lower() == 'bolivia':
            from apps.bolivia.bolivia_app import BoliviaSeismicApp
            app = BoliviaSeismicApp(country_config)
        elif pais.lower() == 'peru':
            from apps.peru.peru_app import PeruSeismicApp
            app = PeruSeismicApp(country_config)
        else:
            # Fallback a aplicación unificada
            app = UnifiedSeismicApp(country_config)
        
        return app


class UnifiedSeismicApp(AppBase):
    """Aplicación sísmica unificada que se adapta según configuración"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config, Ui_MainWindow)
        
        # Configurar título específico del país
        self.setWindowTitle(config.get('window_title', 'Análisis Sísmico'))
        
        # Configurar widget de parámetros sísmicos
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
        """Conectar señales específicas según el país"""
        # Conectar botón de actualizar datos
        self.ui.b_actualizar.clicked.connect(self.update_seismic_data)
        
        # Conectar análisis modal
        self.ui.b_modal.clicked.connect(self.show_modal_analysis)
        
        # Conectar análisis de cortantes
        self.ui.b_cortantes.clicked.connect(self.calculate_shear_forces)
        
        # Conectar análisis de desplazamientos
        self.ui.b_desplazamiento.clicked.connect(self.calculate_displacements)
        self.ui.b_derivas.clicked.connect(self.calculate_drifts)

    def _apply_default_values(self):
        """Aplicar valores por defecto según configuración"""
        defaults = self.config.get('parametros_defecto', {})
        
        # Datos del proyecto
        if 'ubicacion' in defaults:
            self.ui.le_ubicacion.setText(defaults['ubicacion'])
        if 'autor' in defaults:
            self.ui.le_autor.setText(defaults['autor'])
        if 'proyecto' in defaults:
            self.ui.le_proyecto.setText(defaults['proyecto'])
        if 'fecha' in defaults:
            self.ui.le_fecha.setText(defaults['fecha'])
        
        # Parámetros sísmicos
        seismic_defaults = {k: v for k, v in defaults.items() 
                           if k not in ['ubicacion', 'autor', 'proyecto', 'fecha']}
        self.seismic_params_widget.set_parameters(seismic_defaults)

    def _on_seismic_params_changed(self):
        """Callback cuando cambian parámetros sísmicos"""
        # Actualizar datos del modelo sísmico
        params = self.seismic_params_widget.get_parameters()
        self.update_sismo_parameters(params)

    def update_seismic_data(self):
        """Actualizar datos sísmicos desde la interfaz"""
        # Obtener datos del proyecto
        project_data = self.get_project_data()
        self.sismo.proyecto = project_data['proyecto']
        self.sismo.ubicacion = project_data['ubicacion']
        self.sismo.autor = project_data['autor']
        self.sismo.fecha = project_data['fecha']
        
        # Obtener parámetros sísmicos
        seismic_params = self.seismic_params_widget.get_parameters()
        self.update_sismo_parameters(seismic_params)
        
        self.show_info("Datos actualizados correctamente")

    def update_sismo_parameters(self, params: Dict[str, Any]):
        """Actualizar parámetros del modelo sísmico"""
        for key, value in params.items():
            if hasattr(self.sismo, key):
                setattr(self.sismo, key, value)

    def show_modal_analysis(self):
        """Mostrar análisis modal"""
        try:
            # Conectar con ETABS y obtener datos modales
            modal_data = self.sismo.get_modal_analysis()
            
            if modal_data:
                # Actualizar campos en la interfaz
                self.ui.le_tx.setText(f"{modal_data.get('Tx', 0):.4f}")
                self.ui.le_ty.setText(f"{modal_data.get('Ty', 0):.4f}")
                
                self.show_info("Análisis modal completado")
            else:
                self.show_error("No se pudieron obtener datos modales")
                
        except Exception as e:
            self.show_error(f"Error en análisis modal: {str(e)}")

    def calculate_shear_forces(self):
        """Calcular fuerzas cortantes"""
        try:
            shear_data = self.sismo.calculate_shear_forces()
            
            if shear_data:
                self.ui.le_vestx.setText(f"{shear_data.get('Vx', 0):.2f}")
                self.ui.le_vesty.setText(f"{shear_data.get('Vy', 0):.2f}")
                
                self.show_info("Fuerzas cortantes calculadas")
            else:
                self.show_error("No se pudieron calcular las fuerzas cortantes")
                
        except Exception as e:
            self.show_error(f"Error calculando cortantes: {str(e)}")

    def calculate_displacements(self):
        """Calcular desplazamientos"""
        try:
            displacement_data = self.sismo.calculate_displacements()
            
            if displacement_data:
                self.show_info("Desplazamientos calculados correctamente")
            else:
                self.show_error("No se pudieron calcular los desplazamientos")
                
        except Exception as e:
            self.show_error(f"Error calculando desplazamientos: {str(e)}")

    def calculate_drifts(self):
        """Calcular derivas"""
        try:
            drift_data = self.sismo.calculate_drifts()
            
            if drift_data:
                self.show_info("Derivas calculadas correctamente")
            else:
                self.show_error("No se pudieron calcular las derivas")
                
        except Exception as e:
            self.show_error(f"Error calculando derivas: {str(e)}")

    def generate_report(self):
        """Generar reporte base - implementado en clases específicas"""
        self.show_warning("Función de reporte debe ser implementada en la aplicación específica")


def create_application(country: str = None):
    """
    Función de conveniencia para crear aplicación desde línea de comandos
    
    Args:
        country: País para la aplicación
        
    Returns:
        Instancia de QApplication y aplicación sísmica
    """
    # Crear aplicación Qt
    qt_app = QApplication(sys.argv)
    qt_app.setApplicationName("Análisis Sísmico")
    qt_app.setApplicationVersion("1.0.0")
    
    # Determinar país
    if not country:
        if len(sys.argv) > 1:
            country = sys.argv[1].lower()
        else:
            country = 'bolivia'  # Por defecto
    
    # Crear aplicación sísmica
    seismic_app = SeismicAppFactory.create_app(country)
    
    return qt_app, seismic_app


def main():
    """Función principal para ejecutar la aplicación"""
    try:
        # Crear aplicación
        qt_app, seismic_app = create_application()
        
        # Mostrar ventana
        seismic_app.show()
        
        # Configurar título de país en la barra de título
        country = sys.argv[1] if len(sys.argv) > 1 else 'bolivia'
        print(f"Iniciando aplicación para {country.upper()}...")
        
        # Ejecutar aplicación
        sys.exit(qt_app.exec_())
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Uso: python -m core.app_factory [bolivia|peru]")
        sys.exit(1)
    except Exception as e:
        print(f"Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()