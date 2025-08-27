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
        """Crear interfaz del diálogo"""
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
        
        # Botones de plantillas
        templates_frame = QFrame()
        templates_layout = QHBoxLayout(templates_frame)
        
        self.btn_template_structure = QPushButton("Plantilla Estructura")
        self.btn_template_modeling = QPushButton("Plantilla Modelamiento")
        self.btn_template_loads = QPushButton("Plantilla Cargas")
        
        templates_layout.addWidget(self.btn_template_structure)
        templates_layout.addWidget(self.btn_template_modeling)
        templates_layout.addWidget(self.btn_template_loads)
        
        layout.addWidget(templates_frame)
        
        # Botones principales
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
        """Configurar textos por defecto para plantillas"""
        self.default_texts = {
            'estructura': """La edificación de concreto armado tiene {niveles} niveles y {sotanos} sótanos, con un área en planta aproximada de {area} m². 

El sistema estructural en la dirección X consiste en {sistema_x}, mientras que en la dirección Y se tiene {sistema_y}.

La estructura fue diseñada para resistir cargas de gravedad y sísmicas según la norma {norma}, considerando las condiciones del suelo y la ubicación geográfica del proyecto.""",
            
            'modelamiento': """El modelo matemático de la estructura fue desarrollado utilizando elementos finitos tridimensionales.

Se consideraron los siguientes aspectos en el modelamiento:
• Elementos viga representados con elementos frame
• Elementos placa representados con elementos shell
• Masas concentradas en el centro de masa de cada nivel
• Rigidez de losa infinita en su plano
• Condiciones de apoyo empotrado en la base

Las cargas consideradas incluyen peso propio, carga viva y cargas sísmicas según la norma aplicable.""",
            
            'cargas': """Para el análisis sísmico se consideraron las siguientes cargas:

CARGAS PERMANENTES:
• Peso propio de elementos estructurales (calculado automáticamente)
• Acabados: {carga_acabados} kN/m²
• Tabiquería: {carga_tabiqueria} kN/m²

CARGAS VIVAS:
• Sobrecarga de uso: {sobrecarga} kN/m²

CARGAS SÍSMICAS:
• Análisis dinámico modal espectral
• Análisis estático equivalente (verificación)
• Combinaciones de carga según norma {norma}"""
        }

    def _connect_signals(self):
        """Conectar señales del diálogo"""
        self.btn_accept.clicked.connect(self._on_accept)
        self.btn_cancel.clicked.connect(self.reject)
        self.btn_clear.clicked.connect(self._clear_text)
        
        # Conectar botones de plantillas
        self.btn_template_structure.clicked.connect(lambda: self._load_template('estructura'))
        self.btn_template_modeling.clicked.connect(lambda: self._load_template('modelamiento'))
        self.btn_template_loads.clicked.connect(lambda: self._load_template('cargas'))

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
        Configurar tipo de descripción y título
        
        Args:
            desc_type: Tipo de descripción ('descripcion', 'modelamiento', 'cargas')
            title: Título personalizado opcional
        """
        self.description_type = desc_type
        
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
        """Establecer texto existente"""
        self.ui.pt_description.setPlainText(text or "")

    def get_description_text(self) -> str:
        """Obtener texto de la descripción"""
        return self.ui.pt_description.toPlainText().strip()


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