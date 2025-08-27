"""
Aplicación principal de análisis sísmico para Perú - E.030
"""

from PyQt5.QtWidgets import QMessageBox, QFileDialog
from PyQt5.QtCore import QDate
import os

from core.base.app_base import AppBase
from ui.generated.ui_peru import Ui_MainWindow
from apps.peru.config_peru import PERU_CONFIG
from apps.peru.seismic_peru import SeismicPeru
from apps.peru.memory_peru import generate_memory


class PeruSeismicApp(AppBase):
    """Aplicación de análisis sísmico específica para Perú"""
    
    def __init__(self):
        super().__init__(PERU_CONFIG, Ui_MainWindow)
        
        # Usar clase sísmica específica de Perú
        self.sismo = SeismicPeru(PERU_CONFIG)
        
        # Conectar señales específicas de Perú
        self._connect_peru_signals()
        
        # Inicializar valores específicos de Perú
        self._init_peru_values()

    def _connect_peru_signals(self):
        """Conectar señales específicas de la aplicación de Perú"""
        # Análisis sísmico
        self.ui.b_modal.clicked.connect(self.show_modal)
        self.ui.b_irregularidades.clicked.connect(self.show_irregularities)
        self.ui.b_torsion_x.clicked.connect(lambda: self.show_Itorsion('X'))
        self.ui.b_torsion_y.clicked.connect(lambda: self.show_Itorsion('Y'))
        self.ui.b_stiff_x.clicked.connect(lambda: self.show_pisoBlando('X'))
        self.ui.b_stiff_y.clicked.connect(lambda: self.show_pisoBlando('Y'))
        self.ui.b_masa.clicked.connect(self.show_Imasa)
        self.ui.b_shear_s.clicked.connect(lambda: self.show_shear('static'))
        self.ui.b_shear_d.clicked.connect(lambda: self.show_shear('dynamic'))
        self.ui.b_derivas.clicked.connect(self.show_drifts)
        self.ui.b_desplazamiento.clicked.connect(self.show_disp)
        
        # Parámetros sísmicos Perú
        self.ui.cb_zona.currentIndexChanged.connect(self.actualize_zona)
        self.ui.cb_zona.currentIndexChanged.connect(self.actualize_suelo)
        self.ui.cb_suelo.currentIndexChanged.connect(self.actualize_suelo)
        self.ui.cb_categoria.currentIndexChanged.connect(self.actualize_categoria)
        
        # Cambios en combo boxes
        self.ui.cbox_skx.currentIndexChanged.connect(self.show_stiffData)
        self.ui.cbox_sky.currentIndexChanged.connect(self.show_stiffData)
        self.ui.cbox_SDX.currentIndexChanged.connect(self.show_shearData)
        self.ui.cbox_SDY.currentIndexChanged.connect(self.show_shearData)
        self.ui.cbox_SX.currentIndexChanged.connect(self.show_shearData)
        self.ui.cbox_SY.currentIndexChanged.connect(self.show_shearData)
        self.ui.cbox_dX.currentIndexChanged.connect(self.show_dispData)
        self.ui.cbox_dY.currentIndexChanged.connect(self.show_dispData)
        
        # Eventos de entrada
        self.ui.le_p_min.editingFinished.connect(self.show_shearData)
        self.ui.le_max_drift.editingFinished.connect(self.show_dispData)

    def _init_peru_values(self):
        """Inicializar valores específicos de Perú"""
        # Zona sísmica por defecto
        self.ui.cb_zona.setCurrentIndex(1)  # Zona 2
        self.ui.cb_suelo.setCurrentIndex(1)  # S1
        self.ui.cb_categoria.setCurrentIndex(3)  # Categoría C
        
        # Actualizar parámetros sísmicos iniciales
        self.actualize_zona()
        self.actualize_suelo()
        self.actualize_categoria()

    def _init_country_defaults(self, defaults):
        """Inicializar parámetros por defecto específicos de Perú"""
        # Parámetros sísmicos E.030
        if 'Z' in defaults:
            self.sismo.Z = defaults['Z']
        if 'U' in defaults:
            self.sismo.U = defaults['U']
        if 'S' in defaults:
            self.sismo.S = defaults['S']
        if 'Tp' in defaults:
            self.sismo.Tp = defaults['Tp']
        if 'Tl' in defaults:
            self.sismo.Tl = defaults['Tl']

    # Métodos específicos de E.030
    def actualize_zona(self):
        """Actualizar parámetros según zona sísmica seleccionada"""
        zona_idx = self.ui.cb_zona.currentIndex()
        zonas = ['1', '2', '3', '4']
        
        if zona_idx < len(zonas):
            zona = zonas[zona_idx]
            zona_config = self.config['zonas_sismicas'][zona]
            
            # Actualizar factor Z
            self.sismo.Z = zona_config['Z']
            self.ui.le_Z.setText(f"{self.sismo.Z:.2f}")

    def actualize_suelo(self):
        """Actualizar parámetros según tipo de suelo seleccionado"""
        suelo_idx = self.ui.cb_suelo.currentIndex()
        zona_idx = self.ui.cb_zona.currentIndex()
        
        suelos = ['S0', 'S1', 'S2', 'S3']
        zonas = ['1', '2', '3', '4']
        
        if suelo_idx < len(suelos) and zona_idx < len(zonas):
            suelo = suelos[suelo_idx]
            zona = zonas[zona_idx]
            suelo_config = self.config['tipos_suelo'][suelo]
            
            # Actualizar factor S según zona
            s_key = f'S_zona_{zona}'
            if s_key in suelo_config:
                self.sismo.S = suelo_config[s_key]
                self.ui.le_S.setText(f"{self.sismo.S:.2f}")
            
            # Actualizar períodos Tp y Tl
            self.sismo.Tp = suelo_config['Tp']
            self.sismo.Tl = suelo_config['Tl']
            self.ui.le_Tp.setText(f"{self.sismo.Tp:.2f}")
            self.ui.le_Tl.setText(f"{self.sismo.Tl:.2f}")

    def actualize_categoria(self):
        """Actualizar factor de uso según categoría seleccionada"""
        cat_idx = self.ui.cb_categoria.currentIndex()
        categorias = ['A1', 'A2', 'B', 'C', 'D']
        
        if cat_idx < len(categorias):
            categoria = categorias[cat_idx]
            cat_config = self.config['categorias'][categoria]
            
            # Actualizar factor U
            self.sismo.U = cat_config['U']
            self.ui.le_U.setText(f"{self.sismo.U:.2f}")

    # Métodos de análisis sísmico (delegados a la clase SeismicPeru)
    def show_modal(self):
        """Mostrar análisis modal"""
        self.sismo.show_modal_analysis()

    def show_irregularities(self):
        """Mostrar análisis de irregularidades"""
        self.sismo.show_irregularity_analysis()

    def show_Itorsion(self, direction):
        """Mostrar irregularidad por torsión"""
        self.sismo.show_torsion_irregularity(direction)

    def show_pisoBlando(self, direction):
        """Mostrar irregularidad de piso blando"""
        self.sismo.show_soft_story(direction)

    def show_Imasa(self):
        """Mostrar irregularidad de masa"""
        self.sismo.show_mass_irregularity()

    def show_shear(self, analysis_type):
        """Mostrar fuerzas cortantes"""
        self.sismo.show_shear_forces(analysis_type)

    def show_drifts(self):
        """Mostrar derivas de entrepiso"""
        self.sismo.show_drift_analysis()

    def show_disp(self):
        """Mostrar desplazamientos laterales"""
        self.sismo.show_displacement_analysis()

    def show_shearData(self):
        """Mostrar datos de cortante"""
        self.sismo.update_shear_data()

    def show_dispData(self):
        """Mostrar datos de desplazamiento"""
        self.sismo.update_displacement_data()

    def show_stiffData(self):
        """Mostrar datos de rigidez"""
        self.sismo.update_stiffness_data()

    def generate_report(self):
        """Generar memoria de cálculo para Perú"""
        try:
            # Obtener directorio de salida
            output_dir = QFileDialog.getExistingDirectory(
                self, 
                "Seleccionar directorio de salida",
                os.path.expanduser("~")
            )
            
            if output_dir:
                # Actualizar datos del proyecto desde la interfaz
                self.sismo.proyecto = self.ui.le_proyecto.text()
                self.sismo.ubicacion = self.ui.le_ubicacion.text()
                self.sismo.autor = self.ui.le_autor.text()
                self.sismo.fecha = self.ui.le_fecha.text()
                
                # Generar memoria
                generate_memory(self.sismo, output_dir)
                
                # Mostrar mensaje de éxito
                msg = QMessageBox()
                msg.setWindowTitle("Éxito")
                msg.setText("Memoria generada correctamente")
                msg.setIcon(QMessageBox.Information)
                msg.exec_()
                
                # Abrir archivo PDF generado
                os.startfile(os.path.join(output_dir, "memoria.pdf"))
                
        except Exception as e:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText(f"No se pudo generar la memoria: {str(e)}")
            msg.setIcon(QMessageBox.Critical)
            msg.exec_()