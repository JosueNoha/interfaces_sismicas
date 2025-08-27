"""
Módulo específico para Bolivia - Extensiones y funcionalidades particulares
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QPushButton, QLabel
from pathlib import Path

from core.base.app_base import AppBase


class BoliviaSeismicApp(AppBase):
    """Extensiones específicas para la aplicación de Bolivia"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Agregar funcionalidades específicas de Bolivia
        self._setup_bolivia_extensions()
    
    def _setup_bolivia_extensions(self):
        """Configurar extensiones específicas de Bolivia"""
        # Agregar botón para mapa sísmico si existe
        if self.config.get('mapa_sismico'):
            self._add_seismic_map_button()
        
        # Configurar validaciones específicas de Bolivia
        self._setup_bolivia_validations()
    
    def _add_seismic_map_button(self):
        """Agregar botón para mostrar mapa sísmico de Bolivia"""
        # Agregar botón en el grupo de parámetros sísmicos
        self.b_mapa_bolivia = QPushButton("Ver Mapa Sísmico")
        self.b_mapa_bolivia.clicked.connect(self.show_bolivia_seismic_map)
        
        # Agregar al layout de parámetros sísmicos
        layout = self.ui.seismic_params_layout
        current_row = layout.rowCount()
        layout.addWidget(self.b_mapa_bolivia, current_row, 0, 1, 2)
    
    def _setup_bolivia_validations(self):
        """Configurar validaciones específicas para parámetros de Bolivia"""
        # Conectar validaciones de rangos para parámetros bolivianos
        if hasattr(self.seismic_params_widget, 'sb_fa'):
            self.seismic_params_widget.sb_fa.valueChanged.connect(
                self._validate_bolivia_params
            )
        if hasattr(self.seismic_params_widget, 'sb_fv'):
            self.seismic_params_widget.sb_fv.valueChanged.connect(
                self._validate_bolivia_params
            )
    
    def show_bolivia_seismic_map(self):
        """Mostrar mapa sísmico específico de Bolivia"""
        mapa_path = Path(__file__).parent / 'resources' / 'images' / self.config['mapa_sismico']
        
        if mapa_path.exists():
            self.show_image(str(mapa_path), "Mapa Sísmico de Bolivia - CNBDS 2023")
        else:
            self.show_warning("Mapa sísmico no encontrado")
    
    def _validate_bolivia_params(self):
        """Validar parámetros específicos de Bolivia"""
        params = self.seismic_params_widget.get_parameters()
        
        # Validaciones según CNBDS 2023
        warnings = []
        
        if 'Fa' in params:
            fa = params['Fa']
            if fa < 0.8 or fa > 3.0:
                warnings.append(f"Factor Fa ({fa}) fuera del rango típico (0.8-3.0)")
        
        if 'Fv' in params:
            fv = params['Fv']
            if fv < 0.6 or fv > 2.5:
                warnings.append(f"Factor Fv ({fv}) fuera del rango típico (0.6-2.5)")
        
        if 'So' in params:
            so = params['So']
            if so < 0.1 or so > 4.0:
                warnings.append(f"Parámetro So ({so}) fuera del rango típico (0.1-4.0)")
        
        # Mostrar advertencias si las hay
        if warnings:
            message = "Advertencias de parámetros:\n" + "\n".join(warnings)
            self.show_warning(message)
    
    def calculate_bolivia_spectrum(self):
        """Calcular espectro de respuesta según CNBDS 2023"""
        try:
            params = self.seismic_params_widget.get_parameters()
            
            # Parámetros necesarios para Bolivia
            Fa = params.get('Fa', 1.86)
            Fv = params.get('Fv', 0.63)
            So = params.get('So', 2.9)
            
            # Calcular parámetros espectrales según CNBDS 2023
            To = 0.15 * Fv / Fa
            Ts = 0.5 * Fv / Fa
            TL = 4 * Fv / Fa
            SDS = 2.5 * Fa * So
            SD1 = 1.25 * Fv * So
            
            # Actualizar objeto sismo
            self.sismo.To = To
            self.sismo.Ts = Ts
            self.sismo.TL = TL
            self.sismo.SDS = SDS
            self.sismo.SD1 = SD1
            
            # Mostrar resultados
            info = f"""Parámetros Espectrales Calculados (CNBDS 2023):
            
To = {To:.4f} s
Ts = {Ts:.4f} s  
TL = {TL:.4f} s
SDS = {SDS:.4f}
SD1 = {SD1:.4f}"""
            
            self.show_info(info)
            
            return True
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Bolivia: {str(e)}")
            return False
    
    def generate_report(self):
        """Generar reporte específico de Bolivia"""
        try:
            # Validar parámetros antes de generar
            if not self._validate_required_params():
                return
            
            # Calcular espectro
            if not self.calculate_bolivia_spectrum():
                return
            
            # Seleccionar directorio de salida
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # Actualizar datos
            self.update_seismic_data()
            
            # Generar usando memoria específica de Bolivia
            from apps.bolivia.memory_bolivia import generate_memory
            
            success = generate_memory(
                self.sismo, 
                output_dir,
                delete_tex=True,  # Limpiar archivos temporales
                run_twice=True    # Ejecutar LaTeX dos veces para referencias
            )
            
            if success:
                self.show_info(f"Memoria de cálculo Bolivia generada en:\n{output_dir}")
            else:
                self.show_error("Error generando la memoria de cálculo")
                
        except Exception as e:
            self.show_error(f"Error en generación de reporte Bolivia: {str(e)}")
    
    def _validate_required_params(self) -> bool:
        """Validar que todos los parámetros requeridos estén presentes"""
        project_data = self.get_project_data()
        params = self.seismic_params_widget.get_parameters()
        
        required_project = ['proyecto', 'ubicacion', 'autor']
        required_params = ['Fa', 'Fv', 'So']
        
        # Validar datos del proyecto
        for field in required_project:
            if not project_data.get(field, '').strip():
                self.show_error(f"El campo '{field}' es requerido")
                return False
        
        # Validar parámetros sísmicos
        for param in required_params:
            if param not in params:
                self.show_error(f"El parámetro '{param}' es requerido")
                return False
        
        return True


# Función de conveniencia para crear app de Bolivia
def create_bolivia_app():
    """Crear aplicación específica de Bolivia"""
    from core.config.app_config import BOLIVIA_CONFIG
    return BoliviaSeismicApp(BOLIVIA_CONFIG)