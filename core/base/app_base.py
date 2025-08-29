"""
Clase base mejorada para aplicaciones sísmicas con manejo de combinaciones ETABS
"""

from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIcon
from pathlib import Path
import os

from core.base.seismic_base import SeismicBase
from core.utils.etabs_utils import connect_to_etabs, get_unique_cases


class AppBase(QMainWindow):
    """Clase base mejorada para aplicaciones sísmicas"""
    
    def __init__(self, config, ui_class):
        super().__init__()
        
        self.config = config
        self.sismo = SeismicBase(config)
        
        # Configurar interfaz
        self.ui = ui_class()
        self.ui.setupUi(self)
        
        # Conexión ETABS
        self.ETABSObject = None
        self.SapModel = None
        
        # Configurar funcionalidad común
        self._setup_icon()
        self._connect_common_signals()
        self._init_default_values()
        self._setup_combinations()

    def _setup_icon(self):
        """Configurar icono de la aplicación"""
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _connect_common_signals(self):
        """Conectar señales comunes"""
        # Botones de imágenes
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
        
        # Conectar botones de combinaciones
        self._connect_combination_signals()
        
        # Agregar botón para actualizar todas las combinaciones
        if hasattr(self.ui, 'seismic_params_layout'):
            from PyQt5.QtWidgets import QPushButton
            self.b_refresh_all = QPushButton("🔄 Actualizar Todas las Combinaciones")
            self.b_refresh_all.clicked.connect(self.refresh_all_combinations)
            layout = self.ui.seismic_params_layout
            current_row = layout.rowCount()
            layout.addWidget(self.b_refresh_all, current_row, 0, 1, 4)

    def _connect_combination_signals(self):
        """Conectar señales relacionadas con combinaciones"""
        from core.utils.etabs_utils import update_seismic_combinations
        self.ui.b_refresh_dynamic.clicked.connect(lambda _: update_seismic_combinations([self.ui.cb_comb_dynamic],self.SapModel))
        self.ui.b_refresh_static.clicked.connect(lambda _: update_seismic_combinations([self.ui.cb_comb_static],self.SapModel))
        self.ui.b_refresh_displacement.clicked.connect(lambda _: update_seismic_combinations([self.ui.cb_comb_displacement],self.SapModel))

    def _setup_combinations(self):
        """Configurar ComboBoxes de combinaciones con valores por defecto"""
        # Obtener casos por defecto del país
        load_cases = self.config.get('load_cases', {})
        
        # Configurar combinaciones dinámicas por defecto
        dynamic_cases = load_cases.get('dinamico_x', []) + load_cases.get('dinamico_y', [])
        for case in set(dynamic_cases):  # Usar set para eliminar duplicados
            self.ui.cb_comb_dynamic.addItem(case)
        
        # Configurar combinaciones estáticas por defecto
        static_cases = load_cases.get('estatico_x', []) + load_cases.get('estatico_y', [])
        for case in set(static_cases):
            self.ui.cb_comb_static.addItem(case)
        
        # Configurar combinaciones de desplazamiento (usar dinámicas por defecto)
        for case in set(dynamic_cases):
            self.ui.cb_comb_displacement.addItem(case)

    def _refresh_dynamic_combinations(self):
        """Actualizar combinaciones dinámicas desde ETABS"""
        if not self._connect_etabs():
            return
        
        from core.utils.etabs_utils import update_seismic_combinations
        
        success = update_seismic_combinations([self.ui.cb_comb_dynamic], self.SapModel)
        
        if success:
            count = self.ui.cb_comb_dynamic.count()
            self.show_info(f"Combinaciones dinámicas actualizadas: {count} elementos")
        else:
            self.show_error("Error actualizando combinaciones dinámicas desde ETABS")

    # def _refresh_static_combinations(self):
    #     """Actualizar combinaciones estáticas desde ETABS"""
    #     if not self._connect_etabs():
    #         return
        
    #     try:
    #         # Obtener todas las combinaciones
    #         _, load_combos, _ = self.SapModel.RespCombo.GetNameList()
    #         load_combos = [combo for combo in load_combos if combo[0] != '~' and 'Modal' not in combo]
            
    #         # Obtener casos sísmicos para filtrar
    #         _, load_cases, _ = self.SapModel.LoadCases.GetNameList()
    #         seism_cases = [case for case in load_cases if 
    #                       case[0] != '~' and 'Modal' not in case and
    #                       self.SapModel.LoadCases.GetTypeOAPI_1(case)[2] == 5]
            
    #         # Filtrar combinaciones no sísmicas (estáticas)
    #         static_combos = []
    #         for combo in load_combos:
    #             try:
    #                 unique_cases = set(get_unique_cases(self.SapModel, combo))
    #                 # Si no intersecta con casos sísmicos, es estática
    #                 if not unique_cases.intersection(set(seism_cases)):
    #                     static_combos.append(combo)
    #             except:
    #                 continue
            
    #         # Actualizar ComboBox
    #         current_selection = self.ui.cb_comb_static.currentText()
    #         self.ui.cb_comb_static.clear()
    #         self.ui.cb_comb_static.addItems(static_combos)
            
    #         # Restaurar selección si existe
    #         if current_selection in static_combos:
    #             self.ui.cb_comb_static.setCurrentText(current_selection)
            
    #         self.show_info(f"Combinaciones estáticas actualizadas: {len(static_combos)} elementos")
            
    #     except Exception as e:
    #         self.show_error(f"Error actualizando combinaciones estáticas: {e}")

    # def _refresh_displacement_combinations(self):
    #     """Actualizar combinaciones de desplazamiento desde ETABS"""
    #     if not self._connect_etabs():
    #         return
        
    #     from core.utils.etabs_utils import update_seismic_combinations
        
    #     success = update_seismic_combinations([self.ui.cb_comb_displacement], self.SapModel)
        
    #     if success:
    #         count = self.ui.cb_comb_displacement.count()
    #         self.show_info(f"Combinaciones de desplazamiento actualizadas: {count} elementos")
    #     else:
    #         self.show_error("Error actualizando combinaciones de desplazamiento")

    def refresh_all_combinations(self):
        """Actualizar todas las combinaciones de una vez"""
        if not self._connect_etabs():
            return
        
        from core.utils.etabs_utils import update_seismic_combinations
        
        try:
            # Actualizar dinámicas y desplazamientos (usan la misma lógica)
            seismic_combos = [self.ui.cb_comb_dynamic, self.ui.cb_comb_static, self.ui.cb_comb_displacement]
            success_seismic = update_seismic_combinations(seismic_combos, self.SapModel)
            
            if success_seismic:
                self.show_info("✅ Todas las combinaciones actualizadas desde ETABS")
            else:
                self.show_warning("⚠️ Actualización parcial - revise la conexión con ETABS")
                
        except Exception as e:
            self.show_error(f"Error actualizando combinaciones: {e}")

    def _connect_etabs(self) -> bool:
        """Conectar con ETABS si no está conectado"""
        if self.SapModel is None:
            self.ETABSObject, self.SapModel = connect_to_etabs()
            if self.SapModel is None:
                self.show_warning("No se pudo conectar con ETABS. Verifique que esté abierto.")
                return False
        return True

    def _init_default_values(self):
        """Inicializar valores por defecto"""
        # Configurar fecha actual
        current_date = QDate.currentDate()
        self.ui.le_fecha.setText(current_date.toString("dd/MM/yyyy"))
        
        # Aplicar valores por defecto del país
        defaults = self.config.get('parametros_defecto', {})
        if 'proyecto' in defaults:
            self.ui.le_proyecto.setText(defaults['proyecto'])
        if 'ubicacion' in defaults:
            self.ui.le_ubicacion.setText(defaults['ubicacion'])
        if 'autor' in defaults:
            self.ui.le_autor.setText(defaults['autor'])

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
            self.sismo.urls_imagenes[image_type] = file_path
            self.show_info(f"Imagen {image_type} cargada: {Path(file_path).name}")

    def open_description_dialog(self, desc_type: str):
        """Abrir diálogo de descripción"""
        from shared.dialogs.descriptions_dialog import get_description
        
        # Títulos según tipo
        titles = {
            'descripcion': 'Descripción de la Estructura',
            'modelamiento': 'Criterios de Modelamiento',
            'cargas': 'Descripción de Cargas Consideradas'
        }
        
        # Obtener descripción existente
        existing_desc = self.sismo.descriptions.get(desc_type, '')
        
        # Mostrar diálogo
        texto, accepted = get_description(
            parent=self,
            desc_type=desc_type,
            title=titles.get(desc_type),
            existing_text=existing_desc
        )
        
        if accepted:
            # Actualizar descripción en el modelo
            self.sismo.descriptions[desc_type] = texto
            
            # Actualizar label en interfaz
            label_mapping = {
                'descripcion': self.ui.lb_descripcion,
                'modelamiento': self.ui.lb_modelamiento,
                'cargas': self.ui.lb_cargas
            }
            
            label = label_mapping.get(desc_type)
            if label:
                if texto.strip():
                    label.setText('Descripción cargada')
                else:
                    label.setText('Sin Descripción')

    def get_project_data(self):
        """Obtener datos del proyecto desde interfaz"""
        return {
            'proyecto': self.ui.le_proyecto.text(),
            'ubicacion': self.ui.le_ubicacion.text(),
            'autor': self.ui.le_autor.text(),
            'fecha': self.ui.le_fecha.text()
        }

    def get_selected_combinations(self):
        """Obtener combinaciones seleccionadas"""
        return {
            'dynamic': self.ui.cb_comb_dynamic.currentText(),
            'static': self.ui.cb_comb_static.currentText(),
            'displacement': self.ui.cb_comb_displacement.currentText()
        }

    def update_sismo_data(self):
        """Actualizar datos del objeto sismo desde interfaz"""
        # Datos del proyecto
        project_data = self.get_project_data()
        for key, value in project_data.items():
            setattr(self.sismo, key, value)
        
        # Combinaciones seleccionadas
        combinations = self.get_selected_combinations()
        self.sismo.loads.selected_combinations = combinations

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

    # Métodos virtuales para ser implementados en clases derivadas
    def generate_report(self):
        """Generar reporte - implementar en clases derivadas"""
        self.show_warning("Función de reporte no implementada para esta aplicación")

    def calculate_shear_forces(self):
        """Calcular fuerzas cortantes - implementar en clases derivadas"""
        pass

    def calculate_displacements(self):
        """Calcular desplazamientos - implementar en clases derivadas"""
        pass

    def calculate_drifts(self):
        """Calcular derivas - implementar en clases derivadas"""
        pass