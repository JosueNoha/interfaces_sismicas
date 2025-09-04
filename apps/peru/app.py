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
from PyQt5.QtWidgets import QFrame, QComboBox, QLineEdit


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
        self._initialize_peru_defaults()

    
    def _setup_peru_extensions(self):
        """Configurar funcionalidad específica de Perú"""
        # Agregar selectores específicos de E.030
        self._add_peru_selectors()
        
        # Conectar validaciones
        self._connect_peru_validations()
    
    def _add_peru_selectors(self):
        """Agregar selectores específicos de Perú"""
        try:
            if not hasattr(self.ui, 'seismic_params_card'):
                return
                
            card = self.ui.seismic_params_card
            
            # Selector de zona sísmica
            self.cb_zona = QComboBox()
            self.cb_zona.addItems(['1', '2', '3', '4'])  # Solo números
            self.cb_zona.setCurrentText('2')  # Lima por defecto
            self.cb_zona.currentIndexChanged.connect(self._actualize_zona)
            
            
            # Selector de tipo de suelo
            self.cb_suelo = QComboBox()
            self.cb_suelo.addItems(['S0', 'S1', 'S2', 'S3'])
            self.cb_suelo.setCurrentText('S1')
            self.cb_suelo.currentTextChanged.connect(self._actualize_suelo)
            
            
            # Selector de categoría
            self.cb_categoria = QComboBox()
            self.cb_categoria.addItems(['A1', 'A2', 'B', 'C', 'D'])
            self.cb_categoria.setCurrentText('B')
            self.cb_categoria.currentTextChanged.connect(self._actualize_categoria)
            
            current_row = 0
            card.add_field(current_row,0,'Zona Sísmica:',self.cb_zona,'cb_zona','Zona del Proyecto')
            card.add_field(current_row,2,'Tipo de Suelo:',self.cb_suelo,'cb_suelo','Tipo de Suelo')
            card.add_field(current_row,4,'Categoría:',self.cb_categoria,'cb_categoria','Categoría del Proyecto')
            
            # AGREGAR parámetros específicos E.030
            self._add_peru_parameter_display(card,current_row+1)
            
        except Exception as e:
            print(f"Error agregando selectores Perú: {e}")

    def _actualize_zona(self):
        """Actualizar factor Z según zona"""
        try:
            Z = {'0': '0.10', '1': '0.25', '2': '0.35', '3': '0.45'}  # index 0-3
            z_value = float(Z[str(self.cb_suelo.currentIndex())])
            
            self.sismo.Z = z_value
            # Verificar que el campo existe antes de actualizarlo
            if hasattr(self, 'le_z_display'):
                self.le_z_display.setText(f'{z_value:.3f}')
            
            self._actualize_suelo()  # Recalcular S que depende de zona
            
        except Exception as e:
            print(f"Error actualizando zona: {e}")

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
            #self.le_u_display.setStyleSheet("QLineEdit { background-color: white; }")
        else:
            self.le_u_display.setReadOnly(True)
            #self.le_u_display.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

    def get_espectro(self):
        import numpy as np
        Z,U,S,Tp,Tl = self.sismo.Z,self.sismo.U,self.sismo.S,self.sismo.Tp,self.sismo.Tl 
        
        T = np.arange(0, 4+0.01, 0.01)
        Sa = np.zeros_like(T)

        idx1 = T <= Tp
        idx2 = (T > Tp) & (T <= Tl)
        idx3 = T >= Tl

        # Tramo 1
        Sa[idx1] = 2.5*Z*U*S
        # Tramo 2
        Sa[idx2] = 2.5*Tp/T[idx2]*Z*U*S
        # Tramo 3 
        Sa[idx3] = 2.5*Tp*Tl/T[idx3]**2*Z*U*S
        
        self.sismo.Sa_max = max(Sa)*1.2
        
        
        return T, Sa
    
    def save_espectro(self,output_dir):
        import numpy as np
        from  pathlib import Path
        T,Sa = self.get_espectro()
        datos = np.column_stack((T, Sa))
        np.savetxt(Path(output_dir) / 'espectro_peru.txt' , datos, fmt="%.3f")
            
    def _initialize_peru_defaults(self):
        """Inicializar valores por defecto de Perú después de crear la interfaz"""
        try:
            # Verificar que todos los widgets necesarios existan
            required_widgets = ['cb_zona', 'cb_categoria', 'cb_suelo']
            for widget_name in required_widgets:
                if not hasattr(self, widget_name):
                    print(f"Widget {widget_name} no encontrado, reintentando...")
                    self._initialize_peru_defaults()
                    return
            
            print("✅ Inicializando valores por defecto Perú...")
            self._actualize_zona()  # Zona 2 por defecto (index 1)
            self._actualize_categoria()
            print("✅ Valores inicializados correctamente")
            
        except Exception as e:
            print(f"Error inicializando valores Perú: {e}")

    def _add_peru_parameter_display(self, card, current_row):
        """Agregar campos de parámetros específicos E.030 (solo lectura)"""
        try:
            self.le_z_display = QLineEdit()
            self.le_z_display.setReadOnly(True)
            self.le_u_display = QLineEdit()
            self.le_u_display.setReadOnly(True)
            self.le_s_display = QLineEdit()
            self.le_s_display.setReadOnly(True)
            self.le_tp_display = QLineEdit()
            self.le_tp_display.setReadOnly(True)
            self.le_tl_display = QLineEdit()
            self.le_tl_display.setReadOnly(True)
            
            card.add_field(current_row,0,'Z:',self.le_z_display,'le_z_display','Factor Z')
            card.add_field(current_row,2,'S:',self.le_s_display,'le_s_display','Factor S')
            card.add_field(current_row,4,'U:',self.le_u_display,'le_u_display','Factor U')
            card.add_field(current_row+1,0,'Tp (s):',self.le_tp_display,'le_tp_display','Periodo Tp')
            card.add_field(current_row+1,2,'Tl (s):',self.le_tl_display,'le_tl_display','Periodo Tl')
            
        except Exception as e:
            print(f"Error agregando parámetros Perú: {e}")
            

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
    
    
    def generate_report(self):
        """Generar reporte específico de Perú"""
        try:
            # Seleccionar directorio
            output_dir = self.get_output_directory()
            
            if not output_dir:
                return
            
            from apps.peru.memory import PeruMemoryGenerator
            memory_generator = PeruMemoryGenerator(self.sismo, output_dir)
            
            self.save_espectro(memory_generator.output_dir)
            self.update_all_data()
            # Generar memoria
            tex_file = memory_generator.generate_memory()
                
            self.show_info(
                f"✅ Memoria Perú generada!\n\n"
                f"📁 {output_dir}\n"
                f"📄 {tex_file.name}\n\n"
                f"Incluye: parámetros E.030, espectro, análisis modal"
            )
       
                
        except Exception as e:
            self.show_error(f"Error en reporte Perú: {str(e)}")