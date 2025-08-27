"""Diálogo de descripciones compartido"""
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QPlainTextEdit, QLabel

class DescriptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Descripción")
        self.setMinimumSize(600, 400)
        self.setModal(True)
        self.name = None
        self._create_ui()

    def _create_ui(self):
        layout = QVBoxLayout(self)
        
        self.label_description = QLabel("Ingrese la descripción:")
        layout.addWidget(self.label_description)
        
        self.ui = self
        self.ui.pt_description = QPlainTextEdit()
        layout.addWidget(self.ui.pt_description)
        
        buttons_layout = QHBoxLayout()
        self.btn_accept = QPushButton("Aceptar")
        self.btn_cancel = QPushButton("Cancelar")
        
        self.btn_accept.clicked.connect(self.accept)
        self.btn_cancel.clicked.connect(self.reject)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_accept)
        buttons_layout.addWidget(self.btn_cancel)
        layout.addLayout(buttons_layout)

    def get_description(self):
        return self.ui.pt_description.toPlainText()
    
    def set_description(self, text):
        self.ui.pt_description.setPlainText(text)