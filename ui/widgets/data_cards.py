
"""
Widget tipo card/tarjeta para datos del proyecto
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QLineEdit, QWidget, QSizePolicy, QComboBox,
                            QDoubleSpinBox,QPushButton)
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
    """Card que envuelve de parámetros sísmicos"""
    
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
            
            
class UnitsParamsCard(DataCard):
    """Card de unidades"""
    units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("UNIDADES DE TRABAJO", "🏗️", parent)
        self._create_fields()
        self.connect_signals()
        
    def _create_fields(self):
        from core.config.units_config import get_unit_options, get_default_unit
        """Crear campos específicos de unidades"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        self.content_layout.setColumnStretch(5, 1)
        
        # Crear combo boxes para cada categoría
        self.combos = {}
        # Alturas
        #group_layout.addWidget(QLabel("Alturas:"), 0, 0)
        self.combos['alturas'] = QComboBox()
        self.combos['alturas'].addItems(get_unit_options('alturas'))
        self.combos['alturas'].setCurrentText(get_default_unit('alturas'))
        self.add_field(0, 0, "Alturas:", self.combos['alturas'], "alturas", "Unidad de alturas")
        
        # Desplazamientos
        # group_layout.addWidget(QLabel("Desplazamientos:"), 0, 2)
        self.combos['desplazamientos'] = QComboBox()
        self.combos['desplazamientos'].addItems(get_unit_options('desplazamientos'))
        self.combos['desplazamientos'].setCurrentText(get_default_unit('desplazamientos'))
        self.add_field(0, 2, "Desplazamientos:", self.combos['desplazamientos'], "desplazamientos", "Unidad de desplazamientos")
        
        # Fuerzas
        # group_layout.addWidget(QLabel("Fuerzas:"), 0, 4)
        self.combos['fuerzas'] = QComboBox()
        self.combos['fuerzas'].addItems(get_unit_options('fuerzas'))
        self.combos['fuerzas'].setCurrentText(get_default_unit('fuerzas'))
        self.add_field(0, 4, "fuerzas:", self.combos['fuerzas'], "fuerzas", "Unidad de fuerzas")
        
    def connect_signals(self):
        """Conectar señales"""
        for categoria, combo in self.combos.items():
            combo.currentTextChanged.connect(self._on_unit_changed)
            
    def _on_unit_changed(self):
        """Cuando cambia una unidad"""
        units = self.get_current_units()
        self.units_changed.emit(units)
        
    def get_current_units(self):
        """Obtener unidades actuales seleccionadas"""
        return {categoria: combo.currentText() 
                for categoria, combo in self.combos.items()}
        
    def set_units(self, units_dict):
        """Establecer unidades específicas"""
        for categoria, unidad in units_dict.items():
            if categoria in self.combos:
                combo = self.combos[categoria]
                if unidad in [combo.itemText(i) for i in range(combo.count())]:
                    combo.setCurrentText(unidad)
                    
                    
class ModalCard(DataCard):
    """Card de análisis modal"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("ANÁLISIS MODAL", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        from core.config.units_config import get_unit_options, get_default_unit
        """Crear campos específicos de unidades"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # % Mínimo de Masa Participativa
        self.le_modal = QLineEdit("90")
        self.add_field(0, 2, "Masa Mínima (%):", self.le_modal, "le_modal", "% Mínimo de Masa Participativa")
        
        # Resultados Modales
        self.le_tx = QLineEdit()
        self.le_tx.setReadOnly(True)
        self.le_ty = QLineEdit()
        self.le_ty.setReadOnly(True)
        self.add_field(1, 0, "Periodo Tx:", self.le_tx, "le_tx", "Periodo Tx")
        self.add_field(1, 2, "Periodo Ty:", self.le_ty, "le_ty", "Periodo Ty")
        
        # Masa participativa acumulada
        self.le_participacion_x = QLineEdit()
        self.le_participacion_x.setReadOnly(True)
        self.le_participacion_y = QLineEdit()
        self.le_participacion_y.setReadOnly(True)
        self.add_field(2, 0, "Masa X (%):", self.le_participacion_x, "le_participacion_x", "Masa X (%)")
        self.add_field(2, 2, "Masa Y (%):", self.le_participacion_y, "le_participacion_y", "Masa Y (%)")
        
        # Botón para ver tabla
        self.b_modal = QPushButton("Ver Data")
        self.add_field(3, 2, "", self.b_modal, "b_modal", "Botón de ver data")
        
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
            
