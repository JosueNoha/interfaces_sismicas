"""
Generador de tablas LaTeX centralizado
Basado en las tablas de Perú como estándar, otras normas pueden sobrescribir
"""

import pandas as pd
from typing import Optional, Dict, Any


class SeismicTableGenerator:
    """Generador centralizado de tablas sísmicas en LaTeX"""
    
    def __init__(self, seismic_instance):
        """
        Inicializar generador de tablas
        
        Args:
            seismic_instance: Instancia de análisis sísmico
        """
        self.seismic = seismic_instance
        
    def generate_modal_table(self) -> str:
        """Generar tabla de análisis modal"""
        if not self._has_modal_data():
            return self._get_no_data_table("Análisis Modal", 
                ["Modo", "Período (s)", "UX (%)", "UY (%)", "SumUX (%)", "SumUY (%)"])
        
        modal_data = self.seismic.tables.modal
        
        table_content = """\\begin{table}[H]
\\centering
\\caption{Análisis Modal - Períodos y Masas Participativas}
\\label{tab:modal_analysis}
\\footnotesize
\\begin{tabular}{|c|c|c|c|c|c|}
\\hline
\\textbf{Modo} & \\textbf{Período (s)} & \\textbf{UX (\\%)} & \\textbf{UY (\\%)} & \\textbf{SumUX (\\%)} & \\textbf{SumUY (\\%)} \\\\
\\hline
"""
        
        # Mostrar máximo 12 modos más importantes
        for _, row in modal_data.head(12).iterrows():
            mode = int(row.get('Mode', 0))
            period = float(row.get('Period', 0))
            ux = float(row.get('UX', 0))
            uy = float(row.get('UY', 0))
            sum_ux = float(row.get('SumUX', 0))
            sum_uy = float(row.get('SumUY', 0))
            
            table_content += f"{mode} & {period:.4f} & {ux:.1f} & {uy:.1f} & {sum_ux:.1f} & {sum_uy:.1f} \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_drift_table_x(self) -> str:
        """Generar tabla de derivas dirección X"""
        return self._generate_drift_table('X')
    
    def generate_drift_table_y(self) -> str:
        """Generar tabla de derivas dirección Y"""
        return self._generate_drift_table('Y')
    
    def _generate_drift_table(self, direction: str) -> str:
        """Generar tabla de derivas para una dirección específica"""
        if not self._has_drift_data():
            return self._get_no_data_table(f"Derivas Dirección {direction}", 
                ["Piso", f"Deriva {direction}", "Límite", "Verificación"])
        
        drift_data = self.seismic.tables.drift_table
        drift_column = f'Drifts_{direction.lower()}'
        
        # Límite de deriva por defecto (puede ser sobrescrito por normas específicas)
        drift_limit = self._get_drift_limit()
        
        table_content = f"""\\begin{{table}}[H]
\\centering
\\caption{{Derivas de Entrepiso - Dirección {direction}}}
\\label{{tab:drifts_{direction.lower()}}}
\\footnotesize
\\begin{{tabular}}{{|c|c|c|c|}}
\\hline
\\textbf{{Piso}} & \\textbf{{Deriva {direction}}} & \\textbf{{Límite}} & \\textbf{{Verificación}} \\\\
\\hline
"""
        
        for _, row in drift_data.iterrows():
            story = str(row.get('Story', ''))
            drift = float(row.get(drift_column, 0.0))
            verification = "✓" if drift <= drift_limit else "✗"
            
            table_content += f"{story} & {drift:.4f} & {drift_limit:.3f} & {verification} \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_displacement_table(self) -> str:
        """Generar tabla de desplazamientos laterales"""
        if not self._has_displacement_data():
            return self._get_no_data_table("Desplazamientos Laterales", 
                ["Piso", "Despl. X", "Despl. Y"])
        
        disp_data = self.seismic.tables.displacements
        
        table_content = """\\begin{table}[H]
\\centering
\\caption{Desplazamientos Laterales}
\\label{tab:displacements}
\\footnotesize
\\begin{tabular}{|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{Despl. X} & \\textbf{Despl. Y} \\\\
\\hline
"""
        
        for _, row in disp_data.iterrows():
            story = str(row.get('Story', ''))
            disp_x = float(row.get('Maximum_x', 0.0))
            disp_y = float(row.get('Maximum_y', 0.0))
            
            table_content += f"{story} & {disp_x:.1f} & {disp_y:.1f} \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_shear_table_dynamic(self) -> str:
        """Generar tabla de cortantes dinámicos"""
        if not hasattr(self.seismic, 'shear_dynamic') or self.seismic.shear_dynamic is None:
            return self._get_no_data_table("Cortantes Dinámicos", 
                ["Piso", "Cortante X", "Cortante Y"])
        
        data = self._process_shear_for_table(self.seismic.shear_dynamic)
        
        table_content = f"""\\begin{{table}}[H]
    \\centering
    \\caption{{Cortantes Dinámicos por Piso}}
    \\label{{tab:shear_dynamic}}
    \\footnotesize
    \\begin{{tabular}}{{|c|c|c|}}
    \\hline
    \\textbf{{Piso}} & \\textbf{{Cortante X (tonf)}} & \\textbf{{Cortante Y (tonf)}} \\\\
    \\hline
    """
        
        for _, row in data.iterrows():
            story = row['Story']
            vx = row.get('V_x', row.get('VX', 0.0))
            vy = row.get('V_y', row.get('VY', 0.0))
            table_content += f"{story} & {vx:.3f} & {vy:.3f} \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_shear_table_static(self) -> str:
        """Generar tabla de cortantes estáticos"""
        if not hasattr(self.seismic, 'shear_static') or self.seismic.shear_static is None:
            return self._get_no_data_table("Cortantes Estáticos", 
                ["Piso", "Cortante X", "Cortante Y"])
        
        data = self._process_shear_for_table(self.seismic.shear_static)
        
        table_content = f"""\\begin{{table}}[H]
    \\centering
    \\caption{{Cortantes Estáticos por Piso}}
    \\label{{tab:shear_static}}
    \\footnotesize
    \\begin{{tabular}}{{|c|c|c|}}
    \\hline
    \\textbf{{Piso}} & \\textbf{{Cortante X (tonf)}} & \\textbf{{Cortante Y (tonf)}} \\\\
    \\hline
    """
        
        for _, row in data.iterrows():
            story = row['Story']
            vx = row.get('V_x', row.get('VX', 0.0))
            vy = row.get('V_y', row.get('VY', 0.0))
            table_content += f"{story} & {vx:.3f} & {vy:.3f} \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content

    
    def _process_shear_for_table(self, shear_data):
        """Procesar datos de cortante para formato de tabla según lógica original"""
        import re
        
        # Filtrar solo ubicación Bottom para cortantes por piso
        bottom_data = shear_data[shear_data['Location'] == 'Bottom'].copy()
        bottom_data = bottom_data[['Story', 'OutputCase', 'V']]
        
        # Obtener casos de carga X e Y
        seism_loads = getattr(self.seismic.loads, 'seism_loads', {})
        
        # Determinar si es dinámico o estático basado en los casos
        cases_x = [seism_loads.get('SDX', '')] # suponer caso dinámico
        if cases_x[0] in str(bottom_data['OutputCase'].values):
            cases_y = [seism_loads.get('SDY', '')]
        else:
            cases_x = [seism_loads.get('SSX', '')]  
            cases_y = [seism_loads.get('SSY', '')]
        
        # Filtrar casos vacíos
        cases_x = [c for c in cases_x if c]
        cases_y = [c for c in cases_y if c]
        
        if not cases_x or not cases_y:
            return bottom_data  # Retornar datos sin procesar si no hay casos
        
        # Crear regex para filtrar casos X e Y
        regex_x = '^(' + '|'.join(re.escape(c) for c in cases_x) + ')'
        regex_y = '^(' + '|'.join(re.escape(c) for c in cases_y) + ')'
        
        # Separar datos X e Y y combinar (lógica de tu código original)
        data_x = bottom_data[bottom_data['OutputCase'].str.match(regex_x)]
        data_y = bottom_data[bottom_data['OutputCase'].str.match(regex_y)]
        
        # Merge para tener X e Y en la misma fila por Story
        combined_data = data_x.merge(data_y, on='Story', suffixes=('_x', '_y'))
        
        # Renombrar columnas para consistencia
        if 'V_x' in combined_data.columns and 'V_y' in combined_data.columns:
            combined_data = combined_data[['Story', 'V_x', 'V_y']]
        
        return combined_data
        
    def generate_stiffness_table_x(self) -> str:
        """Generar tabla de irregularidad de rigidez dirección X"""
        return self._generate_stiffness_table('X')
    
    def generate_stiffness_table_y(self) -> str:
        """Generar tabla de irregularidad de rigidez dirección Y"""
        return self._generate_stiffness_table('Y')
    
    def _generate_stiffness_table(self, direction: str) -> str:
        """Generar tabla de irregularidad de rigidez"""
        table_content = f"""\\begin{{table}}[H]
\\centering
\\caption{{Irregularidad de Rigidez - Dirección {direction}}}
\\label{{tab:stiffness_{direction.lower()}}}
\\footnotesize
\\begin{{tabular}}{{|c|c|c|c|}}
\\hline
\\textbf{{Piso}} & \\textbf{{Rigidez}} & \\textbf{{Relación}} & \\textbf{{Irregular}} \\\\
\\hline
"""
        
        # Datos de ejemplo (requiere implementación específica con ETABS)
        for i in range(1, 6):
            table_content += f"Piso {i} & - & - & No \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_mass_table(self) -> str:
        """Generar tabla de irregularidad de masa"""
        table_content = """\\begin{table}[H]
\\centering
\\caption{Irregularidad de Masa}
\\label{tab:mass_irregularity}
\\footnotesize
\\begin{tabular}{|c|c|c|c|}
\\hline
\\textbf{Piso} & \\textbf{Masa} & \\textbf{Relación} & \\textbf{Irregular} \\\\
\\hline
"""
        
        # Datos de ejemplo
        for i in range(1, 6):
            table_content += f"Piso {i} & - & - & No \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_torsion_table_x(self) -> str:
        """Generar tabla de irregularidad torsional dirección X"""
        return self._generate_torsion_table('X')
    
    def generate_torsion_table_y(self) -> str:
        """Generar tabla de irregularidad torsional dirección Y"""
        return self._generate_torsion_table('Y')
    
    def _generate_torsion_table(self, direction: str) -> str:
        """Generar tabla de irregularidad torsional"""
        table_content = f"""\\begin{{table}}[H]
\\centering
\\caption{{Irregularidad Torsional - Dirección {direction}}}
\\label{{tab:torsion_{direction.lower()}}}
\\footnotesize
\\begin{{tabular}}{{|c|c|c|c|}}
\\hline
\\textbf{{Piso}} & \\textbf{{$\\Delta_{{max}}$}} & \\textbf{{$\\Delta_{{prom}}$}} & \\textbf{{Relación}} \\\\
\\hline
"""
        
        # Datos de ejemplo
        for i in range(1, 6):
            table_content += f"Piso {i} & - & - & - \\\\\n\\hline\n"
        
        table_content += "\\end{tabular}\n\\end{table}"
        return table_content
    
    def generate_all_tables(self) -> Dict[str, str]:
        """
        Generar todas las tablas estándar
        
        Returns:
            Diccionario con todas las tablas generadas
        """
        return {
            # Tablas principales
            'modal': self.generate_modal_table(),
            'drift_x': self.generate_drift_table_x(),
            'drift_y': self.generate_drift_table_y(),
            'displacements': self.generate_displacement_table(),
            'shear_dynamic': self.generate_shear_table_dynamic(),
            'shear_static': self.generate_shear_table_static(),
            
            # Tablas de irregularidades
            'stiffness_x': self.generate_stiffness_table_x(),
            'stiffness_y': self.generate_stiffness_table_y(),
            'mass': self.generate_mass_table(),
            'torsion_x': self.generate_torsion_table_x(),
            'torsion_y': self.generate_torsion_table_y()
        }
    
    # ===== MÉTODOS DE VALIDACIÓN DE DATOS =====
    
    def _has_modal_data(self) -> bool:
        """Verificar si hay datos modales disponibles"""
        return (hasattr(self.seismic, 'tables') and 
                hasattr(self.seismic.tables, 'modal') and 
                self.seismic.tables.modal is not None and 
                not self.seismic.tables.modal.empty)
    
    def _has_drift_data(self) -> bool:
        """Verificar si hay datos de derivas disponibles"""
        return (hasattr(self.seismic, 'tables') and 
                hasattr(self.seismic.tables, 'drift_table') and 
                self.seismic.tables.drift_table is not None and 
                not self.seismic.tables.drift_table.empty)
    
    def _has_displacement_data(self) -> bool:
        """Verificar si hay datos de desplazamientos disponibles"""
        return (hasattr(self.seismic, 'tables') and 
                hasattr(self.seismic.tables, 'displacements') and 
                self.seismic.tables.displacements is not None and 
                not self.seismic.tables.displacements.empty)
    
    def _has_shear_data(self) -> bool:
        """Verificar si hay datos de cortantes disponibles"""
        return (hasattr(self.seismic, 'tables') and 
                hasattr(self.seismic.tables, 'shear_table') and 
                self.seismic.tables.shear_table is not None)
    
    # ===== MÉTODOS DE CONFIGURACIÓN =====
    
    def _get_drift_limit(self) -> float:
        """Obtener límite de deriva desde la instancia sísmica"""
        return getattr(self.seismic, 'max_drift', 0.007)
    
    def _get_no_data_table(self, table_name: str, columns: list) -> str:
        """
        Generar tabla indicando que no hay datos disponibles
        
        Args:
            table_name: Nombre de la tabla
            columns: Lista de nombres de columnas
            
        Returns:
            Tabla LaTeX indicando falta de datos
        """
        num_cols = len(columns)
        col_spec = '|' + 'c|' * num_cols
        
        header = ' & '.join([f"\\textbf{{{col}}}" for col in columns])
        
        table_content = f"""\\begin{{table}}[H]
\\centering
\\caption{{{table_name}}}
\\footnotesize
\\begin{{tabular}}{{{col_spec}}}
\\hline
{header} \\\\
\\hline
\\multicolumn{{{num_cols}}}{{|c|}}{{Datos no disponibles - Requiere conexión con ETABS}} \\\\
\\hline
\\end{{tabular}}
\\end{{table}}"""
        
        return table_content
    



