"""
Generación de memoria LaTeX para Bolivia - CNBDS 2023
Renombrado desde memory_bolivia.py y simplificado usando MemoryBase
"""

import numpy as np
from pathlib import Path
import shutil

from core.base.memory_base import MemoryBase
from core.utils.table_generator import BoliviaTableGenerator


class BoliviaMemoryGenerator(MemoryBase):
    """Generador de memorias LaTeX para análisis sísmico Bolivia - CNBDS 2023"""
    
    def __init__(self, seismic_instance, output_dir):
        super().__init__(seismic_instance, output_dir)
        
        # Path al template específico de Bolivia
        self.templates_dir = Path(__file__).parent / 'resources' / 'templates'
        
        # Variables específicas de Bolivia para el template
        self.template_variables = self._get_bolivia_variables()

    def get_default_template_path(self) -> str:
        """Obtener path del template por defecto de Bolivia"""
        return str(self.templates_dir / 'plantilla_bolivia.ltx')

    def generate_memory(self) -> Path:
        """Generar memoria completa para Bolivia - CNBDS 2023"""
        # Validar datos mínimos
        if not self.validate_seismic_data():
            raise ValueError("Datos sísmicos incompletos para generar memoria")
        
        # Preparar estructura de salida
        self.setup_output_structure()
        
        # Cargar template
        content = self.load_template()
        
        # Reemplazar contenido
        content = self.replace_basic_parameters(content)
        content = self._replace_bolivia_specific_content(content)
        content = self.insert_content_sections(content)
        
        # Generar recursos
        self.actualize_images()
        self.generate_spectrum_data()
        
        # Generar tablas usando generador centralizado
        content = self.insert_tables(content)
        
        # Guardar archivo final
        tex_file = self.save_memory(content, 'memoria_bolivia.tex')
        
        # Compilar a PDF
        self.compile_latex(tex_file, run_twice=True)
        
        return tex_file

    def _get_bolivia_variables(self) -> dict:
        """Obtener variables específicas de Bolivia para el template"""
        variables = {}
        
        # Parámetros sísmicos CNBDS 2023
        if hasattr(self.seismic, 'Fa'):
            variables['Fa'] = self.seismic.Fa
        if hasattr(self.seismic, 'Fv'):
            variables['Fv'] = self.seismic.Fv
        if hasattr(self.seismic, 'So'):
            variables['So'] = self.seismic.So
        
        # Parámetros espectrales calculados
        if hasattr(self.seismic, 'SDS'):
            variables['Samax'] = self.seismic.SDS
        elif hasattr(self.seismic, 'Fa') and hasattr(self.seismic, 'So'):
            variables['Samax'] = round(2.5 * self.seismic.Fa * self.seismic.So, 3)
        
        # Períodos espectrales
        if hasattr(self.seismic, 'Fa') and hasattr(self.seismic, 'Fv'):
            variables.update({
                'To': round(0.15 * self.seismic.Fv / self.seismic.Fa, 4),
                'Ts': round(0.5 * self.seismic.Fv / self.seismic.Fa, 4),
                'Tl': round(4 * self.seismic.Fv / self.seismic.Fa, 4)
            })
        
        # Cortantes si están disponibles
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
        
        # Unidades
        variables['funit'] = getattr(self.seismic, 'u_f', 'kN')
        variables['permin'] = 80.0  # Porcentaje mínimo típico
        
        return variables

    def _create_table_generator(self):
        """Crear generador de tablas específico para Bolivia"""
        return BoliviaTableGenerator(self.seismic)

    def _replace_bolivia_specific_content(self, content: str) -> str:
        """Reemplazar contenido específico de Bolivia"""
        
        # Reemplazar variables específicas de CNBDS 2023
        for var_name, var_value in self.template_variables.items():
            # Diferentes formatos de variables en el template
            patterns = [
                f'@{var_name}.0nn',
                f'@{var_name}.1nu', 
                f'@{var_name}.2nu',
                f'@{var_name}.3nu',
                f'@{var_name}.2F4',
                f'@{var_name}'
            ]
            
            for pattern in patterns:
                if pattern in content:
                    replacement = self._format_variable_value(var_value, pattern)
                    content = content.replace(pattern, replacement)
        
        return content

    def _format_variable_value(self, value, pattern: str) -> str:
        """Formatear valor de variable según el patrón"""
        if '.0nn' in pattern:
            return str(value)
        elif '.1nu' in pattern:
            return f'{float(value):.1f}' if isinstance(value, (int, float)) else str(value)
        elif '.2nu' in pattern:
            return f'{float(value):.2f}' if isinstance(value, (int, float)) else str(value)
        elif '.3nu' in pattern:
            return f'{float(value):.3f}' if isinstance(value, (int, float)) else str(value)
        elif '.2F4' in pattern:
            return f'{float(value):.2f}' if isinstance(value, (int, float)) else str(value)
        else:
            return str(value)

    def _insert_bolivia_tables(self, content: str) -> str:
        """Insertar tablas específicas de Bolivia"""
        
        # Tabla modal
        if hasattr(self.seismic, 'tables') and hasattr(self.seismic.tables, 'modal'):
            modal_content = self._generate_modal_table_bolivia()
            content = content.replace('@table_modal', modal_content)
        
        # Tabla de torsión
        torsion_content = self._generate_torsion_tables_bolivia()
        content = content.replace('@table_torsion_x', torsion_content['x'])
        content = content.replace('@table_torsion_y', torsion_content['y'])
        
        # Tabla de derivas
        drift_content = self._generate_drift_table_bolivia()
        content = content.replace('@table_drifts', drift_content)
        
        # Tabla de desplazamientos
        disp_content = self._generate_displacement_table_bolivia()
        content = content.replace('@table_disp', disp_content)
        
        # Tablas de cortantes
        shear_content = self._generate_shear_tables_bolivia()
        content = content.replace('@table_shear_dynamic', shear_content['dynamic'])
        content = content.replace('@table_shear_static', shear_content['static'])
        
        return content

    def _generate_modal_table_bolivia(self) -> str:
        """Generar tabla modal específica para Bolivia"""
        if not hasattr(self.seismic, 'tables') or not hasattr(self.seismic.tables, 'modal'):
            return "% Tabla modal no disponible"
        
        modal_data = self.seismic.tables.modal
        if modal_data is None or modal_data.empty:
            return "% Datos modales no disponibles"
        
        # Generar tabla LaTeX para CNBDS 2023
        table_content = """\\begin{table}[H]
\\centering
\\caption{Análisis Modal - Períodos y Masas Participativas}
\\label{tab:modal_bolivia}
\\footnotesize
\\begin{tabular}{|c|c|c|c|c|c|}
\\hline
\\textbf{Modo} & \\textbf{Período (s)} & \\textbf{UX (\\%)} & \\textbf{UY (\\%)} & \\textbf{SumUX (\\%)} & \\textbf{SumUY (\\%)} \\\\
\\hline
"""
        
        # Agregar filas de datos
        for _, row in modal_data.head(12).iterrows():  # Mostrar máximo 12 modos
            table_content += f"{int(row['Mode'])} & {row['Period']:.4f} & {row['UX']:.1f} & {row['UY']:.1f} & {row['SumUX']:.1f} & {row['SumUY']:.1f} \\\\\n\\hline\n"
        
        table_content += """\\end{tabular}
\\end{table}
"""
        
        return table_content

    def _generate_torsion_tables_bolivia(self) -> dict:
        """Generar tablas de irregularidad torsional para Bolivia"""
        # Implementación básica - puede expandirse con datos reales
        basic_table = """\\begin{table}[H]
\\centering
\\caption{Irregularidad Torsional}
\\footnotesize
\\begin{tabular}{|c|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{$\\Delta_{max}$} & \\textbf{$\\Delta_{prom}$} & \\textbf{Relación} \\\\
\\hline
% Datos de torsión - requiere implementación específica
Sin datos disponibles & - & - & - \\\\
\\hline
\\end{tabular}
\\end{table}
"""
        
        return {'x': basic_table, 'y': basic_table}

    def _generate_drift_table_bolivia(self) -> str:
        """Generar tabla de derivas para Bolivia"""
        if (hasattr(self.seismic, 'tables') and 
            hasattr(self.seismic.tables, 'drift_table') and 
            self.seismic.tables.drift_table is not None):
            
            drift_data = self.seismic.tables.drift_table
            
            table_content = """\\begin{table}[H]
\\centering
\\caption{Derivas de Entrepiso - CNBDS 2023}
\\label{tab:derivas_bolivia}
\\footnotesize
\\begin{tabular}{|c|c|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{Deriva X} & \\textbf{Deriva Y} & \\textbf{Límite} & \\textbf{Verificación} \\\\
\\hline
"""
            
            limite_deriva = 0.007  # Límite típico para concreto
            
            for _, row in drift_data.iterrows():
                deriva_x = row.get('Drifts_x', 0.0)
                deriva_y = row.get('Drifts_y', 0.0)
                cumple_x = "✓" if deriva_x <= limite_deriva else "✗"
                cumple_y = "✓" if deriva_y <= limite_deriva else "✗"
                
                table_content += f"""{row.get('Story', '')} & {deriva_x:.4f} & {deriva_y:.4f} & {limite_deriva:.3f} & {cumple_x}/{cumple_y} \\\\
\\hline
"""
            
            table_content += """\\end{tabular}
\\end{table}
"""
            return table_content
        
        return "% Tabla de derivas no disponible"

    def _generate_displacement_table_bolivia(self) -> str:
        """Generar tabla de desplazamientos para Bolivia"""
        if (hasattr(self.seismic, 'tables') and 
            hasattr(self.seismic.tables, 'displacements') and 
            self.seismic.tables.displacements is not None):
            
            disp_data = self.seismic.tables.displacements
            
            table_content = """\\begin{table}[H]
\\centering
\\caption{Desplazamientos Laterales Máximos}
\\label{tab:desplazamientos_bolivia}
\\footnotesize
\\begin{tabular}{|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{Despl. X (mm)} & \\textbf{Despl. Y (mm)} \\\\
\\hline
"""
            
            for _, row in disp_data.iterrows():
                table_content += f"{row.get('Story', '')} & {row.get('Maximum_x', 0.0):.1f} & {row.get('Maximum_y', 0.0):.1f} \\\\\n\\hline\n"
            
            table_content += """\\end{tabular}
\\end{table}
"""
            return table_content
        
        return "% Tabla de desplazamientos no disponible"

    def _generate_shear_tables_bolivia(self) -> dict:
        """Generar tablas de cortantes para Bolivia"""
        basic_table = """\\begin{table}[H]
\\centering
\\caption{Fuerzas Cortantes}
\\footnotesize
\\begin{tabular}{|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{Cortante X} & \\textbf{Cortante Y} \\\\
\\hline
% Datos requieren conexión con ETABS
Sin datos disponibles & - & - \\\\
\\hline
\\end{tabular}
\\end{table}"""
        
        return {'dynamic': basic_table, 'static': basic_table}

    def _copy_static_resources(self):
        """Copiar recursos estáticos de Bolivia"""
        # Copiar mapa sísmico de Bolivia si existe
        resources_dir = Path(__file__).parent / 'resources' / 'images'
        if resources_dir.exists():
            try:
                for image_file in resources_dir.glob('*.png'):
                    shutil.copy2(image_file, self.images_dir)
            except Exception as e:
                print(f"Error copiando recursos Bolivia: {e}")

    def generate_spectrum_data(self):
        """Generar datos del espectro específico de Bolivia"""
        try:
            if hasattr(self.seismic, 'espectro_bolivia'):
                T, Sa = self.seismic.espectro_bolivia()
            else:
                # Generar espectro básico con parámetros Bolivia
                T = np.linspace(0.1, 4.0, 100)
                Fa = getattr(self.seismic, 'Fa', 1.86)
                So = getattr(self.seismic, 'So', 2.9)
                Sa = 2.5 * Fa * So * np.ones_like(T)  # Simplificado
            
            data = np.column_stack((T, Sa))
            np.savetxt(self.output_dir / 'espectro_bolivia.txt', data, fmt="%.4f")
            
        except Exception as e:
            print(f"Error generando datos espectro Bolivia: {e}")
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
    generator = BoliviaMemoryGenerator(seismic_instance, output_dir)
    return generator.generate_memory()