"""
Diálogo de descripciones mejorado y compartido entre aplicaciones
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QPlainTextEdit, QLabel, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont


class DescriptionsDialog(QDialog):
    """Diálogo mejorado para editar descripciones de la memoria"""
    
    # Señal emitida cuando se acepta la descripción
    description_accepted = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Descripción")
        self.setMinimumSize(700, 500)
        self.setModal(True)
        
        # Variable para almacenar el tipo de descripción
        self.description_type = None
        
        # Crear interfaz
        self._create_ui()
        self._setup_default_texts()
        
        # Conectar señales
        self._connect_signals()

    def _create_ui(self):
        """Crear interfaz del diálogo - SIN botones de plantillas"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header con título
        header_frame = QFrame()
        header_frame.setStyleSheet("QFrame { background-color: #f0f0f0; border-radius: 5px; padding: 10px; }")
        header_layout = QVBoxLayout(header_frame)
        
        self.label_description = QLabel("Ingrese la descripción:")
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_description.setFont(font)
        self.label_description.setAlignment(Qt.AlignCenter)
        header_layout.addWidget(self.label_description)
        
        layout.addWidget(header_frame)
        
        # Área de texto principal
        self.ui = self  # Para compatibilidad con código existente
        self.ui.pt_description = QPlainTextEdit()
        self.ui.pt_description.setMinimumHeight(300)
        
        # Configurar fuente del texto
        text_font = QFont()
        text_font.setFamily("Segoe UI")
        text_font.setPointSize(10)
        self.ui.pt_description.setFont(text_font)
        
        # Placeholder text
        self.ui.pt_description.setPlaceholderText("Escriba aquí la descripción...")
        
        layout.addWidget(self.ui.pt_description)
        
        # Botones principales (SIN botones de plantillas)
        buttons_layout = QHBoxLayout()
        
        self.btn_clear = QPushButton("Limpiar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_accept = QPushButton("Aceptar")
        
        # Configurar estilos de botones
        self.btn_accept.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        
        self.btn_clear.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #f57c00;
            }
        """)
        
        buttons_layout.addWidget(self.btn_clear)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_cancel)
        buttons_layout.addWidget(self.btn_accept)
        
        layout.addLayout(buttons_layout)

    def _setup_default_texts(self):
        """Configurar textos plantilla según el tipo de descripción"""
        self.default_texts = {
        'descripcion': """La edificación de concreto armado cuenta con múltiples niveles sobre el terreno natural.

El sistema estructural está conformado por pórticos de concreto armado en ambas direcciones principales, los cuales proporcionan la resistencia necesaria ante cargas gravitacionales y sísmicas.

La estructura se considera empotrada en la base y se ha modelado considerando las condiciones del suelo del lugar y las cargas de diseño según la normativa vigente.""",
        
        'modelamiento': """El modelo matemático de la estructura fue desarrollado utilizando elementos finitos tridimensionales.

Se consideraron los siguientes aspectos en el modelamiento:

• Elementos viga representados con elementos frame

• Elementos placa representados con elementos shell  

• Masas concentradas en el centro de masa de cada nivel

• Rigidez de losa infinita en su plano (diafragma rígido)

• Condiciones de apoyo empotrado en la base

• Propiedades mecánicas del concreto según normativa


El análisis incluye la evaluación de modos de vibración y respuesta sísmica según el espectro de diseño correspondiente.""",
        
        'cargas': """Se consideraron las siguientes cargas para el diseño estructural:

CARGAS PERMANENTES:

• Peso propio de elementos estructurales (calculado automáticamente)

• Sobrecarga muerta: 100 kg/m² (tabiquería y acabados)

• Peso de instalaciones y equipos

CARGAS VARIABLES:

• Sobrecarga viva: 200 kg/m² (uso típico de edificación)

• Carga viva de techo: 100 kg/m²

CARGAS SÍSMICAS:

• Aplicadas según la normativa sísmica vigente

