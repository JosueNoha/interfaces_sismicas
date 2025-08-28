"""
Clase base mejorada para generación de memorias de cálculo LaTeX
Centraliza funciones comunes eliminando duplicación
"""

import os
import shutil
import subprocess
from pathlib import Path
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from core.utils.file_utils import ensure_directory_exists, copy_resources
from core.utils.latex_utils import replace_template_variables
from core.utils.table_generator import create_table_generator


class MemoryBase(ABC):
    """Clase base mejorada para generadores de memoria de cálculo"""
    
    def __init__(self, seismic_instance, output_dir: str):
        """
        Inicializar generador de memoria
        
        Args:
            seismic_instance: Instancia de análisis sísmico
            output_dir: Directorio de salida
        """
        self.seismic = seismic_instance
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Configurar paths relativos
        self.images_dir = self.output_dir / 'images'
        self.templates_dir = None  # Se define en clases derivadas
        
        # Variables para el template
        self.template_variables = {}
        
        # Generador de tablas centralizado
        self.table_generator = self._create_table_generator()

    @abstractmethod
    def generate_memory(self) -> Path:
        """Generar memoria completa - implementar en clases derivadas"""
        pass

    def setup_output_structure(self):
        """Crear estructura de directorios de salida"""
        ensure_directory_exists(str(self.images_dir))

    def load_template(self, template_path: Optional[str] = None) -> str:
        """
        Cargar template LaTeX
        
        Args:
            template_path: Ruta específica al template (opcional)
        """
        if template_path is None:
            template_path = self.get_default_template_path()
        
        try:
            with open(template_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template no encontrado: {template_path}")

    def get_default_template_path(self) -> str:
        """Obtener path del template por defecto - implementar en clases derivadas"""
        raise NotImplementedError("Debe implementarse en clases derivadas")

    def save_memory(self, content: str, filename: str = 'memoria.tex') -> Path:
        """
        Guardar memoria LaTeX
        
        Args:
            content: Contenido LaTeX
            filename: Nombre del archivo
            
        Returns:
            Path al archivo guardado
        """
        output_file = self.output_dir / filename
        
        try:
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(content)
            return output_file
        except Exception as e:
            raise Exception(f"Error guardando memoria: {e}")

    def replace_basic_parameters(self, content: str) -> str:
        """Reemplazar parámetros básicos del proyecto"""
        basic_vars = {
            'proyecto': getattr(self.seismic, 'proyecto', ''),
            'ubicacion': getattr(self.seismic, 'ubicacion', ''),
            'autor': getattr(self.seismic, 'autor', ''),
            'fecha': getattr(self.seismic, 'fecha', ''),
        }
        
        # Agregar variables específicas del país si existen
        basic_vars.update(self.template_variables)
        
        return replace_template_variables(content, basic_vars)

    def actualize_images(self):
        """Actualizar imágenes en el directorio de salida"""
        # Crear directorio de imágenes
        ensure_directory_exists(str(self.images_dir))
        
        # Copiar imágenes del proyecto si existen
        if hasattr(self.seismic, 'urls_imagenes'):
            for img_type, img_path in self.seismic.urls_imagenes.items():
                if img_path and os.path.exists(img_path):
                    self._copy_project_image(img_path, f"{img_type}.jpg")
        
        # Guardar gráficos generados por matplotlib
        self._save_matplotlib_figures()
        
        # Copiar recursos estáticos
        self._copy_static_resources()

    def _copy_project_image(self, source_path: str, dest_name: str):
        """Copiar imagen del proyecto al directorio de salida"""
        try:
            dest_path = self.images_dir / dest_name
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            print(f"Error copiando imagen {source_path}: {e}")

    def _save_matplotlib_figures(self):
        """Guardar figuras de matplotlib"""
        figure_mappings = [
            ('fig_drifts', 'derivas.pdf'),
            ('fig_displacements', 'desplazamientos_laterales.pdf'),
            ('fig_spectrum', 'espectro.pdf'),
            ('dynamic_shear_fig', 'cortante_dinamico.pdf'),
            ('static_shear_fig', 'cortante_estatico.pdf')
        ]
        
        for fig_attr, filename in figure_mappings:
            if hasattr(self.seismic, fig_attr):
                fig = getattr(self.seismic, fig_attr)
                if fig is not None:
                    try:
                        fig.savefig(
                            self.images_dir / filename, 
                            dpi=300, 
                            bbox_inches='tight'
                        )
                    except Exception as e:
                        print(f"Error guardando figura {fig_attr}: {e}")

    def _copy_static_resources(self):
        """Copiar recursos estáticos específicos del país"""
        # Implementar en clases derivadas si es necesario
        pass

    def generate_spectrum_data(self):
        """Generar archivo de datos del espectro para gráficos TikZ"""
        try:
            # Intentar obtener datos de espectro del objeto sísmico
            if hasattr(self.seismic, 'espectro_peru'):
                T, Sa = self.seismic.espectro_peru()
                filename = 'espectro_peru.txt'
            elif hasattr(self.seismic, 'espectro_bolivia'):
                T, Sa = self.seismic.espectro_bolivia()
                filename = 'espectro_bolivia.txt'
            else:
                # Generar espectro genérico si no hay método específico
                return self._generate_generic_spectrum()
            
            # Guardar datos
            import numpy as np
            data = np.column_stack((T, Sa))
            np.savetxt(self.output_dir / filename, data, fmt="%.4f")
            
        except Exception as e:
            print(f"Error generando datos de espectro: {e}")

    def _generate_generic_spectrum(self):
        """Generar espectro genérico por defecto"""
        try:
            import numpy as np
            T = np.linspace(0.1, 4.0, 100)
            Sa = 0.25 * np.ones_like(T)  # Espectro constante básico
            
            data = np.column_stack((T, Sa))
            np.savetxt(self.output_dir / 'espectro_generico.txt', data, fmt="%.4f")
            
        except Exception as e:
            print(f"Error generando espectro genérico: {e}")

    def compile_latex(self, tex_file: Path, run_twice: bool = True) -> bool:
        """
        Compilar archivo LaTeX a PDF
        
        Args:
            tex_file: Path al archivo .tex
            run_twice: Si ejecutar pdflatex dos veces para referencias
            
        Returns:
            True si la compilación fue exitosa
        """
        if not shutil.which('pdflatex'):
            print("⚠️  pdflatex no encontrado. Solo se generó el archivo .tex")
            return False
        
        try:
            # Primera compilación
            result = subprocess.run([
                'pdflatex', 
                '-interaction=nonstopmode', 
                str(tex_file)
            ], cwd=self.output_dir, check=True, capture_output=True, text=True)
            
            # Segunda compilación si es necesario (para referencias)
            if run_twice:
                subprocess.run([
                    'pdflatex', 
                    '-interaction=nonstopmode', 
                    str(tex_file)
                ], cwd=self.output_dir, check=True, capture_output=True, text=True)
            
            # Limpiar archivos temporales
            self._clean_latex_temp_files()
            
            print(f"✅ PDF generado exitosamente: {tex_file.with_suffix('.pdf')}")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error compilando LaTeX: {e}")
            print(f"STDOUT: {e.stdout}")
            print(f"STDERR: {e.stderr}")
            return False

    def _clean_latex_temp_files(self):
        """Limpiar archivos temporales de LaTeX"""
        temp_extensions = ['.log', '.aux', '.fdb_latexmk', '.fls', '.toc', 
                          '.out', '.synctex.gz', '.figlist', '.makefile']
        
        for file_path in self.output_dir.iterdir():
            if file_path.suffix in temp_extensions:
                try:
                    file_path.unlink()
                except:
                    pass

    def generate_table_content(self, table_data, table_type: str) -> str:
        """
        Generar contenido LaTeX para tablas
        
        Args:
            table_data: Datos de la tabla (DataFrame o dict)
            table_type: Tipo de tabla ('modal', 'drift', 'displacement', etc.)
            
        Returns:
            Contenido LaTeX de la tabla
        """
        if table_data is None:
            return f"% Tabla {table_type} no disponible"
        
        try:
            if hasattr(table_data, 'to_latex'):
                # Es un DataFrame de pandas
                return table_data.to_latex(
                    index=False,
                    float_format=lambda x: f"{x:.3f}" if isinstance(x, float) else str(x),
                    escape=False
                )
            else:
                # Es otro tipo de datos, generar tabla básica
                return self._generate_basic_table(table_data, table_type)
                
        except Exception as e:
            print(f"Error generando tabla {table_type}: {e}")
            return f"% Error generando tabla {table_type}"

    def _generate_basic_table(self, data, table_type: str) -> str:
        """Generar tabla LaTeX básica"""
        # Implementación básica - puede ser sobrescrita
        return f"""\\begin{{table}}[H]
\\centering
\\caption{{Tabla {table_type}}}
\\begin{{tabular}}{{|c|}}
\\hline
Datos no disponibles \\\\
\\hline
\\end{{tabular}}
\\end{{table}}"""

    def insert_content_sections(self, content: str) -> str:
        """Insertar secciones de contenido descriptivo"""
        # Reemplazar descripciones del proyecto
        descriptions = getattr(self.seismic, 'descriptions', {})
        
        content_replacements = {
            '@content_description': descriptions.get('descripcion', ''),
            '@content_criteria': descriptions.get('modelamiento', ''), 
            '@content_loads': descriptions.get('cargas', '')
        }
        
        for placeholder, description in content_replacements.items():
            if placeholder in content:
                # Escapar caracteres especiales de LaTeX si es necesario
                escaped_desc = description.replace('&', '\\&').replace('%', '\\%')
                content = content.replace(placeholder, escaped_desc)
        
        return content

    def validate_seismic_data(self) -> bool:
        """Validar que el objeto sísmico tenga los datos mínimos requeridos"""
        required_attrs = ['proyecto', 'ubicacion', 'autor', 'fecha']
        
        for attr in required_attrs:
            if not hasattr(self.seismic, attr) or not getattr(self.seismic, attr):
                print(f"⚠️  Atributo requerido '{attr}' no encontrado o vacío")
                return False
        
        return True

    def _create_table_generator(self):
        """
        Crear generador de tablas específico para el país
        Se sobrescribe en clases derivadas para especificar el país
        """
        return create_table_generator(self.seismic)

    def generate_all_tables(self) -> str:
        """
        Generar todas las tablas estándar usando el generador centralizado
        
        Returns:
            Contenido con todas las tablas reemplazadas
        """
        tables = self.table_generator.generate_all_tables()
        
        # Mapeo de nombres de tabla a marcadores en el template
        table_mappings = {
            'modal': '@table_modal',
            'drift_x': '@table_drifts_x',
            'drift_y': '@table_drifts_y', 
            'displacements': '@table_disp',
            'shear_dynamic': '@table_shear_dynamic',
            'shear_static': '@table_shear_static',
            'stiffness_x': '@table_stiffness_x',
            'stiffness_y': '@table_stiffness_y',
            'mass': '@table_mass',
            'torsion_x': '@table_torsion_x',
            'torsion_y': '@table_torsion_y'
        }
        
        return tables, table_mappings

    def insert_tables(self, content: str) -> str:
        """
        Insertar todas las tablas en el contenido LaTeX
        
        Args:
            content: Contenido LaTeX original
            
        Returns:
            Contenido con tablas insertadas
        """
        tables, mappings = self.generate_all_tables()
        
        # Reemplazar cada marcador con su tabla correspondiente
        for table_key, marker in mappings.items():
            if marker in content and table_key in tables:
                content = content.replace(marker, tables[table_key])
        
        return content