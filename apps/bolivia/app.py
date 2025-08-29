"""
Aplicación específica para Bolivia - CNBDS 2023
"""

from core.base.app_base import AppBase
from core.config.app_config import BOLIVIA_CONFIG
from ui.main_window import Ui_MainWindow
from pathlib import Path


class BoliviaSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Bolivia - CNBDS 2023"""
    
    def __init__(self, config=None):
        if config is None:
            config = BOLIVIA_CONFIG
        super().__init__(config, Ui_MainWindow)
        
        # Agregar funcionalidad específica de Bolivia
        self._setup_bolivia_specifics()
    
    def _setup_bolivia_specifics(self):
        """Configurar funcionalidades específicas de Bolivia"""
        # Botón para mapa sísmico
        if self.config.get('parametros_ui', {}).get('mostrar_mapa', False):
            self._add_seismic_map_button()
    
    def _add_seismic_map_button(self):
        """Agregar botón de mapa sísmico"""
        from PyQt5.QtWidgets import QPushButton
        
        try:
            self.b_mapa_bolivia = QPushButton("Ver Mapa Sísmico Bolivia")
            self.b_mapa_bolivia.clicked.connect(self.show_bolivia_seismic_map)
            
            if hasattr(self.ui, 'seismic_params_layout'):
                layout = self.ui.seismic_params_layout
                layout.addWidget(self.b_mapa_bolivia, layout.rowCount(), 0, 1, 2)
        except Exception as e:
            print(f"Error agregando botón de mapa: {e}")
    
    def show_bolivia_seismic_map(self):
        """Mostrar mapa sísmico de Bolivia"""
        map_path = Path(__file__).parent / 'resources' / 'images' / 'MapaSismicoBolivia.png'
        
        if map_path.exists():
            self.show_image(str(map_path), "Mapa Sísmico de Bolivia - CNBDS 2023")
        else:
            self.show_warning(f"Mapa sísmico no encontrado en:\n{map_path}")
    
    def calculate_bolivia_spectrum(self):
        """Calcular espectro según CNBDS 2023"""
        if not hasattr(self, 'seismic_params_widget'):
            return False
            
        try:
            params = self.seismic_params_widget.get_parameters()
            
            Fa = params.get('Fa', 1.86)
            Fv = params.get('Fv', 0.63)  
            So = params.get('So', 2.9)
            
            # Parámetros espectrales CNBDS 2023
            To = 0.15 * Fv / Fa
            Ts = 0.5 * Fv / Fa
            TL = 4 * Fv / Fa
            SDS = 2.5 * Fa * So
            SD1 = 1.25 * Fv * So
            
            # Actualizar modelo
            for param, value in [('To', To), ('Ts', Ts), ('TL', TL), 
                               ('SDS', SDS), ('SD1', SD1), ('Fa', Fa), 
                               ('Fv', Fv), ('So', So)]:
                setattr(self.sismo, param, value)
            
            self.show_info(f"""✅ Parámetros Espectrales CNBDS 2023:

📊 ENTRADA:
   Fa = {Fa:.3f}, Fv = {Fv:.3f}, So = {So:.3f}

📈 CALCULADOS:
   To = {To:.4f} s, Ts = {Ts:.4f} s, TL = {TL:.4f} s
   SDS = {SDS:.4f}, SD1 = {SD1:.4f}""")
            
            return True
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Bolivia: {e}")
            return False
    
    def generate_report(self):
        """Generar reporte Bolivia"""
        try:
            if not self._validate_bolivia_data():
                return
                
            if not self.calculate_bolivia_spectrum():
                return
                
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            self.update_seismic_data()
            
            from apps.bolivia.memory import BoliviaMemoryGenerator
            
            memory_generator = BoliviaMemoryGenerator(self.sismo, output_dir)
            tex_file = memory_generator.generate_memory()
            
            self.show_info(f"""✅ Memoria Bolivia generada:

📁 {output_dir}
📄 {tex_file.name}

Incluye: CNBDS 2023, espectro, análisis modal, gráficos""")
            
        except ImportError as e:
            self.show_error(f"Error importando generador: {e}")
        except Exception as e:
            self.show_error(f"Error generando reporte: {e}")
    
    def _validate_bolivia_data(self):
        """Validar datos requeridos"""
        project_data = self.get_project_data()
        for field in ['proyecto', 'ubicacion', 'autor']:
            if not project_data.get(field, '').strip():
                self.show_error(f"Campo requerido: {field}")
                return False
        
        if not hasattr(self, 'seismic_params_widget'):
            self.show_error("Widget de parámetros no inicializado")
            return False
            
        params = self.seismic_params_widget.get_parameters()
        for param in ['Fa', 'Fv', 'So']:
            if param not in params:
                self.show_error(f"Parámetro requerido: {param}")
                return False
                
        return True