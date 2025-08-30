"""
Interfaz principal unificada con ComboBoxes de combinaciones
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from ui.widgets.units_widget import UnitsWidget

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
        
        # Widget de unidades de trabajo
        self.units_widget = UnitsWidget()
        layout.addWidget(self.units_widget)
        
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

        # Irregularidad torsional
        self._setup_torsion_section(scroll_layout)

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
        
        # Campo para porcentaje mínimo de masa participativa
        self.label_min_mass = QtWidgets.QLabel("% Masa Mín:")
        self.le_min_mass_participation = QtWidgets.QLineEdit("90.0")
        self.le_min_mass_participation.setMaximumWidth(60)
        self.le_min_mass_participation.setToolTip("Porcentaje mínimo de masa participativa acumulada")

        modal_layout.addWidget(self.label_min_mass, 1, 4)
        modal_layout.addWidget(self.le_min_mass_participation, 1, 5)

        # Etiquetas para masa participativa acumulada
        self.label_participacion_x = QtWidgets.QLabel("Masa X (%):")
        self.le_participacion_x = QtWidgets.QLineEdit()
        self.le_participacion_x.setReadOnly(True)

        self.label_participacion_y = QtWidgets.QLabel("Masa Y (%):")
        self.le_participacion_y = QtWidgets.QLineEdit()
        self.le_participacion_y.setReadOnly(True)

        modal_layout.addWidget(self.label_participacion_x, 2, 0)
        modal_layout.addWidget(self.le_participacion_x, 2, 1)
        modal_layout.addWidget(self.label_participacion_y, 2, 2)
        modal_layout.addWidget(self.le_participacion_y, 2, 3)
                
        parent_layout.addWidget(self.group_modal)

    def _setup_combinations_section(self, parent_layout):
        """Configurar sección de selección de combinaciones por dirección"""
        self.group_combinations = QtWidgets.QGroupBox("Selección de Combinaciones de Carga")
        comb_layout = QtWidgets.QGridLayout(self.group_combinations)
        
        # Combinaciones Dinámicas X
        self.label_comb_dynamic_x = QtWidgets.QLabel("Dinámicas X:")
        self.cb_comb_dynamic_x = QtWidgets.QComboBox()
        self.cb_comb_dynamic_x.setEditable(True)
        
        # Combinaciones Dinámicas Y  
        self.label_comb_dynamic_y = QtWidgets.QLabel("Dinámicas Y:")
        self.cb_comb_dynamic_y = QtWidgets.QComboBox()
        self.cb_comb_dynamic_y.setEditable(True)
        
        comb_layout.addWidget(self.label_comb_dynamic_x, 0, 0)
        comb_layout.addWidget(self.cb_comb_dynamic_x, 0, 1)
        comb_layout.addWidget(self.label_comb_dynamic_y, 0, 2)
        comb_layout.addWidget(self.cb_comb_dynamic_y, 0, 3)
        
        # Combinaciones Estáticas X
        self.label_comb_static_x = QtWidgets.QLabel("Estáticas X:")
        self.cb_comb_static_x = QtWidgets.QComboBox()
        self.cb_comb_static_x.setEditable(True)
        
        # Combinaciones Estáticas Y
        self.label_comb_static_y = QtWidgets.QLabel("Estáticas Y:")
        self.cb_comb_static_y = QtWidgets.QComboBox()
        self.cb_comb_static_y.setEditable(True)

        comb_layout.addWidget(self.label_comb_static_x, 1, 0)
        comb_layout.addWidget(self.cb_comb_static_x, 1, 1)
        comb_layout.addWidget(self.label_comb_static_y, 1, 2)
        comb_layout.addWidget(self.cb_comb_static_y, 1, 3)
        
        # Combinaciones de Desplazamientos X
        self.label_comb_displacement_x = QtWidgets.QLabel("Desplaz. X:")
        self.cb_comb_displacement_x = QtWidgets.QComboBox()
        self.cb_comb_displacement_x.setEditable(True)

        # Combinaciones de Desplazamientos Y
        self.label_comb_displacement_y = QtWidgets.QLabel("Desplaz. Y:")
        self.cb_comb_displacement_y = QtWidgets.QComboBox()
        self.cb_comb_displacement_y.setEditable(True)
        
        comb_layout.addWidget(self.label_comb_displacement_x, 2, 0)
        comb_layout.addWidget(self.cb_comb_displacement_x, 2, 1)
        comb_layout.addWidget(self.label_comb_displacement_y, 2, 2)
        comb_layout.addWidget(self.cb_comb_displacement_y, 2, 3) 
        
        # Botón refresh
        self.b_refresh_combinations = QtWidgets.QPushButton("🔄 Actualizar Combinaciones")
        self.b_refresh_combinations.setToolTip("Obtener combinaciones sísmicas desde ETABS")
        comb_layout.addWidget(self.b_refresh_combinations, 3, 0, 1, 4)
        
        parent_layout.addWidget(self.group_combinations)

    def _setup_shear_section(self, parent_layout):
        """Configurar sección de fuerzas cortantes organizadas por dirección"""
        self.group_shear = QtWidgets.QGroupBox("Fuerzas Cortantes")
        shear_layout = QtWidgets.QGridLayout(self.group_shear)
        
        # Botón calcular
        self.b_cortantes = QtWidgets.QPushButton("Calcular Cortantes")
        shear_layout.addWidget(self.b_cortantes, 0, 0, 1, 4)
        
        # Factor de escala - fila independiente
        self.label_scale_factor = QtWidgets.QLabel("Factor Escala Mín (%):")
        self.le_scale_factor = QtWidgets.QLineEdit("80.0")
        shear_layout.addWidget(self.label_scale_factor, 1, 1)
        shear_layout.addWidget(self.le_scale_factor, 1, 2)
        
        # Headers por dirección
        label_x = QtWidgets.QLabel("Dirección X")
        label_x.setAlignment(QtCore.Qt.AlignCenter)
        label_x.setStyleSheet("font-weight: bold;")
        label_y = QtWidgets.QLabel("Dirección Y")
        label_y.setAlignment(QtCore.Qt.AlignCenter) 
        label_y.setStyleSheet("font-weight: bold;")
        
        shear_layout.addWidget(label_x, 2, 1)
        shear_layout.addWidget(label_y, 2, 2)
        
        # Columna X - Dinámico, Estático, Factor
        self.label_vdx = QtWidgets.QLabel("V din:")
        self.le_vdx = QtWidgets.QLineEdit()
        self.le_vdx.setReadOnly(True)
        shear_layout.addWidget(self.label_vdx, 3, 0)
        shear_layout.addWidget(self.le_vdx, 3, 1)
        
        self.label_vsx = QtWidgets.QLabel("V est:")
        self.le_vsx = QtWidgets.QLineEdit()
        self.le_vsx.setReadOnly(True)
        shear_layout.addWidget(self.label_vsx, 4, 0)
        shear_layout.addWidget(self.le_vsx, 4, 1)
        
        self.label_fx = QtWidgets.QLabel("F.E.:")
        self.le_fx = QtWidgets.QLineEdit()
        self.le_fx.setReadOnly(True)
        shear_layout.addWidget(self.label_fx, 5, 0)
        shear_layout.addWidget(self.le_fx, 5, 1)
        
        # Columna Y - Dinámico, Estático, Factor  
        self.label_vdy = QtWidgets.QLabel("V din:")
        self.le_vdy = QtWidgets.QLineEdit()
        self.le_vdy.setReadOnly(True)
        shear_layout.addWidget(self.label_vdy, 3, 2)
        shear_layout.addWidget(self.le_vdy, 3, 3)
        
        self.label_vsy = QtWidgets.QLabel("V est:")
        self.le_vsy = QtWidgets.QLineEdit()
        self.le_vsy.setReadOnly(True)
        shear_layout.addWidget(self.label_vsy, 4, 2)
        shear_layout.addWidget(self.le_vsy, 4, 3)
        
        self.label_fy = QtWidgets.QLabel("F.E.:")
        self.le_fy = QtWidgets.QLineEdit()
        self.le_fy.setReadOnly(True)
        shear_layout.addWidget(self.label_fy, 5, 2)
        shear_layout.addWidget(self.le_fy, 5, 3)
        
        self.b_view_dynamic = QtWidgets.QPushButton("Ver Gráfico Dinámico")
        self.b_view_static = QtWidgets.QPushButton("Ver Gráfico Estático")

        shear_layout.addWidget(self.b_view_dynamic, 6, 1)
        shear_layout.addWidget(self.b_view_static, 6, 2)
        
        parent_layout.addWidget(self.group_shear)

    def _setup_displacement_section(self, parent_layout):
        """Configurar sección de desplazamientos y derivas"""
        self.group_displacements = QtWidgets.QGroupBox("Desplazamientos y Derivas")
        displ_layout = QtWidgets.QGridLayout(self.group_displacements)
        
        self.b_desplazamiento = QtWidgets.QPushButton("Calcular Desplazamientos")
        self.b_derivas = QtWidgets.QPushButton("Calcular Derivas")
        
        displ_layout.addWidget(self.b_desplazamiento, 0, 0)
        displ_layout.addWidget(self.b_derivas, 0, 1)
        
        # Agregar campo para límite de deriva máxima
        self.label_max_drift = QtWidgets.QLabel("Deriva Máxima:")
        self.le_max_drift = QtWidgets.QLineEdit("0.007")
        self.le_max_drift.setToolTip("Límite máximo de deriva (0.007 para concreto armado)")
        
        displ_layout.addWidget(self.label_max_drift, 1, 0)
        displ_layout.addWidget(self.le_max_drift, 1, 1)
        
        # AGREGAR: Campos de resultados de desplazamientos
        self.label_desp_max_x = QtWidgets.QLabel("Desp. máx X:")
        self.le_desp_max_x = QtWidgets.QLineEdit()
        self.le_desp_max_x.setReadOnly(True)
        self.le_desp_max_x.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

        self.label_desp_max_y = QtWidgets.QLabel("Desp. máx Y:")
        self.le_desp_max_y = QtWidgets.QLineEdit()
        self.le_desp_max_y.setReadOnly(True)
        self.le_desp_max_y.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

        displ_layout.addWidget(self.label_desp_max_x, 2, 0)
        displ_layout.addWidget(self.le_desp_max_x, 2, 1)
        displ_layout.addWidget(self.label_desp_max_y, 2, 2)
        displ_layout.addWidget(self.le_desp_max_y, 2, 3)
        
        # AGREGAR: Campos de resultados de derivas
        self.label_deriva_max_x = QtWidgets.QLabel("Deriva máx X:")
        self.le_deriva_max_x = QtWidgets.QLineEdit()
        self.le_deriva_max_x.setReadOnly(True)
        self.le_deriva_max_x.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

        self.label_deriva_max_y = QtWidgets.QLabel("Deriva máx Y:")
        self.le_deriva_max_y = QtWidgets.QLineEdit()
        self.le_deriva_max_y.setReadOnly(True)
        self.le_deriva_max_y.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")

        displ_layout.addWidget(self.label_deriva_max_x, 3, 0)
        displ_layout.addWidget(self.le_deriva_max_x, 3, 1)
        displ_layout.addWidget(self.label_deriva_max_y, 3, 2)
        displ_layout.addWidget(self.le_deriva_max_y, 3, 3)

        # AGREGAR: Campos para pisos donde ocurren las derivas máximas
        self.label_piso_deriva_x = QtWidgets.QLabel("Piso X:")
        self.le_piso_deriva_x = QtWidgets.QLineEdit()
        self.le_piso_deriva_x.setReadOnly(True)
        self.le_piso_deriva_x.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        self.le_piso_deriva_x.setMaximumWidth(80)

        self.label_piso_deriva_y = QtWidgets.QLabel("Piso Y:")
        self.le_piso_deriva_y = QtWidgets.QLineEdit()
        self.le_piso_deriva_y.setReadOnly(True)
        self.le_piso_deriva_y.setStyleSheet("QLineEdit { background-color: #f0f0f0; }")
        self.le_piso_deriva_y.setMaximumWidth(80)

        displ_layout.addWidget(self.label_piso_deriva_x, 4, 0)
        displ_layout.addWidget(self.le_piso_deriva_x, 4, 1)
        displ_layout.addWidget(self.label_piso_deriva_y, 4, 2)
        displ_layout.addWidget(self.le_piso_deriva_y, 4, 3)
        
        parent_layout.addWidget(self.group_displacements)

    def _setup_torsion_section(self, parent_layout):
        """Configurar sección de irregularidad torsional"""
        self.group_torsion = QtWidgets.QGroupBox("Irregularidad Torsional")
        torsion_layout = QtWidgets.QGridLayout(self.group_torsion)
        
        # Selector de combinación para torsión
        self.label_torsion_combo = QtWidgets.QLabel("Combinación:")
        self.cb_torsion_combo = QtWidgets.QComboBox()
        self.cb_torsion_combo.addItems(["Dinámicas", "Estáticas", "Desplazamientos"])
        self.cb_torsion_combo.setCurrentText("Dinámicas")
        
        torsion_layout.addWidget(self.label_torsion_combo, 0, 0)
        torsion_layout.addWidget(self.cb_torsion_combo, 0, 1)
        
        # Botón calcular torsión
        self.b_torsion = QtWidgets.QPushButton("Calcular Irregularidad Torsional")
        torsion_layout.addWidget(self.b_torsion, 0, 2)
        
        # Resultados torsión por dirección
        label_tor_x = QtWidgets.QLabel("Torsión X")
        label_tor_x.setAlignment(QtCore.Qt.AlignCenter)
        label_tor_x.setStyleSheet("font-weight: bold;")
        label_tor_y = QtWidgets.QLabel("Torsión Y")
        label_tor_y.setAlignment(QtCore.Qt.AlignCenter)
        label_tor_y.setStyleSheet("font-weight: bold;")
        
        torsion_layout.addWidget(label_tor_x, 1, 1)
        torsion_layout.addWidget(label_tor_y, 1, 2)
        
        # Campos de resultados
        self.label_delta_max_x = QtWidgets.QLabel("Δ máx:")
        self.le_delta_max_x = QtWidgets.QLineEdit()
        self.le_delta_max_x.setReadOnly(True)
        
        self.label_delta_prom_x = QtWidgets.QLabel("Δ prom:")
        self.le_delta_prom_x = QtWidgets.QLineEdit()
        self.le_delta_prom_x.setReadOnly(True)
        
        self.label_relacion_x = QtWidgets.QLabel("Relación:")
        self.le_relacion_x = QtWidgets.QLineEdit()
        self.le_relacion_x.setReadOnly(True)
        
        torsion_layout.addWidget(self.label_delta_max_x, 2, 0)
        torsion_layout.addWidget(self.le_delta_max_x, 2, 1)
        
        torsion_layout.addWidget(self.label_delta_prom_x, 3, 0)
        torsion_layout.addWidget(self.le_delta_prom_x, 3, 1)
        
        torsion_layout.addWidget(self.label_relacion_x, 4, 0)
        torsion_layout.addWidget(self.le_relacion_x, 4, 1)
        
        # Campos Y (misma estructura)
        self.le_delta_max_y = QtWidgets.QLineEdit()
        self.le_delta_max_y.setReadOnly(True)
        self.le_delta_prom_y = QtWidgets.QLineEdit()
        self.le_delta_prom_y.setReadOnly(True)
        self.le_relacion_y = QtWidgets.QLineEdit()
        self.le_relacion_y.setReadOnly(True)
        
        torsion_layout.addWidget(self.le_delta_max_y, 2, 2)
        torsion_layout.addWidget(self.le_delta_prom_y, 3, 2)
        torsion_layout.addWidget(self.le_relacion_y, 4, 2)

        # Botón ver tabla detallada
        self.b_torsion_table = QtWidgets.QPushButton("Ver Tabla Detallada")
        torsion_layout.addWidget(self.b_torsion_table, 0, 3)

        # Campo para límite configurable
        self.label_torsion_limit = QtWidgets.QLabel("Límite:")
        self.le_torsion_limit = QtWidgets.QLineEdit("1.30")
        self.le_torsion_limit.setMaximumWidth(60)
        self.le_torsion_limit.setToolTip("Límite para irregularidad torsional (1.30 normal, 1.50 extrema)")

        torsion_layout.addWidget(self.label_torsion_limit, 0, 4)
        torsion_layout.addWidget(self.le_torsion_limit, 0, 5)
        
        parent_layout.addWidget(self.group_torsion)

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