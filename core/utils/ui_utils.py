"""
Utilidades comunes para interfaces de usuario PyQt5
"""

from PyQt5.QtWidgets import QComboBox, QLineEdit, QMessageBox
from PyQt5.QtCore import QDate
from typing import Dict, Any, Optional


def connect_combo_signals(combo_mapping: Dict[QComboBox, callable]) -> None:
    """
    Conecta señales de QComboBox a sus respectivos métodos
    
    Args:
        combo_mapping: Diccionario {combo: método_callback}
    """
    for combo, callback in combo_mapping.items():
        combo.currentTextChanged.connect(callback)
        combo.currentIndexChanged.connect(callback)


def load_default_values(ui_elements: Dict[str, Any], default_values: Dict[str, Any]) -> None:
    """
    Carga valores por defecto en elementos UI
    
    Args:
        ui_elements: Diccionario con elementos UI
        default_values: Valores por defecto a cargar
    """
    for key, value in default_values.items():
        if key in ui_elements:
            element = ui_elements[key]
            
            if isinstance(element, QLineEdit):
                element.setText(str(value))
            elif isinstance(element, QComboBox):
                # Buscar y seleccionar el índice correspondiente
                index = element.findText(str(value))
                if index >= 0:
                    element.setCurrentIndex(index)


def validate_float_input(line_edit: QLineEdit, field_name: str = "Campo") -> Optional[float]:
    """
    Valida entrada float en QLineEdit
    
    Args:
        line_edit: Widget QLineEdit a validar
        field_name: Nombre del campo para mensajes de error
        
    Returns:
        Valor float si es válido, None si hay error
    """
    try:
        value = float(line_edit.text())
        line_edit.setStyleSheet("")  # Limpiar estilo de error
        return value
    except ValueError:
        line_edit.setStyleSheet("QLineEdit { border: 2px solid red; }")
        show_error_message(f"Error en {field_name}", 
                          f"El valor '{line_edit.text()}' no es un número válido")
        return None


def validate_required_fields(required_fields: Dict[str, QLineEdit]) -> bool:
    """
    Valida que campos requeridos no estén vacíos
    
    Args:
        required_fields: Diccionario {nombre_campo: QLineEdit}
        
    Returns:
        True si todos los campos están llenos, False caso contrario
    """
    empty_fields = []
    
    for field_name, line_edit in required_fields.items():
        if not line_edit.text().strip():
            line_edit.setStyleSheet("QLineEdit { border: 2px solid red; }")
            empty_fields.append(field_name)
        else:
            line_edit.setStyleSheet("")
    
    if empty_fields:
        show_error_message("Campos requeridos", 
                          f"Los siguientes campos son obligatorios:\n" + 
                          "\n".join(f"• {field}" for field in empty_fields))
        return False
    
    return True


def show_error_message(title: str, message: str) -> None:
    """
    Muestra mensaje de error
    
    Args:
        title: Título del mensaje
        message: Contenido del mensaje
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Critical)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_info_message(title: str, message: str) -> None:
    """
    Muestra mensaje de información
    
    Args:
        title: Título del mensaje
        message: Contenido del mensaje
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def show_success_message(title: str, message: str) -> None:
    """
    Muestra mensaje de éxito
    
    Args:
        title: Título del mensaje
        message: Contenido del mensaje
    """
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Information)
    msg.setWindowTitle(title)
    msg.setText(message)
    msg.exec_()


def setup_date_field(line_edit: QLineEdit) -> None:
    """
    Configura campo de fecha con valor actual
    
    Args:
        line_edit: Campo de fecha a configurar
    """
    current_date = QDate.currentDate().toString("dd/MM/yyyy")
    line_edit.setText(current_date)


def clear_form_errors(line_edits: list) -> None:
    """
    Limpia estilos de error de los campos del formulario
    
    Args:
        line_edits: Lista de QLineEdit a limpiar
    """
    for line_edit in line_edits:
        line_edit.setStyleSheet("")


def get_combo_value_safe(combo: QComboBox, default: str = "") -> str:
    """
    Obtiene valor de QComboBox de forma segura
    
    Args:
        combo: QComboBox del cual obtener valor
        default: Valor por defecto si hay error
        
    Returns:
        Texto seleccionado o valor por defecto
    """
    try:
        return combo.currentText()
    except:
        return default


def set_combo_value_safe(combo: QComboBox, value: str) -> bool:
    """
    Establece valor en QComboBox de forma segura
    
    Args:
        combo: QComboBox donde establecer valor
        value: Valor a establecer
        
    Returns:
        True si se pudo establecer, False caso contrario
    """
    try:
        index = combo.findText(value)
        if index >= 0:
            combo.setCurrentIndex(index)
            return True
        return False
    except:
        return False


def format_number_display(value: float, decimals: int = 2) -> str:
    """
    Formatea número para mostrar en UI
    
    Args:
        value: Valor numérico
        decimals: Número de decimales
        
    Returns:
        Número formateado como string
    """
    return f"{value:.{decimals}f}"