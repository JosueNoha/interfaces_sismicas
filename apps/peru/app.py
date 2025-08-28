"""
Aplicación específica para Perú - E.030
Consolidada desde peru_app.py y seismic_peru.py eliminando duplicación
"""


from typing import Dict, Any, Tuple
from PyQt5.QtWidgets import QPushButton, QLabel, QComboBox

from core.base.app_base import AppBase
from core.config.app_config import PERU_CONFIG
from ui.main_window import Ui_MainWindow


class PeruSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Perú - E.030"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Usar configuración por defecto si no se proporciona
        if config is None:
            config = PERU_CONFIG
            
        # Llamar al constructor base con UI class
        super().__init__(config, Ui_MainWindow)
        
        # Parámetros específicos E.030 (consolidados desde seismic_peru.py)
        self._init_peru_params()
        
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
        
        # Configurar extensiones específicas de Perú
        self._setup_peru_extensions()
    
    def _init_peru_params(self):
        """Inicializar parámetros específicos de E.030"""
        defaults = self.config.get('parametros_defecto', {})
        
        # Parámetros sísmicos E.030
        self.sismo.Z = defaults.get('Z', 0.25)  # Factor de zona
        self.sismo.U = defaults.get('U', 1.00)  # Factor de uso
        self.sismo.S = defaults.get('S', 1.20)  # Factor de suelo
        self.sismo.Tp = defaults.get('Tp', 0.60)  # Período TP
        self.sismo.Tl = defaults.get('Tl', 2.00)  # Período TL
        
        # Configuración de unidades para Perú
        self.sismo.u_h = 'm'    # Unidad altura
        self.sismo.u_d = 'mm'   # Unidad desplazamiento
        self.sismo.u_f = 'kN'   # Unidad fuerza
    
    def _setup_peru_extensions(self):
        """Configurar extensiones específicas de Perú"""
        # Agregar selectores de zona y categoría
        self._add_zone_selector()
        self._add_category_selector()
        
        # Configurar validaciones específicas de Perú
        self._setup_peru_validations()
    
    def _add_zone_selector(self):
        """Agregar selector de zona sísmica"""
        try:
            if not hasattr(self.ui, 'seismic_params_layout'):
                return
                
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
        except Exception as e:
            print(f"Error agregando selector de zona: {e}")
    
    def _add_category_selector(self):
        """Agregar selector de categoría de edificación"""
        try:
            if not hasattr(self.ui, 'seismic_params_layout'):
                return
                
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
        except Exception as e:
            print(f"Error agregando selector de categoría: {e}")
    
    def _on_zone_changed(self, zone_text: str):
        """Callback cuando cambia la zona sísmica"""
        z_value = self.zonas_peru.get(zone_text, 0.25)
        
        # Actualizar el spinbox de Z si existe
        if hasattr(self, 'seismic_params_widget') and hasattr(self.seismic_params_widget, 'sb_z'):
            self.seismic_params_widget.sb_z.setValue(z_value)
        
        # Actualizar parámetro en el modelo
        self.sismo.Z = z_value
        self._validate_peru_params()
    
    def _on_category_changed(self, category_text: str):
        """Callback cuando cambia la categoría"""
        u_value = self.factores_uso.get(category_text, 1.0)
        
        # Actualizar el combo de U si existe
        if hasattr(self, 'seismic_params_widget') and hasattr(self.seismic_params_widget, 'cb_u'):
            index = self.seismic_params_widget.cb_u.findText(str(u_value))
            if index >= 0:
                self.seismic_params_widget.cb_u.setCurrentIndex(index)
        
        # Actualizar parámetro en el modelo
        self.sismo.U = u_value
        self._validate_peru_params()
    
    def _setup_peru_validations(self):
        """Configurar validaciones específicas para parámetros de Perú"""
        # Las validaciones se conectarán cuando el widget esté disponible
        pass
    
    def _validate_peru_params(self):
        """Validar parámetros específicos de Perú según E.030"""
        if not hasattr(self, 'seismic_params_widget'):
            return
            
        try:
            params = self.seismic_params_widget.get_parameters()
            warnings = []
            
            # Obtener rangos de validación desde configuración
            espectro_config = self.config.get('espectro_config', {})
            rangos_z = espectro_config.get('rangos_z', (0.10, 0.45))
            rangos_s = espectro_config.get('rangos_s', (0.80, 2.00))
            rangos_tp = espectro_config.get('rangos_tp', (0.4, 1.0))
            rangos_tl = espectro_config.get('rangos_tl', (1.5, 3.0))
            
            # Validar factor Z
            if 'Z' in params:
                z = params['Z']
                if z < rangos_z[0] or z > rangos_z[1]:
                    warnings.append(f"Factor Z ({z:.3f}) fuera del rango E.030 ({rangos_z[0]}-{rangos_z[1]})")
            
            # Validar factor S
            if 'S' in params:
                s = params['S']
                if s < rangos_s[0] or s > rangos_s[1]:
                    warnings.append(f"Factor S ({s:.2f}) fuera del rango típico ({rangos_s[0]}-{rangos_s[1]})")
            
            # Validar períodos
            if 'Tp' in params and 'Tl' in params:
                tp = params['Tp']
                tl = params['Tl']
                if tp >= tl:
                    warnings.append(f"Tp ({tp:.2f}s) debe ser menor que Tl ({tl:.2f}s)")
                if tp < rangos_tp[0] or tp > rangos_tp[1]:
                    warnings.append(f"Tp ({tp:.2f}s) fuera del rango típico ({rangos_tp[0]}-{rangos_tp[1]}s)")
                if tl < rangos_tl[0] or tl > rangos_tl[1]:
                    warnings.append(f"Tl ({tl:.2f}s) fuera del rango típico ({rangos_tl[0]}-{rangos_tl[1]}s)")
            
            # Mostrar advertencias si las hay
            if warnings:
                message = "⚠️ Advertencias de parámetros E.030:\n\n" + "\n".join(f"• {w}" for w in warnings)
                message += "\n\nVerifique que los valores sean apropiados para el proyecto."
                self.show_warning(message)
                
        except Exception as e:
            print(f"Error validando parámetros Perú: {e}")
    
    # ===== FUNCIONES DE ESPECTRO E.030 (consolidadas desde seismic_peru.py) =====
    
    def get_C(self, T):
        """Calcular factor de amplificación C según E.030"""
        if T <= self.sismo.Tp:
            return 2.5
        elif T <= self.sismo.Tl:
            return 2.5 * (self.sismo.Tp / T)
        else:
            return 2.5 * (self.sismo.Tp * self.sismo.Tl) / (T**2)
    
    def espectro_peru(self) -> Tuple:
        """Generar espectro de respuesta para Perú según E.030"""
        # ✅ Importación lazy de numpy para evitar recursión
        import numpy as np
        
        T = np.arange(0, 4+0.01, 0.01)
        Sa = np.zeros_like(T)

        # Calcular espectro por tramos según E.030
        idx1 = T <= self.sismo.Tp
        idx2 = (T > self.sismo.Tp) & (T <= self.sismo.Tl)  
        idx3 = T > self.sismo.Tl

        # Tramo 1: T ≤ Tp
        Sa[idx1] = 2.5 * self.sismo.Z * self.sismo.U * self.sismo.S
        
        # Tramo 2: Tp < T ≤ Tl
        Sa[idx2] = 2.5 * self.sismo.Tp / T[idx2] * self.sismo.Z * self.sismo.U * self.sismo.S
        
        # Tramo 3: T > Tl
        Sa[idx3] = 2.5 * self.sismo.Tp * self.sismo.Tl / (T[idx3]**2) * self.sismo.Z * self.sismo.U * self.sismo.S
        
        # Almacenar valor máximo para gráficos
        self.sismo.Sa_max = max(Sa) * 1.2
        
        return T, Sa
    
    def calculate_peru_spectrum(self) -> Tuple:
        """Calcular espectro de respuesta según E.030 con validaciones"""
        try:
            # ✅ Importación lazy de numpy
            import numpy as np
            
            # Obtener parámetros desde la interfaz
            if hasattr(self, 'seismic_params_widget'):
                params = self.seismic_params_widget.get_parameters()
                
                # Actualizar parámetros del modelo
                self.sismo.Z = params.get('Z', self.sismo.Z)
                self.sismo.U = float(params.get('U', self.sismo.U))
                self.sismo.S = params.get('S', self.sismo.S)
                self.sismo.Tp = params.get('Tp', self.sismo.Tp)
                self.sismo.Tl = params.get('Tl', self.sismo.Tl)
            
            # Generar espectro
            T, Sa = self.espectro_peru()
            
            # Factor de reducción (asumir R=8 para pórticos)
            R = 8.0
            self.sismo.R = R
            
            # Mostrar información del espectro
            info = f"""✅ Espectro de Respuesta E.030 Calculado:

📊 PARÁMETROS DE ENTRADA:
   Z = {self.sismo.Z:.3f} (Factor de zona)
   U = {self.sismo.U:.1f} (Factor de uso)
   S = {self.sismo.S:.2f} (Factor de suelo)
   Tp = {self.sismo.Tp:.2f} s (Período de plataforma)
   Tl = {self.sismo.Tl:.2f} s (Período largo)
   R = {R:.1f} (Factor de reducción asumido)

📈 RESULTADOS:
   Sa máxima = {np.max(Sa):.4f} g
   Espectro generado con {len(T)} puntos

🔍 Use este espectro para el análisis dinámico."""
            
            self.show_info(info)
            
            return T, Sa
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Perú: {str(e)}")
            return [], []
    
    def calculate_static_forces(self):
        """Calcular fuerzas estáticas equivalentes según E.030"""
        try:
            # Obtener parámetros básicos
            Z = self.sismo.Z
            U = self.sismo.U
            S = self.sismo.S
            
            # Asumir valores típicos para el ejemplo
            C = 2.5  # Factor de amplificación sísmica máximo
            R = 8.0  # Factor de reducción típico para pórticos
            
            # Calcular coeficiente sísmico
            coef_sismico = Z * U * C * S / R
            
            # Mostrar resultado
            info = f"""📊 Coeficiente Sísmico E.030:

🔢 FÓRMULA: C/R = (Z × U × C × S) / R

📈 VALORES:
   Z = {Z:.3f} (Factor de zona)
   U = {U:.1f} (Factor de uso)  
   C = {C:.1f} (Factor de amplificación)
   S = {S:.2f} (Factor de suelo)
   R = {R:.1f} (Factor de reducción)

🎯 RESULTADO:
   C/R = {coef_sismico:.4f}

💡 Este coeficiente se multiplica por el peso sísmico para obtener la fuerza cortante basal."""
            
            self.show_info(info)
            
            # Actualizar modelo
            self.sismo.coef_sismico = coef_sismico
            
        except Exception as e:
            self.show_error(f"Error calculando fuerzas estáticas: {str(e)}")
    
    def generate_spectrum_plot(self):
        """Generar gráfico del espectro dinámico"""
        try:
            # ✅ Importaciones lazy para evitar recursión
            import matplotlib
            matplotlib.use('Agg')
            from matplotlib.figure import Figure
            
            T, Sa = self.calculate_peru_spectrum()
            if len(Sa) == 0:
                return None
                
            fig = Figure(figsize=(10, 6), dpi=100)
            ax = fig.add_subplot(111)
            
            ax.plot(T, Sa, 'r-', linewidth=2, label='Espectro E.030')
            ax.axvline(x=self.sismo.Tp, color='g', linestyle='--', alpha=0.7)
            ax.axvline(x=self.sismo.Tl, color='b', linestyle='--', alpha=0.7)
            
            ax.text(self.sismo.Tp, max(Sa)*0.9, f'Tp={self.sismo.Tp}s', fontsize=10)
            ax.text(self.sismo.Tl, max(Sa)*0.8, f'Tl={self.sismo.Tl}s', fontsize=10)
            
            ax.set_xlabel('Período T (s)')
            ax.set_ylabel('Sa (m/s²)')
            ax.set_title('Espectro de Respuesta E.030')
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            fig.tight_layout()
            self.sismo.fig_spectrum = fig
            
            return fig
            
        except Exception as e:
            self.show_error(f"Error generando gráfico de espectro: {e}")
            return None
    
    def generate_report(self):
        """Generar reporte específico de Perú"""
        try:
            # Validar parámetros requeridos
            if not self._validate_required_params():
                return
            
            # Calcular espectro
            T, Sa = self.calculate_peru_spectrum()
            if len(Sa) == 0:
                self.show_error("No se pudo calcular el espectro. Verifique los parámetros.")
                return
            
            # Seleccionar directorio de salida
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # Actualizar todos los datos del modelo
            self.update_seismic_data()
            
            # Generar usando memoria específica de Perú
            try:
                from apps.peru.memory import PeruMemoryGenerator
                
                # Crear generador de memoria
                memory_generator = PeruMemoryGenerator(self.sismo, output_dir)
                
                # Generar memoria completa
                tex_file = memory_generator.generate_memory()
                
                self.show_info(
                    f"✅ Memoria de cálculo Perú generada exitosamente!\n\n"
                    f"📁 Directorio: {output_dir}\n"
                    f"📄 Archivo: {tex_file.name}\n\n"
                    f"La memoria incluye:\n"
                    f"• Parámetros sísmicos E.030\n"
                    f"• Espectro de respuesta\n"
                    f"• Análisis modal (si disponible)\n"
                    f"• Gráficos y tablas"
                )
                
            except ImportError as e:
                self.show_error(f"Error importando generador de memoria Perú: {e}")
            except Exception as e:
                self.show_error(f"Error generando memoria: {e}")
                
        except Exception as e:
            self.show_error(f"Error en generación de reporte Perú: {str(e)}")
    
    def _validate_required_params(self) -> bool:
        """Validar parámetros requeridos para Perú"""
        # Validar datos del proyecto
        project_data = self.get_project_data()
        required_project = ['proyecto', 'ubicacion', 'autor']
        
        for field in required_project:
            if not project_data.get(field, '').strip():
                self.show_error(f"❌ El campo '{field}' es requerido para generar la memoria.")
                return False
        
        # Validar parámetros sísmicos
        if not hasattr(self, 'seismic_params_widget'):
            self.show_error("❌ Widget de parámetros sísmicos no está inicializado.")
            return False
            
        params = self.seismic_params_widget.get_parameters()
        required_params = ['Z', 'U', 'S', 'Tp', 'Tl']
        
        for param in required_params:
            if param not in params:
                self.show_error(f"❌ El parámetro '{param}' es requerido para E.030.")
                return False
        
        return True


# Función de conveniencia para crear app de Perú
def create_peru_app():
    """Crear aplicación específica de Perú con configuración por defecto"""
    return PeruSeismicApp(PERU_CONFIG)