"""
Generación de memoria de cálculo para Perú - E.030
Adaptado desde el código existente de seism_memory.py
"""

import os
import shutil
import subprocess
from pathlib import Path
import re

from core.base.memory_base import MemoryBase
from core.utils import unit_tool

u = unit_tool.Units()

# Diccionario de unidades (mantenido del código original)
unit_dict = {
    'mm': u.mm,
    'm': u.m, 
    'cm': u.cm,
    'pies': u.ft,
    'pulg': u.inch,
    'tonf': u.tonf,
    'kN': u.kN,
    'kip': 4.4482*u.kN
}


class PeruMemoryGenerator(MemoryBase):
    """Generador de memoria específico para Perú - E.030"""
    
    def __init__(self, config):
        super().__init__(config)
        self.latex_template = config.get('template_path', 'apps/peru/resources/templates/plantilla_peru.ltx')


def save_variables(variables_dict, content):
    """Reemplazar variables en el template LaTeX"""
    for var_name, var_value in variables_dict.items():
        if var_name not in ['content', 'seism']:
            # Reemplazar diferentes formatos de variable
            patterns = [
                f'@{var_name}.0nn',
                f'@{var_name}.1nu',
                f'@{var_name}.2nu',
                f'@{var_name}.3nu',
                f'@{var_name}'
            ]
            
            for pattern in patterns:
                if pattern in content:
                    if '.0nn' in pattern:
                        replacement = str(var_value)
                    elif '.1nu' in pattern:
                        replacement = f'{float(var_value):.1f}' if isinstance(var_value, (int, float)) else str(var_value)
                    elif '.2nu' in pattern:
                        replacement = f'{float(var_value):.2f}' if isinstance(var_value, (int, float)) else str(var_value)
                    elif '.3nu' in pattern:
                        replacement = f'{float(var_value):.3f}' if isinstance(var_value, (int, float)) else str(var_value)
                    else:
                        replacement = str(var_value)
                    
                    content = content.replace(pattern, replacement)
    
    return content


def espectro_respuestas(seism, output_dir):
    """Generar archivo de datos del espectro para el gráfico LaTeX"""
    try:
        T, Sa = seism.espectro_peru()
        
        # Crear archivo de datos para TikZ
        espectro_file = os.path.join(output_dir, 'espectro_peru.txt')
        with open(espectro_file, 'w') as f:
            for t, sa in zip(T, Sa):
                f.write(f'{t:.3f} {sa:.6f}\n')
                
    except Exception as e:
        print(f"Error generando espectro: {e}")


def actualize_images(seism, output_dir):
    """Copiar imágenes necesarias para la memoria"""
    base_path = Path(__file__).parent
    source_dir = base_path / 'resources' / 'images'
    out_images_dir = Path(output_dir) / 'images'
    
    if not os.path.exists(out_images_dir):
        os.makedirs(out_images_dir)

    # Guardar gráficos generados por matplotlib
    if hasattr(seism, 'fig_drifts'):
        seism.fig_drifts.savefig(os.path.join(out_images_dir, "derivas.pdf"), dpi=300, bbox_inches='tight')

    if hasattr(seism, 'fig_displacements'):
        seism.fig_displacements.savefig(os.path.join(out_images_dir, "desplazamientos_laterales.pdf"), dpi=300, bbox_inches='tight')

    # Gráficos de cortantes
    if hasattr(seism, 'dynamic_shear_fig'):
        seism.dynamic_shear_fig.savefig(os.path.join(out_images_dir, "cortante_dinamico.pdf"), dpi=300, bbox_inches='tight')
    
    if hasattr(seism, 'static_shear_fig'):
        seism.static_shear_fig.savefig(os.path.join(out_images_dir, "cortante_estatico.pdf"), dpi=300, bbox_inches='tight')

    # Copiar imágenes estáticas desde resources
    if source_dir.exists():
        extensiones_imagen = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff')
        for archivo in os.listdir(source_dir):
            origen_archivo = os.path.join(source_dir, archivo)
            destino_archivo = os.path.join(out_images_dir, archivo)
            if os.path.isfile(origen_archivo) and archivo.lower().endswith(extensiones_imagen):
                shutil.copy2(origen_archivo, destino_archivo)


def modal_table(modal_data, content):
    """Insertar tabla modal en el contenido LaTeX"""
    if modal_data is None:
        return content
        
    # Generar tabla LaTeX para análisis modal
    table_content = "\\begin{table}[H]\n\\centering\n\\caption{Análisis Modal}\n"
    table_content += "\\begin{tabular}{|c|c|c|c|c|c|}\n\\hline\n"
    table_content += "Modo & Período (s) & UX (\\%) & UY (\\%) & SumUX (\\%) & SumUY (\\%) \\\\\n\\hline\n"
    
    for _, row in modal_data.iterrows():
        table_content += f"{row['Mode']} & {row['Period']:.3f} & {row['UX']:.1f} & {row['UY']:.1f} & {row['SumUX']:.1f} & {row['SumUY']:.1f} \\\\\n\\hline\n"
    
    table_content += "\\end{tabular}\n\\end{table}\n"
    
    # Insertar en el contenido (buscar marcador específico)
    content = content.replace("@modal_table", table_content)
    
    return content


