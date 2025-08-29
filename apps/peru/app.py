"""
Aplicación específica para Perú - E.030
Simplificada usando funcionalidad centralizada
"""

from typing import Tuple
from PyQt5.QtWidgets import QLabel, QComboBox
from core.base.app_base import AppBase
from core.config.app_config import PERU_CONFIG
from core.utils.common_validations import create_validator
from ui.main_window import Ui_MainWindow


class PeruSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Perú - E.030"""
    
    def __init__(self, config=None):
        if config is None:
            config = PERU_CONFIG
            
        super().__init__(config, Ui_MainWindow)
        
        # Validador específico para Perú
        self.validator = create_validator(self.config)
        
        # Datos específicos E.030
        self.zonas_peru = {
            'Zona 1': 0.10, 'Zona 2': 0.25, 'Zona 3': 0.35, 'Zona 4': 0.45
        }
        
        self.factores_uso = {
            'A1 - Esenciales': 1.5, 'A2 - Importantes': 1.3,
            'B - Comunes': 1.0, 'C - Menores': 0.8
        }
        
        # Configurar extensiones específicas
        self._setup_peru_extensions()
    
    def _setup_peru_extensions(self):
        """Configurar funcionalidad específica de Perú"""
        # Agregar selectores específicos de E.030
        self._add_peru_selectors()
        
        # Conectar validaciones
        self._connect_peru_validations()
    
    def _add_peru_selectors(self):
        """Agregar selectores específicos de Perú"""
        try:
            if not hasattr(self.ui, 'seismic_params_layout'):
                return
                
            layout = self.ui.seismic_params_layout
            current_row = layout.rowCount()
            
            # Selector de zona sísmica
            self.label_zona = QLabel("Zona Sísmica:")
            self.cb_zona = QComboBox()
            self.cb_zona.addItems(list(self.zonas_peru.keys()))
            self.cb_zona.setCurrentText('Zona 2')  # Lima por defecto
            self.cb_zona.currentTextChanged.connect(self._on_zone_changed)
            
            layout.addWidget(self.label_zona, current_row, 0)
            layout.addWidget(self.cb_zona, current_row, 1)
            
            # Selector de categoría
            self.label_categoria = QLabel("Categoría:")
            self.cb_categoria = QComboBox()
            self.cb_categoria.addItems(list(self.factores_uso.keys()))
            self.cb_categoria.setCurrentText('B - Comunes')
            self.cb_categoria.currentTextChanged.connect(self._on_category_changed)
            
            layout.addWidget(self.label_categoria, current_row, 2)
            layout.addWidget(self.cb_categoria, current_row, 3)
            
        except Exception as e:
            print(f"Error agregando selectores Perú: {e}")
    
    def _connect_peru_validations(self):
        """Conectar validaciones específicas para Perú"""
        if hasattr(self, 'seismic_params_widget'):
            self.seismic_params_widget.connect_param_changed(self._validate_peru_params)
    
    def _on_zone_changed(self, zone_text: str):
        """Callback cuando cambia la zona sísmica"""
        z_value = self.zonas_peru.get(zone_text, 0.25)
        
        # Actualizar parámetro Z en el widget si existe
        if hasattr(self, 'seismic_params_widget'):
            params = self.seismic_params_widget.get_parameters()
            params['Z'] = z_value
            self.seismic_params_widget.set_parameters(params)
        
        self.sismo.Z = z_value
        self._validate_peru_params()
    
    def _on_category_changed(self, category_text: str):
        """Callback cuando cambia la categoría"""
        u_value = self.factores_uso.get(category_text, 1.0)
        
        # Actualizar parámetro U en el widget si existe
        if hasattr(self, 'seismic_params_widget'):
            params = self.seismic_params_widget.get_parameters()
            params['U'] = u_value
            self.seismic_params_widget.set_parameters(params)
        
        self.sismo.U = u_value
        self._validate_peru_params()
    
    def _validate_peru_params(self):
        """Validar parámetros específicos de Perú usando validador centralizado"""
        if not hasattr(self, 'seismic_params_widget'):
            return
            
        try:
            params = self.seismic_params_widget.get_parameters()
            is_valid, warnings = self.validator.validate_parameters(params)
            
            if warnings:
                message = "⚠️ Advertencias E.030:\n\n" + "\n".join(f"• {w}" for w in warnings)
                message += "\n\nVerifique que los valores sean apropiados."
                self.show_warning(message)
                
        except Exception as e:
            print(f"Error validando parámetros Perú: {e}")
    
    def calculate_peru_spectrum(self) -> Tuple:
        """Calcular espectro de respuesta según E.030"""
        try:
            import numpy as np
            
            # Obtener parámetros desde interfaz
            if hasattr(self, 'seismic_params_widget'):
                params = self.seismic_params_widget.get_parameters()
                self.sismo.Z = float(params.get('Z', self.sismo.Z))
                self.sismo.U = float(params.get('U', self.sismo.U))
                self.sismo.S = float(params.get('S', self.sismo.S))
                self.sismo.Tp = float(params.get('Tp', self.sismo.Tp))
                self.sismo.Tl = float(params.get('Tl', self.sismo.Tl))
            
            # Generar espectro E.030
            T = np.arange(0, 4+0.01, 0.01)
            Sa = np.zeros_like(T)
            
            # Tramos según E.030
            idx1 = T <= self.sismo.Tp
            idx2 = (T > self.sismo.Tp) & (T <= self.sismo.Tl)  
            idx3 = T > self.sismo.Tl
            
            base_value = 2.5 * self.sismo.Z * self.sismo.U * self.sismo.S
            
            Sa[idx1] = base_value
            Sa[idx2] = base_value * self.sismo.Tp / T[idx2]
            Sa[idx3] = base_value * self.sismo.Tp * self.sismo.Tl / (T[idx3]**2)
            
            # Almacenar para gráficos
            self.sismo.Sa_max = max(Sa) * 1.2
            
            info = f"""✅ Espectro E.030 Calculado:

