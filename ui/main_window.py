"""
Interfaz principal unificada con ComboBoxes de combinaciones
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ui.widgets.data_cards import (ProjectDataCard, SeismicParamsCard, UnitsParamsCard, ModalCard, CombinationsCard, ShearCard, DisplacementCard, 
DriftCard, TorsionCard, PortadaCard, DescripcionEstructuraCard, CriteriosModelamientoCard,
DescripcionCargasCard, ModosPrincipalesCard)

from PyQt5.QtWidgets import QTabWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setMinimumSize(QtCore.QSize(1000, 600))
        
        # Widget central
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # Layout principal
        self.main_layout = QtWidgets.QVBoxLayout(self.centralwidget)
        
        # Header con título
        self._setup_header()
        
        # TabWidget principal
        self._setup_tabs()
        
        # Botones inferiores
        self._setup_bottom_buttons()
        
        MainWindow.setCentralWidget(self.centralwidget)
        
        # Status bar
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        MainWindow.setStatusBar(self.statusbar)
        
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        
    def _connect_memory_signals(self):
        """Conectar señales de la pestaña de memoria"""
        
        # Conexiones para carga de imágenes
        self.ui.b_portada.clicked.connect(lambda: self.load_image('portada'))
        self.ui.b_planta.clicked.connect(lambda: self.load_image('planta'))
        self.ui.b_3D.clicked.connect(lambda: self.load_image('3d'))
        self.ui.b_defX.clicked.connect(lambda: self.load_image('defX'))
        self.ui.b_defY.clicked.connect(lambda: self.load_image('defY'))
        
        # Conexiones para descripciones
        self.ui.b_descripcion.clicked.connect(lambda: self.open_description_dialog('descripcion'))
        self.ui.b_modelamiento.clicked.connect(lambda: self.open_description_dialog('modelamiento'))
        self.ui.b_cargas.clicked.connect(lambda: self.open_description_dialog('cargas'))
        
    def get_memory_sections_status(self):
        """Obtener estado de las secciones de memoria (activadas/desactivadas)"""
        return {
            'portada': self.ui.cb_portada.isChecked(),
            'descripcion_estructura': self.ui.cb_desc_estructura.isChecked(),
            'criterios_modelamiento': self.ui.cb_criterios.isChecked(),
            'descripcion_cargas': self.ui.cb_cargas.isChecked(),
            'modos_principales': self.ui.cb_modos.isChecked()
        }
        
    def initialize_memory_defaults(self):
        """Inicializar valores por defecto de la memoria"""
        # Establecer textos por defecto usando las descripciones actuales
        if hasattr(self.sismo, 'descriptions'):
            descriptions = self.sismo.descriptions
            
            # Actualizar estados de texto si hay contenido por defecto
            if descriptions.get('descripcion', '').strip():
                self.ui._update_text_status('descripcion', True)
            if descriptions.get('modelamiento', '').strip():
                self.ui._update_text_status('modelamiento', True)  
            if descriptions.get('cargas', '').strip():
                self.ui._update_text_status('cargas', True)

    def _setup_header(self):
        """Configurar header con título"""
        header_layout = QtWidgets.QHBoxLayout()
        
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setBold(True)
        self.label_title.setFont(font)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        
        header_layout.addWidget(self.label_title)
        self.main_layout.addLayout(header_layout)

    def _setup_tabs(self):
        """Configurar pestañas principales"""
        self.tabWidget = StyledTabWidget(self.centralwidget)
        
        # Tab Datos Generales
        self._setup_general_tab()
        
        # Tab Análisis Sísmico
        self._setup_seismic_tab()
        
        # Tab Memoria
        self._setup_memory_tab()
        
        self.main_layout.addWidget(self.tabWidget)

    def _setup_general_tab(self):
        """Tab de datos generales del proyecto"""
        self.tab_general = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tab_general)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        
        # Card de datos del proyecto  
        self.project_data_card = ProjectDataCard()
        scroll_layout.addWidget(self.project_data_card)
        
        # Para compatibilidad con el código existente, crear referencias
        self.le_proyecto = self.project_data_card.le_proyecto
        self.le_ubicacion = self.project_data_card.le_ubicacion  
        self.le_autor = self.project_data_card.le_autor
        self.le_fecha = self.project_data_card.le_fecha
        
        # # Grupo de parámetros sísmicos (contenedor dinámico)
        self.seismic_params_card = SeismicParamsCard()
        scroll_layout.addWidget(self.seismic_params_card)
        
        
        # Configurar scroll
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        
        self.tabWidget.addTab(self.tab_general, "Datos Generales")

    def _setup_seismic_tab(self):
        """Tab de análisis sísmico con ComboBoxes de combinaciones"""
        self.tab_seismic = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tab_seismic)
        
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        # Widget de unidades de trabajo
        self.units_widget = UnitsParamsCard()
        scroll_layout.addWidget(self.units_widget)
        
        # Análisis Modal
        card = ModalCard()
        scroll_layout.addWidget(card)
        self.modal_card = card
        
        # Selección de Combinaciones
        card = CombinationsCard()
        scroll_layout.addWidget(card)
        
        self.cb_comb_static_x = card.cb_comb_static_x
        self.cb_comb_static_y = card.cb_comb_static_y
        self.cb_comb_dynamic_x = card.cb_comb_dynamic_x
        self.cb_comb_dynamic_y = card.cb_comb_dynamic_y
        self.cb_comb_displacement_x = card.cb_comb_displacement_x
        self.cb_comb_displacement_y = card.cb_comb_displacement_y
        
        # Fuerzas cortantes
        card = ShearCard()
        scroll_layout.addWidget(card)
        
        self.le_scale_factor = card.le_scale_factor
        self.le_vdx = card.le_vdx
        self.le_vdy = card.le_vdy
        self.le_vsx = card.le_vsx
        self.le_vsy = card.le_vsy
        self.le_fx = card.le_fx
        self.le_fy = card.le_fy
        self.b_view_dynamic = card.b_view_dynamic
        self.b_view_static = card.b_view_static
      
        # Desplazamientos y derivas
        card = DisplacementCard()
        scroll_layout.addWidget(card)
        
        self.le_desp_max_x = card.le_desp_max_x
        self.le_desp_max_y = card.le_desp_max_y
        self.b_desplazamiento = card.b_desplazamiento

        card = DriftCard()
        scroll_layout.addWidget(card)
        self.drift_card = card

        # Irregularidad torsional
        card = TorsionCard()
        scroll_layout.addWidget(card)
        self.torsion_card = card

        # Configurar scroll
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tabWidget.addTab(self.tab_seismic, "Análisis Sísmico")
        
    def _setup_memory_tab(self):
        """Tab de memoria de cálculo con secciones organizadas"""
        self.tab_memory = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tab_memory)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        # Secciones de memoria organizadas
        card = PortadaCard()
        scroll_layout.addWidget(card)
        self.b_portada = card.b_portada
        self.lb_portada_status = card.lb_portada_status
        
        card = DescripcionEstructuraCard()
        scroll_layout.addWidget(card)
        self.cb_desc_estructura = card.cb_desc_estructura
        self.b_descripcion = card.b_descripcion
        self.lb_descripcion = card.lb_descripcion
        
        card = CriteriosModelamientoCard()
        scroll_layout.addWidget(card)
        self.cb_criterios = card.cb_criterios
        self.b_modelamiento = card.b_modelamiento
        self.lb_modelamiento = card.lb_modelamiento
        self.b_3D = card.b_3D
        self.lb_3d_status = card.lb_3d_status
        self.b_planta = card.b_planta
        self.lb_planta_status = card.lb_planta_status
        
        card = DescripcionCargasCard()
        scroll_layout.addWidget(card)
        self.cb_cargas = card.cb_cargas
        self.b_cargas = card.b_cargas
        self.lb_cargas = card.lb_cargas
        
        card = ModosPrincipalesCard()
        scroll_layout.addWidget(card)
        self.cb_modos = card.cb_modos
        self.b_defX = card.b_defX
        self.lb_defx_status = card.lb_defx_status
        self.b_defY = card.b_defY
        self.lb_defy_status = card.lb_defy_status
        
        # Configurar scroll
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tabWidget.addTab(self.tab_memory, "Memoria")
        

    def _toggle_section_content(self, widgets, enabled):
        """Habilitar/deshabilitar widgets de una sección"""
        for widget in widgets:
            widget.setEnabled(enabled)
            
    def _update_image_status(self, image_type: str, file_path: str = None):
        """Actualizar estado visual de carga de imagen"""
        status_mappings = {
            'portada': self.lb_portada_status,
            'planta': self.lb_planta_status,
            '3d': self.lb_3d_status,
            'defX': self.lb_defx_status,
            'defY': self.lb_defy_status
        }
        
        status_label = status_mappings.get(image_type)
        if status_label:
            if file_path:
                filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
                status_label.setText(f"✅ {filename}")
                status_label.setStyleSheet("color: green;")
            else:
                default_text = "Imagen por defecto" if image_type == 'portada' else "Sin imagen"
                status_label.setText(default_text)
                status_label.setStyleSheet("color: gray;")
                
        # ✅ Verificar si ambas imágenes de modos están cargadas
        if image_type in ['defX', 'defY'] and hasattr(self, 'cb_modos'):
            defx_loaded = hasattr(self, 'lb_defx_status') and "✅" in self.lb_defx_status.text()
            defy_loaded = hasattr(self, 'lb_defy_status') and "✅" in self.lb_defy_status.text()
            
            if defx_loaded and defy_loaded:
                self.cb_modos.setEnabled(True)
                self.cb_modos.setChecked(True)
            else:
                self.cb_modos.setEnabled(False)
                self.cb_modos.setChecked(False)

    def _update_text_status(self, text_type: str, has_text: bool = True):
        """Actualizar estado visual de carga de texto"""
        status_mappings = {
            'descripcion': self.lb_descripcion,
            'modelamiento': self.lb_modelamiento,
            'cargas': self.lb_cargas
        }
        
        checkbox_mappings = {
            'descripcion': self.cb_desc_estructura,
            'modelamiento': self.cb_criterios,
            'cargas': self.cb_cargas
        }
        
        status_label = status_mappings.get(text_type)
        checkbox = checkbox_mappings.get(text_type)
        
        if status_label:
            if has_text:
                status_label.setText("✅ Texto cargado")
                status_label.setStyleSheet("color: green;")
                if checkbox:
                    checkbox.setEnabled(True)
                    checkbox.setChecked(True)
            else:
                status_label.setText("Sin texto")
                status_label.setStyleSheet("color: gray;")
                if checkbox:
                    checkbox.setEnabled(False)
                    checkbox.setChecked(False)


    def _setup_bottom_buttons(self):
        """Configurar botones inferiores"""
        buttons_layout = QtWidgets.QHBoxLayout()
        
        # Espaciador
        spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        buttons_layout.addItem(spacer)
        
        # Botón actualizar
        self.b_actualizar = QtWidgets.QPushButton("Actualizar Datos")
        self.b_actualizar.setMinimumSize(QtCore.QSize(120, 30))
        buttons_layout.addWidget(self.b_actualizar)
        
        # Botón reporte
        self.b_reporte = QtWidgets.QPushButton("Generar Reporte")
        self.b_reporte.setMinimumSize(QtCore.QSize(120, 30))
        buttons_layout.addWidget(self.b_reporte)
        
        # Espaciador
        buttons_layout.addItem(spacer)
        
        self.main_layout.addLayout(buttons_layout)

    def retranslateUi(self, MainWindow):
        """Configurar textos de la interfaz"""
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Análisis Sísmico"))
        self.label_title.setText(_translate("MainWindow", "Análisis Sísmico"))
        
        # Tab names
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_general), _translate("MainWindow", "Datos Generales"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_seismic), _translate("MainWindow", "Análisis Sísmico"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_memory), _translate("MainWindow", "Memoria"))
        
        # Botones principales
        self.b_actualizar.setText(_translate("MainWindow", "Actualizar Datos"))
        self.b_reporte.setText(_translate("MainWindow", "Generar Reporte"))
        
        
class StyledTabWidget(QTabWidget):
    """TabWidget con estilos modernos aplicados automáticamente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.apply_modern_styles()
    
    def apply_modern_styles(self):
        """Aplicar estilos modernos al TabWidget"""
        self.setStyleSheet("""
            /* ===== TAB WIDGET ===== */
            QTabWidget {
                background-color: #ffffff;
                border: none;
            }
            
            /* ===== TAB BAR ===== */
            QTabWidget::pane {
                background-color: #ffffff;
                border: 2px solid #e3f2fd;
                border-radius: 8px;
                margin-top: -1px;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
            }
            
            /* ===== TABS ===== */
            QTabBar::tab {
                background-color: #f5f5f5;
                color: #424242;
                padding: 12px 20px;
                margin-right: 2px;
                border: 2px solid #e0e0e0;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                min-width: 120px;
                font-weight: 500;
                font-size: 11px;
            }
            
            QTabBar::tab:selected {
                background-color: #ffffff;
                color: #1976d2;
                border: 2px solid #e3f2fd;
                border-bottom: 2px solid #ffffff;
                font-weight: 600;
            }
            
            QTabBar::tab:hover:!selected {
                background-color: #eeeeee;
                color: #212121;
                border-color: #bdbdbd;
            }
            
            QTabBar::tab:pressed {
                background-color: #e0e0e0;
            }
            
            /* ===== FIRST AND LAST TABS ===== */
            QTabBar::tab:first {
                margin-left: 0px;
            }
            
            QTabBar::tab:last {
                margin-right: 0px;
            }
            
            /* ===== DISABLED STATE ===== */
            QTabBar::tab:disabled {
                background-color: #fafafa;
                color: #bdbdbd;
                border-color: #eeeeee;
            }
            
            /* ===== TAB CONTENT AREA ===== */
            QTabWidget::pane {
                position: absolute;
                top: -2px;
            }
            
            QTabWidget::pane:top {
                top: -2px;
            }
            
            /* ===== SCROLL BUTTONS (si hay muchas tabs) ===== */
            QTabBar::scroller {
                width: 20px;
            }
            
            QTabBar QToolButton {
                background-color: #f5f5f5;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
            }
            
            QTabBar QToolButton:hover {
                background-color: #eeeeee;
                border-color: #bdbdbd;
            }
            
            QTabBar QToolButton::right-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #424242;
                width: 0px;
                height: 0px;
            }
            
            QTabBar QToolButton::left-arrow {
                image: none;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #424242;
                width: 0px;
                height: 0px;
            }
        """)
    
    def apply_accent_color(self, accent_color="#2196f3"):
        """Aplicar color de acento personalizado"""
        # Versión con color personalizable
        accent_light = self._lighten_color(accent_color, 0.9)  # Para bordes
        accent_text = self._darken_color(accent_color, 0.2)    # Para texto
        
        custom_style = f"""
            QTabBar::tab:selected {{
                color: {accent_text};
                border: 2px solid {accent_light};
                border-bottom: 2px solid #ffffff;
            }}
            
            QTabWidget::pane {{
                border: 2px solid {accent_light};
            }}
        """
        
        current_style = self.styleSheet()
        self.setStyleSheet(current_style + custom_style)
    
    def _lighten_color(self, hex_color, factor):
        """Aclarar un color hexadecimal"""
        # Implementación simple - en producción usar QColor
        if hex_color == "#2196f3":
            return "#e3f2fd"
        return "#e0e0e0"  # Fallback
    
    def _darken_color(self, hex_color, factor):
        """Oscurecer un color hexadecimal"""
        # Implementación simple - en producción usar QColor
        if hex_color == "#2196f3":
            return "#1976d2"
        return "#424242"  # Fallback
    