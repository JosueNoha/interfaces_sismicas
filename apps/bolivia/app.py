"""
Aplicación específica para Bolivia - CNBDS 2023
Simplificada usando funcionalidad centralizada
"""

from pathlib import Path
from core.base.app_base import AppBase
from core.config.app_config import BOLIVIA_CONFIG
from core.utils.common_validations import create_validator
from ui.main_window import Ui_MainWindow


class BoliviaSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Bolivia - CNBDS 2023"""
    
    def __init__(self, config=None):
        if config is None:
            config = BOLIVIA_CONFIG
            
        super().__init__(config, Ui_MainWindow)
        
        # Validador específico para Bolivia
        self.validator = create_validator(self.config)
        
        # Configurar extensiones específicas
        self._setup_bolivia_extensions()
    
    def _setup_bolivia_extensions(self):
        """Configurar funcionalidad específica de Bolivia"""
        # Agregar botón para mapa sísmico
        if self.config.get('parametros_ui', {}).get('mostrar_mapa', False):
            self._add_seismic_map_button()
        
        # Conectar validaciones
        self._connect_bolivia_validations()
    
    def _add_seismic_map_button(self):
        """Agregar botón para mostrar mapa sísmico de Bolivia"""
        try:
            from PyQt5.QtWidgets import QPushButton
            
            self.b_mapa_bolivia = QPushButton("Ver Mapa Sísmico Bolivia")
            self.b_mapa_bolivia.clicked.connect(self.show_bolivia_seismic_map)
            
            # Agregar al layout de parámetros sísmicos
            if hasattr(self.ui, 'seismic_params_layout'):
                layout = self.ui.seismic_params_layout
                current_row = layout.rowCount()
                layout.addWidget(self.b_mapa_bolivia, current_row, 0, 1, 2)
        except Exception as e:
            print(f"Error agregando botón de mapa: {e}")
    
    def _connect_bolivia_validations(self):
        """Conectar validaciones específicas para Bolivia"""
        # Las validaciones se ejecutan cuando cambian los parámetros
        if hasattr(self, 'seismic_params_widget'):
            self.seismic_params_widget.connect_param_changed(self._validate_bolivia_params)
    
    def show_bolivia_seismic_map(self):
        """Mostrar mapa sísmico específico de Bolivia"""
        map_filename = self.config.get('mapa_sismico', 'MapaSismicoBolivia.png')
        map_path = Path(__file__).parent / 'resources' / 'images' / map_filename
        
        if map_path.exists():
            self.show_image(str(map_path), "Mapa Sísmico de Bolivia - CNBDS 2023")
        else:
            self.show_warning(
                f"Mapa sísmico no encontrado en:\n{map_path}\n\n"
                "Verifique que el archivo esté en la carpeta de recursos."
            )
    
    def _validate_bolivia_params(self):
        """Validar parámetros específicos de Bolivia usando validador centralizado"""
        if not hasattr(self, 'seismic_params_widget'):
            return
            
        try:
            params = self.seismic_params_widget.get_parameters()
            is_valid, warnings = self.validator.validate_parameters(params)
            
            if warnings:
                message = "⚠️ Advertencias CNBDS 2023:\n\n" + "\n".join(f"• {w}" for w in warnings)
                message += "\n\nVerifique que los valores sean correctos para el sitio."
                self.show_warning(message)
                
        except Exception as e:
            print(f"Error validando parámetros Bolivia: {e}")
    
    def calculate_bolivia_spectrum(self):
        """Calcular espectro de respuesta según CNBDS 2023"""
        try:
            if not hasattr(self, 'seismic_params_widget'):
                self.show_error("Widget de parámetros no inicializado")
                return False
                
            params = self.seismic_params_widget.get_parameters()
            
            # Parámetros CNBDS 2023
            Fa = float(params.get('Fa', 1.86))
            Fv = float(params.get('Fv', 0.63))
            So = float(params.get('So', 2.9))
            
            # Calcular parámetros espectrales
            To = 0.15 * Fv / Fa
            Ts = 0.5 * Fv / Fa
            TL = 4 * Fv / Fa
            SDS = 2.5 * Fa * So
            SD1 = 1.25 * Fv * So
            
            # Actualizar modelo sísmico
            self.sismo.To = To
            self.sismo.Ts = Ts
            self.sismo.TL = TL
            self.sismo.SDS = SDS
            self.sismo.SD1 = SD1
            self.sismo.Fa = Fa
            self.sismo.Fv = Fv
            self.sismo.So = So

            if self.sismo.espectro_bolivia:
                T, Sa = self.sismo.espectro_bolivia()
                self.sismo.fig_spectrum = self.sismo._create_spectrum_figure(T, Sa, 'bolivia')
            
            # Mostrar resultados
            info = f"""✅ Parámetros Espectrales CNBDS 2023:

📊 ENTRADA:
   Fa = {Fa:.3f}, Fv = {Fv:.3f}, So = {So:.3f}

📈 CALCULADO:
   To = {To:.4f} s, Ts = {Ts:.4f} s, TL = {TL:.4f} s
   SDS = {SDS:.4f}, SD1 = {SD1:.4f}"""
            
            self.show_info(info)
            return True
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Bolivia: {str(e)}")
            return False
    
    def generate_report(self):
        """Generar reporte específico de Bolivia"""
        try:
            # Validar datos del proyecto
            project_data = self.get_project_data()
            from core.utils.common_validations import validate_project_data
            
            is_valid, errors = validate_project_data(project_data)
            if not is_valid:
                self.show_error("Errores en datos del proyecto:\n" + "\n".join(f"• {e}" for e in errors))
                return
            
            # Validar combinaciones
            combinations = self.get_selected_combinations()
            from core.utils.common_validations import validate_combinations
            
            is_valid, warnings = validate_combinations(combinations)
            if warnings:
                self.show_warning("Combinaciones no seleccionadas:\n" + "\n".join(f"• {w}" for w in warnings))
            
            # Calcular espectro
            if not self.calculate_bolivia_spectrum():
                return
            
            # Seleccionar directorio
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # AGREGAR: Calcular cortantes antes de generar memoria
            self.calculate_shear_forces()
            
            # Actualizar modelo
            self.update_sismo_data()
            
            # Generar memoria usando clase centralizada
            try:
                from apps.bolivia.memory import BoliviaMemoryGenerator
                
                memory_generator = BoliviaMemoryGenerator(self.sismo, output_dir)
                tex_file = memory_generator.generate_memory()
                
                self.show_info(
                    f"✅ Memoria Bolivia generada!\n\n"
                    f"📁 {output_dir}\n"
                    f"📄 {tex_file.name}\n\n"
                    f"Incluye: parámetros CNBDS 2023, espectro, análisis modal"
                )
                
            except ImportError as e:
                self.show_error(f"Error importando generador Bolivia: {e}")
            except Exception as e:
                self.show_error(f"Error generando memoria: {e}")
                
        except Exception as e:
            self.show_error(f"Error en reporte Bolivia: {str(e)}")