class CombinationsCard(DataCard):
    """Card de combinaciones de Carga"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("SELECCIÓN DE COMBINACIONES DE CARGA", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Combinaciones Estáticas
        self.cb_comb_static_x = QComboBox()
        self.cb_comb_static_y = QComboBox()
        self.add_field(0, 0, "Estáticas X:", self.cb_comb_static_x, "cb_comb_static_x", "Combinaciones estáticas en X")
        self.add_field(0, 2, "Estáticas Y:", self.cb_comb_static_y, "cb_comb_static_y", "Combinaciones estáticas en Y")
        
        # Combinaciones Dinámicas
        self.cb_comb_dynamic_x = QComboBox()
        self.cb_comb_dynamic_y = QComboBox()
        self.add_field(1, 0, "Dinámicas X:", self.cb_comb_dynamic_x, "cb_comb_dynamic_x", "Combinaciones dinámicas en X")
        self.add_field(1, 2, "Dinámicas Y:", self.cb_comb_dynamic_y, "cb_comb_dynamic_y", "Combinaciones dinámicas en Y")
        
        # Combinaciones de Desplazamientos
        self.cb_comb_displacement_x = QComboBox()
        self.cb_comb_displacement_y = QComboBox()
        self.add_field(2, 0, "Desplaz. X:", self.cb_comb_displacement_x, "cb_comb_displacement_x", "Combinaciones de desplazamiento en X")
        self.add_field(2, 2, "Desplaz. Y:", self.cb_comb_displacement_y, "cb_comb_displacement_y", "Combinaciones de desplazamiento en Y")
        
        
    
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
   
   
class ShearCard(DataCard):
    """Card de Fuerzas Cortantes"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("FUERZAS CORTANTES", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # % min
        self.le_scale_factor = QLineEdit("80.0")
        self.add_field(0, 2, "% Mín. Fuerzas Dinámicas:", self.le_scale_factor, "le_scale_factor", "% Mín. Fuerzas Dinámicas")
        
        # V dinámico
        self.le_vdx = QLineEdit()
        self.le_vdx.setReadOnly(True)
        self.le_vdy = QLineEdit()
        self.le_vdy.setReadOnly(True)
        self.add_field(1, 0, "V dinámico X:", self.le_vdx, "le_vdx", "Cortante dinámica en X")
        self.add_field(1, 2, "V dinámico Y:", self.le_vdy, "le_vdy", "Cortante dinámica en Y")
        
        # V Estático
        self.le_vsx = QLineEdit()
        self.le_vsx.setReadOnly(True)
        self.le_vsy = QLineEdit()
        self.le_vsy.setReadOnly(True)
        self.add_field(2, 0, "V estático X:", self.le_vsx, "le_vsx", "Cortante estático en X")
        self.add_field(2, 2, "V estático Y:", self.le_vsy, "le_vsy", "Cortante estático en Y")
        
        # Factores de Escala
        self.le_fx = QLineEdit()
        self.le_fx.setReadOnly(True)
        self.le_fy = QLineEdit()
        self.le_fy.setReadOnly(True)
        self.add_field(3, 0, "F.E. X:", self.le_fx, "le_fx", "Factor de escala en X")
        self.add_field(3, 2, "F.E. Y:", self.le_fy, "le_fy", "Factor de escala en Y")
        
        # Botones
        self.b_view_dynamic = QPushButton("Ver Gráfico Dinámico")
        self.b_view_static = QPushButton("Ver Gráfico Estático")
        self.add_field(4, 0, "", self.b_view_static, "b_view_static", "Ver Gráfico Estático")
        self.add_field(4, 2, "", self.b_view_dynamic, "b_view_dynamic", "Ver Gráfico Dinámico")
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
class DisplacementCard(DataCard):
    """Card de Desplazamientos"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Desplazamientos", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Desplazamientos
        self.le_desp_max_x = QLineEdit()
        self.le_desp_max_x.setReadOnly(True)
        self.le_desp_max_y = QLineEdit()
        self.le_desp_max_y.setReadOnly(True)
        self.add_field(0, 0, "Desp. máx X:", self.le_desp_max_x, "le_desp_max_x", "Desplazamiento máx X")
        self.add_field(0, 2, "Desp. máx Y:", self.le_desp_max_y, "le_desp_max_y", "Desplazamiento máx Y")
        
      
        # Boton
        self.b_desplazamiento = QPushButton("Calcular Desplazamientos")
        self.add_field(1, 0, "", self.b_desplazamiento, "b_desplazamiento", "")
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
class DriftCard(DataCard):
    """Card de Derivas"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Derivas", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Deriva Máxima
        self.le_max_drift = QLineEdit("0.007")
        self.add_field(0, 2, "Deriva Máxima:", self.le_max_drift, "le_max_drift", "Deriva Máxima")
        
        # Derivas
        self.le_deriva_max_x = QLineEdit()
        self.le_deriva_max_x.setReadOnly(True)
        self.le_deriva_max_y = QLineEdit()
        self.le_deriva_max_y.setReadOnly(True)
        self.add_field(1, 0, "Deriva máx X:", self.le_deriva_max_x, "le_deriva_max_x", "Deriva máx X")
        self.add_field(1, 2, "Deriva máx Y:", self.le_deriva_max_y, "le_deriva_max_y", "Deriva máx Y")
        
        # Pisos de deriva máxima
        self.le_piso_deriva_x = QLineEdit()
        self.le_piso_deriva_x.setReadOnly(True)
        self.le_piso_deriva_y = QLineEdit()
        self.le_piso_deriva_y.setReadOnly(True)
        self.add_field(1, 0, "Piso X:", self.le_piso_deriva_x, "le_piso_deriva_x", "Piso de la deriva máx X")
        self.add_field(1, 2, "Piso Y:", self.le_piso_deriva_y, "le_piso_deriva_y", "Piso de la deriva máx Y")
        
        # Boton
        self.b_derivas = QPushButton("Calcular Derivas")
        self.add_field(3, 0, "", self.b_derivas, "b_derivas", "")
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
    
