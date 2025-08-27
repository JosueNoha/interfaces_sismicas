"""
Clase base actualizada para aplicaciones sísmicas - Funcionalidad común de interfaz
"""

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap, QIcon
from pathlib import Path
import os

from core.base.seismic_base import SeismicBase


class AppBase(QMainWindow):
    """Clase base para aplicaciones de análisis sísmico"""
    
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
        
        # Configurar icono si está disponible
        self._setup_icon()
        
        # Diálogo de descripciones (común)
        from shared.dialogs import DescriptionsDialog
        self.ui_descriptions = DescriptionsDialog()
        
        # Conectar señales comunes
        self._connect_common_signals()
        
        # Inicializar valores por defecto
        self._init_default_values()

    def _setup_icon(self):
        """Configurar icono de la aplicación"""
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

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
        
        # Botón generar reporte
        self.ui.b_reporte.clicked.connect(self.generate_report)

    def _init_default_values(self):
        """Inicializar valores por defecto"""
        # Configurar fecha actual
        current_date = QDate.currentDate()
        self.ui.le_fecha.setText(current_date.toString("dd/MM/yyyy"))

    def load_image(self, image_type: str):
        """Cargar imagen del tipo especificado"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar imagen para {image_type}",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif);;Todos los archivos (*)"
        )
        
        if file_path:
            # Guardar ruta en el objeto sismo
            setattr(self.sismo, f'url_{image_type}', file_path)
            
            # Actualizar interfaz para mostrar que se cargó la imagen
            self.show_info(f"Imagen {image_type} cargada: {Path(file_path).name}")

    def open_description_dialog(self, desc_type: str):
        """Abrir diálogo de descripción"""
        # Configurar título según tipo
        titles = {
            'descripcion': 'Descripción de la Estructura',
            'modelamiento': 'Criterios de Modelamiento', 
            'cargas': 'Descripción de Cargas Consideradas'
        }
        
        self.ui_descriptions.label_description.setText(f"Ingrese {titles.get(desc_type, 'descripción')}:")
        
        # Cargar descripción existente si la hay
        existing_desc = getattr(self.sismo, f'desc_{desc_type}', '')
        self.ui_descriptions.ui.pt_description.setPlainText(existing_desc)
        
        # Mostrar diálogo
        if self.ui_descriptions.exec_() == self.ui_descriptions.accepted:
            # Obtener texto ingresado
            texto = self.ui_descriptions.ui.pt_description.toPlainText().strip()
            
            # Actualizar label correspondiente
            label_mapping = {
                'descripcion': self.ui.lb_descripcion,
                'modelamiento': self.ui.lb_modelamiento,
                'cargas': self.ui.lb_cargas
            }
            
            label = label_mapping.get(desc_type)
            if label:
                if texto:
                    label.setText('Descripción cargada')
                else:
                    label.setText('Sin Descripción')
            
            # Guardar en objeto sismo
            setattr(self.sismo, f'desc_{desc_type}', texto)

    def get_project_data(self):
        """Obtener datos del proyecto desde interfaz"""
        return {
            'proyecto': self.ui.le_proyecto.text(),
            'ubicacion': self.ui.le_ubicacion.text(),
            'autor': self.ui.le_autor.text(),
            'fecha': self.ui.le_fecha.text()
        }

    def update_sismo_data(self):
        """Actualizar datos del objeto sismo desde interfaz"""
        project_data = self.get_project_data()
        self.sismo.proyecto = project_data['proyecto']
        self.sismo.ubicacion = project_data['ubicacion']
        self.sismo.autor = project_data['autor']
        self.sismo.fecha = project_data['fecha']

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
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de salida",
            str(Path.home() / "Documents")
        )
        return directory

    def show_image(self, image_path: str, title: str = "Imagen"):
        """Mostrar imagen en ventana emergente"""
        if not os.path.exists(image_path):
            self.show_error(f"No se encontró la imagen: {image_path}")
            return
        
        dialog = QMessageBox(self)
        dialog.setWindowTitle(title)
        
        pixmap = QPixmap(image_path)
        # Escalar imagen si es muy grande
        if pixmap.width() > 800 or pixmap.height() > 600:
            pixmap = pixmap.scaled(800, 600, aspectRatioMode=1)  # Qt.KeepAspectRatio
        
        dialog.setIconPixmap(pixmap)
        dialog.exec_()

    # Métodos virtuales para ser implementados en clases derivadas
    def generate_report(self):
        """Generar reporte - implementar en clases derivadas"""
        self.show_warning("Función de reporte no implementada para esta aplicación")

    def set_loads(self):
        """Conectar con ETABS - implementar en clases derivadas"""
        pass

    def set_parameters(self):
        """Obtener parámetros del modelo - implementar en clases derivadas"""  
        pass