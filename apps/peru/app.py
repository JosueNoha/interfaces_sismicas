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
from PyQt5.QtWidgets import QLabel, QComboBox, QLineEdit


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
        
        # Inicializar valores por defecto después de crear la interfaz
        self._actualize_zona(1)  # Zona 2 por defecto
        self._actualize_categoria()
    
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
            self.cb_zona.addItems(['1', '2', '3', '4'])  # Solo números
            self.cb_zona.setCurrentText('2')  # Lima por defecto
            self.cb_zona.currentIndexChanged.connect(self._actualize_zona)
            
            layout.addWidget(self.label_zona, current_row, 0)
            layout.addWidget(self.cb_zona, current_row, 1)
            
            # Selector de tipo de suelo
            self.label_suelo = QLabel("Tipo de Suelo:")
            self.cb_suelo = QComboBox()
            self.cb_suelo.addItems(['S0', 'S1', 'S2', 'S3'])
            self.cb_suelo.setCurrentText('S1')
            self.cb_suelo.currentTextChanged.connect(self._actualize_suelo)
            
            layout.addWidget(self.label_suelo, current_row, 2)
            layout.addWidget(self.cb_suelo, current_row, 3)
            
            current_row += 1
            
            # Selector de categoría
            self.label_categoria = QLabel("Categoría:")
            self.cb_categoria = QComboBox()
            self.cb_categoria.addItems(['A1', 'A2', 'B', 'C', 'D'])
            self.cb_categoria.setCurrentText('B')
            self.cb_categoria.currentTextChanged.connect(self._actualize_categoria)
            
            layout.addWidget(self.label_categoria, current_row, 0)
            layout.addWidget(self.cb_categoria, current_row, 1)
            
            # AGREGAR parámetros específicos E.030
            self._add_peru_parameter_display_internal(layout, current_row + 1)
            
        except Exception as e:
            print(f"Error agregando selectores Perú: {e}")

    def _actualize_zona(self, index):
        """Actualizar factor Z según zona"""
        Z = {'0': '0.10', '1': '0.25', '2': '0.35', '3': '0.45'}  # index 0-3
        z_value = float(Z[str(index)])
        
        self.sismo.Z = z_value
        self.le_z_display.setText(f'{z_value:.3f}')
        self._actualize_suelo()  # Recalcular S que depende de zona

    def _actualize_suelo(self):
        """Actualizar parámetros S, Tp, Tl según tipo de suelo"""
        import pandas as pd
        
        S = pd.DataFrame({
            'S0': [0.8] * 4,
            'S1': [1.0] * 4,
            'S2': [1.6, 1.2, 1.15, 1.05],
            'S3': [2.0, 1.4, 1.2, 1.1]
        })
        Tp = {'S0': 0.3, 'S1': 0.4, 'S2': 0.6, 'S3': 1.0}
        Tl = {'S0': 3.0, 'S1': 2.5, 'S2': 2.0, 'S3': 1.6}
        
        zona_index = self.cb_zona.currentIndex()
        suelo = self.cb_suelo.currentText()
        
        s_value = S.loc[zona_index, suelo]
        tp_value = Tp[suelo]
        tl_value = Tl[suelo]
        
        # Actualizar modelo sísmico
        self.sismo.S = s_value
        self.sismo.Tp = tp_value
        self.sismo.Tl = tl_value
        
        # Actualizar campos de display
        self.le_s_display.setText(f'{s_value:.2f}')
        self.le_tp_display.setText(f'{tp_value:.1f}')
        self.le_tl_display.setText(f'{tl_value:.1f}')

    def _actualize_categoria(self):
        """Actualizar factor U según categoría"""
        U = {'A1': 1.5, 'A2': 1.5, 'B': 1.3, 'C': 1.0, 'D': 1.0}
        cat = self.cb_categoria.currentText()
        u_value = U[cat]
        
        self.sismo.U = u_value
        self.le_u_display.setText(f'{u_value:.1f}')
        
        # Habilitar edición para A1 y D (valores variables)
        if cat in ['A1', 'D']:
            self.le_u_display.setReadOnly(False)
            self.le_u_display.setStyleSheet("QLineEdit { background-color: white; }")
        else:
            self.le_u_display.setReadOnly(True)
            self.le_u_display.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

    def _add_peru_parameter_display(self, layout, start_row):
        """Agregar campos de parámetros específicos E.030 (solo lectura)"""
        try:
            current_row = start_row
            
            # Factor de suelo (editable)
            self.label_soil_factor = QLabel("Factor Suelo:")
            self.le_soil_factor = QLineEdit("1.0")
            self.le_soil_factor.setToolTip("Factor de amplificación por tipo de suelo")
            self.le_soil_factor.textChanged.connect(self._validate_soil_factor)
            
            layout.addWidget(self.label_soil_factor, current_row, 0)
            layout.addWidget(self.le_soil_factor, current_row, 1)
            
            current_row += 1
            
            # Parámetros E.030 (solo lectura)
            readonly_style = "QLineEdit { background-color: #f0f0f0; }"
            
            # Fila Z, U
            self.label_z_display = QLabel("Z:")
            self.le_z_display = QLineEdit()
            self.le_z_display.setReadOnly(True)
            self.le_z_display.setStyleSheet(readonly_style)
            
            self.label_u_display = QLabel("U:")
            self.le_u_display = QLineEdit()
            self.le_u_display.setReadOnly(True)
            self.le_u_display.setStyleSheet(readonly_style)
            
            layout.addWidget(self.label_z_display, current_row, 0)
            layout.addWidget(self.le_z_display, current_row, 1)
            layout.addWidget(self.label_u_display, current_row, 2)
            layout.addWidget(self.le_u_display, current_row, 3)
            
            current_row += 1
            
            # Fila S, Tp, Tl
            self.label_s_display = QLabel("S:")
            self.le_s_display = QLineEdit()
            self.le_s_display.setReadOnly(True)
            self.le_s_display.setStyleSheet(readonly_style)
            
            self.label_tp_display = QLabel("Tp (s):")
            self.le_tp_display = QLineEdit()
            self.le_tp_display.setReadOnly(True)
            self.le_tp_display.setStyleSheet(readonly_style)
            
            self.label_tl_display = QLabel("Tl (s):")
            self.le_tl_display = QLineEdit()
            self.le_tl_display.setReadOnly(True)
            self.le_tl_display.setStyleSheet(readonly_style)
            
            layout.addWidget(self.label_s_display, current_row, 0)
            layout.addWidget(self.le_s_display, current_row, 1)
            layout.addWidget(self.label_tp_display, current_row, 2)
            layout.addWidget(self.le_tp_display, current_row, 3)
            
            current_row += 1
            
            layout.addWidget(self.label_tl_display, current_row, 0)
            layout.addWidget(self.le_tl_display, current_row, 1)
            
        except Exception as e:
            print(f"Error agregando parámetros Perú: {e}")
            
    def _validate_soil_factor(self):
        """Validar factor de suelo"""
        try:
            value = float(self.le_soil_factor.text())
            if 0.8 <= value <= 2.0:
                self.le_soil_factor.setStyleSheet("")
                self.sismo.soil_factor = value
            else:
                self.le_soil_factor.setStyleSheet("QLineEdit { border: 2px solid orange; }")
        except ValueError:
            self.le_soil_factor.setStyleSheet("QLineEdit { border: 2px solid red; }")

    def _update_peru_parameters_display(self):
        """Actualizar parámetros E.030 en campos de solo lectura"""
        if hasattr(self, 'seismic_params_widget'):
            params = self.seismic_params_widget.get_parameters()
            
            self.le_z_display.setText(f"{params.get('Z', 0.0):.3f}")
            self.le_u_display.setText(f"{params.get('U', 0.0):.1f}")
            self.le_s_display.setText(f"{params.get('S', 0.0):.2f}")
            self.le_tp_display.setText(f"{params.get('Tp', 0.0):.2f}")
            self.le_tl_display.setText(f"{params.get('Tl', 0.0):.2f}")
        else:
            # Valores directos del modelo
            self.le_z_display.setText(f"{getattr(self.sismo, 'Z', 0.0):.3f}")
            self.le_u_display.setText(f"{getattr(self.sismo, 'U', 0.0):.1f}")
            self.le_s_display.setText(f"{getattr(self.sismo, 'S', 0.0):.2f}")
            self.le_tp_display.setText(f"{getattr(self.sismo, 'Tp', 0.0):.2f}")
            self.le_tl_display.setText(f"{getattr(self.sismo, 'Tl', 0.0):.2f}")
        
    def _connect_peru_validations(self):
        """Conectar validaciones específicas para Perú"""
        if hasattr(self, 'seismic_params_widget'):
            self.seismic_params_widget.connect_param_changed(self._validate_peru_params)
    
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
            
            # Actualizar display de parámetros
            self._update_peru_parameters_display()
            
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