def torsion_table(torsion_x, torsion_y, content):
    """Insertar tabla de torsión en el contenido LaTeX"""
    if torsion_x is None or torsion_y is None:
        return content
        
    # Implementar tabla de torsión
    table_content = "\\begin{table}[H]\n\\centering\n\\caption{Irregularidad por Torsión}\n"
    table_content += "\\begin{tabular}{|c|c|c|}\n\\hline\n"
    table_content += "Piso & Dirección X & Dirección Y \\\\\n\\hline\n"
    # Agregar datos de torsión procesados
    table_content += "\\end{tabular}\n\\end{table}\n"
    
    content = content.replace("@torsion_table", table_content)
    return content


def shear_table(shear_static, shear_dynamic, content):
    """Insertar tabla de cortantes en el contenido LaTeX"""
    if shear_static is None or shear_dynamic is None:
        return content
        
    # Implementar tabla de cortantes
    table_content = "\\begin{table}[H]\n\\centering\n\\caption{Fuerzas Cortantes}\n"
    table_content += "\\begin{tabular}{|c|c|c|c|c|}\n\\hline\n"
    table_content += "Piso & Estático X & Estático Y & Dinámico X & Dinámico Y \\\\\n\\hline\n"
    # Agregar datos procesados
    table_content += "\\end{tabular}\n\\end{table}\n"
    
    content = content.replace("@shear_table", table_content)
    return content


def drift_table(table_drifts, content):
    """Insertar tabla de derivas en el contenido LaTeX"""
    if table_drifts is None:
        return content
        
    # Implementar tabla de derivas
    table_content = "\\begin{table}[H]\n\\centering\n\\caption{Derivas de Entrepiso}\n"
    table_content += "\\begin{tabular}{|c|c|c|}\n\\hline\n"
    table_content += "Piso & Deriva X (\\%) & Deriva Y (\\%) \\\\\n\\hline\n"
    
    for _, row in table_drifts.iterrows():
        table_content += f"{row['Story']} & {row['Drifts_x']:.3f} & {row['Drifts_y']:.3f} \\\\\n\\hline\n"
    
    table_content += "\\end{tabular}\n\\end{table}\n"
    
    content = content.replace("@drift_table", table_content)
    return content


def disp_table(table_disp, content):
    """Insertar tabla de desplazamientos en el contenido LaTeX"""
    if table_disp is None:
        return content
        
    # Implementar tabla de desplazamientos
    table_content = "\\begin{table}[H]\n\\centering\n\\caption{Desplazamientos Laterales}\n"
    table_content += "\\begin{tabular}{|c|c|c|}\n\\hline\n"
    table_content += "Piso & Desplazamiento X (mm) & Desplazamiento Y (mm) \\\\\n\\hline\n"
    
    for _, row in table_disp.iterrows():
        table_content += f"{row['Story']} & {row['Maximum_x']:.1f} & {row['Maximum_y']:.1f} \\\\\n\\hline\n"
    
    table_content += "\\end{tabular}\n\\end{table}\n"
    
    content = content.replace("@disp_table", table_content)
    return content


def general_variables(seism, content):
    """Procesar variables generales del proyecto"""
    # Procesar imágenes del proyecto
    image_replacements = {
        '@image_portada': '',
        '@image_planta': '',
        '@image_3d': '',
        '@image_defX': '',
        '@image_defY': ''
    }
    
    # Verificar si hay imágenes cargadas
    if hasattr(seism, 'urls_imagenes'):
        for key, url in seism.urls_imagenes.items():
            if url and os.path.exists(url):
                # Procesar imagen para inclusión en LaTeX
                image_name = f"{key}.jpg"  # Asumiendo formato jpg
                latex_include = f"\\includegraphics[width=0.8\\textwidth]{{{image_name}}}"
                image_replacements[f'@image_{key}'] = latex_include
    
    # Aplicar reemplazos
    for pattern, replacement in image_replacements.items():
        content = content.replace(pattern, replacement)
    
    # Procesar contenido de descripciones
    if hasattr(seism, 'descriptions'):
        content_replacements = {
            '@content_description': seism.descriptions.get('descripcion', ''),
            '@content_criteria': seism.descriptions.get('modelamiento', ''),
            '@content_loads': seism.descriptions.get('cargas', '')
        }
        
        for pattern, replacement in content_replacements.items():
            content = content.replace(pattern, replacement)
    
    return content


