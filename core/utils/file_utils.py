"""
Utilidades para manejo de archivos y directorios
"""

import os
import shutil
from pathlib import Path
from typing import Optional


def create_output_directory(base_dir: str, folder_name: str = "reporte_sismico") -> str:
    """
    Crea directorio de salida único, agregando número si ya existe
    
    Args:
        base_dir: Directorio base donde crear la carpeta
        folder_name: Nombre base de la carpeta
        
    Returns:
        Ruta del directorio creado
    """
    output_dir = os.path.join(base_dir, folder_name)
    count = 1
    
    while os.path.exists(output_dir):
        output_dir = os.path.join(base_dir, f'{folder_name}_{count}')
        count += 1
    
    os.makedirs(output_dir)
    return output_dir


def ensure_directory_exists(directory: str) -> None:
    """
    Asegura que un directorio existe, creándolo si es necesario
    
    Args:
        directory: Ruta del directorio
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


def copy_resources(source_dir: str, dest_dir: str, resource_type: str = "images") -> None:
    """
    Copia recursos (imágenes, templates, etc.) al directorio de destino
    
    Args:
        source_dir: Directorio fuente de recursos
        dest_dir: Directorio destino
        resource_type: Tipo de recursos a copiar (images, templates)
    """
    source_path = Path(source_dir) / resource_type
    dest_path = Path(dest_dir) / resource_type
    
    if source_path.exists():
        ensure_directory_exists(str(dest_path))
        
        # Copiar todos los archivos del directorio
        for item in source_path.iterdir():
            if item.is_file():
                shutil.copy2(str(item), str(dest_path))
            elif item.is_dir():
                shutil.copytree(str(item), str(dest_path / item.name), 
                              dirs_exist_ok=True)


def get_resource_path(app_name: str, resource_type: str, filename: str) -> Path:
    """
    Obtiene la ruta a un recurso específico de la aplicación
    
    Args:
        app_name: Nombre de la aplicación (bolivia, peru)
        resource_type: Tipo de recurso (templates, images)
        filename: Nombre del archivo
        
    Returns:
        Path al recurso
    """
    base_path = Path(__file__).parent.parent.parent
    return base_path / "apps" / app_name / "resources" / resource_type / filename


def read_template(template_path: str, encoding: str = 'utf-8') -> str:
    """
    Lee un archivo template LaTeX
    
    Args:
        template_path: Ruta al template
        encoding: Codificación del archivo
        
    Returns:
        Contenido del template
    """
    try:
        with open(template_path, 'r', encoding=encoding) as file:
            return file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template no encontrado: {template_path}")
    except UnicodeDecodeError:
        raise UnicodeDecodeError(f"Error de codificación en template: {template_path}")


def write_latex_file(content: str, output_path: str, encoding: str = 'utf-8') -> None:
    """
    Escribe contenido LaTeX a archivo
    
    Args:
        content: Contenido LaTeX
        output_path: Ruta de salida
        encoding: Codificación del archivo
    """
    try:
        with open(output_path, 'w', encoding=encoding) as file:
            file.write(content)
    except Exception as e:
        raise Exception(f"Error escribiendo archivo LaTeX: {e}")


def get_shared_resource_path(filename: str) -> Path:
    """
    Obtiene ruta a recurso compartido (iconos, etc.)
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Path al recurso compartido
    """
    base_path = Path(__file__).parent.parent.parent
    return base_path / "shared_resources" / filename


def validate_file_exists(filepath: str) -> bool:
    """
    Valida si un archivo existe
    
    Args:
        filepath: Ruta al archivo
        
    Returns:
        True si existe, False caso contrario
    """
    return os.path.exists(filepath) and os.path.isfile(filepath)


def validate_directory_exists(dirpath: str) -> bool:
    """
    Valida si un directorio existe
    
    Args:
        dirpath: Ruta al directorio
        
    Returns:
        True si existe, False caso contrario
    """
    return os.path.exists(dirpath) and os.path.isdir(dirpath)