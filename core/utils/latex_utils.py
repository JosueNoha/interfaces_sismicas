"""
Utilidades LaTeX compartidas para generación de reportes sísmicos
"""

import re
import pandas as pd
from typing import Optional
from typing import Optional, Dict, Any


def escape_for_latex(text):
    text = re.sub(r'\\\\(?=\s*(?:\n|$))', r'\\\\\\\\', text)
    text = re.sub(r'(?<!\\)\\([a-zA-Z])', r'\\\\\1', text)
    return text

def distribute_images(image_1,image_2):
    from PIL import Image
    # Cargar la imagen
    im_1 = Image.open(image_1)
    width, height = im_1.size
    relation_1 = width / height
    im_2 = Image.open(image_2)
    width, height = im_2.size
    relation_2 = width / height
    
    width_1 = 0.95*relation_1/(relation_1+relation_2)
    width_2 = 0.95*relation_2/(relation_1+relation_2)
    #width=0.54\textwidth
    return fr'{width_1:.2f}\textwidth', fr'{width_2:.2f}\textwidth'

def dataframe_latex(df: pd.DataFrame, columns: list = None, decimals: int = 2, 
                   escape: bool = True) -> str:
    """
    Convierte DataFrame a tabla LaTeX tabular
    
    Args:
        df: DataFrame a convertir
        columns: Lista de nombres de columnas a usar
        decimals: Número de decimales para números
        escape: Si escapar caracteres especiales
        
    Returns:
        Código LaTeX de la tabla
    """
    if columns:
        df_work = df.copy()
        df_work.columns = columns
    else:
        df_work = df.copy()
    
    # Formatear números con decimales especificados
    for col in df_work.columns:
        if df_work[col].dtype in ['float64', 'float32', 'int64', 'int32']:
            df_work[col] = df_work[col].round(decimals)
    
    # Generar código LaTeX
    num_cols = len(df_work.columns)
    col_spec = '|' + 'c|' * num_cols
    
    latex_code = f"\\begin{{tabular}}{{{col_spec}}}\n"
    latex_code += "\\hline\n"
    
    # Encabezados
    headers = []
    for col in df_work.columns:
        header = escape_for_latex(str(col)) if escape else str(col)
        headers.append(f"\\textbf{{{header}}}")
    
    latex_code += " & ".join(headers) + " \\\\\n"
    latex_code += "\\hline\n"
    
    # Datos
    for _, row in df_work.iterrows():
        row_data = []
        for value in row:
            if escape:
                row_data.append(escape_for_latex(str(value)))
            else:
                row_data.append(str(value))
        
        latex_code += " & ".join(row_data) + " \\\\\n"
        latex_code += "\\hline\n"
    
    latex_code += "\\end{tabular}"
    
    return latex_code


def table_wrapper(caption: str, label: Optional[str] = None) -> str:
    """
    Genera wrapper de tabla LaTeX con caption y label
    
    Args:
        caption: Título de la tabla
        label: Etiqueta opcional para referenciar
        
    Returns:
        Template de wrapper con placeholder {tabular_code}
    """
    label_code = f"\\label{{tab:{label.lower().replace(' ', '_')}}}" if label else ""
    
    wrapper = f"""\\begin{{table}}[H]
\\centering
\\caption{{{caption}}}
{label_code}
{{tabular_code}}
\\end{{table}}"""
    
    return wrapper

def replace_template_variables(content: str, variables: Dict[str, Any]) -> str:
    """
    Reemplaza variables en template LaTeX (MEJORADO)
    Maneja múltiples patrones de formato usados en Bolivia y Perú
    """
    for var, value in variables.items():
        # Patrones consolidados de ambos países
        patterns = [
            # Bolivia patterns
            rf'@{re.escape(var)}.0nn',  # Entero
            rf'@{re.escape(var)}.1nu',  # 1 decimal
            rf'@{re.escape(var)}.2nu',  # 2 decimales
            rf'@{re.escape(var)}.3nu',  # 3 decimales  
            rf'@{re.escape(var)}.2F4',  # Formato especial Bolivia
            # Patrón básico
            rf'@{re.escape(var)}',
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, str(value), content)
    
    return content

def extract_table(content: str, caption: str) -> str:
    """
    Extrae una tabla LaTeX específica del contenido basado en el caption
    
    Args:
        content: Contenido LaTeX completo
        caption: Caption de la tabla a extraer
        
    Returns:
        Código LaTeX de la tabla extraída
    """
    # Buscar patrón de tabla con el caption específico
    pattern = rf'\\begin{{table}}.*?\\caption{{{re.escape(caption)}}}.*?\\end{{table}}'
    match = re.search(pattern, content, re.DOTALL)
    
    if match:
        return match.group(0)
    else:
        return ""


def highlight_column(table_latex: str, column_identifier: str, 
                    text_color: str = '[rgb]{1,0,0}', text_bf: bool = True,
                    first_row: int = 3) -> str:
    """
    Resalta una columna específica en una tabla LaTeX
    
    Args:
        table_latex: Código LaTeX de la tabla
        column_identifier: Identificador de la columna a resaltar
        text_color: Color del texto (formato LaTeX)
        text_bf: Si aplicar negrita
        first_row: Fila desde donde empezar a resaltar
        
    Returns:
        Tabla LaTeX con columna resaltada
    """
    lines = table_latex.split('\n')
    result_lines = []
    
    # Encontrar el índice de la columna basado en el identificador
    header_line = None
    for i, line in enumerate(lines):
        if '\\textbf{' in line and column_identifier in line:
            header_line = line
            # Contar posición de la columna
            parts = line.split('&')
            col_index = -1
            for j, part in enumerate(parts):
                if column_identifier in part:
                    col_index = j
                    break
            break
    
    if col_index == -1:
        return table_latex
    
    # Aplicar resaltado a las filas de datos
    row_count = 0
    for line in lines:
        if '\\\\' in line and '&' in line and '\\textbf{' not in line:
            row_count += 1
            if row_count >= first_row:
                parts = line.split('&')
                if col_index < len(parts):
                    value = parts[col_index].strip()
                    if text_bf:
                        highlighted = f"\\textcolor{text_color}{{\\textbf{{{value}}}}}"
                    else:
                        highlighted = f"\\textcolor{text_color}{{{value}}}"
                    parts[col_index] = highlighted
                    line = '&'.join(parts)
        
        result_lines.append(line)
    
    return '\n'.join(result_lines)


def replace_template_variables(content: str, variables: dict) -> str:
    """
    Reemplaza variables en template LaTeX
    
    Args:
        content: Contenido del template
        variables: Diccionario con variables a reemplazar
        
    Returns:
        Contenido con variables reemplazadas
    """
    for var, value in variables.items():
        # Formato: @variable.0nn o @variable
        patterns = [
            rf'@{re.escape(var)}.0nn',
            rf'@{re.escape(var)}'
        ]
        
        for pattern in patterns:
            content = re.sub(pattern, str(value), content)
    
    return content