def numeric_variables(seism, content=None):
    """Procesar todas las variables numéricas del análisis"""
    if content is None:
        latex_template = seism.config.get('template_path', 'apps/peru/resources/templates/plantilla_peru.ltx')
        with open(latex_template, 'r', encoding='utf-8') as file:
            content = file.read()
    
    # Variables sísmicas básicas E.030
    Z, U, S, Tp, Tl = seism.Z, seism.U, seism.S, seism.Tp, seism.Tl

    # Variables de proyecto
    proyecto = seism.proyecto
    ubicacion = seism.ubicacion  
    autor = seism.autor
    fecha = seism.fecha
    
    # Variables calculadas (si están disponibles)
    Samax = getattr(seism, 'Sa_max', 0)
    
    # Variables de cortante (si están disponibles)
    Vsx = getattr(seism, 'Vsx', 0)
    Vsy = getattr(seism, 'Vsy', 0) 
    Vdx = getattr(seism, 'Vdx', 0)
    Vdy = getattr(seism, 'Vdy', 0)
    
    if Vsx > 0 and Vsy > 0:
        perVdsx = Vdx/Vsx*100
        perVdsy = Vdy/Vsy*100
    else:
        perVdsx = perVdsy = 0
        
    # Variables de factores de escala (si están disponibles)
    FEx = getattr(seism, 'FEx', 1.0)
    FEy = getattr(seism, 'FEy', 1.0)
    
    # Variables de límites
    mpmin = getattr(seism, 'mp_min', 0)
    permin = getattr(seism, 'per_min', 80)
    funit = seism.u_f
    
    # Variables de desplazamientos (si están disponibles)
    if hasattr(seism, 'disp_h') and hasattr(seism, 'disp_x') and hasattr(seism, 'disp_y'):
        hb = seism.disp_h.max() if hasattr(seism.disp_h, 'max') else 0
        dispMaxx = seism.disp_x.max() if hasattr(seism.disp_x, 'max') else 0
        dispMaxy = seism.disp_y.max() if hasattr(seism.disp_y, 'max') else 0
        smin1 = hb*0.006
        smin2 = max(smin1/2, 1.5*u.cm)
        sminx = dispMaxx*2/3
        sminy = dispMaxy*2/3  
        smin = max(smin2, sminx, sminy)
    else:
        hb = dispMaxx = dispMaxy = smin = 0
    
    # Variable global para unidades (mantenido del código original)
    global F4
    F4 = unit_dict[seism.u_f]
    
    return save_variables(locals(), content)


def generate_memory(seism, output_dir, content=None, delete_tex=False, run_twice=False):
    """Generar memoria de cálculo completa para Perú - E.030"""
    
    # Leer template si no se proporciona contenido
    if content is None:
        latex_template = seism.config.get('template_path', 'apps/peru/resources/templates/plantilla_peru.ltx')
        with open(latex_template, 'r', encoding='utf-8') as file:
            content = file.read()
    
    latex_out = os.path.join(output_dir, "memoria.tex")
    
    # Actualizar imágenes y generar gráficos
    actualize_images(seism, output_dir)
    espectro_respuestas(seism, output_dir)
    
    # Insertar tablas si están disponibles
    if hasattr(seism, 'tables'):
        if hasattr(seism.tables, 'modal') and seism.tables.modal is not None:
            content = modal_table(seism.tables.modal, content)
            
        if hasattr(seism.tables, 'torsion_table'):
            # Procesar datos de torsión por dirección
            torsion_data = seism.tables.torsion_table
            # Separar por casos sísmicos X e Y (implementación simplificada)
            content = torsion_table(torsion_data, torsion_data, content)
            
        if hasattr(seism.tables, 'drift_table'):
            drift_data = seism.tables.drift_table[['Story', 'Drifts_x', 'Drifts_y']]
            content = drift_table(drift_data, content)
            
        if hasattr(seism.tables, 'displacements'):
            disp_data = seism.tables.displacements[['Story', 'Maximum_x', 'Maximum_y']]
            content = disp_table(disp_data, content)
    
    # Procesar variables numéricas y generales
    content = numeric_variables(seism, content)
    content = general_variables(seism, content)
    
    # Escribir archivo LaTeX
    with open(latex_out, 'w', encoding='utf-8') as file:
        file.write(content)
    
    # Compilar PDF si pdflatex está disponible
    if shutil.which('pdflatex') is not None:
        try:
            # Primera compilación
            subprocess.run(['pdflatex', '-interaction=nonstopmode', latex_out], 
                         cwd=output_dir, check=True, capture_output=True)
            
            # Segunda compilación si es necesario (para referencias)
            if run_twice:
                subprocess.run(['pdflatex', '-interaction=nonstopmode', latex_out], 
                             cwd=output_dir, check=True, capture_output=True)
            
            # Limpiar archivos temporales
            extensiones_temp = ('.log', '.aux', '.fdb_latexmk', '.fls', '.toc')
            for archivo in os.listdir(output_dir):
                ruta_archivo = os.path.join(output_dir, archivo)
                if os.path.isfile(ruta_archivo) and archivo.endswith(extensiones_temp):
                    try:
                        os.remove(ruta_archivo)
                    except:
                        pass
            
        except subprocess.CalledProcessError as e:
            print(f"Error compilando LaTeX: {e}")
            raise
    else:
        print("pdflatex no encontrado. Solo se generó el archivo .tex")
    
    # Eliminar archivo .tex si se solicita
    if delete_tex:
        try:
            os.remove(latex_out)
            shutil.rmtree(os.path.join(output_dir, "images"), ignore_errors=True)
        except:
            pass