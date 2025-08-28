"""
Generación de memoria LaTeX para Perú - E.030
Renombrado desde memory_peru.py y simplificado usando MemoryBase
"""

import numpy as np
from pathlib import Path

from core.base.memory_base import MemoryBase
from core.utils.table_generator import PeruTableGenerator


class PeruMemoryGenerator(MemoryBase):
    """Generador de memorias LaTeX para análisis sísmico Perú - E.030"""
    
    def __init__(self, seismic_instance, output_dir):
        super().__init__(seismic_instance, output_dir)
        
        # Path al template específico de Perú
        self.templates_dir = Path(__file__).parent / 'resources' / 'templates'
        
        # Variables específicas de Perú para el template
        self.template_variables = self._get_peru_variables()

    def get_default_template_path(self) -> str:
        """Obtener path del template por defecto de Perú"""
        return str(self.templates_dir / 'plantilla_peru.ltx')

    def generate_memory(self) -> Path:
        """Generar memoria completa para Perú - E.030"""
        # Validar datos mínimos
        if not self.validate_seismic_data():
            raise ValueError("Datos sísmicos incompletos para generar memoria")
        
        # Preparar estructura de salida
        self.setup_output_structure()
        
        # Cargar template
        content = self.load_template()
        
        # Reemplazar contenido
        content = self.replace_basic_parameters(content)
        content = self._replace_peru_specific_content(content)
        content = self.insert_content_sections(content)
        
        # Generar recursos
        self.actualize_images()
        self.generate_spectrum_data()
        
        # Generar tablas usando generador centralizado
        content = self.insert_tables(content)
        
        # Guardar archivo final
        tex_file = self.save_memory(content, 'memoria_peru.tex')
        
        # Compilar a PDF
        self.compile_latex(tex_file, run_twice=True)
        
        return tex_file

    def _get_peru_variables(self) -> dict:
        """Obtener variables específicas de Perú para el template"""
        variables = {}
        
        # Parámetros sísmicos E.030
        for param in ['Z', 'U', 'S', 'Tp', 'Tl']:
            if hasattr(self.seismic, param):
                variables[param] = getattr(self.seismic, param)
        
        # Sa máxima para gráficos
        if hasattr(self.seismic, 'Sa_max'):
            variables['Samax'] = self.seismic.Sa_max
        elif hasattr(self.seismic, 'Z') and hasattr(self.seismic, 'U') and hasattr(self.seismic, 'S'):
            variables['Samax'] = round(2.5 * self.seismic.Z * self.seismic.U * self.seismic.S, 3)
        
        # Cortantes y otros datos
        if hasattr(self.seismic, 'data'):
            data = self.seismic.data
            variables.update({
                'Vdx': getattr(data, 'Vdx', 0.0),
                'Vdy': getattr(data, 'Vdy', 0.0),
                'Vsx': getattr(data, 'Vsx', 0.0),
                'Vsy': getattr(data, 'Vsy', 0.0),
                'FEx': getattr(data, 'FEx', 1.0),
                'FEy': getattr(data, 'FEy', 1.0)
            })
        
        # Cálculo de porcentajes
        if 'Vdx' in variables and 'Vsx' in variables and variables['Vsx'] > 0:
            variables['perVdsx'] = round(variables['Vdx'] / variables['Vsx'] * 100, 1)
        if 'Vdy' in variables and 'Vsy' in variables and variables['Vsy'] > 0:
            variables['perVdsy'] = round(variables['Vdy'] / variables['Vsy'] * 100, 1)
        
        # Unidades y límites
        variables['uf'] = getattr(self.seismic, 'u_f', 'kN')
        variables['ud'] = getattr(self.seismic, 'u_d', 'mm')
        variables['uh'] = getattr(self.seismic, 'u_h', 'm')
        
        return variables

    def _create_table_generator(self):
        """Crear generador de tablas específico para Perú"""
        return PeruTableGenerator(self.seismic)

    def _replace_peru_specific_content(self, content: str) -> str:
        """Reemplazar contenido específico de Perú"""
        
        # Reemplazar variables específicas de E.030
        for var_name, var_value in self.template_variables.items():
            patterns = [
                f'@{var_name}.0nn',
                f'@{var_name}.2nu',
                f'@{var_name}.2F4',
                f'@{var_name}'
            ]
            
            for pattern in patterns:
                if pattern in content:
                    if '.0nn' in pattern:
                        replacement = str(var_value)
                    elif '.2nu' in pattern or '.2F4' in pattern:
                        replacement = f'{float(var_value):.2f}' if isinstance(var_value, (int, float)) else str(var_value)
                    else:
                        replacement = str(var_value)
                    
                    content = content.replace(pattern, replacement)
        
        return content

    def generate_spectrum_data(self):
        """Generar datos del espectro específico de Perú"""
        try:
            if hasattr(self.seismic, 'espectro_peru'):
                T, Sa = self.seismic.espectro_peru()
            else:
                # Generar espectro básico con parámetros E.030
                T = np.linspace(0.1, 4.0, 100)
                Z = getattr(self.seismic, 'Z', 0.25)
                U = getattr(self.seismic, 'U', 1.0)
                S = getattr(self.seismic, 'S', 1.2)
                Sa = 2.5 * Z * U * S * np.ones_like(T)  # Simplificado
            
            data = np.column_stack((T, Sa))
            np.savetxt(self.output_dir / 'espectro_peru.txt', data, fmt="%.4f")
            
        except Exception as e:
            print(f"Error generando datos espectro Perú: {e}")
            super().generate_spectrum_data()  # Fallback al método base


# Función de conveniencia para compatibilidad
def generate_memory(seismic_instance, output_dir, **kwargs):
    """
    Función de compatibilidad con el código anterior
    
    Args:
        seismic_instance: Instancia de análisis sísmico
        output_dir: Directorio de salida
        **kwargs: Argumentos adicionales (ignorados por compatibilidad)
    """
    generator = PeruMemoryGenerator(seismic_instance, output_dir)
    return generator.generate_memory()