class TorsionCard(DataCard):
    """Card de Irregularidad por Torsión"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Irregularidad Torsional", "🏗️", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Combinación para torsión
        self.cb_torsion_combo = QComboBox()
        self.cb_torsion_combo.addItems(["Dinámicas", "Estáticas", "Desplazamientos"])
        self.add_field(0, 2, "Combinación:", self.cb_torsion_combo, "cb_torsion_combo", "Combinación para el cálculo")
        
        self.le_torsion_limit = QLineEdit("1.30")
        self.add_field(1, 2, "Ratio límite:", self.le_torsion_limit, "le_torsion_limit", "Ratio límite")
        
        # Ratios
        self.le_relacion_x = QLineEdit()
        self.le_relacion_x.setReadOnly(True)
        self.le_relacion_y = QLineEdit()
        self.le_relacion_x.setReadOnly(True)
        self.add_field(2, 0, "Ratio en X:", self.le_relacion_x, "le_relacion_x", "Ration en X")
        self.add_field(2, 2, "Ratio en Y:", self.le_relacion_y, "le_relacion_y", "Ration en Y")
        
        # Irregularidad
        self.le_irregularidad_x = QLineEdit()
        self.le_irregularidad_x.setReadOnly(True)
        self.le_irregularidad_y = QLineEdit()
        self.le_irregularidad_y.setReadOnly(True)
        self.add_field(3, 0, "", self.le_irregularidad_x, "le_irregularidad_x", "")
        self.add_field(3, 2, "", self.le_irregularidad_y, "le_irregularidad_y", "")
        
        # Boton
        self.b_torsion_table = QPushButton("Ver Tabla")
        self.add_field(4, 0, "", self.b_torsion_table, "b_torsion_table", "")
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)