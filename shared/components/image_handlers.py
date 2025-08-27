"""Manejadores de imágenes compartidos"""
import os
from pathlib import Path
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt

class ImageHandler:
    @staticmethod
    def load_and_display_image(image_path, label_widget, max_width=300, max_height=200):
        try:
            if not image_path or not os.path.exists(image_path):
                label_widget.clear()
                label_widget.setText("Sin imagen")
                label_widget.setAlignment(Qt.AlignCenter)
                return False, "Archivo no encontrado"
            
            pixmap = QPixmap(image_path)
            if pixmap.isNull():
                label_widget.clear()
                label_widget.setText("Error al cargar imagen")
                label_widget.setAlignment(Qt.AlignCenter)
                return False, "No se pudo cargar la imagen"
            
            scaled_pixmap = pixmap.scaled(max_width, max_height, 
                                        Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            label_widget.setPixmap(scaled_pixmap)
            label_widget.setAlignment(Qt.AlignCenter)
            return True, "Imagen cargada exitosamente"
            
        except Exception as e:
            label_widget.clear()
            label_widget.setText("Error al procesar imagen")
            label_widget.setAlignment(Qt.AlignCenter)
            return False, f"Error: {str(e)}"
    
    @staticmethod
    def clear_image_display(label_widget, placeholder_text="Sin imagen"):
        label_widget.clear()
        label_widget.setText(placeholder_text)
        label_widget.setAlignment(Qt.AlignCenter)
    
    @staticmethod
    def is_valid_image_file(file_path):
        if not file_path or not os.path.exists(file_path):
            return False
        
        valid_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff'}
        extension = Path(file_path).suffix.lower()
        
        if extension not in valid_extensions:
            return False
        
        try:
            pixmap = QPixmap(file_path)
            return not pixmap.isNull()
        except:
            return False