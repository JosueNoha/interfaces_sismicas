"""
Clase base mejorada para aplicaciones sísmicas - Centralizada y escalable
"""

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap, QIcon
from pathlib import Path
import os

from core.base.seismic_base import SeismicBase
from ui.widgets.seismic_params_widget import SeismicParamsWidget
from core.utils.etabs_utils import connect_to_etabs, get_modal_data, get_drift_data, get_displacement_data, get_story_forces

class AppBase(QMainWindow):
    """Clase base centralizada para aplicaciones de análisis sísmico"""
    
    def __init__(self, config, ui_class):
        """
        Inicializar aplicación base
        config: configuración específica del país
        ui_class: clase de interfaz generada (Ui_MainWindow)
        """
        super().__init__()
        
        self.config = config
        self.sismo = SeismicBase(config)
        
        # Configurar interfaz
        self.ui = ui_class()
        self.ui.setupUi(self)
        
        # Configurar título y ventana
        self.setWindowTitle(config.get('window_title', 'Análisis Sísmico'))
        self._setup_icon()
        
        # Widget de parámetros sísmicos dinámico
        self._setup_seismic_params_widget()
        
        # Diálogo de descripciones
        from shared.dialogs import DescriptionsDialog
        self.ui_descriptions = DescriptionsDialog()
        
        # Conectar señales comunes
        self._connect_common_signals()
        
        # Inicializar valores por defecto
        self._init_default_values()
        
        # Variables ETABS
        self.ETABSObject = None
        self.SapModel = None
        self.etabs_connected = False

    def _setup_icon(self):
        """Configurar icono de la aplicación"""
        icon_path = self.config.get('icon_path', 'shared_resources/yabar_logo.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _setup_seismic_params_widget(self):
        """Configurar widget de parámetros sísmicos específico del país"""
        if not hasattr(self.ui, 'seismic_params_layout'):
            return
            
        # Crear widget dinámico según configuración del país
        self.seismic_params_widget = SeismicParamsWidget(self.config, self)
        self.ui.seismic_params_layout.addWidget(self.seismic_params_widget)
        
        # Conectar cambios de parámetros
        self.seismic_params_widget.connect_param_changed(self._on_seismic_params_changed)
        
        # Aplicar valores por defecto del país
        defaults = self.config.get('parametros_defecto', {})
        seismic_defaults = {k: v for k, v in defaults.items() 
                           if k not in ['proyecto', 'ubicacion', 'autor', 'fecha']}
        if seismic_defaults:
            self.seismic_params_widget.set_parameters(seismic_defaults)

    def _connect_common_signals(self):
        """Conectar señales comunes entre aplicaciones"""
        # Botones de carga de imágenes
        self.ui.b_portada.clicked.connect(lambda: self.load_image('portada'))
        self.ui.b_planta.clicked.connect(lambda: self.load_image('planta'))
        self.ui.b_3D.clicked.connect(lambda: self.load_image('3d'))
        self.ui.b_defX.clicked.connect(lambda: self.load_image('defX'))
        self.ui.b_defY.clicked.connect(lambda: self.load_image('defY'))
        
        # Botones de descripciones
        self.ui.b_descripcion.clicked.connect(lambda: self.open_description_dialog('descripcion'))
        self.ui.b_modelamiento.clicked.connect(lambda: self.open_description_dialog('modelamiento'))
        self.ui.b_cargas.clicked.connect(lambda: self.open_description_dialog('cargas'))
        
        # Botones principales
        self.ui.b_actualizar.clicked.connect(self.update_seismic_data)
        self.ui.b_reporte.clicked.connect(self.generate_report)
        
        # ✅ IMPLEMENTACIÓN del eventListener b_modal
        if hasattr(self.ui, 'b_modal'):
            self.ui.b_modal.clicked.connect(self.show_modal_analysis)
        
        # Otros botones de análisis
        if hasattr(self.ui, 'b_cortantes'):
            self.ui.b_cortantes.clicked.connect(self.calculate_shear_forces)
        if hasattr(self.ui, 'b_desplazamiento'):
            self.ui.b_desplazamiento.clicked.connect(self.calculate_displacements)
        if hasattr(self.ui, 'b_derivas'):
            self.ui.b_derivas.clicked.connect(self.calculate_drifts)

    def _init_default_values(self):
        """Inicializar valores por defecto"""
        # Fecha actual
        current_date = QDate.currentDate()
        self.ui.le_fecha.setText(current_date.toString("dd/MM/yyyy"))
        
        # Datos del proyecto desde configuración
        defaults = self.config.get('parametros_defecto', {})
        project_fields = {
            'ubicacion': 'le_ubicacion',
            'autor': 'le_autor', 
            'proyecto': 'le_proyecto'
        }
        
        for key, ui_element in project_fields.items():
            if key in defaults and hasattr(self.ui, ui_element):
                getattr(self.ui, ui_element).setText(str(defaults[key]))

    def _on_seismic_params_changed(self):
        """Callback cuando cambian parámetros sísmicos"""
        if hasattr(self, 'seismic_params_widget'):
            params = self.seismic_params_widget.get_parameters()
            self._update_sismo_parameters(params)

    def _update_sismo_parameters(self, params):
        """Actualizar parámetros del modelo sísmico"""
        for key, value in params.items():
            setattr(self.sismo, key, value)

    # ===== MÉTODOS COMUNES DE INTERFAZ =====

    def connect_etabs(self):
        """Conectar con ETABS"""
        try:
            self.ETABSObject, self.SapModel = connect_to_etabs()
            
            if self.SapModel is not None:
                self.etabs_connected = True
                self.show_info("✅ Conectado a ETABS exitosamente")
                return True
            else:
                self.etabs_connected = False
                self.show_error("❌ No se pudo conectar a ETABS\nVerifique que ETABS esté abierto")
                return False
                
        except Exception as e:
            self.etabs_connected = False
            self.show_error(f"Error conectando a ETABS: {e}")
            return False

    def load_image(self, image_type: str):
        """Cargar imagen del tipo especificado"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar imagen para {image_type}",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif);;Todos los archivos (*)"
        )
        
        if file_path:
            # Guardar ruta en URLs de imágenes
            self.sismo.urls_imagenes[image_type] = file_path
            self.show_info(f"Imagen {image_type} cargada: {Path(file_path).name}")

    def open_description_dialog(self, desc_type: str):
        """Abrir diálogo de descripción"""
        titles = {
            'descripcion': 'Descripción de la Estructura',
            'modelamiento': 'Criterios de Modelamiento', 
            'cargas': 'Descripción de Cargas Consideradas'
        }
        
        self.ui_descriptions.set_description_type(desc_type, titles.get(desc_type))
        
        # Cargar descripción existente
        existing_desc = self.sismo.descriptions.get(desc_type, '')
        self.ui_descriptions.set_existing_text(existing_desc)
        
        # Mostrar diálogo
        if self.ui_descriptions.exec_() == self.ui_descriptions.Accepted:
            texto = self.ui_descriptions.get_description_text()
            
            # Actualizar label correspondiente
            label_mapping = {
                'descripcion': self.ui.lb_descripcion,
                'modelamiento': self.ui.lb_modelamiento,
                'cargas': self.ui.lb_cargas
            }
            
            label = label_mapping.get(desc_type)
            if label:
                label.setText('Descripción cargada' if texto else 'Sin Descripción')
            
            # Guardar en objeto sismo
            self.sismo.descriptions[desc_type] = texto

    def get_project_data(self):
        """Obtener datos del proyecto desde interfaz"""
        return {
            'proyecto': self.ui.le_proyecto.text(),
            'ubicacion': self.ui.le_ubicacion.text(),
            'autor': self.ui.le_autor.text(),
            'fecha': self.ui.le_fecha.text()
        }

    def update_seismic_data(self):
        """Actualizar datos del objeto sismo desde interfaz"""
        # Datos del proyecto
        project_data = self.get_project_data()
        for key, value in project_data.items():
            setattr(self.sismo, key, value)
        
        # Parámetros sísmicos
        if hasattr(self, 'seismic_params_widget'):
            seismic_params = self.seismic_params_widget.get_parameters()
            self._update_sismo_parameters(seismic_params)
        
        self.show_info("Datos actualizados correctamente")

    # ===== MÉTODOS DE ANÁLISIS (implementación básica) =====

    def show_modal_analysis(self):
        """Mostrar análisis modal"""
        if not self.etabs_connected:
            if not self.connect_etabs():
                return
        
        try:
            modal_data = get_modal_data(self.SapModel)
            if modal_data is not None and not modal_data.empty:
                # Almacenar en objeto sismo
                self.sismo.tables.modal = modal_data
                
                # Obtener períodos fundamentales
                mode_x = modal_data[modal_data.UX == max(modal_data.UX)].index[0]
                mode_y = modal_data[modal_data.UY == max(modal_data.UY)].index[0]
                Tx = modal_data['Period'][mode_x] if not modal_data.empty else 0
                Ty = modal_data['Period'][mode_y] if not modal_data.empty else 0
                
                # Actualizar interfaz
                if hasattr(self.ui, 'le_tx'):
                    self.ui.le_tx.setText(f"{Tx:.4f}")
                if hasattr(self.ui, 'le_ty'):
                    self.ui.le_ty.setText(f"{Ty:.4f}")
                
                # Almacenar en modelo
                self.sismo.data.Tx = Tx
                self.sismo.data.Ty = Ty
                
                # Mostrar resumen
                sum_ux = modal_data['SumUX'].max()
                sum_uy = modal_data['SumUY'].max()
                
                self.show_info(f"""✅ Análisis Modal Completado:

📊 PERÍODOS FUNDAMENTALES:
Tx = {Tx:.4f} s
Ty = {Ty:.4f} s

📈 MASA PARTICIPATIVA:
ΣUX = {sum_ux:.1f}%
ΣUY = {sum_uy:.1f}%

🔍 Modos analizados: {len(modal_data)}""")
                
            else:
                self.show_warning("No se encontraron datos modales\nVerifique que el análisis modal esté completo")
                
        except Exception as e:
            self.show_error(f"Error obteniendo datos modales: {e}")

    def calculate_shear_forces(self):
        """Calcular fuerzas cortantes"""
        if not self.etabs_connected:
            if not self.connect_etabs():
                return
        
        try:
            story_forces = get_story_forces(self.SapModel)
            
            if story_forces is not None and not story_forces.empty:
                # Obtener cortante basal (último piso)
                base_story = story_forces['Story'].iloc[-1]
                base_forces = story_forces[
                    (story_forces['Story'] == base_story) & 
                    (story_forces['Location'] == 'Bottom')
                ]
                
                if not base_forces.empty:
                    # Buscar casos sísmicos dinámicos
                    load_cases = self.config.get('load_cases', {})
                    dynamic_cases = load_cases.get('dinamico_x', []) + load_cases.get('dinamico_y', [])
                    
                    Vx = 0
                    Vy = 0
                    
                    for case in dynamic_cases:
                        case_data = base_forces[base_forces['OutputCase'].str.contains(case, na=False)]
                        if not case_data.empty:
                            if 'X' in case:
                                Vx = max(Vx, abs(case_data['VX'].iloc[0]) if 'VX' in case_data.columns else 0)
                            if 'Y' in case:
                                Vy = max(Vy, abs(case_data['VY'].iloc[0]) if 'VY' in case_data.columns else 0)
                    
                    # Actualizar interfaz
                    if hasattr(self.ui, 'le_vestx'):
                        self.ui.le_vestx.setText(f"{Vx:.2f}")
                    if hasattr(self.ui, 'le_vesty'):
                        self.ui.le_vesty.setText(f"{Vy:.2f}")
                    
                    # Almacenar en modelo
                    self.sismo.data.Vdx = Vx
                    self.sismo.data.Vdy = Vy
                    
                    self.show_info(f"""✅ Cortantes Calculados:

🔧 CORTANTE BASAL DINÁMICO:
Vx = {Vx:.2f} kN
Vy = {Vy:.2f} kN""")
                    
            else:
                self.show_warning("No se encontraron fuerzas de piso\nVerifique el análisis en ETABS")
                
        except Exception as e:
            self.show_error(f"Error calculando cortantes: {e}")

    def calculate_displacements(self):
        """Calcular desplazamientos"""
        if not self.etabs_connected:
            if not self.connect_etabs():
                return
        
        try:
            disp_data = get_displacement_data(self.SapModel)
            
            if disp_data is not None and not disp_data.empty:
                # Almacenar en objeto sismo
                self.sismo.tables.displacements = disp_data
                
                max_disp_x = disp_data['Maximum_x'].max()
                max_disp_y = disp_data['Maximum_y'].max()
                
                self.show_info(f"""✅ Desplazamientos Calculados:

📐 DESPLAZAMIENTOS MÁXIMOS:
X = {max_disp_x:.1f} mm
Y = {max_disp_y:.1f} mm

📋 Datos por piso: {len(disp_data)} niveles""")
            
            else:
                self.show_warning("No se encontraron datos de desplazamiento")
                
        except Exception as e:
            self.show_error(f"Error calculando desplazamientos: {e}")

    def calculate_drifts(self):
        """Calcular derivas"""
        if not self.etabs_connected:
            if not self.connect_etabs():
                return
        
        try:
            drift_data = get_drift_data(self.SapModel)
            
            if drift_data is not None and not drift_data.empty:
                # Almacenar en objeto sismo
                self.sismo.tables.drift_table = drift_data
                
                max_drift_x = drift_data['DriftX'].max() if 'DriftX' in drift_data.columns else 0
                max_drift_y = drift_data['DriftY'].max() if 'DriftY' in drift_data.columns else 0
                
                # Límite típico (7‰ para concreto)
                limit = 0.007
                cumple_x = "✓" if max_drift_x <= limit else "✗"
                cumple_y = "✓" if max_drift_y <= limit else "✗"
                
                self.show_info(f"""✅ Derivas Calculadas:

📊 DERIVAS MÁXIMAS:
X = {max_drift_x:.4f} {cumple_x} (límite: 0.007)
Y = {max_drift_y:.4f} {cumple_y} (límite: 0.007)

📋 Datos por piso: {len(drift_data)} niveles""")
                
            else:
                self.show_warning("No se encontraron datos de deriva")
                
        except Exception as e:
            self.show_error(f"Error calculando derivas: {e}")

    # ===== MÉTODOS DE UTILIDAD =====

    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Mostrar mensaje de información"""
        QMessageBox.information(self, "Información", message)

    def show_warning(self, message: str):
        """Mostrar mensaje de advertencia"""
        QMessageBox.warning(self, "Advertencia", message)

    def get_output_directory(self) -> str:
        """Seleccionar directorio de salida para reportes"""
        return QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de salida",
            str(Path.home() / "Documents")
        )

    def show_image(self, image_path: str, title: str = "Imagen"):
        """Mostrar imagen en ventana emergente"""
        if not os.path.exists(image_path):
            self.show_error(f"No se encontró la imagen: {image_path}")
            return
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        
        pixmap = QPixmap(image_path)
        if pixmap.width() > 800 or pixmap.height() > 600:
            pixmap = pixmap.scaled(800, 600, aspectRatioMode=1)
        
        dialog.setIconPixmap(pixmap)
        dialog.exec_()

    # ===== MÉTODOS VIRTUALES PARA CLASES DERIVADAS =====

    def generate_report(self):
        """Generar reporte - implementar en clases derivadas"""
        self.show_warning("Función de reporte debe implementarse en aplicación específica")

    def validate_country_params(self):
        """Validar parámetros específicos del país - implementar en clases derivadas"""
        pass