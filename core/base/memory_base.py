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
import numpy as np
from typing import Tuple

from core.utils.file_utils import ensure_directory_exists, copy_resources
from core.utils.latex_utils import replace_template_variables
from core.utils.table_generator import create_table_generator
import re


class MemoryBase(ABC):
    """Clase base mejorada para generadores de memoria de cálculo"""
    
    def __init__(self, seismic_instance, base_output_dir: str):
        """
        Inicializar generador de memoria
        
        Args:
            seismic_instance: Instancia de análisis sísmico
            output_dir: Directorio de salida
        """
        self.seismic = seismic_instance
        
        # Crear directorio único basado en el nombre del proyecto
        self.base_output_dir = Path(base_output_dir)
        self.output_dir = self._create_unique_project_directory()
        self.images_dir = self.output_dir / 'images'
        
        # Se define en clases derivadas
        self.templates_dir = None
        self.template_variables = {}
        
    def _create_unique_project_directory(self) -> Path:
        """
        Crear directorio único para el proyecto con formato:
        proyecto_name, proyecto_name_1, proyecto_name_2, etc.
        """
        # Obtener nombre del proyecto
        project_name = getattr(self.seismic, 'proyecto', 'proyecto_sismico')
        
        # Limpiar nombre: espacios por _, caracteres especiales
        clean_name = re.sub(r'[^\w\s-]', '', project_name)
        clean_name = re.sub(r'[-\s]+', '_', clean_name).strip('_').lower()
        
        if not clean_name:
            clean_name = 'proyecto_sismico'
        
        # Buscar nombre único
        project_dir = self.base_output_dir / clean_name
        counter = 1
        
        while project_dir.exists():
            project_dir = self.base_output_dir / f"{clean_name}_{counter}"
            counter += 1
        
        # Crear directorio
        project_dir.mkdir(parents=True, exist_ok=True)
        print(f"📁 Directorio creado: {project_dir.name}")
        
        return project_dir


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

    @abstractmethod
    def get_default_template_path(self) -> str:
        """Path del template por defecto - implementar en clases derivadas"""
        pass
    
    @abstractmethod  
    def _get_country_resources_path(self) -> Path:
        """Path a recursos del país - implementar en clases derivadas"""
        pass
    
    def get_output_directory_name(self) -> str:
        """Obtener nombre del directorio de salida creado"""
        return self.output_dir.name

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
        
    def save_variables(self,var_dict,content=None):   
        #extraer nombres de variables
        if content == None:
            content = self.load_template()
        from core.utils import unit_tool
        u = unit_tool.Units()
        u_dict = self.seismic.units
        units = {'ud':getattr(u,u_dict['desplazamientos']),
                 'uh':getattr(u,u_dict['alturas']),
                 'uf':getattr(u,u_dict['fuerzas']),
                 'nu':1}
        
        matches = set(re.findall(r'@([a-zA-Z_][a-zA-Z0-9_\\_]*)\.(\d)([a-zA-Z0-9_]+)',content))
        for match in matches:
            variable = match[0]
            unit = match[-1]
            if unit in units.keys():
                f_conv = units[unit]
                n_dec = match[1]
                pattern = (f'@{match[0]}.{match[1]}{match[2]}',
                            f'{var_dict[variable]/f_conv:.{n_dec}f}')
            elif unit == 'nn':
                pattern = (f'@{match[0]}.{match[1]}{match[2]}',
                            f'{var_dict[variable]}')
            else:
                continue
                
            #reemplazar las variables
            if variable in var_dict.keys():
                content = re.sub(*pattern, content)

        return content

    
    def get_general_variables(self):

        Vsx = self.seismic.data.Vsx
        Vsy = self.seismic.data.Vsy
        Vdx = self.seismic.data.Vdx
        Vdy = self.seismic.data.Vdy   
        units = self.seismic.units
        
        variables = dict(
            Vsx = Vsx,
            Vsy = Vsy,
            Vdx = Vdx,
            Vdy = Vdy,
            perVdsx = Vdx/Vsx*100,
            perVdsy = Vdy/Vsy*100,
            FEx = self.seismic.data.FEx,
            FEy = self.seismic.data.FEy,
            mpmin = self.seismic.min_mass_participation,
            permin = self.seismic.min_percent,
            proyecto = self.seismic.project_data['proyecto'],
            ubicacion = self.seismic.project_data['ubicacion'],
            autor = self.seismic.project_data['autor'],
            fecha = self.seismic.project_data['fecha'],
            ud = units['desplazamientos'],
            uh = units['alturas'],
            uf = units['fuerzas'],
        )

        return variables
    
    def _copy_from_directory(self, source_dir: Path) -> int:
        """
        Copiar archivos desde directorio (MÉTODO COMÚN)
        Returns: número de archivos copiados
        """
        copied_count = 0
        extensions = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.bmp', '*.svg']
        
        for ext in extensions:
            for image_file in source_dir.glob(ext):
                try:
                    dest_path = self.images_dir / image_file.name
                    shutil.copy2(image_file, dest_path)
                    copied_count += 1
                except Exception as e:
                    print(f"    ❌ Error copiando {image_file.name}: {e}")
        
        return copied_count
    
    def _copy_country_images(self):
        """Copiar imágenes específicas del país (MÉTODO COMÚN)"""
        country = getattr(self, 'country', 'generic')
        country_images = self._get_country_resources_path() / 'images'
        
        if country_images.exists():
            copied = self._copy_from_directory(country_images)
            print(f"  ✓ {copied} imágenes de {country}")
        else:
            print(f"  ℹ️ Sin recursos específicos: {country}")

    def _copy_shared_images(self):
        """Copiar imágenes compartidas"""
        shared_images = Path(__file__).parent.parent.parent / 'shared' / 'resources' / 'images'
        
        if shared_images.exists():
            copied = self._copy_from_directory(shared_images)
            print(f"  ✓ {copied} imágenes compartidas")
            
    
    def compile_latex(self, tex_file: Path, run_twice: bool = False):
        """
        Compilar archivo LaTeX a PDF (CONSOLIDADO)
        Elimina duplicación total entre Bolivia y Perú
        """
        try:
            original_cwd = os.getcwd()
            os.chdir(tex_file.parent)
            
            cmd = ['pdflatex', '-interaction=nonstopmode', tex_file.name]
            
            # Primera compilación
            print("🔄 Compilando LaTeX...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error en compilación LaTeX:")
                print(result.stdout[-500:] if result.stdout else "Sin salida")
                raise Exception("Error en compilación LaTeX")
            
            # Segunda compilación si se requiere
            if run_twice:
                print("🔄 Segunda compilación...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception("Error en segunda compilación LaTeX")
            
            # Limpiar archivos temporales
            self._clean_latex_temp_files(tex_file)
            
            print(f"✅ PDF generado: {tex_file.with_suffix('.pdf')}")
            os.chdir(original_cwd)
            
        except FileNotFoundError:
            raise Exception("pdflatex no encontrado. Instale distribución LaTeX")
        except Exception as e:
            try:
                os.chdir(original_cwd)
            except:
                pass
            raise e
    
    def _clean_latex_temp_files(self, tex_file: Path):
        """Limpiar archivos temporales LaTeX (CONSOLIDADO)"""
        temp_extensions = ['.aux', '.log', '.fdb_latexmk', '.fls', '.synctex.gz', '.toc']
        
        for ext in temp_extensions:
            temp_file = tex_file.with_suffix(ext)
            if temp_file.exists():
                try:
                    temp_file.unlink()
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
    
    
    def _copy_existing_user_images(self):
        """Copiar solo las imágenes que ya existen y fueron cargadas"""
        print("  🖼️ Copiando imágenes del usuario...")
        
        if not hasattr(self.seismic, 'urls_imagenes') or not self.seismic.urls_imagenes:
            print("    ⚠️ No hay imágenes cargadas por el usuario")
            return
            
        image_mappings = {
            'portada': 'portada.jpg',
            'planta': 'planta_tipica.jpg', 
            '3d': 'vista_3d.jpg',
            'defX': 'deformada_x.jpg',
            'defY': 'deformada_y.jpg'
        }
        
        copied_count = 0
        for img_type, dest_name in image_mappings.items():
            img_path = self.seismic.urls_imagenes.get(img_type)
            if img_path and os.path.exists(img_path):
                try:
                    dest_path = self.images_dir / dest_name
                    shutil.copy2(img_path, dest_path)
                    print(f"    ✓ {dest_name} copiada desde {Path(img_path).name}")
                    copied_count += 1
                except Exception as e:
                    print(f"    ❌ Error copiando {dest_name}: {e}")
            else:
                print(f"    ⚠️ {img_type}: No cargada o no existe")
        
        print(f"  📊 Imágenes usuario: {copied_count}/{len(image_mappings)} copiadas")
    

    def actualize_images(self):
        """Copiar todas las imágenes necesarias (CONSOLIDADO)"""
        print("🖼️ Actualizando imágenes...")
        
        # 1. Imágenes específicas del país
        self._copy_country_images()
        
        # 2. Imágenes compartidas (si existen)
        self._copy_shared_images()
        
        # 3. Gráficos generados
        self._save_generated_plots()

    def _save_generated_plots(self):
        """Guardar gráficos generados por análisis"""
        country = getattr(self, 'country', 'generic')
        country_images = self._get_country_resources_path() / 'images'
        
        figure_mapings = {'fig_displacements':"desplazamientos_laterales.pdf",
                          'fig_drifts':"derivas.pdf",
                          'static_shear_fig':"cortante_dinamico.pdf",
                          'dynamic_shear_fig':"cortante_estatico.pdf"
                          }
        
        if country_images.exists():
            for figure,name in figure_mapings.items():
                self.save_figure(getattr(self.seismic,figure),country_images,name)
        else:
            print(f"  ℹ️ Sin recursos específicos: {country}")
            
    def save_figure(self,figure,path,name):
        """Guardar figura"""
        figure.savefig(os.path.join(path, name), dpi=300, bbox_inches='tight')
                
                
    def insert_content_sections(self, content: str) -> str:
        """
        Insertar secciones de contenido (descripciones, etc.)
        
        Args:
            content: Contenido LaTeX base
            
        Returns:
            Contenido con secciones insertadas
        """
        # Insertar descripciones si existen

        descriptions = self.seismic.descriptions
        
        # Descripción de estructura
        if self.seismic.generate_description:
            section_description = r'\section{Descripción de la Estructura}'+'\n\n'
            section_description += descriptions.get('descripcion', '')
        else:
            section_description = ''
        content = content.replace(r'@content\_description', section_description)
        
        # Criterios de modelamiento
        if self.seismic.generate_criteria:
            section_modelamiento = r'\section{Criterios de modelamiento y cargas usadas}'+'\n \n' 
            section_modelamiento += descriptions.get('modelamiento', 'Sin criterios especificados.')
        else:
            section_modelamiento = ''
        content = content.replace(r'@content\_criteria', section_modelamiento)
        
        # Descripción de cargas
        if self.seismic.generate_criteria:
            section_cargas = r'\section{Cargas usadas}'+'\n \n'
            section_cargas += descriptions.get('cargas', 'Sin descripción de cargas.')
        else:
            section_cargas = ''
        content = content.replace(r'@content\_loads', section_cargas)

        # Modos principales
        if self.seismic.insert_modes:
            import textwrap
            import core.utils.latex_utils as ltx
            
            wrapper = textwrap.dedent('''
            \\begin{{figure}}[H]
                \centering
                \subfigure[Modo 1]{{\includegraphics[width={width_1}]{{images/{image_1} }}}}
                \subfigure[Modo 2]{{\includegraphics[width={width_2}]{{images/{image_2} }}}}
                \caption{{Modos principales del edificio}}
                \label{{modos}}
            \end{{figure}}
            ''')
            
            out_images_dir = self.images_dir
            seism = self.seismic
            i_nameX = Path(seism.urls_imagenes['defX']).name
            i_nameY = Path(seism.urls_imagenes['defY']).name
            shutil.copy(seism.urls_imagenes['defX'], out_images_dir / i_nameX)
            shutil.copy(seism.urls_imagenes['defY'], out_images_dir / i_nameY)
            
            width_1,width_2 = ltx.distribute_images(out_images_dir/i_nameX,
                                                    out_images_dir/i_nameY)
            image_modes = wrapper.format(width_1=width_1,width_2=width_2,
                                        image_1=i_nameX,image_2=i_nameY)
        else:
            image_modes = ''
        
        content = content.replace(r'@image\_modes', image_modes)
  

        
        return content
                

    

    



    def insert_tables(self, content: str) -> str:
        """Insertar tablas - personalizar en clases derivadas"""
        # Implementación base, se puede sobreescribir  
        return content


            



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



    def _create_table_generator(self):
        """
        Crear generador de tablas específico para el país
        Se sobrescribe en clases derivadas para especificar el país
        """
        return create_table_generator(self.seismic)


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


   
    def _generate_existing_table_data(self):
        """Generar datos para las tablas que ya existen"""
        print("  📋 Generando datos de tablas...")
        
        if not hasattr(self.seismic, 'data'):
            print("    ⚠️ No hay datos de análisis disponibles")
            return
            
        # Generar tabla modal si existe
        if hasattr(self.seismic.data, 'modal_data') and self.seismic.data.modal_data:
            self._save_modal_table_data()
        else:
            print("    ⚠️ Datos modales no disponibles")
        
        # Generar tabla torsional si existe  
        if hasattr(self.seismic.data, 'torsion_data') and self.seismic.data.torsion_data:
            self._save_torsion_table_data()
        else:
            print("    ⚠️ Datos torsionales no disponibles")

    def _save_modal_table_data(self):
        """Guardar datos de tabla modal en formato para LaTeX"""
        try:
            data = self.seismic.data.modal_data
            
            # Crear archivo de datos modales para LaTeX
            modal_file = self.output_dir / 'modal_data.txt'
            
            with open(modal_file, 'w', encoding='utf-8') as f:
                f.write("% Datos modales generados automáticamente\n")
                f.write("Modo,Periodo,Frecuencia,UX,UY,RZ\n")
                
                for i, row in enumerate(data):
                    periodo = row.get('period', 0)
                    freq = 1/periodo if periodo > 0 else 0
                    ux = row.get('ux', 0) * 100  # Convertir a porcentaje
                    uy = row.get('uy', 0) * 100
                    rz = row.get('rz', 0) * 100
                    
                    f.write(f"{i+1},{periodo:.3f},{freq:.3f},{ux:.1f},{uy:.1f},{rz:.1f}\n")
            
            print("  ✓ Datos modales guardados")
            
        except Exception as e:
            print(f"  ⚠️ Error guardando datos modales: {e}")

    def _save_torsion_table_data(self):
        """Guardar datos de tabla de irregularidad torsional"""
        try:
            data = self.seismic.data.torsion_data
            
            torsion_file = self.output_dir / 'torsion_data.txt'
            
            with open(torsion_file, 'w', encoding='utf-8') as f:
                f.write("% Datos de irregularidad torsional\n")
                f.write("Piso,Delta_max_X,Delta_prom_X,Relacion_X,Delta_max_Y,Delta_prom_Y,Relacion_Y\n")
                
                for row in data:
                    story = row.get('story', '')
                    delta_max_x = row.get('delta_max_x', 0)
                    delta_prom_x = row.get('delta_prom_x', 0) 
                    rel_x = delta_max_x / delta_prom_x if delta_prom_x > 0 else 0
                    delta_max_y = row.get('delta_max_y', 0)
                    delta_prom_y = row.get('delta_prom_y', 0)
                    rel_y = delta_max_y / delta_prom_y if delta_prom_y > 0 else 0
                    
                    f.write(f"{story},{delta_max_x:.3f},{delta_prom_x:.3f},{rel_x:.3f},")
                    f.write(f"{delta_max_y:.3f},{delta_prom_y:.3f},{rel_y:.3f}\n")
            
            print("  ✓ Datos torsionales guardados")
            
        except Exception as e:
            print(f"  ⚠️ Error guardando datos torsionales: {e}")

    def insert_existing_tables_in_memory(self, content: str) -> str:
        """
        Insertar las tablas existentes en el contenido LaTeX
        """
        # Generar tabla modal
        if hasattr(self.seismic.data, 'modal_data') and self.seismic.data.modal_data:
            modal_table = self._generate_modal_latex_table()
            content = content.replace('@table_modal', modal_table)
        else:
            content = content.replace('@table_modal', '% Tabla modal no disponible')
        
        # Generar tabla de irregularidad torsional
        if hasattr(self.seismic.data, 'torsion_data') and self.seismic.data.torsion_data:
            torsion_table = self._generate_torsion_latex_table()
            content = content.replace('@table_torsion', torsion_table)
        else:
            content = content.replace('@table_torsion', '% Tabla torsional no disponible')
        
        return content

    def _generate_modal_latex_table(self) -> str:
        """Generar tabla modal en formato LaTeX desde datos existentes"""
        try:
            data = self.seismic.data.modal_data
            
            table = """\\begin{table}[H]
\\centering
\\caption{Análisis Modal - Períodos y Masa Participativa}
\\footnotesize
\\begin{tabular}{|c|c|c|c|c|c|}
\\hline
\\textbf{Modo} & \\textbf{Período (s)} & \\textbf{Frecuencia (Hz)} & \\textbf{UX (\\%)} & \\textbf{UY (\\%)} & \\textbf{RZ (\\%)} \\\\
\\hline
    """
            
            for i, row in enumerate(data):
                periodo = row.get('period', 0)
                freq = 1/periodo if periodo > 0 else 0
                ux = row.get('ux', 0) * 100
                uy = row.get('uy', 0) * 100 
                rz = row.get('rz', 0) * 100
                
                table += f"{i+1} & {periodo:.3f} & {freq:.3f} & {ux:.1f} & {uy:.1f} & {rz:.1f} \\\\\n\\hline\n"
            
            table += """\\end{tabular}
    \\end{table}
    """
            return table
            
        except Exception as e:
            print(f"⚠️ Error generando tabla modal LaTeX: {e}")
            return "% Error en tabla modal"

    def _generate_torsion_latex_table(self) -> str:
        """Generar tabla de irregularidad torsional en formato LaTeX"""
        try:
            data = self.seismic.data.torsion_data
            
            table = """\\begin{table}[H]
\\centering
\\caption{Irregularidad Torsional por Piso}
\\footnotesize
\\begin{tabular}{|c|c|c|c|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{$\\delta_{max,X}$} & \\textbf{$\\delta_{prom,X}$} & \\textbf{Relación X} & \\textbf{$\\delta_{max,Y}$} & \\textbf{$\\delta_{prom,Y}$} & \\textbf{Relación Y} \\\\
\\hline
    """
            
            for row in data:
                story = row.get('story', '')
                delta_max_x = row.get('delta_max_x', 0)
                delta_prom_x = row.get('delta_prom_x', 0)
                rel_x = delta_max_x / delta_prom_x if delta_prom_x > 0 else 0
                delta_max_y = row.get('delta_max_y', 0) 
                delta_prom_y = row.get('delta_prom_y', 0)
                rel_y = delta_max_y / delta_prom_y if delta_prom_y > 0 else 0
                
                table += f"{story} & {delta_max_x:.3f} & {delta_prom_x:.3f} & {rel_x:.3f} & "
                table += f"{delta_max_y:.3f} & {delta_prom_y:.3f} & {rel_y:.3f} \\\\\n\\hline\n"
            
            table += """\\end{tabular}
    \\end{table}
    """
            return table
            
        except Exception as e:
            print(f"⚠️ Error generando tabla torsional LaTeX: {e}")
            return "% Error en tabla torsional"

   