• Espectro de respuesta según las condiciones del sitio

• Combinaciones de carga incluyendo efectos sísmicos"""
        }

    def _connect_signals(self):
        """Conectar señales del diálogo"""
        self.btn_accept.clicked.connect(self._on_accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear.clicked.connect(self._on_clear)

    def _load_template(self, template_type: str):
        """Cargar plantilla de texto"""
        if template_type in self.default_texts:
            current_text = self.ui.pt_description.toPlainText()
            
            # Si ya hay texto, preguntar si desea reemplazar
            if current_text.strip():
                from PyQt5.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self, 
                    'Confirmar', 
                    '¿Desea reemplazar el texto actual con la plantilla?',
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply != QMessageBox.Yes:
                    return
            
            # Cargar plantilla
            template_text = self.default_texts[template_type]
            self.ui.pt_description.setPlainText(template_text)
            
            # Mover cursor al final
            cursor = self.ui.pt_description.textCursor()
            cursor.movePosition(cursor.End)
            self.ui.pt_description.setTextCursor(cursor)

    def _clear_text(self):
        """Limpiar el texto"""
        from PyQt5.QtWidgets import QMessageBox
        
        if self.ui.pt_description.toPlainText().strip():
            reply = QMessageBox.question(
                self, 
                'Confirmar', 
                '¿Está seguro de que desea limpiar todo el texto?',
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.ui.pt_description.clear()

    def _on_accept(self):
        """Manejar aceptación del diálogo"""
        text = self.ui.pt_description.toPlainText().strip()
        self.description_accepted.emit(text)
        self.accept()

    def set_description_type(self, desc_type: str, title: str = None):
        """
        Configurar tipo de descripción con texto plantilla automático
        
        Args:
            desc_type: Tipo de descripción ('descripcion', 'modelamiento', 'cargas')
            title: Título personalizado opcional
        """
        self.description_type = desc_type
        
        # Configurar título
        if title:
            self.label_description.setText(title)
        else:
            titles = {
                'descripcion': 'Descripción de la Estructura',
                'modelamiento': 'Criterios de Modelamiento',
                'cargas': 'Descripción de Cargas Consideradas'
            }
            self.label_description.setText(titles.get(desc_type, 'Ingrese la descripción:'))
            
    def set_existing_text(self, text: str):
        """Establecer texto existente o plantilla si está vacío"""
        if self.description_type and self.description_type in self.default_texts:
            template_text = self.default_texts[self.description_type]
            self.ui.pt_description.setPlainText(template_text)
        else:
            self.ui.pt_description.clear()

    def get_description_text(self) -> str:
        """Obtener texto de la descripción"""
        return self.ui.pt_description.toPlainText().strip()
    
    def _on_clear(self):
        """Limpiar el texto"""
        from PyQt5.QtWidgets import QMessageBox
        
        reply = QMessageBox.question(
            self, 'Confirmar', '¿Desea limpiar todo el texto?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.ui.pt_description.clear()

    def _on_accept(self):
        """Manejar aceptación del diálogo"""
        text = self.ui.pt_description.toPlainText().strip()
        self.description_accepted.emit(text)
        self.accept()


# Función de conveniencia para usar el diálogo
def get_description(parent=None, desc_type: str = None, title: str = None, existing_text: str = ""):
    """
    Función de conveniencia para obtener descripción
    
    Args:
        parent: Widget padre
        desc_type: Tipo de descripción
        title: Título del diálogo
        existing_text: Texto existente
        
    Returns:
        Tuple (texto, aceptado)
    """
    dialog = DescriptionsDialog(parent)
    
    if desc_type:
        dialog.set_description_type(desc_type, title)
    elif title:
        dialog.label_description.setText(title)
    
    if existing_text:
        dialog.set_existing_text(existing_text)
    
    result = dialog.exec_()
    
    if result == dialog.Accepted:
        return dialog.get_description_text(), True
    else:
        return "", False