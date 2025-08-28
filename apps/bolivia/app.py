"""
Aplicación específica para Bolivia - CNBDS 2023
Renombrado desde bolivia_app.py por consistencia
"""

from typing import Dict, Any
from PyQt5.QtWidgets import QPushButton
from pathlib import Path

from core.base.app_base import AppBase
from core.config.app_config import BOLIVIA_CONFIG
from ui.main_window import Ui_MainWindow


class BoliviaSeismicApp(AppBase):
    """Aplicación específica para análisis sísmico de Bolivia - CNBDS 2023"""
    
    def __init__(self, config: Dict[str, Any] = None):
        # Usar configuración por defecto si no se proporciona
        if config is None:
            config = BOLIVIA_CONFIG
        
        # Llamar al constructor base con UI class
        super().__init__(config, Ui_MainWindow)
        
        # Configurar extensiones específicas de Bolivia
        self._setup_bolivia_extensions()
    
    def _setup_bolivia_extensions(self):
        """Configurar extensiones específicas de Bolivia"""
        # Agregar botón para mapa sísmico si existe
        if self.config.get('parametros_ui', {}).get('mostrar_mapa', False):
            self._add_seismic_map_button()
        
        # Configurar validaciones específicas de Bolivia
        self._setup_bolivia_validations()
    
    def _add_seismic_map_button(self):
        """Agregar botón para mostrar mapa sísmico de Bolivia"""
        try:
            # Agregar botón en el grupo de parámetros sísmicos
            self.b_mapa_bolivia = QPushButton("Ver Mapa Sísmico Bolivia")
            self.b_mapa_bolivia.clicked.connect(self.show_bolivia_seismic_map)
            
            # Agregar al layout de parámetros sísmicos
            if hasattr(self.ui, 'seismic_params_layout'):
                layout = self.ui.seismic_params_layout
                current_row = layout.rowCount()
                layout.addWidget(self.b_mapa_bolivia, current_row, 0, 1, 2)
        except Exception as e:
            print(f"Error agregando botón de mapa: {e}")
    
    def _setup_bolivia_validations(self):
        """Configurar validaciones específicas para parámetros de Bolivia"""
        # Conectar validaciones cuando se inicialice el widget de parámetros
        if hasattr(self, 'seismic_params_widget'):
            # Validaciones para factores Fa y Fv
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
        # Buscar mapa en recursos de Bolivia
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
        """Validar parámetros específicos de Bolivia según CNBDS 2023"""
        if not hasattr(self, 'seismic_params_widget'):
            return
            
        try:
            params = self.seismic_params_widget.get_parameters()
            warnings = []
            
            # Obtener rangos de validación desde configuración
            espectro_config = self.config.get('espectro_config', {})
            rangos_fa = espectro_config.get('rangos_fa', (0.8, 3.0))
            rangos_fv = espectro_config.get('rangos_fv', (0.6, 2.5))
            rangos_so = espectro_config.get('rangos_so', (0.1, 4.0))
            
            # Validaciones según CNBDS 2023
            if 'Fa' in params:
                fa = params['Fa']
                if fa < rangos_fa[0] or fa > rangos_fa[1]:
                    warnings.append(
                        f"Factor Fa ({fa:.2f}) fuera del rango típico ({rangos_fa[0]}-{rangos_fa[1]})"
                    )
            
            if 'Fv' in params:
                fv = params['Fv']
                if fv < rangos_fv[0] or fv > rangos_fv[1]:
                    warnings.append(
                        f"Factor Fv ({fv:.2f}) fuera del rango típico ({rangos_fv[0]}-{rangos_fv[1]})"
                    )
            
            if 'So' in params:
                so = params['So']
                if so < rangos_so[0] or so > rangos_so[1]:
                    warnings.append(
                        f"Parámetro So ({so:.2f}) fuera del rango típico ({rangos_so[0]}-{rangos_so[1]})"
                    )
            
            # Mostrar advertencias si las hay
            if warnings:
                message = "⚠️ Advertencias de parámetros CNBDS 2023:\n\n" + "\n".join(f"• {w}" for w in warnings)
                message += "\n\nVerifique que los valores sean correctos para el sitio del proyecto."
                self.show_warning(message)
                
        except Exception as e:
            print(f"Error validando parámetros Bolivia: {e}")
    
    def calculate_bolivia_spectrum(self):
        """Calcular espectro de respuesta según CNBDS 2023"""
        try:
            # Obtener parámetros desde la interfaz
            if not hasattr(self, 'seismic_params_widget'):
                self.show_error("Widget de parámetros no inicializado")
                return False
                
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
            
            # Actualizar objeto sismo con parámetros calculados
            self.sismo.To = To
            self.sismo.Ts = Ts
            self.sismo.TL = TL
            self.sismo.SDS = SDS
            self.sismo.SD1 = SD1
            self.sismo.Fa = Fa
            self.sismo.Fv = Fv
            self.sismo.So = So
            
            # Mostrar resultados
            info = f"""✅ Parámetros Espectrales CNBDS 2023 Calculados:

📊 PARÁMETROS DE ENTRADA:
   Fa = {Fa:.3f}
   Fv = {Fv:.3f}  
   So = {So:.3f}

📈 PARÁMETROS ESPECTRALES:
   To = {To:.4f} s
   Ts = {Ts:.4f} s  
   TL = {TL:.4f} s
   SDS = {SDS:.4f}
   SD1 = {SD1:.4f}

🔍 Los parámetros han sido almacenados en el modelo."""
            
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
                self.show_error("No se pudo calcular el espectro. Verifique los parámetros.")
                return
            
            # Seleccionar directorio de salida
            output_dir = self.get_output_directory()
            if not output_dir:
                return
            
            # Actualizar todos los datos del modelo
            self.update_seismic_data()
            
            # Generar usando memoria específica de Bolivia
            try:
                from apps.bolivia.memory import BoliviaMemoryGenerator
                
                # Crear generador de memoria
                memory_generator = BoliviaMemoryGenerator(self.sismo, output_dir)
                
                # Generar memoria completa
                tex_file = memory_generator.generate_memory()
                
                self.show_info(
                    f"✅ Memoria de cálculo Bolivia generada exitosamente!\n\n"
                    f"📁 Directorio: {output_dir}\n"
                    f"📄 Archivo: {tex_file.name}\n\n"
                    f"La memoria incluye:\n"
                    f"• Parámetros sísmicos CNBDS 2023\n"
                    f"• Espectro de respuesta\n"
                    f"• Análisis modal (si disponible)\n"
                    f"• Gráficos y tablas"
                )
                
            except ImportError as e:
                self.show_error(f"Error importando generador de memoria Bolivia: {e}")
            except Exception as e:
                self.show_error(f"Error generando memoria: {e}")
                
        except Exception as e:
            self.show_error(f"Error en generación de reporte Bolivia: {str(e)}")
    
    def _validate_required_params(self) -> bool:
        """Validar que todos los parámetros requeridos estén presentes"""
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
        required_params = ['Fa', 'Fv', 'So']
        
        for param in required_params:
            if param not in params:
                self.show_error(f"❌ El parámetro '{param}' es requerido para Bolivia (CNBDS 2023).")
                return False
        
        return True


# Función de conveniencia para crear app de Bolivia
def create_bolivia_app():
    """Crear aplicación específica de Bolivia con configuración por defecto"""
    return BoliviaSeismicApp(BOLIVIA_CONFIG)