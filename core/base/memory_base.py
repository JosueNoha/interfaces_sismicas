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


    def _copy_project_image(self, source_path: str, dest_name: str):
        """Copiar imagen del proyecto al directorio de salida"""
        try:
            dest_path = self.images_dir / dest_name
            shutil.copy2(source_path, dest_path)
        except Exception as e:
            print(f"Error copiando imagen {source_path}: {e}")
            

    def _save_matplotlib_figures(self):
        """Guardar todas las figuras de matplotlib con mejor logging"""
        figure_mappings = [
            ('fig_drifts', 'derivas.pdf', 'Derivas'),
            ('fig_displacements', 'desplazamientos_laterales.pdf', 'Desplazamientos'),
            ('fig_spectrum', 'espectro.pdf', 'Espectro'),
            ('dynamic_shear_fig', 'cortante_dinamico.pdf', 'Cortante Dinámico'),
            ('static_shear_fig', 'cortante_estatico.pdf', 'Cortante Estático')
        ]
        
        saved_count = 0
        for fig_attr, filename, display_name in figure_mappings:
            if hasattr(self.seismic, fig_attr):
                fig = getattr(self.seismic, fig_attr)
                if fig is not None:
                    try:
                        output_path = self.images_dir / filename
                        fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
                        print(f"✓ {display_name} guardado: {filename}")
                        saved_count += 1
                    except Exception as e:
                        print(f"✗ Error guardando {display_name}: {e}")
                else:
                    print(f"⚠ {display_name}: figura es None")
            else:
                print(f"⚠ {display_name}: no existe en el objeto sísmico")
        
        print(f"📊 Total figuras guardadas: {saved_count}/5")

    def _save_single_figure(self, fig, filename, fig_name):
        """Guardar una sola figura con manejo de errores centralizado"""
        try:
            output_path = self.images_dir / filename
            fig.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
            print(f"✓ {fig_name} guardado: {output_path.name}")
        except Exception as e:
            print(f"✗ Error guardando {fig_name}: {e}")

    def _copy_static_resources(self):
        """Copiar recursos estáticos específicos del país - implementar en clases derivadas"""
        # Implementación por defecto vacía
        # Las clases derivadas deben sobrescribir este método
        print("  ℹ️ Sin recursos estáticos específicos definidos")

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

    def validate_required_data(self) -> tuple[bool, list]:
        """
        Validar los datos esenciales para generar memoria
        
        Returns:
            tuple: (es_valido, lista_errores)
        """
        errors = []
        
        # 1. Validar parámetros sísmicos mínimos según país
        country = getattr(self, 'country', '').lower()
        
        if country == 'bolivia':
            required_params = ['I']
        elif country == 'peru':
            required_params = ['U'] 
        else:
            required_params = []
        
        for param in required_params:
            if not hasattr(self.seismic, param) or getattr(self.seismic, param) is None:
                errors.append(f"❌ Falta parámetro: {param}")
        
        # 2. Validar que existan imágenes cargadas
        if not hasattr(self.seismic, 'urls_imagenes') or not self.seismic.urls_imagenes:
            errors.append("❌ No se han cargado imágenes del proyecto")
        else:
            # Contar imágenes válidas
            valid_images = 0
            for img_type, img_path in self.seismic.urls_imagenes.items():
                if img_path and os.path.exists(img_path):
                    valid_images += 1
            
            if valid_images == 0:
                errors.append("❌ Ninguna imagen válida encontrada")
        
        # 3. Validar que existan algunos datos de análisis
        if not hasattr(self.seismic, 'data') or not self.seismic.data:
            errors.append("❌ No hay datos de análisis disponibles")
        
        return len(errors) == 0, errors

    def _validate_required_images(self) -> list:
        """Validar que las imágenes requeridas estén disponibles"""
        errors = []
        
        required_images = {
            'portada': 'Imagen de portada',
            'planta': 'Planta típica', 
            '3d': 'Vista 3D',
            'defX': 'Deformada en X',
            'defY': 'Deformada en Y'
        }
        
        if not hasattr(self.seismic, 'urls_imagenes'):
            errors.append("❌ No se han cargado imágenes del proyecto")
            return errors
        
        missing_count = 0
        for img_key, img_desc in required_images.items():
            img_path = self.seismic.urls_imagenes.get(img_key)
            if not img_path or not os.path.exists(img_path):
                errors.append(f"❌ Falta imagen: {img_desc}")
                missing_count += 1
        
        # Información sobre recursos estáticos disponibles
        if missing_count > 0:
            errors.append(f"💡 Tip: Algunos recursos estáticos del país pueden estar disponibles automáticamente")
        
        return errors

    def _validate_required_tables(self) -> list:
        """Validar que las tablas requeridas estén disponibles"""
        errors = []
        
        # Validar datos básicos para tablas
        if not hasattr(self.seismic, 'data'):
            errors.append("❌ No hay datos de análisis disponibles")
            return errors
        
        data = self.seismic.data
        
        # Validar tabla modal
        if not hasattr(data, 'modal_data') or not data.modal_data:
            errors.append("❌ Datos de análisis modal no disponibles")
        
        # Validar tabla de irregularidad torsional  
        if not hasattr(data, 'torsion_data') or not data.torsion_data:
            errors.append("❌ Datos de irregularidad torsional no disponibles")
        
        return errors

    def _validate_existing_plots(self) -> list:
        """Validar que los gráficos matplotlib existentes estén disponibles"""
        errors = []
        
        required_plots = {
            'fig_drifts': 'Gráfico de derivas',
            'fig_displacements': 'Gráfico de desplazamientos',
            'fig_spectrum': 'Gráfico del espectro'
        }
        
        for fig_attr, fig_desc in required_plots.items():
            if not hasattr(self.seismic, fig_attr):
                errors.append(f"❌ Falta gráfico: {fig_desc}")
            else:
                fig = getattr(self.seismic, fig_attr)
                if fig is None:
                    errors.append(f"❌ Gráfico no generado: {fig_desc}")
        
        return errors

    def actualize_images(self):
        """Actualizar imágenes en el directorio de salida"""
        # Crear directorio de imágenes
        ensure_directory_exists(str(self.images_dir))
        
        # AGREGAR: Asegurar que las figuras existan antes de guardar
        self._ensure_figures_exist()
        
        # Copiar imágenes del proyecto si existen
        if hasattr(self.seismic, 'urls_imagenes'):
            for img_type, img_path in self.seismic.urls_imagenes.items():
                if img_path and os.path.exists(img_path):
                    self._copy_project_image(img_path, f"{img_type}.jpg")
        
        # Guardar gráficos generados por matplotlib
        self._save_matplotlib_figures()
        
        # Copiar recursos estáticos
        self._copy_static_resources()
        
    def _ensure_figures_exist(self):
        """Asegurar que las figuras matplotlib existan antes de guardar"""
        # Si las figuras no existen, intentar crearlas desde datos existentes
        if hasattr(self.seismic, 'shear_dynamic') and not self.seismic.shear_dynamic.empty:
            if not hasattr(self.seismic, 'dynamic_shear_fig') or self.seismic.dynamic_shear_fig is None:
                # Recrear figura dinámica usando casos guardados
                sx = getattr(self.seismic, '_saved_sx_dynamic', [])
                sy = getattr(self.seismic, '_saved_sy_dynamic', [])
                if sx and sy:
                    self.seismic.dynamic_shear_fig = self.seismic._create_shear_figure(
                        self.seismic.shear_dynamic, sx, sy, 'dynamic'
                    )
        
        if hasattr(self.seismic, 'shear_static') and not self.seismic.shear_static.empty:
            if not hasattr(self.seismic, 'static_shear_fig') or self.seismic.static_shear_fig is None:
                # Recrear figura estática usando casos guardados
                sx = getattr(self.seismic, '_saved_sx_static', [])
                sy = getattr(self.seismic, '_saved_sy_static', [])
                if sx and sy:
                    self.seismic.static_shear_fig = self.seismic._create_shear_figure(
                        self.seismic.shear_static, sx, sy, 'static'
                    )

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

    def _save_existing_matplotlib_figures(self):
        """Guardar solo las figuras matplotlib que ya existen"""
        print("  📈 Guardando gráficos generados...")
        
        figure_mappings = [
            # CAMBIAR ESTOS NOMBRES:
            ('fig_drifts', 'derivas.pdf'),                    # ✓ Correcto
            ('fig_displacements', 'desplazamientos_laterales.pdf'),  # ✓ Correcto  
            ('fig_spectrum', 'espectro.pdf'),                 # ✓ Correcto
            ('dynamic_shear_fig', 'cortante_dinamico.pdf'),  # ✓ Correcto
            ('static_shear_fig', 'cortante_estatico.pdf')    # ✓ Correcto
        ]
        
        saved_count = 0
        for fig_attr, filename in figure_mappings:
            if hasattr(self.seismic, fig_attr):
                fig = getattr(self.seismic, fig_attr)
                if fig is not None:
                    try:
                        output_path = self.images_dir / filename
                        fig.savefig(
                            output_path, 
                            dpi=300, 
                            bbox_inches='tight'
                        )
                        print(f"    ✓ {filename} guardado")
                        saved_count += 1
                    except Exception as e:
                        print(f"    ❌ Error guardando {filename}: {e}")
                else:
                    print(f"    ⚠️ {fig_attr}: Figura es None")
            else:
                print(f"    ⚠️ {fig_attr}: Atributo no existe en self.seismic")
        
        print(f"  📊 Gráficos matplotlib: {saved_count}/{len(figure_mappings)} guardados")
        
        # AGREGAR DEBUG INFO:
        print("  🔍 DEBUG - Atributos de figuras disponibles:")
        for attr in dir(self.seismic):
            if 'fig' in attr.lower() or 'shear' in attr.lower():
                value = getattr(self.seismic, attr, None)
                if value is not None:
                    print(f"    • {attr}: {'Figura' if hasattr(value, 'savefig') else type(value)}")

    def _force_generate_missing_plots(self):
        """Ejecutar métodos backend existentes para generar gráficos faltantes"""
        print("🔄 Ejecutando métodos backend para generar gráficos...")
        
        try:
            # Derivas
            if not hasattr(self.seismic, 'fig_drifts') or self.seismic.fig_drifts is None:
                print("  📊 Ejecutando cálculo de derivas...")
                if hasattr(self.seismic, 'calculate_drifts'):
                    self.seismic.calculate_drifts(None, False)  # SapModel=None, use_combo=False
                elif hasattr(self.seismic, '_create_drift_figure'):
                    self.seismic.fig_drifts = self.seismic._create_drift_figure()
            
            # Desplazamientos
            if not hasattr(self.seismic, 'fig_displacements') or self.seismic.fig_displacements is None:
                print("  📈 Ejecutando cálculo de desplazamientos...")
                if hasattr(self.seismic, 'calculate_displacements'):
                    self.seismic.calculate_displacements()
                elif hasattr(self.seismic, '_create_displacement_figure'):
                    self.seismic.fig_displacements = self.seismic._create_displacement_figure()
            
            # Cortantes
            if (not hasattr(self.seismic, 'dynamic_shear_fig') or self.seismic.dynamic_shear_fig is None or
                not hasattr(self.seismic, 'static_shear_fig') or self.seismic.static_shear_fig is None):
                print("  ⚡ Ejecutando cálculo de cortantes...")
                if hasattr(self.seismic, 'calculate_shear_forces'):
                    self.seismic.calculate_shear_forces()
                elif hasattr(self.seismic, '_create_shear_figure'):
                    # Si existen los datos, crear las figuras
                    if hasattr(self.seismic, 'shear_dynamic') and not self.seismic.shear_dynamic.empty:
                        self.seismic.dynamic_shear_fig = self.seismic._create_shear_figure(
                            self.seismic.shear_dynamic, [], [], 'dynamic'
                        )
                    if hasattr(self.seismic, 'shear_static') and not self.seismic.shear_static.empty:
                        self.seismic.static_shear_fig = self.seismic._create_shear_figure(
                            self.seismic.shear_static, [], [], 'static'
                        )
            
            # Espectro
            if not hasattr(self.seismic, 'fig_spectrum') or self.seismic.fig_spectrum is None:
                print("  📊 Ejecutando generación del espectro...")
                if hasattr(self.seismic, 'generate_spectrum_plot'):
                    self.seismic.generate_spectrum_plot()
                elif hasattr(self.seismic, '_create_spectrum_figure'):
                    self.seismic.fig_spectrum = self.seismic._create_spectrum_figure()
            
            print("✅ Métodos backend ejecutados")
            
        except Exception as e:
            print(f"⚠️ Error ejecutando métodos backend: {e}")
 

    def _generate_dummy_plot(self, plot_attr: str, plot_name: str):
        """Generar gráfico dummy si no existe el real"""
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f'{plot_name}\n(Datos no disponibles)', 
                    ha='center', va='center', fontsize=14, 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgray"))
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.set_title(plot_name)
            
            # Asignar la figura al atributo correspondiente
            setattr(self.seismic, plot_attr, fig)
            print(f"    → Generado gráfico placeholder para {plot_name}")
            
        except Exception as e:
            print(f"    ❌ Error generando placeholder: {e}")

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
        
    def validate_seismic_data(self) -> bool:
        """Validación básica de datos sísmicos"""
        if not self.seismic:
            return False
        
        # Solo validar que existan los parámetros mínimos
        country = getattr(self, 'country', '').lower()
        
        if country == 'bolivia':
            return hasattr(self.seismic, 'I') 
        elif country == 'peru':
            return hasattr(self.seismic, 'U')
        else:
            return True

    def insert_content_sections(self, content: str) -> str:
        """
        Insertar secciones de contenido (descripciones, etc.)
        
        Args:
            content: Contenido LaTeX base
            
        Returns:
            Contenido con secciones insertadas
        """
        # Insertar descripciones si existen
        if hasattr(self.seismic, 'descriptions'):
            descriptions = self.seismic.descriptions
            
            # Descripción de estructura
            desc_estructura = descriptions.get('descripcion', 'Sin descripción proporcionada.')
            content = content.replace('@descripcion_estructura', desc_estructura)
            
            # Criterios de modelamiento
            desc_modelamiento = descriptions.get('modelamiento', 'Sin criterios especificados.')
            content = content.replace('@criterios_modelamiento', desc_modelamiento)
            
            # Descripción de cargas
            desc_cargas = descriptions.get('cargas', 'Sin descripción de cargas.')
            content = content.replace('@descripcion_cargas', desc_cargas)
        
        else:
            # Valores por defecto si no hay descripciones
            content = content.replace('@descripcion_estructura', 'Sin descripción proporcionada.')
            content = content.replace('@criterios_modelamiento', 'Sin criterios especificados.')
            content = content.replace('@descripcion_cargas', 'Sin descripción de cargas.')
        
        return content

    def generate_spectrum_data(self):
        """Generar datos del espectro de respuesta para gráficos"""
        try:
            # Crear datos básicos del espectro si no existen
            T = np.linspace(0.01, 4.0, 400)
            
            # Intentar usar método específico del país si existe
            if hasattr(self.seismic, 'calculate_spectrum'):
                Sa = self.seismic.calculate_spectrum(T)
            else:
                # Generar espectro genérico usando parámetros disponibles
                Sa = self._generate_generic_spectrum(T)
            
            # Guardar datos para LaTeX
            spectrum_data = np.column_stack((T, Sa))
            spectrum_file = self.output_dir / 'espectro_datos.txt'
            
            np.savetxt(spectrum_file, spectrum_data, 
                    fmt="%.4f", delimiter="\t",
                    header="Periodo(s)\tSa(g)")
            
            print(f"✅ Datos del espectro guardados: {spectrum_file}")
            
        except Exception as e:
            print(f"⚠️ Error generando datos del espectro: {e}")

    def _generate_generic_spectrum(self, T):
        """Generar espectro genérico usando parámetros disponibles"""
        # Parámetros por defecto
        I = getattr(self.seismic, 'I', 1.0)
        R = getattr(self.seismic, 'R', 3.0)
        
        # Intentar usar parámetros específicos del país
        if hasattr(self.seismic, 'Z'):  # Perú
            Z = getattr(self.seismic, 'Z', 0.25)
            U = getattr(self.seismic, 'U', 1.0)
            S = getattr(self.seismic, 'S', 1.0)
            Sa_max = 2.5 * Z * U * S * I / R
        elif hasattr(self.seismic, 'Fa'):  # Bolivia
            Fa = getattr(self.seismic, 'Fa', 1.86)
            So = getattr(self.seismic, 'So', 2.9)
            Sa_max = 2.5 * Fa * So * I / R
        else:
            Sa_max = 1.0  # Valor por defecto
        
        # Crear espectro simplificado
        Sa = np.full_like(T, Sa_max)
        
        return Sa

    def compile_latex(self, tex_file: Path, run_twice: bool = False):
        """
        Compilar archivo LaTeX a PDF
        
        Args:
            tex_file: Ruta al archivo .tex
            run_twice: Si ejecutar pdflatex dos veces (para referencias)
        """
        try:
            import subprocess
            import os
            
            # Cambiar al directorio del archivo
            original_cwd = os.getcwd()
            os.chdir(tex_file.parent)
            
            # Comando pdflatex
            cmd = ['pdflatex', '-interaction=nonstopmode', tex_file.name]
            
            # Primera compilación
            print("🔄 Compilando LaTeX (1/2 si es necesario)...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"❌ Error en primera compilación LaTeX:")
                print(result.stdout[-500:] if result.stdout else "Sin stdout")
                print(result.stderr[-500:] if result.stderr else "Sin stderr")
                raise Exception("Error en compilación LaTeX")
            
            # Segunda compilación si es necesario
            if run_twice:
                print("🔄 Compilando LaTeX (2/2)...")
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"❌ Error en segunda compilación LaTeX:")
                    print(result.stdout[-500:] if result.stdout else "Sin stdout")
                    raise Exception("Error en segunda compilación LaTeX")
            
            # Limpiar archivos temporales
            self._clean_latex_temp_files(tex_file)
            
            print(f"✅ PDF generado: {tex_file.with_suffix('.pdf')}")
            
            # Restaurar directorio original
            os.chdir(original_cwd)
            
        except FileNotFoundError:
            raise Exception("pdflatex no encontrado. Instale una distribución LaTeX (MiKTeX, TeX Live, etc.)")
        except Exception as e:
            # Restaurar directorio original en caso de error
            try:
                os.chdir(original_cwd)
            except:
                pass
            raise e

    def _clean_latex_temp_files(self, tex_file: Path):
        """Limpiar archivos temporales de LaTeX"""
        temp_extensions = ['.aux', '.log', '.fdb_latexmk', '.fls', '.synctex.gz']
        
        for ext in temp_extensions:
            temp_file = tex_file.with_suffix(ext)
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass  # Ignorar errores al eliminar temporales
