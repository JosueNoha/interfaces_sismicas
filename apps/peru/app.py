"""
Aplicación específica para Perú - E.030
"""

from core.base.app_base import AppBase
from core.config.app_config import PERU_CONFIG
from ui.main_window import Ui_MainWindow


class PeruSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Perú - E.030"""
    
    def __init__(self, config=None):
        if config is None:
            config = PERU_CONFIG
        super().__init__(config, Ui_MainWindow)
        
        # Configurar específicos de Perú
        self._setup_peru_specifics()
    
    def _setup_peru_specifics(self):
        """Configurar funcionalidades específicas de Perú"""
        # Zonas sísmicas y factores de uso E.030
        self.zonas_peru = {
            'Zona 1': 0.10, 'Zona 2': 0.25, 
            'Zona 3': 0.35, 'Zona 4': 0.45
        }
        
        self.factores_uso = {
            'A1 - Esenciales': 1.5, 'A2 - Importantes': 1.3,
            'B - Comunes': 1.0, 'C - Menores': 0.8
        }
    
    def calculate_peru_spectrum(self):
        """Calcular espectro según E.030"""
        if not hasattr(self, 'seismic_params_widget'):
            return False, None, None
            
        try:
            import numpy as np
            
            params = self.seismic_params_widget.get_parameters()
            
            Z = params.get('Z', 0.25)
            U = float(params.get('U', 1.0))
            S = params.get('S', 1.2)
            Tp = params.get('Tp', 0.6)
            Tl = params.get('Tl', 2.0)
            
            # Actualizar modelo
            for param, value in [('Z', Z), ('U', U), ('S', S), ('Tp', Tp), ('Tl', Tl)]:
                setattr(self.sismo, param, value)
            
            # Generar espectro E.030
            T = np.arange(0, 4+0.01, 0.01)
            Sa = np.zeros_like(T)
            
            idx1 = T <= Tp
            idx2 = (T > Tp) & (T <= Tl)  
            idx3 = T > Tl
            
            Sa[idx1] = 2.5 * Z * U * S
            Sa[idx2] = 2.5 * Tp / T[idx2] * Z * U * S
            Sa[idx3] = 2.5 * Tp * Tl / (T[idx3]**2) * Z * U * S
            
            self.sismo.Sa_max = max(Sa) * 1.2
            
            self.show_info(f"""✅ Espectro E.030 Calculado:

📊 ENTRADA:
   Z = {Z:.3f}, U = {U:.1f}, S = {S:.2f}
   Tp = {Tp:.2f} s, Tl = {Tl:.2f} s

📈 RESULTADO:
   Sa máxima = {np.max(Sa):.4f} g
   {len(T)} puntos generados""")
            
            return True, T, Sa
            
        except Exception as e:
            self.show_error(f"Error calculando espectro Perú: {e}")
            return False, None, None
    
    def generate_report(self):
        """Generar reporte Perú"""
        try:
            if not self._validate_peru_data():
                return
                
            success, T, Sa = self.calculate_peru_spectrum()
            if not success:
                return
                
            output_dir = self.get_output_directory()
            if not output_dir:
                return
                
            self.update_seismic_data()
            
            from apps.peru.memory import PeruMemoryGenerator
            
            memory_generator = PeruMemoryGenerator(self.sismo, output_dir)
            tex_file = memory_generator.generate_memory()
            
            self.show_info(f"""✅ Memoria Perú generada:

📁 {output_dir}
📄 {tex_file.name}

Incluye: E.030, espectro, análisis modal, gráficos""")
            
        except ImportError as e:
            self.show_error(f"Error importando generador: {e}")
        except Exception as e:
            self.show_error(f"Error generando reporte: {e}")
    
    def _validate_peru_data(self):
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
        for param in ['Z', 'U', 'S', 'Tp', 'Tl']:
            if param not in params:
                self.show_error(f"Parámetro requerido: {param}")
                return False
                
        return True