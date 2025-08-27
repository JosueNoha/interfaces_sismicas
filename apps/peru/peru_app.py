"""
Módulo específico para Perú - Extensiones y funcionalidades particulares
"""

import numpy as np
from typing import Dict, Any, Tuple
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox, QGridLayout

from core.app_factory import UnifiedSeismicApp


class PeruSeismicApp(UnifiedSeismicApp):
    """Extensiones específicas para la aplicación de Perú"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Tabla de zonas sísmicas del Perú
        self.zonas_peru = {
            'Zona 1': 0.10,
            'Zona 2': 0.25, 
            'Zona 3': 0.35,
            'Zona 4': 0.45
        }
        
        # Factores de uso según E.030
        self.factores_uso = {
            'A1 - Esenciales': 1.5,
            'A2 - Importantes': 1.3,
            'B - Comunes': 1.0,
            'C - Menores': 0.8
        }
        
        # Agregar funcionalidades específicas de Perú
        self._setup_peru_extensions()
    
    def _setup_peru_extensions(self):
        """Configurar extensiones específicas de Perú"""
        # Agregar selectores de zona y categoría
        self._add_zone_selector()
        self._add_category_selector()
        
        # Configurar validaciones específicas de Perú
        self._setup_peru_validations()
    
    def _add_zone_selector(self):
        """Agregar selector de zona sísmica"""
        layout = self.ui.seismic_params_layout
        current_row = layout.rowCount()
        
        # Etiqueta y combo para zona
        self.label_zona = QLabel("Zona Sísmica:")
        self.cb_zona = QComboBox()
        self.cb_zona.addItems(list(self.zonas_peru.keys()))
        self.cb_zona.setCurrentText('Zona 2')  # Lima por defecto
        self.cb_zona.currentTextChanged.connect(self._on_zone_changed)
        
        layout.addWidget(self.label_zona, current_row, 0)
        layout.addWidget(self.cb_zona, current_row, 1)
    
    def _add_category_selector(self):
        """Agregar selector de categoría de edificación"""
        layout = self.ui.seismic_params_layout
        current_row = layout.rowCount()
        
        # Etiqueta y combo para categoría
        self.label_cat_uso = QLabel("Categoría:")
        self.cb_cat_uso = QComboBox()
        self.cb_cat_uso.addItems(list(self.factores_uso.keys()))
        self.cb_cat_uso.setCurrentText('B - Comunes')
        self.cb_cat_uso.currentTextChanged.connect(self._on_category_changed)
        
        layout.addWidget(self.label_cat_uso, current_row, 0)
        layout.addWidget(self.cb_cat_uso, current_row, 1)
    
    def _on_zone_changed(self, zone_text: str):
        """Callback cuando cambia la zona sísmica"""
        z_value = self.zonas_peru.get(zone_text, 0.25)
        
        # Actualizar el spinbox de Z si existe
        if hasattr(self.seismic_params_widget, 'sb_z'):
            self.seismic_params_widget.sb_z.setValue(z_value)
        
        self._validate_peru_params()
    
    def _on_category_changed(self, category_text: str):
        """Callback cuando cambia la categoría"""
        u_value = self.factores_uso.get(category_text, 1.0)
        
        # Actualizar el combo de U si existe
        if hasattr(self.seismic_params_widget, 'cb_u'):
            index = self.seismic_params_widget.cb_u.findText(str(u_value))
            if index >= 0:
                self.seismic_params_widget.cb_u.setCurrentIndex(index)
        
        self._validate_peru_params()
    
    def _setup_peru_validations(self):
        """Configurar validaciones específicas para parámetros de Perú"""
        # Conectar validaciones cuando cambien los parámetros
        if hasattr(self.seismic_params_widget, 'sb_z'):
            self.seismic_params_widget.sb_z.valueChanged.connect(
                self._validate_peru_params
            )
        if hasattr(self.seismic_params_widget, 'sb_s'):
            self.seismic_params_widget.sb_s.valueChanged.connect(
                self._validate_peru_params
            )
    
    def _validate_peru_params(self):
        """Validar parámetros específicos de Perú según E.030"""
        params = self.seismic_params_widget.get_parameters()
        warnings = []
        
        # Validar factor Z
        if 'Z' in params:
            z = params['Z']
            if z < 0.10 or z > 0.45:
                warnings.append(f"Factor Z ({z}) fuera del rango E.030 (0.10-0.45)")
        
        # Validar factor S
        if 'S' in params:
            s = params['S']
            if s < 0.80 or s > 2.00:
                warnings.append(f"Factor S ({s}) fuera del rango típico (0.80-2.00)")
        
        # Validar períodos
        if 'Tp' in params and 'Tl' in params:
            tp = params['Tp']
            tl = params['Tl']
            if tp >= tl:
                warnings.append(f"Tp ({tp}) debe ser menor que Tl ({tl})")
        
        # Mostrar advertencias si las hay
        if warnings:
            message = "Advertencias de parámetros E.030:\n" + "\n".join(warnings)
            self.show_warning(message)
    
    def calculate_peru_spectrum(self) -> Tuple[np.ndarray, np.ndarray]:
        """Calcular espectro de respuesta según E.030"""
        try:
            params = self.seismic_params_widget.get_parameters()
            
            # Parámetros de E.030
            Z = params.get('Z', 0.25)
            U = float(params.get('U', 1.0))
            S = params.get('S', 1.20)
            Tp = params.get('Tp', 0.6)
            Tl = params.get('Tl', 2.0)
            
            # Factor de reducción (asumir R=8 para pórticos)
            R = 8.0
            
            # Crear vector de períodos
            T = np.linspace(0.1, 5.0, 100)
            
            # Calcular espectro según E.030
            Sa = np.zeros_like(T)
            
            for i, period in enumerate(T):
                if period <= Tp:
                    # Sa = Z*U*S*(1 + T/Tp * 1.5)/R
                    Sa[i] = Z * U * S * (1 + period/Tp * 1.5) / R
                elif Tp < period <= Tl:
                    # Sa = Z*U*S*2.5/R
                    Sa[i] = Z * U * S * 2.5 / R
                else:
                    # Sa = Z*U*S*2.5*Tl/T/R
                    Sa[i] = Z * U * S * 2.5 * Tl / period / R
            
            # Actualizar objeto sismo
            self.sismo.Z = Z
            self.sismo.U = U
            self.sismo.S = S
            self.sismo.Tp = Tp
            self.sismo.Tl = Tl
            self.sismo.R = R
            self.sismo.Sa_max = np.max(Sa)
            
            # Mostrar información del espectro
            info = f"""Espectro de Respuesta E.030 Calculado:

Parámetros:
Z = {Z}
U = {U}
S = {S}
Tp = {Tp} s
Tl = {Tl} s
R = {R}

Sa máxima = {np.max(Sa):.4f} g"""
            
            self.show_info(info)
            
            return T, Sa
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Perú: {str(e)}")
            return np.array([]), np.array([])
    
    def calculate_static_forces(self):
        """Calcular fuerzas estáticas equivalentes según E.030"""
        try:
            params = self.seismic_params_widget.get_parameters()
            
            # Obtener parámetros básicos
            Z = params.get('Z', 0.25)
            U = float(params.get('U', 1.0))
            S = params.get('S', 1.20)
            
            # Asumir valores típicos para el ejemplo
            C = 2.5  # Factor de amplificación sísmica
            R = 8.0  # Factor de reducción
            
            # Calcular coeficiente sísmico
            coef_sismico = Z * U * C * S / R
            
            # Mostrar resultado
            info = f"""Coeficiente Sísmico (E.030):

C/R = {coef_sismico:.4f}

Donde:
Z = {Z} (Factor de zona)
U = {U} (Factor de uso)  
C = {C} (Factor de amplificación)
S = {S} (Factor de suelo)
R = {R} (Factor de reducción)"""
            
            self.show_info(info)
            
            # Actualizar modelo
            self.sismo.coef_sismico = coef_sismico
            
        except Exception as e:
            self.show_error(f"Error calculando fuerzas estáticas: {str(e)}")
    
    def generate_report(self):
        """Generar reporte específico de Perú"""
        try:
            # Validar parámetros requeridos
            if not self._validate_required_params():
                return
            
            # Calcular espectro
            T, Sa = self.calculate_peru_spectrum()
            if len(Sa) == 0:
                return
            
            # Seleccionar directorio
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # Actualizar datos
            self.update_seismic_data()
            
            # Generar usando memoria específica de Perú
            from apps.peru.memory_peru import generate_memory
            
            success = generate_memory(
                self.sismo,
                output_dir,
                delete_tex=True,
                run_twice=True
            )
            
            if success:
                self.show_info(f"Memoria de cálculo Perú generada en:\n{output_dir}")
            else:
                self.show_error("Error generando la memoria de cálculo")
                
        except Exception as e:
            self.show_error(f"Error en generación de reporte Perú: {str(e)}")
    
    def _validate_required_params(self) -> bool:
        """Validar parámetros requeridos para Perú"""
        project_data = self.get_project_data()
        params = self.seismic_params_widget.get_parameters()
        
        required_project = ['proyecto', 'ubicacion', 'autor']
        required_params = ['Z', 'U', 'S', 'Tp', 'Tl']
        
        # Validar datos del proyecto
        for field in required_project:
            if not project_data.get(field, '').strip():
                self.show_error(f"El campo '{field}' es requerido")
                return False
        
        # Validar parámetros sísmicos
        for param in required_params:
            if param not in params:
                self.show_error(f"El parámetro '{param}' es requerido para E.030")
                return False
        
        return True


# Función de conveniencia para crear app de Perú
def create_peru_app():
    """Crear aplicación específica de Perú"""
    from core.config.app_config import PERU_CONFIG
    return PeruSeismicApp(PERU_CONFIG)