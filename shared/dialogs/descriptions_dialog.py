"""
Diálogo de descripciones compartido entre aplicaciones
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLabel
from PyQt5.QtCore import Qt


class DescriptionsDialog(QDialog):
    """Diálogo para editar descripciones de la memoria"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setWindowTitle("Descripción")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        
        # Crear interfaz
        self._create_ui()
        
        # Variable para almacenar el tipo de descripción
        self.name = None

    def _create_ui(self):
        """Crear interfaz del diálogo"""
        layout = QVBoxLayout(self)
        
        # Etiqueta
        self.label_description = QLabel("Ingrese la descripción:")
        layout.addWidget(self.label_description)
        
        # Área de texto
        self.ui = self  # Para compatibilidad con código existente
        self.ui.pt_description = QPlainTextEdit()
        self.ui.pt_description.setPlainText("")
        layout.addWidget(self.ui.pt_description)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        self.btn_accept = QPushButton("Aceptar")
        self.btn_cancel = QPushButton("Cancelar")
        
        self.btn_accept.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_accept)
        buttons_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(buttons_layout)