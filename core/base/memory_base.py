"""
Clase base para aplicaciones sísmicas - Funcionalidad común de interfaz
"""

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QPixmap

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
        
        # Diálogo de descripciones (común)
        from shared.dialogs import DescriptionsDialog
        self.ui_descriptions = DescriptionsDialog()
        
        # Conectar señales comunes
        self._connect_common_signals()
        
        # Inicializar valores por defecto
        self._init_default_values()

    def _connect_common_signals(self):
        """Conectar señales comunes entre aplicaciones"""
        # Botones de carga de imágenes
        self.ui.b_portada.clicked.connect(lambda: self.load_image('portada'))
        self.ui.b_planta.clicked.connect(lambda: self.load_image('planta'))
        self.ui.b_3D.clicked.connect(lambda: self.load_image('3d'))
        self.ui.b_defX.clicked.connect(lambda: self.load_image('defX'))
        self.ui.b_defY.clicked.connect(lambda: self.load_image('defY'))
        
        # Botones de descripciones
        self.ui.b_descripcion.clicked.connect(lambda: self.open_descriptions('descripcion'))
        self.ui.b_modelamiento.clicked.connect(lambda: self.open_descriptions('modelamiento'))
        self.ui.b_cargas.clicked.connect(lambda: self.open_descriptions('cargas'))
        
        # Conexión con ETABS
        self.ui.b_actualizar.clicked.connect(self.set_loads)
        
        # Botones de análisis
        self.ui.b_desplazamiento.clicked.connect(self.set_parameters)
        
        # Generación de reporte
        self.ui.b_reporte.clicked.connect(self.generate_report)
        
        # Diálogo descripciones
        self.ui_descriptions.accepted.connect(self.set_descriptions)

    def _init_default_values(self):
        """Inicializar valores por defecto de la interfaz"""
        # Fecha actual
        fecha_actual = QDate.currentDate().toString("dd/MM/yyyy")
        self.ui.le_fecha.setText(fecha_actual)
        
        # Valores por defecto del país
        defaults = self.config.get('parametros_defecto', {})
        
        if 'ubicacion' in defaults:
            self.ui.le_ubicacion.setText(defaults['ubicacion'])
            self.sismo.ubicacion = defaults['ubicacion']
            
        if 'autor' in defaults:
            self.ui.le_autor.setText(defaults['autor'])
            self.sismo.autor = defaults['autor']

        # Parámetros específicos del país (implementar en clases derivadas)
        self._init_country_defaults(defaults)

    def _init_country_defaults(self, defaults):
        """Inicializar parámetros por defecto específicos del país"""
        pass

    def load_image(self, image_type):
        """Cargar imagen desde archivo"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar imagen para {image_type}",
            "",
            "Archivos de imagen (*.png *.jpg *.jpeg *.gif *.bmp)"
        )
        
        if file_path:
            label_name = f'lb_{image_type}'
            if hasattr(self.ui, label_name):
                label = getattr(self.ui, label_name)
                
                pixmap = QPixmap(file_path)
                if not pixmap.isNull():
                    scaled_pixmap = pixmap.scaled(
                        label.size(), 
                        aspectRatioMode=1,
                        transformMode=1
                    )
                    label.setPixmap(scaled_pixmap)
                    label.setText("")
                    
                    self.sismo.set_imagen(image_type, file_path)
                else:
                    self.show_error("No se pudo cargar la imagen seleccionada")

    def open_descriptions(self, desc_type):
        """Abrir diálogo de descripciones"""
        default_text = self.sismo.get_descripcion(desc_type)
        
        self.ui_descriptions.ui.pt_description.setPlainText(default_text)
        self.ui_descriptions.show()
        self.ui_descriptions.name = desc_type

    def set_descriptions(self):
        """Establecer descripción desde diálogo"""
        if not hasattr(self.ui_descriptions, 'name') or not self.ui_descriptions.name:
            return
            
        desc_type = self.ui_descriptions.name
        texto = self.ui_descriptions.ui.pt_description.toPlainText()
        
        label_name = f'lb_{desc_type}'
        if hasattr(self.ui, label_name):
            label = getattr(self.ui, label_name)
            label.setText('Descripción cargada')
        
        self.sismo.set_descripcion(desc_type, texto)
        self.ui_descriptions.close()

    def set_loads(self):
        """Conectar con ETABS - implementar en clases derivadas"""
        pass

    def set_parameters(self):
        """Obtener parámetros del modelo - implementar en clases derivadas"""  
        pass

    def generate_report(self):
        """Generar reporte - implementar en clases derivadas"""
        pass

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

    def show_error(self, message):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message):
        """Mostrar mensaje de información"""
        QMessageBox.information(self, "Información", message)

    def get_output_directory(self):
        """Seleccionar directorio de salida para reportes"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de salida",
            "~/Documents"
        )
        return directory