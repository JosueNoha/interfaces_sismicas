"""Manejadores de archivos compartidos"""
import os
import json
import shutil
from pathlib import Path
from PyQt5.QtWidgets import QFileDialog

class FileManager:
    @staticmethod
    def select_image_file(parent, title="Seleccionar imagen"):
        file_path, _ = QFileDialog.getOpenFileName(
            parent, title, "",
            "Archivos de imagen (*.png *.jpg *.jpeg *.bmp *.gif);;Todos los archivos (*)"
        )
        return file_path if file_path else None
    
    @staticmethod
    def select_save_file(parent, title="Guardar archivo", default_name="", file_filter=""):
        file_path, _ = QFileDialog.getSaveFileName(parent, title, default_name, file_filter)
        return file_path if file_path else None
    
    @staticmethod
    def copy_file(source_path, destination_path, overwrite=False):
        try:
            source = Path(source_path)
            destination = Path(destination_path)
            
            if not source.exists():
                return False, "El archivo origen no existe"
            
            if destination.exists() and not overwrite:
                return False, "El archivo destino ya existe"
            
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            return True, "Archivo copiado exitosamente"
        except Exception as e:
            return False, f"Error al copiar archivo: {str(e)}"
    
    @staticmethod
    def save_json(data, file_path):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True, "JSON guardado exitosamente"
        except Exception as e:
            return False, f"Error al guardar JSON: {str(e)}"