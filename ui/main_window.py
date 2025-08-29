"""
Interfaz principal unificada con ComboBoxes de combinaciones
"""

from PyQt5 import QtCore, QtGui, QtWidgets


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
        
        # Grupo de información del proyecto
        self.group_project = QtWidgets.QGroupBox("Información del Proyecto")
        project_layout = QtWidgets.QGridLayout(self.group_project)
        
        # Campos del proyecto
        self.label_proyecto = QtWidgets.QLabel("Proyecto:")
        self.le_proyecto = QtWidgets.QLineEdit()
        self.label_ubicacion = QtWidgets.QLabel("Ubicación:")
        self.le_ubicacion = QtWidgets.QLineEdit()
        self.label_autor = QtWidgets.QLabel("Autor:")
        self.le_autor = QtWidgets.QLineEdit()
        self.label_fecha = QtWidgets.QLabel("Fecha:")
        self.le_fecha = QtWidgets.QLineEdit()
        
        project_layout.addWidget(self.label_proyecto, 0, 0)
        project_layout.addWidget(self.le_proyecto, 0, 1)
        project_layout.addWidget(self.label_ubicacion, 0, 2)
        project_layout.addWidget(self.le_ubicacion, 0, 3)
        project_layout.addWidget(self.label_autor, 1, 0)
        project_layout.addWidget(self.le_autor, 1, 1)
        project_layout.addWidget(self.label_fecha, 1, 2)
        project_layout.addWidget(self.le_fecha, 1, 3)
        
        layout.addWidget(self.group_project)
        
        # Grupo de parámetros sísmicos (contenedor dinámico)
        self.group_seismic_params = QtWidgets.QGroupBox("Parámetros Sísmicos")
        self.seismic_params_layout = QtWidgets.QGridLayout(self.group_seismic_params)
        layout.addWidget(self.group_seismic_params)
        
        # Espaciador
        layout.addStretch()
        
        self.tabWidget.addTab(self.tab_general, "Datos Generales")

    def _setup_seismic_tab(self):
        """Tab de análisis sísmico con ComboBoxes de combinaciones"""
        self.tab_seismic = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tab_seismic)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        # Análisis Modal
        self._setup_modal_section(scroll_layout)
        
        # Selección de Combinaciones
        self._setup_combinations_section(scroll_layout)
        
        # Fuerzas cortantes
        self._setup_shear_section(scroll_layout)
        
        # Desplazamientos y derivas
        self._setup_displacement_section(scroll_layout)
        
        # Configurar scroll
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tabWidget.addTab(self.tab_seismic, "Análisis Sísmico")

    def _setup_modal_section(self, parent_layout):
        """Configurar sección de análisis modal"""
        self.group_modal = QtWidgets.QGroupBox("Análisis Modal")
        modal_layout = QtWidgets.QGridLayout(self.group_modal)
        
        self.label_modal_min = QtWidgets.QLabel("% Mínimo Masa Participativa:")
        self.le_modal = QtWidgets.QLineEdit("90")
        self.b_modal = QtWidgets.QPushButton("Ver Data")
        
        modal_layout.addWidget(self.label_modal_min, 0, 0)
        modal_layout.addWidget(self.le_modal, 0, 1)
        modal_layout.addWidget(self.b_modal, 0, 2)
        
        # Resultados modales
        self.label_tx = QtWidgets.QLabel("Periodo Tx:")
        self.le_tx = QtWidgets.QLineEdit()
        self.le_tx.setReadOnly(True)
        self.label_ty = QtWidgets.QLabel("Periodo Ty:")
        self.le_ty = QtWidgets.QLineEdit()
        self.le_ty.setReadOnly(True)
        
        modal_layout.addWidget(self.label_tx, 1, 0)
        modal_layout.addWidget(self.le_tx, 1, 1)
        modal_layout.addWidget(self.label_ty, 1, 2)
        modal_layout.addWidget(self.le_ty, 1, 3)
        
        parent_layout.addWidget(self.group_modal)

    def _setup_combinations_section(self, parent_layout):
        """Configurar sección de selección de combinaciones"""
        self.group_combinations = QtWidgets.QGroupBox("Selección de Combinaciones de Carga")
        comb_layout = QtWidgets.QGridLayout(self.group_combinations)
        
        # Combinaciones Dinámicas
        self.label_comb_dynamic = QtWidgets.QLabel("Combinaciones Dinámicas:")
        self.cb_comb_dynamic = QtWidgets.QComboBox()
        self.cb_comb_dynamic.setEditable(True)
        self.b_refresh_dynamic = QtWidgets.QPushButton("↻")
        self.b_refresh_dynamic.setMaximumWidth(30)
        self.b_refresh_dynamic.setToolTip("Actualizar combinaciones dinámicas")
        
        comb_layout.addWidget(self.label_comb_dynamic, 0, 0)
        comb_layout.addWidget(self.cb_comb_dynamic, 0, 1)
        comb_layout.addWidget(self.b_refresh_dynamic, 0, 2)
        
        # Combinaciones Estáticas
        self.label_comb_static = QtWidgets.QLabel("Combinaciones Estáticas:")
        self.cb_comb_static = QtWidgets.QComboBox()
        self.cb_comb_static.setEditable(True)
        self.b_refresh_static = QtWidgets.QPushButton("↻")
        self.b_refresh_static.setMaximumWidth(30)
        self.b_refresh_static.setToolTip("Actualizar combinaciones estáticas")
        
        comb_layout.addWidget(self.label_comb_static, 1, 0)
        comb_layout.addWidget(self.cb_comb_static, 1, 1)
        comb_layout.addWidget(self.b_refresh_static, 1, 2)
        
        # Combinaciones de Desplazamientos
        self.label_comb_displacement = QtWidgets.QLabel("Combinaciones Desplazamientos:")
        self.cb_comb_displacement = QtWidgets.QComboBox()
        self.cb_comb_displacement.setEditable(True)
        self.b_refresh_displacement = QtWidgets.QPushButton("↻")
        self.b_refresh_displacement.setMaximumWidth(30)
        self.b_refresh_displacement.setToolTip("Actualizar combinaciones desplazamientos")
        
        comb_layout.addWidget(self.label_comb_displacement, 2, 0)
        comb_layout.addWidget(self.cb_comb_displacement, 2, 1)
        comb_layout.addWidget(self.b_refresh_displacement, 2, 2)
        
        parent_layout.addWidget(self.group_combinations)

    def _setup_shear_section(self, parent_layout):
        """Configurar sección de fuerzas cortantes"""
        self.group_shear = QtWidgets.QGroupBox("Fuerzas Cortantes")
        shear_layout = QtWidgets.QGridLayout(self.group_shear)
        
        self.b_cortantes = QtWidgets.QPushButton("Calcular Cortantes")
        shear_layout.addWidget(self.b_cortantes, 0, 0, 1, 4)
        
        # Campos de cortantes
        self.label_vestx = QtWidgets.QLabel("Vestx:")
        self.le_vestx = QtWidgets.QLineEdit()
        self.le_vestx.setReadOnly(True)
        self.label_vesty = QtWidgets.QLabel("Vesty:")
        self.le_vesty = QtWidgets.QLineEdit()
        self.le_vesty.setReadOnly(True)
        
        shear_layout.addWidget(self.label_vestx, 1, 0)
        shear_layout.addWidget(self.le_vestx, 1, 1)
        shear_layout.addWidget(self.label_vesty, 1, 2)
        shear_layout.addWidget(self.le_vesty, 1, 3)
        
        parent_layout.addWidget(self.group_shear)

    def _setup_displacement_section(self, parent_layout):
        """Configurar sección de desplazamientos y derivas"""
        self.group_displacements = QtWidgets.QGroupBox("Desplazamientos y Derivas")
        displ_layout = QtWidgets.QGridLayout(self.group_displacements)
        
        self.b_desplazamiento = QtWidgets.QPushButton("Calcular Desplazamientos")
        self.b_derivas = QtWidgets.QPushButton("Calcular Derivas")
        
        displ_layout.addWidget(self.b_desplazamiento, 0, 0)
        displ_layout.addWidget(self.b_derivas, 0, 1)
        
        parent_layout.addWidget(self.group_displacements)

    def _setup_memory_tab(self):
        """Tab de memoria de cálculo"""
        self.tab_memory = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(self.tab_memory)
        
        # Scroll area
        scroll = QtWidgets.QScrollArea()
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QtWidgets.QVBoxLayout(scroll_widget)
        
        # Imágenes
        self._setup_images_section(scroll_layout)
        
        # Descripciones
        self._setup_descriptions_section(scroll_layout)
        
        # Configurar scroll
        scroll.setWidget(scroll_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        self.tabWidget.addTab(self.tab_memory, "Memoria")

    def _setup_images_section(self, parent_layout):
        """Configurar sección de imágenes"""
        self.group_images = QtWidgets.QGroupBox("Imágenes del Proyecto")
        images_layout = QtWidgets.QGridLayout(self.group_images)
        
        # Portada
        self.label_portada = QtWidgets.QLabel("Portada:")
        self.b_portada = QtWidgets.QPushButton("Cargar Imagen")
        images_layout.addWidget(self.label_portada, 0, 0)
        images_layout.addWidget(self.b_portada, 0, 1)
        
        # Planta
        self.label_planta = QtWidgets.QLabel("Planta Típica:")
        self.b_planta = QtWidgets.QPushButton("Cargar Imagen")
        images_layout.addWidget(self.label_planta, 0, 2)
        images_layout.addWidget(self.b_planta, 0, 3)
        
        # 3D
        self.label_3d = QtWidgets.QLabel("Captura 3D:")
        self.b_3D = QtWidgets.QPushButton("Cargar Imagen")
        images_layout.addWidget(self.label_3d, 1, 0)
        images_layout.addWidget(self.b_3D, 1, 1)
        
        # Deformadas
        self.label_defx = QtWidgets.QLabel("Deformada X:")
        self.b_defX = QtWidgets.QPushButton("Cargar Imagen")
        images_layout.addWidget(self.label_defx, 1, 2)
        images_layout.addWidget(self.b_defX, 1, 3)
        
        self.label_defy = QtWidgets.QLabel("Deformada Y:")
        self.b_defY = QtWidgets.QPushButton("Cargar Imagen")
        images_layout.addWidget(self.label_defy, 2, 0)
        images_layout.addWidget(self.b_defY, 2, 1)
        
        parent_layout.addWidget(self.group_images)

    def _setup_descriptions_section(self, parent_layout):
        """Configurar sección de descripciones"""
        self.group_descriptions = QtWidgets.QGroupBox("Descripciones")
        desc_layout = QtWidgets.QGridLayout(self.group_descriptions)
        
        # Descripción de estructura
        self.label_desc_estructura = QtWidgets.QLabel("Descripción de la Estructura:")
        self.b_descripcion = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_descripcion = QtWidgets.QLabel("Sin Descripción")
        
        desc_layout.addWidget(self.label_desc_estructura, 0, 0)
        desc_layout.addWidget(self.b_descripcion, 0, 1)
        desc_layout.addWidget(self.lb_descripcion, 0, 2)
        
        # Criterios de modelamiento
        self.label_modelamiento = QtWidgets.QLabel("Criterios de Modelamiento:")
        self.b_modelamiento = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_modelamiento = QtWidgets.QLabel("Sin Descripción")
        
        desc_layout.addWidget(self.label_modelamiento, 1, 0)
        desc_layout.addWidget(self.b_modelamiento, 1, 1)
        desc_layout.addWidget(self.lb_modelamiento, 1, 2)
        
        # Descripción de cargas
        self.label_cargas = QtWidgets.QLabel("Descripción de Cargas:")
        self.b_cargas = QtWidgets.QPushButton("Agregar Descripción")
        self.lb_cargas = QtWidgets.QLabel("Sin Descripción")
        
        desc_layout.addWidget(self.label_cargas, 2, 0)
        desc_layout.addWidget(self.b_cargas, 2, 1)
        desc_layout.addWidget(self.lb_cargas, 2, 2)
        
        parent_layout.addWidget(self.group_descriptions)

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