# ===== CLASES ESPECIALIZADAS PARA NORMAS ESPECÍFICAS =====

class BoliviaTableGenerator(SeismicTableGenerator):
    """Generador de tablas específico para Bolivia - CNBDS 2023"""
    
    def _get_drift_limit(self) -> float:
        """Límite de deriva específico para Bolivia"""
        # CNBDS 2023 - puede variar según el sistema estructural
        return 0.007  # Concreto armado típico


class PeruTableGenerator(SeismicTableGenerator):
    """Generador de tablas específico para Perú - E.030"""
    
    def _get_drift_limit(self) -> float:
        """Límite de deriva específico para Perú"""
        # E.030 - límite para concreto armado
        return 0.007


# ===== FUNCIÓN FACTORY =====

def create_table_generator(seismic_instance, country: str = None) -> SeismicTableGenerator:
    """
    Crear generador de tablas específico para el país
    
    Args:
        seismic_instance: Instancia de análisis sísmico
        country: País ('bolivia', 'peru', o None para genérico)
        
    Returns:
        Generador de tablas apropiado
    """
    if country == 'bolivia':
        return BoliviaTableGenerator(seismic_instance)
    elif country == 'peru':
        return PeruTableGenerator(seismic_instance)
    else:
        # Generador genérico por defecto
        return SeismicTableGenerator(seismic_instance)