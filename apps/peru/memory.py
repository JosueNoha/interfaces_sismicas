"""
Generación de memoria LaTeX para Perú - E.030
Renombrado desde memory_peru.py y simplificado usando MemoryBase
"""

import numpy as np
from pathlib import Path
import shutil

from core.base.memory_base import MemoryBase
from core.utils.table_generator import PeruTableGenerator
from core.utils.latex_utils import replace_template_variables
from core.utils.file_utils import ensure_directory_exists


class PeruMemoryGenerator(MemoryBase):
    """Generador de memorias LaTeX para análisis sísmico Perú - E.030"""
    
    def __init__(self, seismic_instance, output_dir):
        super().__init__(seismic_instance, output_dir)
        self.country = 'peru'
        
        # Path al template específico de Perú
        self.templates_dir = Path(__file__).parent / 'resources' / 'templates'
        
        # Variables específicas de Perú para el template

    def get_default_template_path(self) -> str:
        """Obtener path del template por defecto de Perú"""
        return str(self.templates_dir / 'plantilla_peru.ltx')
    
    def _get_country_resources_path(self) -> Path:
        """Path a recursos de Perú"""
        return Path(__file__).parent / 'resources'

    def generate_memory(self) -> Path:
        """Generar memoria completa para Perú - E.030"""

        # Preparar estructura de salida
        self.setup_output_structure()
        
        # Cargar template
        content = self.load_template()
        
        # Reemplazar contenido
        content = self.replace_variables(content)
        
        # Reemplazar tablas
        content = self._insert_tables(content)
        
        self.actualize_images()

        content = self.insert_content_sections(content)
    
        # Guardar archivo final
        tex_file = self.save_memory(content, 'memoria_peru.tex')
        
        # Compilar a PDF
        self.compile_latex(tex_file, run_twice=True)
        
        return tex_file
    
    def get_country_variables(self):
        
        variables = dict(
            Z = self.seismic.Z,
            U = self.seismic.U,
            S = self.seismic.S,
            Tp = self.seismic.Tp,
            Tl = self.seismic.Tl,
            Samax = self.seismic.Sa_max
        )
        
        return variables

    def replace_variables(self,content=None):
        if content == None:
            content = self.load_template()
        variables = self.get_general_variables()
        variables.update(self.get_country_variables())
        content = self.save_variables(variables,content)
        return content
        
    
    def _insert_tables(self, content: str) -> str:
        """Insertar tablas específicas de Perú"""
        import re
        import core.utils.latex_utils as ltx
        
        modal_content = self._generate_modal_table_peru()
        content =re.sub(re.escape(r'@table\_modal'),ltx.escape_for_latex(modal_content), content)
        
        # Tabla de torsión
        torsion_content = self._generate_torsion_tables_peru()
        content =re.sub(re.escape(r'@table\_torsion\_x'),ltx.escape_for_latex(torsion_content['x']), content)
        content =re.sub(re.escape(r'@table\_torsion\_y'),ltx.escape_for_latex(torsion_content['y']), content)
        
        # Tabla de derivas 
        drift_content = self._generate_drift_table_peru()
        content =re.sub(re.escape(r'@table\_drifts\_x'),ltx.escape_for_latex(drift_content['x']), content)
        content =re.sub(re.escape(r'@table\_drifts\_y'),ltx.escape_for_latex(drift_content['y']), content)
        
        # Tabla de desplazamientos
        disp_content = self._generate_displacement_table_peru()
        content =re.sub(re.escape(r'@table\_disp'),ltx.escape_for_latex(disp_content), content)
        
        # Tabla de cortantes 
        shear_content = self._generate_shear_table_peru()
        content =re.sub(re.escape(r'@table\_shear\_static'),ltx.escape_for_latex(shear_content['static']), content)
        content =re.sub(re.escape(r'@table\_shear\_dynamic'),ltx.escape_for_latex(shear_content['dynamic']), content)
        
        return content
    
    def _generate_modal_table_peru(self) -> str:
        """Generar tabla modal Perú"""
        if not hasattr(self.seismic, 'tables') or not hasattr(self.seismic.tables, 'modal'):
            return "Tabla modal no disponible"
        
        try:
            table_gen = PeruTableGenerator(self.seismic)
            return table_gen.generate_modal_table()
        except Exception as e:
            print(f"Error tabla modal Perú: {e}")
            return "Error generando tabla modal"

    def _generate_torsion_tables_peru(self) -> dict:
        """Generar tablas de torsión Perú"""
        try:
            table_gen = PeruTableGenerator(self.seismic)
            return {
                'x': table_gen.generate_torsion_table_x(),
                'y': table_gen.generate_torsion_table_y()
            }
        except Exception as e:
            print(f"Error tablas torsión Perú: {e}")
            return {'x': 'Error', 'y': 'Error'}

    def _generate_drift_table_peru(self) -> str:
        """Generar tabla de derivas Perú"""
        try:
            table_gen = PeruTableGenerator(self.seismic)
            return {
                'x': table_gen.generate_drift_table_x(),
                'y': table_gen.generate_drift_table_y()
            }
        except Exception as e:
            print(f"Error tabla derivas Perú: {e}")
            return {'x': 'Error', 'y': 'Error'}


    def _generate_displacement_table_peru(self) -> str:
        """Generar tabla de desplazamientos Perú"""
        try:
            table_gen = PeruTableGenerator(self.seismic)
            return table_gen.generate_displacement_table()
        except Exception as e:
            print(f"Error tabla desplazamientos Perú: {e}")
            
    def _generate_shear_table_peru(self) -> str:
        """Generar tabla de derivas Perú"""
        try:
            table_gen = PeruTableGenerator(self.seismic)
            return {
                'static': table_gen.generate_shear_table_static(),
                'dynamic': table_gen.generate_shear_table_dynamic()
            }
        except Exception as e:
            
            (f"Error tabla derivas Perú: {e}")
            return {'static': 'Error', 'dynamic': 'Error'}
