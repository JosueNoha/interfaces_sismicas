
"""
Widget tipo card/tarjeta para datos del proyecto
"""

from PyQt5.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QGridLayout, 
                            QLabel, QLineEdit, QWidget, QSizePolicy, QComboBox,
                            QCheckBox,QPushButton)
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
        
    def disable_combobox_wheel(self,combo: QComboBox) -> None:
        """
        Desactiva el cambio de valor con rueda del mouse en QComboBox
        
        Args:
            combo: Widget QComboBox a proteger
        """
        combo.wheelEvent = lambda event: None
        
    def _setup_card_style(self):
        """Configurar el estilo base COMPACTO de la card"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            DataCard {
                background-color: #ffffff;
                border: 1px solid #e3f2fd;     /* Reducido de 2px */
                border-radius: 8px;            /* Reducido de 12px */
                margin: 4px;                   /* Reducido de 8px */
            }
            
            DataCard:hover {
                border: 1px solid #2196f3;     /* Reducido de 2px */
                background-color: #fafffe;
            }
        """)
        
        # Política de tamaño
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        
    def _setup_card_structure(self):
        """Configurar estructura base de la card"""
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(12, 8, 12, 12)  # Reducido de (20, 16, 20, 20)
        self.main_layout.setSpacing(8)  # Reducido de 16
        
        # Header si hay título
        if self.title:
            self._create_header()
            
        # Contenedor para el contenido personalizable
        self.content_widget = QWidget()
        self.content_layout = QGridLayout(self.content_widget)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setHorizontalSpacing(12)  # Reducido de 20
        self.content_layout.setVerticalSpacing(6)     # Reducido de 12
        
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
        Agregar campo COMPACTO con label a la card
        """
        # Crear label
        label = QLabel(label_text)
        label.setStyleSheet("""
            QLabel {
                color: #424242;
                font-weight: 600;
                font-size: 10px;        /* Reducido de 11px */
                background: transparent;
                border: none;
                min-width: 70px;
                padding: 2px 0px;      /* Reducido de 4px */
            }
        """)
        
        # Aplicar estilo al widget
        self._apply_field_style(widget)
        
        if tooltip:
            label.setToolTip(tooltip)
            widget.setToolTip(tooltip)
        
        # Política de tamaño
        widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        
        # Configurar altura mínima de la fila (COMPACTA)
        self.content_layout.setRowMinimumHeight(row, 32)  # Reducido de 48
        
        # Agregar al layout
        self.content_layout.addWidget(label, row, col)
        self.content_layout.addWidget(widget, row, col + 1)
        
        # Almacenar referencia
        if field_name:
            self.fields[field_name] = widget
            setattr(self, field_name, widget)
            
    def add_widget(self, row, col, widget, field_name=None, tooltip="", colspan=1):
        """
        Agregar un widget sin label a la card
        
        Args:
            row: Fila en el grid
            col: Columna inicial
            widget: Widget a agregar
            field_name: Nombre interno del campo (opcional)
            tooltip: Tooltip descriptivo
            colspan: Número de columnas que ocupa el widget (default: 1)
        """
        # Aplicar estilo al widget
        self._apply_field_style(widget)
        
        if tooltip:
            widget.setToolTip(tooltip)
        
        # Agregar al layout con colspan
        self.content_layout.addWidget(widget, row, col, 1, colspan)
        
        # Almacenar referencia
        if field_name:
            self.fields[field_name] = widget
            setattr(self, field_name, widget)
    
    def _apply_field_style(self, widget):
        """Aplicar estilo base a los campos usando configuración centralizada"""
        widget_type = widget.__class__.__name__
        
        # Configuración base COMPACTA para todos los widgets
        base_config = {
            'padding': '6px 8px',        # Reducido de '10px 12px'
            'border': '1px solid #e0e0e0',  # Reducido de '2px'
            'border_radius': '6px',      # Reducido de '8px'
            'background_color': '#fafafa',
            'font_size': '10px',         # Reducido de '11px'
            'color': '#333333',
            'min_height': '24px'         # Reducido de '36px'
        }
        
        # Configuraciones específicas por tipo (COMPACTAS)
        widget_configs = {
            'input_widgets': {
                'types': ['QLineEdit', 'QSpinBox', 'QDoubleSpinBox'],
                'config': base_config,
                'height': 28,                # Reducido de 38
                'size_policy': (QSizePolicy.Expanding, QSizePolicy.Fixed)
            },
            'QComboBox': {
                'types': ['QComboBox'],
                'config': {**base_config, 'extra_css': """
                    QComboBox::drop-down { border: none; width: 18px; }
                    QComboBox::down-arrow { image: none; border: none; width: 10px; height: 10px; }
                """},
                'height': 28,                # Reducido de 38
                'size_policy': (QSizePolicy.Expanding, QSizePolicy.Fixed)
            },
            'QPushButton': {
                'types': ['QPushButton'],
                'config': {
                    'padding': '4px 10px',   # Reducido de '8px 16px'
                    'border': '1px solid #ddd',
                    'border_radius': '6px',
                    'background_color': '#ffffff',
                    'font_size': '10px',     # Reducido de '11px'
                    'color': '#212121',
                    'font_weight': '500',
                    'min_height': '22px'     # Reducido de '32px'
                },
                'height': 26,                # Reducido de 36
                'size_policy': (QSizePolicy.Preferred, QSizePolicy.Fixed)
            }
        }
        
        # Aplicar configuración según tipo de widget
        self._configure_widget_by_type(widget, widget_type, widget_configs)
        
    def _configure_widget_by_type(self, widget, widget_type, configs):
        """Configurar widget según su tipo usando las configuraciones centralizadas"""
        for config_name, config_data in configs.items():
            if widget_type in config_data['types']:
                # Aplicar CSS
                css = self._build_css_from_config(widget_type, config_data['config'])
                widget.setStyleSheet(css)
                
                # Aplicar propiedades adicionales
                if 'height' in config_data:
                    widget.setMinimumHeight(config_data['height'])
                    
                if 'size_policy' in config_data:
                    h_policy, v_policy = config_data['size_policy']
                    widget.setSizePolicy(h_policy, v_policy)
                
                return
        
        # Widget tipo no reconocido - aplicar estilo básico
        widget.setStyleSheet("QWidget { font-size: 11px; color: #333333; }")
    
    def _build_css_from_config(self, widget_type, config):
        """Construir CSS desde configuración"""
        css_parts = []
        
        # CSS base
        base_css = self._config_to_css(config)
        css_parts.append(f"{widget_type} {{ {base_css} }}")
        
        # Estados interactivos comunes
        if widget_type in ['QLineEdit', 'QSpinBox', 'QDoubleSpinBox', 'QComboBox']:
            css_parts.extend([
                f"{widget_type}:focus {{ border: 2px solid #2196f3; background-color: #ffffff; outline: none; }}",
                f"{widget_type}:hover {{ border: 2px solid #bbbbbb; }}"
            ])
            
            if widget_type == 'QLineEdit':
                css_parts.append(f"{widget_type}:read-only {{ background-color: #f5f5f5; color: #666666; }}")
        
        elif widget_type == 'QPushButton':
            css_parts.extend([
                f"{widget_type}:hover {{ background-color: #eeeeee; border: 2px solid #bdbdbd; color: #212121; }}",
                f"{widget_type}:pressed {{ background-color: #e0e0e0; border: 2px solid #9e9e9e; }}",
                f"{widget_type}:disabled {{ background-color: #fafafa; border: 2px solid #eeeeee; color: #bdbdbd; }}"
            ])
        
        elif widget_type in ['QCheckBox', 'QRadioButton']:
            css_parts.extend([
                f"{widget_type}::indicator {{ width: 18px; height: 18px; }}",
            ])
        
        # CSS extra si existe
        if 'extra_css' in config:
            css_parts.append(config['extra_css'])
        
        return '\n'.join(css_parts)
    
    def _config_to_css(self, config):
        """Convertir configuración a CSS"""
        css_rules = []
        for key, value in config.items():
            if key == 'extra_css':
                continue
            css_property = key.replace('_', '-')  # background_color -> background-color
            css_rules.append(f"{css_property}: {value};")
        return ' '.join(css_rules)
    
    def set_widget_validation_style(self, widget, validation_state):
        """Aplicar estilo de validación manteniendo el estilo base"""
        # Re-aplicar estilo base
        self._apply_field_style(widget)
        
        # Validaciones específicas usando !important para override
        validation_overrides = {
            'valid': "border-color: #4caf50 !important; background-color: #e8f5e8 !important;",
            'warning': "border-color: #ff9800 !important; background-color: #fff3e0 !important;",
            'error': "border-color: #f44336 !important; background-color: #ffebee !important;"
        }
        
        if validation_state in validation_overrides:
            widget_id = f"validation_{id(widget)}"
            widget.setObjectName(widget_id)
            
            widget_type = widget.__class__.__name__
            current_style = widget.styleSheet()
            validation_css = f"\n{widget_type}#{widget_id} {{ {validation_overrides[validation_state]} }}"
            
            widget.setStyleSheet(current_style + validation_css)
    
    def reset_widget_style(self, widget):
        """Resetear widget al estilo base de la card"""
        widget.setObjectName("")  # Limpiar ID de validación
        self._apply_field_style(widget)
    
            
    def customize_widget(self, widget, **styles):
        """Personalizar estilos específicos de cualquier widget"""
        
        # Aplicar estilo base
        self._apply_field_style(widget)
        
        # Crear stylesheet personalizado
        widget_type = widget.__class__.__name__
        widget_id = f"custom_{id(widget)}"
        widget.setObjectName(widget_id)
        
        custom_styles = []
        for property_name, value in styles.items():
            css_property = property_name.replace('_', '-')  # background_color -> background-color
            custom_styles.append(f"{css_property}: {value};")
        
        if custom_styles:
            custom_css = f"{widget_type}#{widget_id} {{ {''.join(custom_styles)} }}"
            current_style = widget.styleSheet()
            widget.setStyleSheet(current_style + "\n" + custom_css)
        
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
        self.disable_combobox_wheel(self.combos['alturas'])
        self.add_field(0, 0, "Alturas:", self.combos['alturas'], "alturas", "Unidad de alturas")
        
        # Desplazamientos
        # group_layout.addWidget(QLabel("Desplazamientos:"), 0, 2)
        self.combos['desplazamientos'] = QComboBox()
        self.combos['desplazamientos'].addItems(get_unit_options('desplazamientos'))
        self.combos['desplazamientos'].setCurrentText(get_default_unit('desplazamientos'))
        self.disable_combobox_wheel(self.combos['desplazamientos'])
        self.add_field(0, 2, "Desplazamientos:", self.combos['desplazamientos'], "desplazamientos", "Unidad de desplazamientos")
        
        # Fuerzas
        # group_layout.addWidget(QLabel("Fuerzas:"), 0, 4)
        self.combos['fuerzas'] = QComboBox()
        self.combos['fuerzas'].addItems(get_unit_options('fuerzas'))
        self.combos['fuerzas'].setCurrentText(get_default_unit('fuerzas'))
        self.disable_combobox_wheel(self.combos['fuerzas'])
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
    modal_threshold_changed = pyqtSignal(float)  # Cuando cambia el umbral mínimo
    show_modal_table_requested = pyqtSignal()    # Cuando se solicita ver la tabla modal
    
    def __init__(self, parent=None):
        super().__init__("ANÁLISIS MODAL", "🏗️", parent)
        self._create_fields()
        self.connect_signals()
        
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
        
    def connect_signals(self):
        """Conectar señales"""
        # Cuando cambia el umbral mínimo de masa participativa
        self.le_modal.textChanged.connect(self._on_modal_threshold_changed)
        
        # Cuando se presiona el botón de ver tabla
        self.b_modal.clicked.connect(self._on_show_modal_table)
        
    def _on_modal_threshold_changed(self, text):
        """Manejar cambio en umbral de masa participativa"""
        try:
            threshold = float(text)
            if 70.0 <= threshold <= 100.0:
                self.modal_threshold_changed.emit(threshold)
                self.set_widget_validation_style(self.le_modal, 'default')
            else:
                self.set_widget_validation_style(self.le_modal, 'warning')
        except ValueError:
            self.set_widget_validation_style(self.le_modal, 'warning')
            
    def _on_show_modal_table(self):
        """Manejar solicitud de mostrar tabla modal"""
        self.show_modal_table_requested.emit()
        
    def update_modal_results(self, results):
        """✅ Método público para actualizar resultados desde la app principal"""
        if results is None:
            self._clear_results()
            return
        
        self._update_modal_fields(results)
    
    def _update_modal_fields(self, results):
        """Actualizar campos modales y aplicar validación visual consolidada"""
        try:
            # 1. Actualizar períodos fundamentales
            self.le_tx.setText(f"{results['Tx']:.4f}" if results['Tx'] else "N/A")
            self.le_ty.setText(f"{results['Ty']:.4f}" if results['Ty'] else "N/A")
                
            # 2. Actualizar masa participativa
            self.le_participacion_x.setText(f"{results['total_mass_x']:.1f}")
            self.le_participacion_y.setText(f"{results['total_mass_y']:.1f}")
            
            # 3. Validación visual consolidada
            min_mass = self._get_min_mass_participation()
            cumple_x = results['total_mass_x'] >= min_mass
            cumple_y = results['total_mass_y'] >= min_mass
            
            # Aplicar colores directamente
            self.set_widget_validation_style(self.le_participacion_x, 'valid' if cumple_x else 'error')
            self.set_widget_validation_style(self.le_participacion_y, 'valid' if cumple_y else 'error')
            
            
            print(f"✅ Campos actualizados - Tx: {results['Tx']:.4f}s, Ty: {results['Ty']:.4f}s")
            
        except Exception as e:
            print(f"❌ Error actualizando campos: {e}")
            
    def _clear_results(self):
        """Limpiar resultados cuando no hay datos"""
        self.le_tx.setText("N/A")
        self.le_ty.setText("N/A")
        self.le_participacion_x.setText("N/A")
        self.le_participacion_y.setText("N/A")
        
        # Quitar colores de validación
        self.le_participacion_x.setStyleSheet("")
        self.le_participacion_y.setStyleSheet("")
            
    def _get_min_mass_participation(self) -> float:
        """Obtener porcentaje mínimo de masa participativa validado"""
        try:
            min_percent = float(self.le_modal.text())
            if 70.0 <= min_percent <= 100.0:
                return min_percent
            else:
                return 90.0
        except ValueError:
            return 90.0
            
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
        self.disable_combobox_wheel(self.cb_comb_static_x)
        self.disable_combobox_wheel(self.cb_comb_static_y)
        self.add_field(0, 0, "Estáticas X:", self.cb_comb_static_x, "cb_comb_static_x", "Combinaciones estáticas en X")
        self.add_field(0, 2, "Estáticas Y:", self.cb_comb_static_y, "cb_comb_static_y", "Combinaciones estáticas en Y")
        
        # Combinaciones Dinámicas
        self.cb_comb_dynamic_x = QComboBox()
        self.cb_comb_dynamic_y = QComboBox()
        self.disable_combobox_wheel(self.cb_comb_dynamic_x)
        self.disable_combobox_wheel(self.cb_comb_dynamic_y)
        self.add_field(1, 0, "Dinámicas X:", self.cb_comb_dynamic_x, "cb_comb_dynamic_x", "Combinaciones dinámicas en X")
        self.add_field(1, 2, "Dinámicas Y:", self.cb_comb_dynamic_y, "cb_comb_dynamic_y", "Combinaciones dinámicas en Y")
        
        # Combinaciones de Desplazamientos
        self.cb_comb_displacement_x = QComboBox()
        self.cb_comb_displacement_y = QComboBox()
        self.disable_combobox_wheel(self.cb_comb_displacement_x)
        self.disable_combobox_wheel(self.cb_comb_displacement_y)
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
        self.add_field(1, 2, "", self.b_desplazamiento, "b_desplazamiento", "")
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
class DriftCard(DataCard):
    """Card de Derivas"""
    drift_threshold_changed = pyqtSignal(float) # Cuando cambia el umbral máximo
    show_drift_graph_requested = pyqtSignal()    # Cuando se solicita ver la gráfica
    
    def __init__(self, parent=None):
        super().__init__("Derivas", "🏗️", parent)
        self._create_fields()
        self.connect_signals()
        
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
        self.add_field(2, 0, "Piso X:", self.le_piso_deriva_x, "le_piso_deriva_x", "Piso de la deriva máx X")
        self.add_field(2, 2, "Piso Y:", self.le_piso_deriva_y, "le_piso_deriva_y", "Piso de la deriva máx Y")
        
        # Boton
        self.b_derivas = QPushButton("Calcular Derivas")
        self.add_field(3, 2, "", self.b_derivas, "b_derivas", "")
   
    def connect_signals(self):
        """Conectar señales"""
        # Cuando cambia la deriva minima
        self.le_max_drift.textChanged.connect(self._on_drift_threshold_changed)
        
        # Cuando se presiona el botón de ver tabla
        self.b_derivas.clicked.connect(self._on_show_drift_graph)
        
    def _on_show_drift_graph(self):
        """Manejar solicitud de mostrar gráfico de derivas"""
        self.show_drift_graph_requested.emit()
        
    def _on_drift_threshold_changed(self, text):
        """Manejar cambio en umbral de masa participativa"""
        try:
            threshold = float(text)
            if 0.001 <= threshold <= 0.02:
                self.drift_threshold_changed.emit(threshold)
                self.set_widget_validation_style(self.le_max_drift, 'default')
            else:
                self.set_widget_validation_style(self.le_max_drift, 'warning')
        except ValueError:
            self.set_widget_validation_style(self.le_max_drift, 'warning')
            
    def _get_max_drift_limit(self) -> float:
        """Obtener límite máximo de deriva validado"""
        try:
            limit = float(self.le_max_drift.text())
            if 0.001 <= limit <= 0.020:
                return limit
            else:
                return 0.007  # Valor por defecto
        except ValueError:
            return 0.007
    
    def _update_drift_results(self,limit,results):
        """Actualizar campos de resultados de derivas"""
        try:           
            max_x = results.get('max_drift_x', 0.0)
            max_y = results.get('max_drift_y', 0.0)
            story_x = results.get('story_max_x', 'N/A')
            story_y = results.get('story_max_y', 'N/A')
            
            # Actualizar campos
            self.le_deriva_max_x.setText(f"{max_x:.4f}")
            self.le_deriva_max_y.setText(f"{max_y:.4f}")
            self.le_piso_deriva_x.setText(str(story_x))
            self.le_piso_deriva_y.setText(str(story_y))
            
            complies_x = max_x <= limit
            complies_y = max_y <= limit
            
            self._drift_validation(complies_x,complies_y)
        
        except Exception as e:
            print(f"Error actualizando resultados de derivas: {e}")
        
    def _drift_validation(self,complies_x, complies_y):
        """Validar deriva máxima y aplicar colores"""
        try:

            # Validación dirección X
            self.set_widget_validation_style(self.le_deriva_max_x, 'valid' if complies_x else 'error')
            self.set_widget_validation_style(self.le_piso_deriva_x, 'valid' if complies_x else 'error')
            
            # Validación dirección Y
            self.set_widget_validation_style(self.le_deriva_max_y, 'valid' if complies_y else 'error')
            self.set_widget_validation_style(self.le_piso_deriva_y, 'valid' if complies_y else 'error')
                     
        except ValueError:
            # Validación dirección X
            self.set_widget_validation_style(self.le_deriva_max_x, 'default')
            self.set_widget_validation_style(self.le_piso_deriva_x, 'default')
            
            # Validación dirección Y
            self.set_widget_validation_style(self.le_deriva_max_y, 'default')
            self.set_widget_validation_style(self.le_piso_deriva_y, 'default')
    
    
class TorsionCard(DataCard):
    """Card de Irregularidad por Torsión"""
    torsion_threshold_changed = pyqtSignal(float) # Señal de cambio de límite
    show_torsion_table_requested = pyqtSignal() # Solicitud de tabla
    torsion_combo_changed = pyqtSignal() # cambio de combo
    
    def __init__(self, parent=None):
        super().__init__("Irregularidad Torsional", "🏗️", parent)
        self._create_fields()
        self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(1, 1)
        self.content_layout.setColumnStretch(3, 1)
        
        # Combinación para torsión
        self.cb_torsion_combo = QComboBox()
        self.cb_torsion_combo.addItems(["Dinámicas", "Estáticas", "Desplazamientos"])
        self.disable_combobox_wheel(self.cb_torsion_combo)
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
        self.add_field(4, 2, "", self.b_torsion_table, "b_torsion_table", "")
   
    def connect_signals(self):
        """Conectar señales"""
        # Cuando cambia ratio máximo
        self.le_torsion_limit.textChanged.connect(self._on_torsion_limit_changed)
        
        # Cuando se presiona el botón de ver tabla
        self.b_torsion_table.clicked.connect(self._on_show_torsion_table)
        
        # Cuando se cambia de combo
        self.cb_torsion_combo.currentTextChanged.connect(self._on_change_combo)
        
    def _on_show_torsion_table(self):
        """Manejar solicitud de mostrar tabla"""
        self.show_torsion_table_requested.emit()
        
    def _on_change_combo(self):
        """Manejar cambio de combo"""
        self.torsion_combo_changed.emit()
            
    def _on_torsion_limit_changed(self, text):
        """Manejar cambio en umbral de masa participativa"""
        try:
            threshold = float(text)
            if 1.0 <= threshold <= 2.0:
                self.torsion_threshold_changed.emit(threshold)
                self.set_widget_validation_style(self.le_torsion_limit, 'default')
            else:
                self.set_widget_validation_style(self.le_torsion_limit, 'warning')
        except ValueError:
            self.set_widget_validation_style(self.le_torsion_limit, 'warning')
            
    def _get_torsion_limit(self) -> float:
        """Obtener límite de torsión validado"""
        try:
            limit = float(self.le_torsion_limit.text())
            if 1.0 <= limit <= 2.0:
                return limit
            else:
                return 1.3
        except ValueError:
            return None
        
    def _get_torsion_combo(self) -> str:
        """Obtener límite de torsión validado"""
        try:
            return self.cb_torsion_combo.currentText().lower()
        except ValueError:
            return None
        
    def _validate_torsion(self, status_x: str, status_y: str):
        """Aplicar validación automática con colores"""
        # Validar dirección X
        if status_x == 'IRREGULAR':
            self.set_widget_validation_style(self.le_relacion_x, 'error')
            self.set_widget_validation_style(self.le_irregularidad_x, 'error')
        else:
            self.set_widget_validation_style(self.le_relacion_x, 'valid')
            self.set_widget_validation_style(self.le_irregularidad_x, 'valid')
        
        # Validar dirección Y
        if status_y == 'IRREGULAR':
            self.set_widget_validation_style(self.le_relacion_y, 'error')
            self.set_widget_validation_style(self.le_irregularidad_y, 'error')
        else:
            self.set_widget_validation_style(self.le_relacion_y, 'valid')
            self.set_widget_validation_style(self.le_irregularidad_y, 'valid')
    
    def _update_torsion_results(self,torsion_data):
        """Actualizar campos de resultados de torsion"""
        try:
            torsion_limit = self._get_torsion_limit()
            ratio_x = torsion_data.get('ratio_x', 0.0)
            ratio_y = torsion_data.get('ratio_y', 0.0)
            
            # Verificar irregularidad
            irregular_x = ratio_x > torsion_limit
            irregular_y = ratio_y > torsion_limit
            
            status_x = "IRREGULAR" if (irregular_x) else "REGULAR"
            status_y = "IRREGULAR" if (irregular_y) else "REGULAR"
            
            # Actualizar campos_units_widgets
            self.le_irregularidad_x.setText(status_x)
            self.le_relacion_x.setText(f"{ratio_x:.3f}")
            
            self.le_irregularidad_y.setText(status_y)
            self.le_relacion_y.setText(f"{ratio_y:.3f}")
            
            # Validación con colores
            self._validate_torsion(status_x,status_y)
            
        except Exception as e:
            print(f"Error actualizando resultados de derivas: {e}")
    
class PortadaCard(DataCard):
    """Card para portada"""
    
    def __init__(self, parent=None):
        super().__init__("Sección de Portada", "📒", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 2)
        self.content_layout.setColumnStretch(2, 2)
        self.content_layout.setColumnStretch(3, 2)
        
        # Imagen de Portada
        self.b_portada = QPushButton("Cargar Imagen")
        self.lb_portada_status = QLabel("Imagen por defecto")
        self.customize_widget(self.lb_portada_status,color='gray')
        self.add_field(0, 0, "Imagen de Portada:", self.b_portada, "b_portada", "Imagen de Portada")
        self.add_widget(0,2,self.lb_portada_status,'lb_portada_status','')
        
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    

class DescripcionEstructuraCard(DataCard):
    """Card de Descripción de la Estructura"""

    def __init__(self, parent=None):
        super().__init__("Descripción de la Estructura", "📒", parent)
        self._create_fields()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 2)
        self.content_layout.setColumnStretch(2, 2)
        self.content_layout.setColumnStretch(3, 2)
        
        # Checkbox
        self.cb_desc_estructura = QCheckBox("")
        self.cb_desc_estructura.setChecked(False)
        self.cb_desc_estructura.setEnabled(False)
        self.add_field(0, 0, "Incluir en la memoria:", self.cb_desc_estructura, "cb_desc_estructura", "")
        
        # Descripción
        self.b_descripcion = QPushButton("Agregar Texto")
        self.lb_descripcion = QLabel("Sin texto")
        self.customize_widget(self.lb_descripcion,color='gray')
        self.add_field(1, 0, "Contenido de la sección:", self.b_descripcion, "b_descripcion", "Contenido de la sección")
        self.add_widget(1,2,self.lb_descripcion,'lb_descripcion','')
        
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
    
class CriteriosModelamientoCard(DataCard):
    """Card de Descripción de la Estructura"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Criterios de Modelamiento", "📒", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 2)
        self.content_layout.setColumnStretch(2, 2)
        self.content_layout.setColumnStretch(3, 2)
        
        # Checkbox
        self.cb_criterios = QCheckBox("")
        self.cb_criterios.setChecked(False)
        self.cb_criterios.setEnabled(False)
        self.add_field(0, 0, "Incluir en la memoria:", self.cb_criterios, "cb_criterios", "")
        
        # Descripción
        self.b_modelamiento = QPushButton("Agregar Texto")
        self.lb_modelamiento = QLabel("Sin texto")
        self.customize_widget(self.lb_modelamiento,color='gray')
        self.add_field(1, 0, "Contenido de la sección:", self.b_modelamiento, "b_modelamiento", "Contenido de la sección")
        self.add_widget(1,2,self.lb_modelamiento,'lb_modelamiento','')
        
        # Captura 3D
        self.b_3D = QPushButton("Cargar Imagen")
        self.lb_3d_status = QLabel("Sin imagen")
        self.customize_widget(self.lb_3d_status,color='gray')
        self.add_field(2, 0, "Captura 3D:", self.b_3D, "b_3D", "Captura 3D")
        self.add_widget(2,2,self.lb_3d_status,'lb_3d_status','')
        
        # Planta Típica
        self.b_planta = QPushButton("Cargar Imagen")
        self.lb_planta_status = QLabel("Sin imagen")
        self.customize_widget(self.lb_planta_status,color='gray')
        self.add_field(3, 0, "Planta Típica:", self.b_planta, "b_planta", "Planta Típica")
        self.add_widget(3,2,self.lb_planta_status,'lb_planta_status','')
        
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
class DescripcionCargasCard(DataCard):
    """Card de Descripción de la Estructura"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Descripción de Cargas", "📒", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 2)
        self.content_layout.setColumnStretch(2, 2)
        self.content_layout.setColumnStretch(3, 2)
        
        # Checkbox
        self.cb_cargas = QCheckBox("")
        self.cb_cargas.setChecked(False)
        self.cb_cargas.setEnabled(False)
        self.add_field(0, 0, "Incluir en la memoria:", self.cb_cargas, "cb_cargas", "")
        
        # Descripción
        self.b_cargas = QPushButton("Agregar Texto")
        self.lb_cargas = QLabel("Sin texto")
        self.customize_widget(self.lb_cargas,color='gray')
        self.add_field(1, 0, "Contenido de la sección:", self.b_cargas, "b_cargas", "Contenido de la sección")
        self.add_widget(1,2,self.lb_cargas,'lb_cargas','')
        
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)
    
    
class ModosPrincipalesCard(DataCard):
    """Card de Descripción de la Estructura"""
    #units_changed = pyqtSignal(dict) # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__("Modos Principales del Análisis Modal", "📒", parent)
        self._create_fields()
        #self.connect_signals()
        
    def _create_fields(self):
        """Crear campos específicos"""
        # Configurar expansión de columnas
        self.content_layout.setColumnStretch(0, 1)
        self.content_layout.setColumnStretch(1, 2)
        self.content_layout.setColumnStretch(2, 2)
        self.content_layout.setColumnStretch(3, 2)
        
        # Checkbox
        self.cb_modos = QCheckBox("")
        self.cb_modos.setChecked(False)
        self.cb_modos.setEnabled(False)
        self.add_field(0, 0, "Incluir en la memoria:", self.cb_modos, "cb_modos", "")
        
        # Modos principales
        self.b_defX = QPushButton("Cargar Imagen")
        self.lb_defx_status = QLabel("Sin Imagen")
        self.customize_widget(self.lb_defx_status,color='gray')
        self.add_field(1, 0, "Modo Principal en X:", self.b_defX, "b_defX", "Modo Principal en X")
        self.add_widget(1,2,self.lb_defx_status,'lb_defx_status','')
        
        self.b_defY = QPushButton("Cargar Imagen")
        self.lb_defy_status = QLabel("Sin Imagen")
        self.customize_widget(self.lb_defy_status,color='gray')
        self.add_field(2, 0, "Modo Principal en Y:", self.b_defY, "b_defY", "Modo Principal en Y")
        self.add_widget(2,2,self.lb_defy_status,'lb_defY_status','')
        
   
    # def connect_signals(self):
    #     """Conectar señales"""
    #     for categoria, combo in self.combos.items():
    #         combo.currentTextChanged.connect(self._on_unit_changed)