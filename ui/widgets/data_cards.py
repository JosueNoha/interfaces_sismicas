
"""
Widget tipo card/tarjeta para datos del proyecto
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QLineEdit, QWidget, QSizePolicy, QComboBox,
                            QDoubleSpinBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPainter, QPainterPath
from .seismic_params_widget import SeismicParamsWidget

class DataCard(QFrame):
    """Clase padre para todas las tarjetas de datos"""
    
    # Señal para notificar cambios en los datos
    data_changed = pyqtSignal(str, object)  # (field_name, field_value)
    
    def __init__(self, title="", icon="", parent=None):
        super().__init__(parent)
        self.title = title
        self.icon = icon
        self.fields = {}  # Diccionario para almacenar los campos
        
        self._setup_card_style()
        self._setup_card_structure()
        
    def _setup_card_style(self):
        """Configurar el estilo base de la card"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            DataCard {
                background-color: #ffffff;
                border: 2px solid #e3f2fd;
                border-radius: 12px;
                margin: 8px;
            }
            
            DataCard:hover {
                border: 2px solid #2196f3;
                background-color: #fafffe;
            }
        """)
        
        # Política de tamaño
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
    def _setup_card_structure(self):
        """Configurar estructura base de la card"""
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 16, 20, 20)
        self.main_layout.setSpacing(16)
        
        # Header si hay título
        if self.title:
            self._create_header()
            
        # Contenedor para el contenido personalizable
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setHorizontalSpacing(20)
        self.content_layout.setVerticalSpacing(12)
        
        self.main_layout.addWidget(self.content_widget)
        
    def _create_header(self):
        """Crear header con icono y título"""
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 8)
        
        # Icono
        if self.icon:
            icon_label = QLabel(self.icon)
            icon_label.setStyleSheet("""
                QLabel {
                    font-size: 20px;
                    color: #2196f3;
                    background: transparent;
                    border: none;
                }
            """)
            header_layout.addWidget(icon_label)
        
        # Título
        title_label = QLabel(self.title.upper())
        title_font = QFont()
        title_font.setFamily("Segoe UI")
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setStyleSheet("""
            QLabel {
                color: #1976d2;
                background: transparent;
                border: none;
                margin-left: 8px;
            }
        """)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Línea separadora
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet("""
            QFrame {
                background-color: #e3f2fd;
                border: none;
                max-height: 2px;
                margin: 4px 0px;
            }
        """)
        
        self.main_layout.addLayout(header_layout)
        self.main_layout.addWidget(separator)
    
    def add_field(self, row, col, label_text, widget, field_name=None, tooltip=""):
        """
        Agregar un campo a la card
        
        Args:
            row: Fila en el grid
            col: Columna para el label (widget va en col+1)
            label_text: Texto del label
            widget: Widget del campo
            field_name: Nombre interno del campo (opcional)
            tooltip: Tooltip descriptivo
        """
        # Label
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #424242;
                font-weight: 600;
                font-size: 11px;
                background: transparent;
                border: none;
                min-width: 70px;
            }
        """)
        
        # Aplicar estilo al widget
        self._apply_field_style(widget)
        
        if tooltip:
            widget.setToolTip(tooltip)
            
        widget.setMinimumHeight(38)
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Configurar altura mínima de la fila
        self.content_layout.setRowMinimumHeight(row, 48)
        
        # Agregar al layout
        self.content_layout.addWidget(label, row, col)
        self.content_layout.addWidget(widget, row, col + 1)
        
        # Almacenar referencia
        if field_name:
            self.fields[field_name] = widget
            setattr(self, field_name, widget)
    
    def _apply_field_style(self, widget):
        """Aplicar estilo base a los campos"""
        widget_type = widget.__class__.__name__
        
        if widget_type in ['QLineEdit', 'QSpinBox', 'QDoubleSpinBox']:
            widget.setStyleSheet("""
                QLineEdit, QSpinBox, QDoubleSpinBox {
                    padding: 10px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: #fafafa;
                    font-size: 11px;
                    color: #333333;
                }
                
                QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
                    border: 2px solid #2196f3;
                    background-color: #ffffff;
                    outline: none;
                }
                
                QLineEdit:hover, QSpinBox:hover, QDoubleSpinBox:hover {
                    border: 2px solid #bbbbbb;
                }
            """)
        elif widget_type == 'QComboBox':
            widget.setStyleSheet("""
                QComboBox {
                    padding: 10px 12px;
                    border: 2px solid #e0e0e0;
                    border-radius: 8px;
                    background-color: #fafafa;
                    font-size: 11px;
                    color: #333333;
                }
                
                QComboBox:focus {
                    border: 2px solid #2196f3;
                    background-color: #ffffff;
                }
                
                QComboBox:hover {
                    border: 2px solid #bbbbbb;
                }
                
                QComboBox::drop-down {
                    border: none;
                    width: 20px;
                }
                
                QComboBox::down-arrow {
                    image: none;
                    border: none;
                    width: 12px;
                    height: 12px;
                }
            """)
    
    def get_data(self):
        """Obtener todos los datos de la card (debe ser implementado por subclases)"""
        raise NotImplementedError("Subclases deben implementar get_data()")
    
    def set_data(self, data):
        """Establecer datos en la card (debe ser implementado por subclases)"""
        raise NotImplementedError("Subclases deben implementar set_data()")
    
