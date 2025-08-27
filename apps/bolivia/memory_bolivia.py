"""
Generación de memorias LaTeX específicas para Bolivia
Hereda funcionalidad común de MemoryBase
"""
import re
import shutil
import numpy as np
from pathlib import Path

from core.base.memory_base import MemoryBase
from core.utils import latex_utils as ltx

class BoliviaMemoryGenerator(MemoryBase):
    """Generador de memorias LaTeX para análisis sísmico Bolivia"""
    
    def __init__(self, seismic_instance, output_dir):
        super().__init__(seismic_instance, output_dir)
        self.template_path = Path(__file__).parent / 'resources' / 'templates' / 'plantilla_bolivia.ltx'
        
    def generate_memory(self):
        """Generar memoria completa para Bolivia"""
        # Preparar directorios y archivos base
        self.setup_output_structure()
        
        # Generar contenido específico
        content = self.load_template()
        content = self.replace_basic_parameters(content)
        content = self.replace_bolivia_specific_content(content)
        
        # Actualizar imágenes y datos
        self.actualize_images()
        self.generate_spectrum_data()
        
        # Guardar memoria final
        self.save_memory(content)
        
        return self.output_dir / 'memoria_bolivia.tex'
        
    def replace_bolivia_specific_content(self, content):
        """Reemplazar contenido específico de Bolivia"""
        
        # Configurar parámetros sísmicos Bolivia
        content = self.replace_seismic_parameters_bolivia(content)
        
        # Configurar sistemas estructurales
        content = self.replace_structural_systems_bolivia(content)
        
        # Configurar tablas de derivas
        content = self.replace_drift_tables_bolivia(content)
        
        # Configurar contenido descriptivo
        content = self.replace_descriptive_content(content)
        
        return content
        
    def replace_seismic_parameters_bolivia(self, content):
        """Reemplazar parámetros sísmicos específicos de Bolivia"""
        
        # Parámetros específicos CNBDS 2023
        replacements = {
            '@Fa': str(self.seismic.Fa),
            '@Fv': str(self.seismic.Fv),
            '@So': str(self.seismic.So),
            '@Samax': str(round(2.5 * self.seismic.Fa * self.seismic.So, 2)),
            '@To': str(round(0.15 * self.seismic.Fv / self.seismic.Fa, 2)),
            '@Ts': str(round(0.5 * self.seismic.Fv / self.seismic.Fa, 2)),
            '@Tl': str(round(4 * self.seismic.Fv / self.seismic.Fa, 2))
        }
        
        for key, value in replacements.items():
            content = content.replace(key, value)
            
        return content
        
    def replace_structural_systems_bolivia(self, content):
        """Reemplazar sistemas estructurales Bolivia"""
        
        # Obtener sistemas estructurales
        sist_x = self.seismic.sistema_x
        sist_y = self.seismic.sistema_y
        
        # Datos de sistemas estructurales Bolivia
        data = {
            'Pórticos Especiales de Acero Resistentes a Momento (SMF)':['Pórticos Especiales Resistentes a Momento (SMF)',8],
            'Pórticos Intermedios de Acero Resistentes a Momento (IMF)':['Pórticos Intermedios Resistentes a Momento (IMF)',4.5],
            'Pórticos Ordinarios de Acero Resistentes a Momento (OMF)':['Pórticos Ordinarios Resistentes a Momento (OMF)',4],
            'Pórticos Especiales de Acero Concénticamente Arriostrados':['Pórticos Especiales Concentricamente Arriostrados (SCBF)',7],
            'Pórticos Ordinarios de Acero Concénticamente Arriostrados':['Pórticos Ordinarios Concentricamente Arriostrados (OCBF)',4],
            'Pórticos Acero Excéntricamente Arriostrados':['Pórticos Excéntricamente Arriostrados (EBF)',8],
            'Pórticos de Concreto Armado':['Pórticos',8],
            'Dual de Concreto Armado':['Dual',7],
            'De Muros Estructurales de Concreto Armado':['De muros estructurales',6],
            'Muros de Ductilidad Limita de Concreto Armado':['Muros de ductilidad limitada',4],
            'Albañilería Armada o Confinada':[r'\textbf{Albañilería Armada o Confinada}',3],
            'Madera':[r'\textbf{Madera}',7]
        }
        
        # Generar tabla de sistemas estructurales
        sistema_table = self.generate_structural_system_table(data, sist_x, sist_y)
        content = content.replace('@table_structural_systems', sistema_table)
        
        return content
        
    def replace_drift_tables_bolivia(self, content):
        """Reemplazar tablas de derivas específicas de Bolivia"""
        
        # Generar tabla de derivas según CNBDS 2023
        drift_table = self.generate_bolivia_drift_table()
        content = content.replace('@table_drifts', drift_table)
        
        return content
        
    def generate_bolivia_drift_table(self):
        """Generar tabla de derivas según normativa Bolivia"""
        
        # Límites de deriva CNBDS 2023
        limites_deriva = {
            'Concreto Armado': 0.007,
            'Acero': 0.010,
            'Albañilería': 0.005,
            'Madera': 0.010
        }
        
        # Generar contenido LaTeX para tabla
        tabla_latex = r'''
\begin{table}[H]
\centering
\caption{Límites de deriva de entrepiso - CNBDS 2023}
\label{tab:limites_deriva}
\begin{tabular}{|l|c|}
\hline
\textbf{Material/Sistema} & \textbf{Límite de deriva} \\
\hline
Concreto armado & 0.007 \\
\hline
Acero & 0.010 \\
\hline
Albañilería armada o confinada & 0.005 \\
\hline
Madera & 0.010 \\
\hline
\end{tabular}
\end{table}
'''
        
        return tabla_latex
        
    def generate_spectrum_data(self):
        """Generar datos del espectro de respuesta para Bolivia"""
        T, Sa = self.seismic.espectro_bolivia()
        datos = np.column_stack((T, Sa))
        np.savetxt(self.output_dir / 'espectro_bolivia.txt', datos, fmt="%.3f")
        
    def actualize_images(self):
        """Actualizar imágenes específicas de Bolivia"""
        
        source_dir = Path(__file__).parent / 'resources' / 'images'
        out_images_dir = self.output_dir / 'images'
        
        if not out_images_dir.exists():
            out_images_dir.mkdir(parents=True)
        
        # Copiar mapa sísmico de Bolivia si existe
        mapa_bolivia = source_dir / 'MapaSismicoBolivia.png'
        if mapa_bolivia.exists():
            shutil.copy(mapa_bolivia, out_images_dir / 'MapaSismicoBolivia.png')
        
        # Guardar figuras generadas
        if hasattr(self.seismic, 'fig_drifts') and self.seismic.fig_drifts:
            self.seismic.fig_drifts.savefig(
                out_images_dir / "derivas.pdf", 
                dpi=300, 
                bbox_inches='tight'
            )
        
        if hasattr(self.seismic, 'fig_displacements') and self.seismic.fig_displacements:
            self.seismic.fig_displacements.savefig(
                out_images_dir / "desplazamientos.pdf",
                dpi=300,
                bbox_inches='tight'
            )