📊 PARÁMETROS:
   Z = {self.sismo.Z:.3f}, U = {self.sismo.U:.1f}, S = {self.sismo.S:.2f}
   Tp = {self.sismo.Tp:.2f} s, Tl = {self.sismo.Tl:.2f} s

📈 RESULTADOS:
   Sa máxima = {np.max(Sa):.4f} g
   Puntos generados: {len(T)}"""
            
            self.show_info(info)
            return T, Sa
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Perú: {str(e)}")
            return [], []
    
    def generate_report(self):
        """Generar reporte específico de Perú"""
        try:
            # Validar datos del proyecto
            project_data = self.get_project_data()
            from core.utils.common_validations import validate_project_data
            
            is_valid, errors = validate_project_data(project_data)
            if not is_valid:
                self.show_error("Errores en datos:\n" + "\n".join(f"• {e}" for e in errors))
                return
            
            # Calcular espectro
            T, Sa = self.calculate_peru_spectrum()
            if len(Sa) == 0:
                return
            
            # Seleccionar directorio
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # Actualizar modelo
            self.update_sismo_data()
            
            # Generar memoria
            try:
                from apps.peru.memory import PeruMemoryGenerator
                
                memory_generator = PeruMemoryGenerator(self.sismo, output_dir)
                tex_file = memory_generator.generate_memory()
                
                self.show_info(
                    f"✅ Memoria Perú generada!\n\n"
                    f"📁 {output_dir}\n"
                    f"📄 {tex_file.name}\n\n"
                    f"Incluye: parámetros E.030, espectro, análisis modal"
                )
                
            except ImportError as e:
                self.show_error(f"Error importando generador Perú: {e}")
            except Exception as e:
                self.show_error(f"Error generando memoria: {e}")
                
        except Exception as e:
            self.show_error(f"Error en reporte Perú: {str(e)}")