class ProjectDataCard(DataCard):
    """Card para datos del proyecto"""
    
    def __init__(self, parent=None):
        super().__init__("DATOS DEL PROYECTO", "📋", parent)
        self._create_fields()
        self._connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos del proyecto"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Crear campos
        self.le_proyecto = QLineEdit()
        self.le_ubicacion = QLineEdit()
        self.le_autor = QLineEdit()
        self.le_fecha = QLineEdit()
        
        # Agregar al grid
        self.add_field(0, 0, "Proyecto:", self.le_proyecto, "le_proyecto", "Nombre del proyecto")
        self.add_field(0, 2, "Ubicación:", self.le_ubicacion, "le_ubicacion", "Ubicación geográfica")
        self.add_field(1, 0, "Autor:", self.le_autor, "le_autor", "Ingeniero responsable")
        self.add_field(1, 2, "Fecha:", self.le_fecha, "le_fecha", "Fecha de análisis")
        
    def _connect_signals(self):
        """Conectar señales"""
        for field_name, widget in self.fields.items():
            if hasattr(widget, 'textChanged'):
                widget.textChanged.connect(
                    lambda text, name=field_name: self.data_changed.emit(name, text)
                )
    
    def get_data(self):
        """Obtener datos del proyecto"""
        return {
            'proyecto': self.le_proyecto.text(),
            'ubicacion': self.le_ubicacion.text(),
            'autor': self.le_autor.text(),
            'fecha': self.le_fecha.text()
        }
    
    def set_data(self, data):
        """Establecer datos del proyecto"""
        if 'proyecto' in data:
            self.le_proyecto.setText(data['proyecto'])
        if 'ubicacion' in data:
            self.le_ubicacion.setText(data['ubicacion'])
        if 'autor' in data:
            self.le_autor.setText(data['autor'])
        if 'fecha' in data:
            self.le_fecha.setText(data['fecha'])
            
class SeismicParamsCard(DataCard):
    """Card que envuelve el SeismicParamsWidget existente"""
    
    def __init__(self, parent=None):
        # Inicializar card con título - SIN config inicialmente
        super().__init__("PARÁMETROS SÍSMICOS", "🏗️", parent)
        
        # Inicializar sin widget hasta tener config
        self.seismic_widget = None
    
    
    def _apply_modern_styles(self):
        """Aplicar estilos modernos al widget interno"""
        if self.seismic_widget:
            self.seismic_widget.setStyleSheet("""
                QLabel {
                    color: #424242;
                    font-weight: 600;
                    font-size: 11px;
                    background: transparent;
                    border: none;
                    min-width: 70px;
                }
                
                QDoubleSpinBox, QComboBox, QSpinBox {
                    padding: 8px 10px;
                    border: 2px solid #e0e0e0;
                    border-radius: 6px;
                    background-color: #fafafa;
                    font-size: 11px;
                    color: #333333;
                }
                
                QDoubleSpinBox:focus, QComboBox:focus, QSpinBox:focus {
                    border: 2px solid #2196f3;
                    background-color: #ffffff;
                    outline: none;
                }
                
                QDoubleSpinBox:hover, QComboBox:hover, QSpinBox:hover {
                    border: 2px solid #bbbbbb;
                }
            """)
    
    
    def get_data(self):
        """Obtener datos del SeismicParamsWidget existente"""
        if self.seismic_widget and hasattr(self.seismic_widget, 'get_parameters'):
            return self.seismic_widget.get_parameters()
        return {}
    
    def set_data(self, data):
        """Establecer datos en el SeismicParamsWidget existente"""
        if self.seismic_widget and hasattr(self.seismic_widget, 'set_parameters'):
            self.seismic_widget.set_parameters(data)
    
    def connect_param_changed(self, callback):
        """Conectar señales de cambio (si existen en el widget)"""
        if self.seismic_widget and hasattr(self.seismic_widget, 'connect_param_changed'):
            self.seismic_widget.connect_param_changed(callback)