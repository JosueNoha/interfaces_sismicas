"""
Interfaz principal unificada con ComboBoxes de combinaciones
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ui.widgets.data_cards import (ProjectDataCard, SeismicParamsCard, UnitsParamsCard, ModalCard, CombinationsCard, ShearCard, DisplacementCard, 
DriftCard, TorsionCard)

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
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        
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
        
        self.le_modal = card.le_modal
        self.le_tx = card.le_tx
        self.le_ty = card.le_ty
        self.le_participacion_x = card.le_participacion_x
        self.le_participacion_y = card.le_participacion_y
        self.b_modal = card.b_modal
        
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
        
        self.le_max_drift = card.le_max_drift
        self.le_deriva_max_x = card.le_deriva_max_x
        self.le_deriva_max_y = card.le_deriva_max_y
        self.le_piso_deriva_x = card.le_piso_deriva_x
        self.le_piso_deriva_y = card.le_piso_deriva_y
        self.b_derivas = card.b_derivas

        # Irregularidad torsional
        card = TorsionCard()
        scroll_layout.addWidget(card)
        
        self.cb_torsion_combo = card.cb_torsion_combo
        self.le_torsion_limit = card.le_torsion_limit
        self.le_relacion_x = card.le_relacion_x
        self.le_relacion_y = card.le_relacion_y
        self.le_irregularidad_x = card.le_irregularidad_x
        self.le_irregularidad_y = card.le_irregularidad_y
        self.b_torsion_table = card.b_torsion_table


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
        self._setup_portada_section(scroll_layout)
        self._setup_descripcion_estructura_section(scroll_layout)
        self._setup_criterios_modelamiento_section(scroll_layout)
        self._setup_descripcion_cargas_section(scroll_layout)
        self._setup_modos_principales_section(scroll_layout)
        
        # Configurar scroll
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tabWidget.addTab(self.tab_memory, "Memoria")
        
    
    def _setup_portada_section(self, parent_layout):
        """Sección de Portada"""
        self.group_portada = QtWidgets.QGroupBox()
        portada_layout = QtWidgets.QVBoxLayout(self.group_portada)
        
        # Checkbox para incluir sección
        content_layout = QtWidgets.QHBoxLayout()
        self.label_portada = QtWidgets.QLabel("Imagen de Portada:")
        self.b_portada = QtWidgets.QPushButton("Cargar Imagen")
        self.lb_portada_status = QtWidgets.QLabel("Imagen por defecto")
        self.lb_portada_status.setStyleSheet("color: gray;")
            
        
        content_layout.addWidget(self.label_portada)
        content_layout.addWidget(self.b_portada)
        content_layout.addWidget(self.lb_portada_status)
        content_layout.addStretch()
        portada_layout.addLayout(content_layout)
        
        parent_layout.addWidget(self.group_portada)

    def _setup_descripcion_estructura_section(self, parent_layout):
        """Sección de Descripción de la Estructura"""
        self.group_desc_estructura = QtWidgets.QGroupBox()
        desc_layout = QtWidgets.QVBoxLayout(self.group_desc_estructura)
        
        # Checkbox para incluir sección
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.cb_desc_estructura = QtWidgets.QCheckBox("Descripción de la Estructura")
        self.cb_desc_estructura.setChecked(False)
        self.cb_desc_estructura.setEnabled(False)
        checkbox_layout.addWidget(self.cb_desc_estructura)
        checkbox_layout.addStretch()
        desc_layout.addLayout(checkbox_layout)
        
        # Contenido de la sección
        content_layout = QtWidgets.QHBoxLayout()
        self.label_desc_estructura = QtWidgets.QLabel("Descripción:")
        self.b_descripcion = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_descripcion = QtWidgets.QLabel("Sin texto")
        self.lb_descripcion.setStyleSheet("color: gray;")
        
        content_layout.addWidget(self.label_desc_estructura)
        content_layout.addWidget(self.b_descripcion)
        content_layout.addWidget(self.lb_descripcion)
        content_layout.addStretch()
        desc_layout.addLayout(content_layout)
        
        parent_layout.addWidget(self.group_desc_estructura)

    def _setup_criterios_modelamiento_section(self, parent_layout):
        """Sección de Criterios de Modelamiento"""
        self.group_criterios = QtWidgets.QGroupBox()
        criterios_layout = QtWidgets.QVBoxLayout(self.group_criterios)
        
        # Checkbox para incluir sección
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.cb_criterios = QtWidgets.QCheckBox("Criterios de Modelamiento")
        self.cb_criterios.setChecked(False)
        self.cb_criterios.setEnabled(False)
        checkbox_layout.addWidget(self.cb_criterios)
        checkbox_layout.addStretch()
        criterios_layout.addLayout(checkbox_layout)
        
        # Contenido de la sección - Texto
        text_layout = QtWidgets.QHBoxLayout()
        self.label_modelamiento = QtWidgets.QLabel("Descripción:")
        self.b_modelamiento = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_modelamiento = QtWidgets.QLabel("Sin texto")
        self.lb_modelamiento.setStyleSheet("color: gray;")
        
        text_layout.addWidget(self.label_modelamiento)
        text_layout.addWidget(self.b_modelamiento)
        text_layout.addWidget(self.lb_modelamiento)
        text_layout.addStretch()
        criterios_layout.addLayout(text_layout)
        
        # Contenido de la sección - Imágenes
        images_layout = QtWidgets.QGridLayout()
        
        # Captura 3D
        self.label_3d = QtWidgets.QLabel("Captura 3D:")
        self.b_3D = QtWidgets.QPushButton("Cargar Imagen")
        self.lb_3d_status = QtWidgets.QLabel("Sin imagen")
        self.lb_3d_status.setStyleSheet("color: gray;")
        
        images_layout.addWidget(self.label_3d, 0, 0)
        images_layout.addWidget(self.b_3D, 0, 1)
        images_layout.addWidget(self.lb_3d_status, 0, 2)
        
        # Planta Típica
        self.label_planta = QtWidgets.QLabel("Planta Típica:")
        self.b_planta = QtWidgets.QPushButton("Cargar Imagen")
        self.lb_planta_status = QtWidgets.QLabel("Sin imagen")
        self.lb_planta_status.setStyleSheet("color: gray;")
        
        images_layout.addWidget(self.label_planta, 1, 0)
        images_layout.addWidget(self.b_planta, 1, 1)
        images_layout.addWidget(self.lb_planta_status, 1, 2)
        
        criterios_layout.addLayout(images_layout)
        
        parent_layout.addWidget(self.group_criterios)

    def _setup_descripcion_cargas_section(self, parent_layout):
        """Sección de Descripción de Cargas"""
        self.group_cargas = QtWidgets.QGroupBox()
        cargas_layout = QtWidgets.QVBoxLayout(self.group_cargas)
        
        # Checkbox para incluir sección
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.cb_cargas = QtWidgets.QCheckBox("Descripción de Cargas")
        self.cb_cargas.setChecked(False)
        self.cb_cargas.setEnabled(False)
        checkbox_layout.addWidget(self.cb_cargas)
        checkbox_layout.addStretch()
        cargas_layout.addLayout(checkbox_layout)
        
        # Contenido de la sección
        content_layout = QtWidgets.QHBoxLayout()
        self.label_cargas = QtWidgets.QLabel("Descripción:")
        self.b_cargas = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_cargas = QtWidgets.QLabel("Sin texto")
        self.lb_cargas.setStyleSheet("color: gray;")
        
        content_layout.addWidget(self.label_cargas)
        content_layout.addWidget(self.b_cargas)
        content_layout.addWidget(self.lb_cargas)
        content_layout.addStretch()
        cargas_layout.addLayout(content_layout)
        
        parent_layout.addWidget(self.group_cargas)

    def _setup_modos_principales_section(self, parent_layout):
        """Sección de Modos Principales del Análisis Modal"""
        self.group_modos = QtWidgets.QGroupBox()
        modos_layout = QtWidgets.QVBoxLayout(self.group_modos)
        
        # Checkbox para incluir sección
        checkbox_layout = QtWidgets.QHBoxLayout()
        self.cb_modos = QtWidgets.QCheckBox("Modos Principales del Análisis Modal")
        self.cb_modos.setChecked(False)
        self.cb_modos.setEnabled(False)
        checkbox_layout.addWidget(self.cb_modos)
        checkbox_layout.addStretch()
        modos_layout.addLayout(checkbox_layout)
        
        # Contenido de la sección - Imágenes de modos
        images_layout = QtWidgets.QGridLayout()
        
        # Modo Principal en X
        self.label_defx = QtWidgets.QLabel("Modo Principal en X:")
        self.b_defX = QtWidgets.QPushButton("Cargar Imagen")
        self.lb_defx_status = QtWidgets.QLabel("Sin imagen")
        self.lb_defx_status.setStyleSheet("color: gray;")
        
        images_layout.addWidget(self.label_defx, 0, 0)
        images_layout.addWidget(self.b_defX, 0, 1)
        images_layout.addWidget(self.lb_defx_status, 0, 2)
        
        # Modo Principal en Y
        self.label_defy = QtWidgets.QLabel("Modo Principal en Y:")
        self.b_defY = QtWidgets.QPushButton("Cargar Imagen")
        self.lb_defy_status = QtWidgets.QLabel("Sin imagen")
        self.lb_defy_status.setStyleSheet("color: gray;")
        
        images_layout.addWidget(self.label_defy, 1, 0)
        images_layout.addWidget(self.b_defY, 1, 1)
        images_layout.addWidget(self.lb_defy_status, 1, 2)
        
        modos_layout.addLayout(images_layout)
        
        parent_layout.addWidget(self.group_modos)

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