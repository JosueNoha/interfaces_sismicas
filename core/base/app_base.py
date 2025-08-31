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
        
        # Actualizar combinaciones al inicio
        self._auto_refresh_combinations()

    def _setup_icon(self):
        """Configurar icono de la aplicación"""
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _connect_common_signals(self):
        """Conectar señales comunes"""
        # Botones de análisis sísmico
        self.ui.b_modal.clicked.connect(self.show_modal_table)
        self.ui.b_cortantes.clicked.connect(self.calculate_shear_forces)
        self.ui.b_desplazamiento.clicked.connect(self.calculate_displacements)
        self.ui.b_derivas.clicked.connect(self.calculate_drifts)
        self.ui.b_actualizar.clicked.connect(self.update_all_data)
        
        # Gráfico de cortantes
        self.ui.b_view_dynamic.clicked.connect(lambda: self._show_plot('dynamic'))
        self.ui.b_view_static.clicked.connect(lambda: self._show_plot('static'))
        
        # Validacion de deriva maxima
        self.ui.le_max_drift.textChanged.connect(self._validate_max_drift)

        # Botón irregularidad torsional
        self.ui.b_torsion.clicked.connect(self.calculate_torsion)
        self.ui.b_torsion_table.clicked.connect(self.show_torsion_table)
        self.ui.le_torsion_limit.textChanged.connect(self._validate_torsion_limit)
        
        # Validación de masa participativa mínima
        self.ui.le_min_mass_participation.textChanged.connect(self._validate_min_mass_participation)
        
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
        
        # Conectar widget de unidades
        if hasattr(self.ui, 'units_widget'):
            self.ui.units_widget.units_changed.connect(self._on_units_changed)
        

    def _connect_combination_signals(self):
        """Conectar señales relacionadas con combinaciones"""
        if hasattr(self.ui, 'b_refresh_combinations'):
            self.ui.b_refresh_combinations.clicked.connect(self.refresh_all_combinations)

    def _setup_combinations(self):
        """Configurar ComboBoxes por dirección con valores por defecto"""
        load_cases = self.config.get('load_cases', {})
        
        # Configurar dinámicas X/Y
        dynamic_x_cases = load_cases.get('dinamico_x', [])
        dynamic_y_cases = load_cases.get('dinamico_y', [])
        
        for case in dynamic_x_cases:
            self.ui.cb_comb_dynamic_x.addItem(case)
        for case in dynamic_y_cases:
            self.ui.cb_comb_dynamic_y.addItem(case)
        
        # Configurar estáticas X/Y
        static_x_cases = load_cases.get('estatico_x', [])
        static_y_cases = load_cases.get('estatico_y', [])
        
        for case in static_x_cases:
            self.ui.cb_comb_static_x.addItem(case)
        for case in static_y_cases:
            self.ui.cb_comb_static_y.addItem(case)
            
        # Configurar desplazamientos
        for case in dynamic_x_cases:
            self.ui.cb_comb_displacement_x.addItem(case)
        for case in dynamic_y_cases:
            self.ui.cb_comb_displacement_y.addItem(case)
            
    def _auto_refresh_combinations(self):
        """Actualizar combinaciones automáticamente al abrir la aplicación"""
        try:
            # Intentar conectar y actualizar
            if self._connect_etabs():
                combo_widgets = [
                    self.ui.cb_comb_dynamic_x, self.ui.cb_comb_dynamic_y,
                    self.ui.cb_comb_static_x, self.ui.cb_comb_static_y,
                    self.ui.cb_comb_displacement_x, self.ui.cb_comb_displacement_y
                ]
                
                from core.utils.etabs_utils import update_seismic_combinations
                success = update_seismic_combinations(combo_widgets, self.SapModel)
                
                if success:
                    print("✅ Combinaciones actualizadas automáticamente desde ETABS")
                    self._auto_select_combinations_by_pattern()
                else:
                    self._set_disconnected_message()
            else:
                self._set_disconnected_message()
                
        except Exception as e:
            print(f"Error en actualización automática: {e}")
            self._set_disconnected_message()

    def _set_disconnected_message(self):
        """Establecer mensaje de no conectado en todos los ComboBoxes"""
        disconnected_message = "No conectado a ETABS"
        
        combo_widgets = [
            self.ui.cb_comb_dynamic_x, self.ui.cb_comb_dynamic_y,
            self.ui.cb_comb_static_x, self.ui.cb_comb_static_y,
            self.ui.cb_comb_displacement_x, self.ui.cb_comb_displacement_y
        ]
    
        for combo in combo_widgets:
            if combo is not None:
                combo.clear()
                combo.addItem(disconnected_message)
                combo.setCurrentText(disconnected_message)

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

    def refresh_all_combinations(self):
        """Actualizar todas las combinaciones por dirección"""
        if not self._connect_etabs():
            return
        
        try:
            combo_widgets = [
                self.ui.cb_comb_dynamic_x, self.ui.cb_comb_dynamic_y,
                self.ui.cb_comb_static_x, self.ui.cb_comb_static_y,
                self.ui.cb_comb_displacement_x, self.ui.cb_comb_displacement_y
            ]
            
            from core.utils.etabs_utils import update_seismic_combinations
            success = update_seismic_combinations(combo_widgets, self.SapModel)
            
            if success:
                # Seleccionar automáticamente por patrones después de actualizar
                selections = self._auto_select_combinations_by_pattern()
                self.show_info(f"✅ Combinaciones actualizadas desde ETABS\n🎯 {selections} selecciones automáticas por patrón")
            else:
                self.show_warning("⚠️ Actualización parcial")
                self._set_disconnected_message()
                
        except Exception as e:
            self.show_error(f"Error: {e}")
            self._set_disconnected_message()
            
    def _auto_select_combinations_by_pattern(self):
        """Seleccionar automáticamente combinaciones que cumplan patrones comunes"""
        try:
            # Patrones base (sin X/Y, se añaden automáticamente)
            base_patterns = {
                'static': ['SE', 'SS', 'S', 'Estat', 'Estatico', 'Static'],
                'dynamic': ['SD', 'SDin', 'Dinamico', 'Dynamic', 'Modal', 'Sdin'],
                'displacement': ['Despl', 'Drift', 'Deriva', 'Displacement', 'Desp']
            }
            
            # Sufijos de dirección que se buscarán
            direction_suffixes = ['X', 'Y']
            
            combo_mapping = {
                ('static', 'X'): self.ui.cb_comb_static_x,
                ('static', 'Y'): self.ui.cb_comb_static_y, 
                ('dynamic', 'X'): self.ui.cb_comb_dynamic_x,
                ('dynamic', 'Y'): self.ui.cb_comb_dynamic_y,
                ('displacement', 'X'): self.ui.cb_comb_displacement_x,
                ('displacement', 'Y'): self.ui.cb_comb_displacement_y
            }
            
            selections_made = 0
            
            for (combo_type, direction), combo_widget in combo_mapping.items():
                if combo_widget is None:
                    continue
                    
                # Obtener todos los items del combo
                all_items = [combo_widget.itemText(i) for i in range(combo_widget.count())]
                
                # Buscar coincidencias con patrones base + dirección
                best_match = None
                best_score = 0  # Para priorizar mejores coincidencias
                
                for base_pattern in base_patterns[combo_type]:
                    for item in all_items:
                        if item == "No conectado a ETABS":
                            continue
                        
                        # Normalizar item (sin espacios, mayúsculas)
                        item_normalized = item.replace(' ', '').replace('-', '').replace('_', '').upper()
                        
                        # Crear patrones posibles con el patrón base + dirección
                        possible_patterns = [
                            f"{base_pattern}{direction}",           # SDX
                            f"{base_pattern} {direction}",          # SD X
                            f"{base_pattern}_{direction}",          # SD_X
                            f"{base_pattern}-{direction}",          # SD-X
                            f"{base_pattern}.{direction}",          # SD.X
                        ]
                        
                        # Buscar coincidencias
                        for pattern in possible_patterns:
                            pattern_normalized = pattern.replace(' ', '').replace('-', '').replace('_', '').replace('.', '').upper()
                            
                            # Coincidencia exacta (mayor prioridad)
                            if pattern_normalized == item_normalized:
                                best_match = item
                                best_score = 100
                                break
                            
                            # Coincidencia parcial (el patrón está contenido en el item)
                            elif pattern_normalized in item_normalized and best_score < 50:
                                best_match = item
                                best_score = 50
                            
                            # Coincidencia inversa (el item está contenido en el patrón extendido)
                            elif item_normalized in pattern_normalized and len(item_normalized) > 2 and best_score < 25:
                                best_match = item
                                best_score = 25
                        
                        # Si encontramos coincidencia exacta, no seguir buscando
                        if best_score == 100:
                            break
                    
                    # Si encontramos coincidencia exacta, no seguir buscando
                    if best_score == 100:
                        break
                
                # Seleccionar la mejor coincidencia encontrada
                if best_match:
                    combo_widget.setCurrentText(best_match)
                    selections_made += 1
                    print(f"✅ {combo_type} {direction}: {best_match} (score: {best_score})")
            
            if selections_made > 0:
                print(f"✅ {selections_made} combinaciones seleccionadas automáticamente por patrón inteligente")
            
            return selections_made
            
        except Exception as e:
            print(f"Error en selección automática por patrón: {e}")
            return 0

    def update_seismic_loads(self):
        """Configurar todas las cargas sísmicas centralizadamente"""
        combinations = self.get_selected_combinations()
        
        self.sismo.loads.seism_loads = {
            'SDX': combinations.get('dynamic_x', ''),
            'SDY': combinations.get('dynamic_y', ''),
            'SSX': combinations.get('static_x', ''),
            'SSY': combinations.get('static_y', ''),
            'dx': combinations.get('displacement_x', ''),
            'dy': combinations.get('displacement_y', '')
        }

    def _connect_etabs(self) -> bool:
        """Conectar con ETABS si no está conectado"""
        if self.SapModel is None:
            self.ETABSObject, self.SapModel = connect_to_etabs()
            if self.SapModel is None:
                # No mostrar warning en actualización automática
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
        if hasattr(self.ui, 'le_max_drift'):
            country = self.config.get('pais', '').lower()
            if country == 'bolivia':
                default_drift = 0.01  # CNBDS 2023
            elif country == 'peru':
                default_drift = 0.007  # E.030 concreto armado
            else:
                default_drift = 0.01  # Valor genérico
            
            self.ui.le_max_drift.setText(str(default_drift))
            self.sismo.max_drift = default_drift
    
    def _validate_max_drift(self):
        """Validar límite de deriva máxima"""
        try:
            drift_limit = float(self.ui.le_max_drift.text())
            if 0.001 <= drift_limit <= 0.020:
                self.ui.le_max_drift.setStyleSheet("")
                # Re-validar derivas existentes si hay datos
                if hasattr(self.sismo, 'drift_results'):
                    self.sismo.max_drift = drift_limit
                    self.sismo.drift_results['limit'] = drift_limit
                    self._update_drift_results()
            else:
                self.ui.le_max_drift.setStyleSheet("QLineEdit { border: 2px solid orange; }")
        except ValueError:
            self.ui.le_max_drift.setStyleSheet("QLineEdit { border: 2px solid red; }")

    def load_image(self, image_type: str):
        """Cargar imagen y conectarla con la memoria"""
        from PyQt5.QtWidgets import QFileDialog
        
        # Asegurar estructura
        if not hasattr(self.sismo, 'urls_imagenes'):
            self.sismo.urls_imagenes = {}
        
        # Seleccionar archivo
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar imagen",
            "",
            "Imágenes (*.png *.jpg *.jpeg *.bmp);;Todos (*.*)"
        )
        
        if file_path:
            self.sismo.urls_imagenes[image_type] = file_path
            print(f"✅ Imagen {image_type} cargada: {Path(file_path).name}")

    def open_description_dialog(self, desc_type: str):
        """Abrir diálogo de descripción con plantilla automática"""
        from shared.dialogs.descriptions_dialog import DescriptionsDialog
        
        # Asegurar estructura
        if not hasattr(self.sismo, 'descriptions'):
            self.sismo.descriptions = {}
        
        # Crear diálogo
        dialog = DescriptionsDialog(parent=self)
        
        # Configurar título según tipo
        titles = {
            'descripcion': 'Descripción de la Estructura',
            'modelamiento': 'Criterios de Modelamiento',
            'cargas': 'Descripción de Cargas'
        }
        
        # Configurar tipo ANTES de establecer texto
        dialog.set_description_type(desc_type, titles.get(desc_type))
        
        # Establecer texto existente (o plantilla si está vacío)
        existing_text = self.sismo.descriptions.get(desc_type, '')
        dialog.set_existing_text(existing_text)
        
        # Mostrar diálogo
        if dialog.exec_() == dialog.Accepted:
            description_text = dialog.get_description_text()
            self.sismo.descriptions[desc_type] = description_text
            
            # Actualizar UI
            self._update_description_ui(desc_type, description_text)
            print(f"✅ Descripción {desc_type} actualizada")
            
    def _update_description_ui(self, desc_type: str, description_text: str):
        """Actualizar elementos de UI relacionados con la descripción"""
        ui_mappings = {
            'descripcion': 'lb_descripcion',
            'modelamiento': 'lb_modelamiento',
            'cargas': 'lb_cargas'
        }
        
        label_name = ui_mappings.get(desc_type)
        if label_name and hasattr(self.ui, label_name):
            label = getattr(self.ui, label_name)
            
            if description_text.strip():
                preview = description_text[:50] + "..." if len(description_text) > 50 else description_text
                label.setText(f"✅ {preview}")
                label.setStyleSheet("color: green;")
                label.setToolTip(f"Descripción completa:\n{description_text}")
            else:
                label.setText("Sin Descripción")
                label.setStyleSheet("color: gray;")
                label.setToolTip("No hay descripción")

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
            'dynamic_x': self.ui.cb_comb_dynamic_x.currentText(),
            'dynamic_y': self.ui.cb_comb_dynamic_y.currentText(),
            'static_x': self.ui.cb_comb_static_x.currentText(),
            'static_y': self.ui.cb_comb_static_y.currentText(),
            'displacement_x': self.ui.cb_comb_displacement_x.currentText(),
            'displacement_y': self.ui.cb_comb_displacement_y.currentText()
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
        
        # Actualizar deriva máxima desde UI
        if hasattr(self.ui, 'le_max_drift'):
            try:
                max_drift_value = float(self.ui.le_max_drift.text())
                self.sismo.max_drift = max_drift_value
            except ValueError:
                # Si hay error, usar valor por defecto
                self.sismo.max_drift = 0.007
                self.ui.le_max_drift.setText("0.007")
                
    def _on_units_changed(self, units_dict):
        """Manejar cambio de unidades de trabajo"""
        # Actualizar unidades en el objeto sísmico
        self.sismo.set_units(units_dict)
        
        # Actualizar tooltips y labels de la interfaz
        self._update_interface_units(units_dict)
        
        # Regenerar gráficos existentes con nuevas unidades
        self._refresh_existing_plots()
        
    def _refresh_existing_plots(self):
        """Regenerar gráficos existentes con las nuevas unidades"""
        # Regenerar gráfico de desplazamientos si existe
        if hasattr(self.sismo, 'disp_x') and hasattr(self.sismo, 'disp_y') and hasattr(self.sismo, 'disp_h'):
            use_combo = getattr(self.sismo, '_used_displacement_combo', False)
            self.sismo.fig_displacements = self.sismo._create_displacement_figure(
                self.sismo.disp_x, self.sismo.disp_y, self.sismo.disp_h, use_combo
            )
        
        # Regenerar gráfico de derivas si existe  
        if hasattr(self.sismo, 'drift_x') and hasattr(self.sismo, 'drift_y') and hasattr(self.sismo, 'drift_h'):
            use_combo = getattr(self.sismo, '_used_drift_combo', False)
            self.sismo.fig_drifts = self.sismo._create_drift_figure(
                self.sismo.drift_x, self.sismo.drift_y, self.sismo.drift_h, use_combo
            )
        
        # Regenerar gráficos de cortantes si existen (con casos guardados)
        if hasattr(self.sismo, 'shear_dynamic') and not self.sismo.shear_dynamic.empty:
            # Usar casos guardados o combinaciones actuales
            sx = getattr(self.sismo, '_saved_sx_dynamic', [])
            sy = getattr(self.sismo, '_saved_sy_dynamic', [])
            if sx and sy:
                self.sismo.dynamic_shear_fig = self.sismo._create_shear_figure(
                    self.sismo.shear_dynamic, sx, sy, 'dynamic'
                )
        
        if hasattr(self.sismo, 'shear_static') and not self.sismo.shear_static.empty:
            # Usar casos guardados o combinaciones actuales
            sx = getattr(self.sismo, '_saved_sx_static', [])
            sy = getattr(self.sismo, '_saved_sy_static', [])
            if sx and sy:
                self.sismo.static_shear_fig = self.sismo._create_shear_figure(
                    self.sismo.shear_static, sx, sy, 'static'
                )
    
    def _update_interface_units(self, units_dict):
        """Actualizar las unidades mostradas en la interfaz"""
        u_f = units_dict.get('fuerzas', 'tonf')
        u_d = units_dict.get('desplazamientos', 'mm')
        
        # Actualizar títulos de grupos si existen
        if hasattr(self.ui, 'group_shear'):
            self.ui.group_shear.setTitle(f"Fuerzas Cortantes ({u_f})")
        if hasattr(self.ui, 'group_displacement'):
            self.ui.group_displacement.setTitle(f"Desplazamientos ({u_d}) y Derivas")
    
    def _force_generate_all_plots(self):
        """Forzar generación de todos los gráficos necesarios"""
        print("🔄 Generando todos los gráficos para memoria...")
        
        try:
            # 1. Forzar cálculo de derivas si no existen
            if not hasattr(self.sismo, 'fig_drifts') or self.sismo.fig_drifts is None:
                print("  📊 Generando gráfico de derivas...")
                self.calculate_drifts()
            
            # 2. Forzar cálculo de desplazamientos si no existen  
            if not hasattr(self.sismo, 'fig_displacements') or self.sismo.fig_displacements is None:
                print("  📈 Generando gráfico de desplazamientos...")
                self.get_displacements()
            
            # 3. Forzar cálculo de cortantes si no existen
            if (not hasattr(self.sismo, 'dynamic_shear_fig') or self.sismo.dynamic_shear_fig is None or
                not hasattr(self.sismo, 'static_shear_fig') or self.sismo.static_shear_fig is None):
                print("  ⚡ Generando gráficos de cortantes...")
                self.calculate_shear_forces()
            
            # 4. Generar espectro si no existe
            if not hasattr(self.sismo, 'fig_spectrum') or self.sismo.fig_spectrum is None:
                print("  📊 Generando gráfico del espectro...")
                if hasattr(self, 'plot_spectrum'):
                    self.plot_spectrum()
            
            print("✅ Todos los gráficos generados")
            
        except Exception as e:
            print(f"⚠️ Error generando gráficos: {e}")
    
    def get_current_units(self):
        """Obtener unidades actuales"""
        if hasattr(self.ui, 'units_widget'):
            return self.ui.units_widget.get_current_units()
        return {'alturas': 'm', 'desplazamientos': 'mm', 'fuerzas': 'tonf'}

    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Mostrar mensaje de información"""
        QMessageBox.information(self, "Información", message)

    def show_warning(self, message: str):
        """Mostrar mensaje de advertencia"""
        QMessageBox.warning(self, "Advertencia", message)

    def _show_plot(self, plot_type):
        """Mostrar gráfico en ventana emergente"""
        fig = getattr(self.sismo, f'{plot_type}_shear_fig', None)
        if fig:
            from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
            from PyQt5.QtWidgets import QDialog, QVBoxLayout
            
            dialog = QDialog(self)
            layout = QVBoxLayout(dialog)
            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            dialog.exec_()

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
        """Generar reporte de memoria - SIMPLIFICADO"""
        try:
            print("\n🚀 INICIANDO GENERACIÓN DE MEMORIA...")
            
            # Solo validar conexión ETABS
            if not self._connect_etabs():
                self.show_message("Error", "No se pudo conectar con ETABS", 'error')
                return
            
            # AGREGAR: Forzar generación de todos los gráficos
            self._force_generate_all_plots()
            
            # Generar memoria usando el generador del país
            print("📄 GENERANDO MEMORIA DE CÁLCULO...")
            
            # Crear directorio de salida
            output_dir = Path("memoria_output")
            output_dir.mkdir(exist_ok=True)
            
            # Usar generador específico del país
            memory_generator = self._create_memory_generator(output_dir)
            
            try:
                tex_file = memory_generator.generate_memory()
                
                self.show_message(
                    "Éxito",
                    f"Memoria generada exitosamente:\n{tex_file}",
                    'info'
                )
                
                # Abrir directorio de salida
                self._open_output_directory(output_dir)
                    
            except ValueError as ve:
                # Error de validación - mostrar mensaje específico
                self.show_message("Datos Incompletos", str(ve), 'warning')
                
            except Exception as e:
                # Error general
                self.show_message("Error", f"Error generando memoria: {e}", 'error')
                
        except Exception as e:
            self.show_message("Error", f"Error inesperado: {e}", 'error')

    def _open_output_directory(self, output_dir):
        """Abrir directorio de salida en el explorador"""
        try:
            import subprocess
            import platform
            
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{output_dir.absolute()}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', str(output_dir.absolute())])
            else:  # Linux
                subprocess.Popen(['xdg-open', str(output_dir.absolute())])
        except:
            pass  # Ignorar errores al abrir directorio

    def _auto_generate_modal(self) -> bool:
        """Generar análisis modal automáticamente"""
        try:
            # Usar método existente si está disponible
            if hasattr(self, 'get_modal_data'):
                self.get_modal_data()
                return True
            return False
        except Exception as e:
            print(f"Error generando modal: {e}")
            return False

    def _auto_generate_drifts(self) -> bool:
        """Generar análisis de derivas automáticamente"""
        try:
            if hasattr(self, 'calculate_drifts'):
                self.calculate_drifts()
                return True
            return False
        except Exception as e:
            print(f"Error generando derivas: {e}")
            return False

    def _auto_generate_displacements(self) -> bool:
        """Generar análisis de desplazamientos automáticamente"""
        try:
            if hasattr(self, 'get_displacements'):
                self.get_displacements()
                return True
            return False
        except Exception as e:
            print(f"Error generando desplazamientos: {e}")
            return False

    def _auto_generate_torsion(self) -> bool:
        """Generar análisis de irregularidad torsional automáticamente"""
        try:
            if hasattr(self, 'calculate_torsion'):
                self.calculate_torsion()
                return True
            elif hasattr(self, 'get_torsion_data'):
                self.get_torsion_data()
                return True
            return False
        except Exception as e:
            print(f"Error generando análisis torsional: {e}")
            return False

    def _auto_generate_spectrum(self) -> bool:
        """Generar espectro de respuesta automáticamente"""
        try:
            # Generar espectro usando parámetros sísmicos actuales
            if hasattr(self.sismo, 'generate_spectrum_plot'):
                self.sismo.generate_spectrum_plot()
                return True
            elif hasattr(self, 'plot_spectrum'):
                self.plot_spectrum()
                return True
            return False
        except Exception as e:
            print(f"Error generando espectro: {e}")
            return False

    def _create_memory_generator(self, output_dir):
        """Crear generador de memoria específico del país"""
        country = self.config.get('country', '').lower()
        
        if country == 'bolivia':
            from apps.bolivia.memory import BoliviaMemoryGenerator
            return BoliviaMemoryGenerator(self.sismo, output_dir)
        elif country == 'peru':
            from apps.peru.memory import PeruMemoryGenerator
            return PeruMemoryGenerator(self.sismo, output_dir)
        else:
            raise ValueError(f"País no soportado: {country}")

    def show_message(self, title: str, message: str, msg_type: str = 'info'):
        """Mostrar mensaje al usuario"""
        from PyQt5.QtWidgets import QMessageBox
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        
        if msg_type == 'error':
            msg_box.setIcon(QMessageBox.Critical)
        elif msg_type == 'warning':
            msg_box.setIcon(QMessageBox.Warning)
        else:
            msg_box.setIcon(QMessageBox.Information)
        
        msg_box.exec_()

    def ensure_required_data_structure(self):
        """Asegurar que exista la estructura de datos necesaria"""
        # Inicializar estructura de datos si no existe
        if not hasattr(self.sismo, 'data'):
            from types import SimpleNamespace
            self.sismo.data = SimpleNamespace()
        
        # Inicializar listas de datos si no existen
        if not hasattr(self.sismo.data, 'modal_data'):
            self.sismo.data.modal_data = []
        
        if not hasattr(self.sismo.data, 'torsion_data'):
            self.sismo.data.torsion_data = []
        
        # Inicializar URLs de imágenes si no existe
        if not hasattr(self.sismo, 'urls_imagenes'):
            self.sismo.urls_imagenes = {
                'portada': '',
                'planta': '',
                '3d': '',
                'defX': '',
                'defY': ''
            }
            
    def calculate_shear_forces(self):
        """Calcular cortantes y factores de escala"""
        if not self._connect_etabs():
            return
        
        try:
            self.update_seismic_loads()
            combinations = self.get_selected_combinations()
            required = ['dynamic_x', 'dynamic_y', 'static_x', 'static_y']
            missing = [k for k in required if not combinations[k].strip()]
            
            if missing:
                self.show_warning(f"Faltan combinaciones: {', '.join(missing)}")
                return
            
            # Configurar cargas sísmicas
            self.sismo.loads.seism_loads = {
                'SDX': combinations['dynamic_x'],
                'SDY': combinations['dynamic_y'], 
                'SSX': combinations['static_x'],
                'SSY': combinations['static_y']
            }
            
            # Calcular cortantes
            success_dyn, success_sta = self.sismo.calculate_shear_forces(self.SapModel)
            
            if success_dyn and success_sta:
                # Obtener cortantes basales
                base_values = self._extract_base_shears()
                
                if base_values:
                    # Actualizar UI
                    self.ui.le_vdx.setText(f"{base_values['vdx']:.2f}")
                    self.ui.le_vdy.setText(f"{base_values['vdy']:.2f}")
                    self.ui.le_vsx.setText(f"{base_values['vsx']:.2f}")
                    self.ui.le_vsy.setText(f"{base_values['vsy']:.2f}")
                    
                    # Calcular factores de escala
                    scale_factors = self._calculate_scale_factors(base_values)
                    self.ui.le_fx.setText(f"{scale_factors['fx']:.3f}")
                    self.ui.le_fy.setText(f"{scale_factors['fy']:.3f}")
                    
                    # Almacenar en modelo
                    self.sismo.data.Vdx = base_values['vdx']
                    self.sismo.data.Vdy = base_values['vdy']
                    self.sismo.data.Vsx = base_values['vsx']
                    self.sismo.data.Vsy = base_values['vsy']
                    self.sismo.data.FEx = scale_factors['fx']
                    self.sismo.data.FEy = scale_factors['fy']
                    
                    self.show_info("✅ Cortantes, factores y gráficos generados")
                else:
                    self.show_error("Error extrayendo cortantes basales")
            else:
                self.show_error("Error calculando cortantes")
                
        except Exception as e:
            self.show_error(f"Error: {e}")
            
    def _extract_base_shears(self):
        """Extraer cortantes basales de los datos calculados"""
        try:
            # Obtener primer piso (base) de cada análisis
            dyn_base = self.sismo.shear_dynamic[
                self.sismo.shear_dynamic['Location'] == 'Bottom'
            ].copy()
            sta_base = self.sismo.shear_static[
                self.sismo.shear_static['Location'] == 'Bottom'  
            ].copy()
            
            # Extraer valores por dirección
            vdx = dyn_base[dyn_base['Direction'] == 'X']['V'].iloc[0] if len(dyn_base[dyn_base['Direction'] == 'X']) > 0 else 0
            vdy = dyn_base[dyn_base['Direction'] == 'Y']['V'].iloc[0] if len(dyn_base[dyn_base['Direction'] == 'Y']) > 0 else 0
            vsx = sta_base[sta_base['Direction'] == 'X']['V'].iloc[0] if len(sta_base[sta_base['Direction'] == 'X']) > 0 else 0
            vsy = sta_base[sta_base['Direction'] == 'Y']['V'].iloc[0] if len(sta_base[sta_base['Direction'] == 'Y']) > 0 else 0
            
            return {'vdx': vdx, 'vdy': vdy, 'vsx': vsx, 'vsy': vsy}
        except:
            return None

    def _calculate_scale_factors(self, base_values):
        """Calcular factores de escala basados en porcentaje mínimo"""
        try:
            min_percent = float(self.ui.le_scale_factor.text()) / 100.0
            
            # Calcular factores (dinámico debe ser >= min_percent * estático)
            fx = max(1.0, (min_percent * base_values['vsx']) / base_values['vdx']) if base_values['vdx'] > 0 else 1.0
            fy = max(1.0, (min_percent * base_values['vsy']) / base_values['vdy']) if base_values['vdy'] > 0 else 1.0
            
            return {'fx': fx, 'fy': fy}
        except:
            return {'fx': 1.0, 'fy': 1.0}

    def calculate_displacements(self):
        """Calcular desplazamientos laterales"""
        if not self._connect_etabs():
            return
            
        try:
            self.update_seismic_loads()
            combinations = self.get_selected_combinations()
            
            # Decidir si usar combinación de desplazamientos o dinámico directo
            use_combo = bool(combinations['displacement_x'] and combinations['displacement_y'])
            
            # Configurar cargas
            if use_combo:
                self.sismo.loads.seism_loads['dx'] = combinations['displacement_x']
                self.sismo.loads.seism_loads['dy'] = combinations['displacement_y']
            else:  
                self.sismo.loads.seism_loads['SDX'] = combinations['dynamic_x']
                self.sismo.loads.seism_loads['SDY'] = combinations['dynamic_y']
            
            success = self.sismo.calculate_displacements(self.SapModel, use_combo)
            
            if success:
                # Actualizar campos de resultados
                self._update_displacement_results()
                self.show_info("✅ Desplazamientos calculados exitosamente")
                self._show_displacements_plot()
            else:
                self.show_error("Error calculando desplazamientos")
                
        except Exception as e:
            self.show_error(f"Error: {e}")
            
    def _update_displacement_results(self):
        """Actualizar campos de resultados de desplazamientos"""
        try:
            if hasattr(self.sismo, 'displacement_results'):
                results = self.sismo.displacement_results
                
                max_x = results.get('max_displacement_x', 0.0)
                max_y = results.get('max_displacement_y', 0.0)
                
                # Actualizar campos
                self.ui.le_desp_max_x.setText(f"{max_x:.3f} mm")
                self.ui.le_desp_max_y.setText(f"{max_y:.3f} mm")
                
                print(f"Debug - Desplazamientos: X={max_x:.3f} mm, Y={max_y:.3f} mm")  # DEBUG
                
            else:
                print("Debug - No hay displacement_results disponibles")  # DEBUG
                self.ui.le_desp_max_x.setText("N/A")
                self.ui.le_desp_max_y.setText("N/A")
                
        except Exception as e:
            print(f"Error actualizando resultados de desplazamientos: {e}")

    def _validate_displacement_results(self, max_x: float, max_y: float):
        """Validar desplazamientos contra límites (si aplica)"""
        # Por ahora solo mostrar, se puede agregar validación específica después
        pass
            
    def _show_displacements_plot(self):
        """Mostrar gráfico de desplazamientos internamente"""
        if hasattr(self.sismo, 'fig_displacements') and self.sismo.fig_displacements is not None:
            try:
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout
                
                # Crear diálogo
                dialog = QDialog(self)
                dialog.setWindowTitle("Desplazamientos Laterales")
                dialog.setMinimumSize(800, 600)
                dialog.setModal(True)
                
                layout = QVBoxLayout(dialog)
                
                # Canvas
                canvas = FigureCanvasQTAgg(self.sismo.fig_displacements)
                layout.addWidget(canvas)
                
                # Botón cerrar
                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_close = QPushButton("Cerrar")
                btn_close.clicked.connect(dialog.accept)
                btn_layout.addWidget(btn_close)
                layout.addLayout(btn_layout)
                
                dialog.exec_()
                
            except Exception as e:
                print(f"Error mostrando gráfico: {e}")

    def calculate_drifts(self):
        """Calcular derivas"""
        if not self._connect_etabs():
            return
            
        try:
            self.update_seismic_loads()
            # Usar combinación de desplazamientos si está seleccionada
            combinations = self.get_selected_combinations()
            
            # Usar combo directo si ambas direcciones están configuradas
            use_combo = bool(combinations['displacement_x'] and combinations['displacement_y'])
            
            # Configurar cargas
            if use_combo:
                self.sismo.loads.seism_loads['dx'] = combinations['displacement_x']
                self.sismo.loads.seism_loads['dy'] = combinations['displacement_y']
            else:  
                self.sismo.loads.seism_loads['SDX'] = combinations['dynamic_x']
                self.sismo.loads.seism_loads['SDY'] = combinations['dynamic_y']
            
            # Obtener límite de deriva
            max_drift_limit = self._get_max_drift_limit()
            self.sismo.max_drift = max_drift_limit
            
            success = self.sismo.calculate_drifts(self.SapModel, use_combo)
            
            if success:
                # Actualizar campos de resultados
                self._update_drift_results()
                
                # Verificar cumplimiento y mostrar mensaje apropiado
                drift_results = getattr(self.sismo, 'drift_results', {})
                complies = drift_results.get('complies_overall', True)
                
                if complies:
                    self.show_info("✅ Derivas calculadas - CUMPLE límites")
                else:
                    self.show_warning("⚠️ Derivas calculadas - EXCEDE límites")
                    
                self._show_drifts_plot()
            else:
                self.show_error("Error calculando derivas")
                
        except Exception as e:
            self.show_error(f"Error: {e}")
    
    def _get_max_drift_limit(self) -> float:
        """Obtener límite máximo de deriva validado"""
        try:
            limit = float(self.ui.le_max_drift.text())
            if 0.001 <= limit <= 0.020:
                self.ui.le_max_drift.setStyleSheet("")
                return limit
            else:
                self.ui.le_max_drift.setStyleSheet("QLineEdit { border: 2px solid orange; }")
                return 0.007  # Valor por defecto
        except ValueError:
            self.ui.le_max_drift.setStyleSheet("QLineEdit { border: 2px solid red; }")
            return 0.007
            
    def _update_drift_results(self):
        """Actualizar campos de resultados de derivas"""
        try:
            if hasattr(self.sismo, 'drift_results'):
                results = self.sismo.drift_results
                
                max_x = results.get('max_drift_x', 0.0)
                max_y = results.get('max_drift_y', 0.0)
                story_x = results.get('story_max_x', 'N/A')
                story_y = results.get('story_max_y', 'N/A')
                limit = results.get('limit', 0.007)
                
                # Actualizar campos
                self.ui.le_deriva_max_x.setText(f"{max_x:.4f}")
                self.ui.le_deriva_max_y.setText(f"{max_y:.4f}")
                self.ui.le_piso_deriva_x.setText(str(story_x))
                self.ui.le_piso_deriva_y.setText(str(story_y))
                
                # Aplicar validación visual
                complies_x = max_x <= limit
                complies_y = max_y <= limit
                
                self._apply_drift_validation(complies_x, complies_y)
                
        except Exception as e:
            print(f"Error actualizando resultados de derivas: {e}")

    def _apply_drift_validation(self, complies_x: bool, complies_y: bool):
        """Aplicar validación visual para derivas"""
        # Validar dirección X
        if complies_x:
            self.ui.le_deriva_max_x.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
            self.ui.le_piso_deriva_x.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
        else:
            self.ui.le_deriva_max_x.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
            self.ui.le_piso_deriva_x.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
        
        # Validar dirección Y
        if complies_y:
            self.ui.le_deriva_max_y.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
            self.ui.le_piso_deriva_y.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
        else:
            self.ui.le_deriva_max_y.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
            self.ui.le_piso_deriva_y.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
            
    def _show_drifts_plot(self):
        """Mostrar gráfico de desplazamientos internamente"""
        if hasattr(self.sismo, 'fig_drifts') and self.sismo.fig_drifts is not None:
            try:
                from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
                from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QHBoxLayout
                
                # Crear diálogo
                dialog = QDialog(self)
                dialog.setWindowTitle("Desplazamientos Relativos Laterales")
                dialog.setMinimumSize(800, 600)
                dialog.setModal(True)
                
                layout = QVBoxLayout(dialog)
                
                # Canvas
                canvas = FigureCanvasQTAgg(self.sismo.fig_drifts)
                layout.addWidget(canvas)
                
                # Botón cerrar
                btn_layout = QHBoxLayout()
                btn_layout.addStretch()
                btn_close = QPushButton("Cerrar")
                btn_close.clicked.connect(dialog.accept)
                btn_layout.addWidget(btn_close)
                layout.addLayout(btn_layout)
                
                dialog.exec_()
                
            except Exception as e:
                print(f"Error mostrando gráfico: {e}")

    def show_modal_data(self):
        """Mostrar análisis modal con validación de masa mínima"""
        if not self._connect_etabs():
            return
        
        from core.utils.etabs_utils import get_modal_data, process_modal_data
        
        modal_data = get_modal_data(self.SapModel)
        if modal_data is not None:
            results = process_modal_data(modal_data)
            if results:
                # Actualizar campos de período
                self.ui.le_tx.setText(f"{results['Tx']:.4f}" if results['Tx'] else "N/A")
                self.ui.le_ty.setText(f"{results['Ty']:.4f}" if results['Ty'] else "N/A")
                
                # Actualizar campos de masa participativa acumulada
                self.ui.le_participacion_x.setText(f"{results['total_mass_x']:.1f}")
                self.ui.le_participacion_y.setText(f"{results['total_mass_y']:.1f}")
                
                # Obtener porcentaje mínimo requerido y validar
                min_mass = self._get_min_mass_participation()
                
                # Validar cumplimiento
                cumple_x = results['total_mass_x'] >= min_mass
                cumple_y = results['total_mass_y'] >= min_mass
                
                # Aplicar validación visual con colores
                self._apply_mass_validation(cumple_x, cumple_y)
                
                # Mostrar información completa
                info = f"✅ ANÁLISIS MODAL:\n\n"
                info += f"📊 PERÍODOS FUNDAMENTALES:\n"
                info += f"   Tx = {results['Tx']:.4f} s\n" if results['Tx'] else "   Tx = N/A\n"
                info += f"   Ty = {results['Ty']:.4f} s\n\n" if results['Ty'] else "   Ty = N/A\n\n"
                
                info += f"🎯 MASA PARTICIPATIVA ACUMULADA:\n"
                info += f"   {'✅' if cumple_x else '❌'} Dirección X: {results['total_mass_x']:.1f}% (mín: {min_mass}%)\n"
                info += f"   {'✅' if cumple_y else '❌'} Dirección Y: {results['total_mass_y']:.1f}% (mín: {min_mass}%)\n\n"
                
                info += f"📈 RESUMEN:\n"
                info += f"   Modos analizados: {results['num_modes']}\n"
                
                # Estado general
                overall_status = "CUMPLE" if (cumple_x and cumple_y) else "NO CUMPLE"
                color = "🟢" if (cumple_x and cumple_y) else "🔴"
                info += f"   {color} VALIDACIÓN: {overall_status}"
                
                # Mostrar como info o warning según cumplimiento
                if cumple_x and cumple_y:
                    self.show_info(info)
                else:
                    self.show_warning(info)
                    
                # Guardar datos para el botón "Ver Data"
                self.modal_table_data = modal_data
                
            else:
                self.show_warning("No se pudieron procesar los datos modales")
        else:
            self.show_warning("No hay datos modales disponibles. Ejecute el análisis modal en ETABS.")

    def _get_min_mass_participation(self) -> float:
        """Obtener porcentaje mínimo de masa participativa validado"""
        try:
            min_percent = float(self.ui.le_min_mass_participation.text())
            if 70.0 <= min_percent <= 95.0:
                self.ui.le_min_mass_participation.setStyleSheet("")
                return min_percent
            else:
                self.ui.le_min_mass_participation.setStyleSheet("QLineEdit { border: 2px solid orange; }")
                return 90.0  # Valor por defecto
        except ValueError:
            self.ui.le_min_mass_participation.setStyleSheet("QLineEdit { border: 2px solid red; }")
            return 90.0

    def _apply_mass_validation(self, complies_x: bool, complies_y: bool):
        """Aplicar validación visual con colores para masa participativa"""
        # Validar dirección X
        if complies_x:
            self.ui.le_participacion_x.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
        else:
            self.ui.le_participacion_x.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
        
        # Validar dirección Y
        if complies_y:
            self.ui.le_participacion_y.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
        else:
            self.ui.le_participacion_y.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")

    def _validate_min_mass_participation(self):
        """Validar y actualizar porcentaje mínimo de masa participativa"""
        min_percent = self._get_min_mass_participation()
        
        # Re-validar datos modales actuales si existen
        if (hasattr(self, 'ui') and 
            hasattr(self.ui, 'le_participacion_x') and 
            hasattr(self.ui, 'le_participacion_y')):
            
            try:
                current_x = float(self.ui.le_participacion_x.text())
                current_y = float(self.ui.le_participacion_y.text())
                
                # Re-aplicar validación con nuevo límite
                complies_x = current_x >= min_percent
                complies_y = current_y >= min_percent
                
                self._apply_mass_validation(complies_x, complies_y)
                
            except (ValueError, AttributeError):
                pass  # No hay datos para re-validar
            
    def show_modal_table(self):
        """Mostrar tabla completa de datos modales"""
        self.show_modal_data()
        if hasattr(self, 'modal_table_data') and self.modal_table_data is not None:
            from shared.dialogs.table_dialog import show_dataframe_dialog
            
            show_dataframe_dialog(
                parent=self,
                dataframe=self.modal_table_data,
                title="Análisis Modal - Períodos y Masas Participativas",
                info_text="Datos completos del análisis modal obtenidos de ETABS"
            )
        else:
            self.show_warning("Primero ejecute 'Ver Data' para obtener los datos modales")
            
    def calculate_torsion(self):
        """Calcular irregularidad torsional"""
        if not self._connect_etabs():
            return
            
        try:
            # Obtener límite configurable
            torsion_limit = self._get_torsion_limit()
            if torsion_limit is None:
                return
                
            # Obtener tipo de combinación seleccionada
            combo_type = self.ui.cb_torsion_combo.currentText().lower()
            combinations = self.get_selected_combinations()
            
            # Seleccionar combinaciones según el tipo
            if combo_type == "dinámicas":
                cases_x = [combinations['dynamic_x']]
                cases_y = [combinations['dynamic_y']]
            elif combo_type == "estáticas":
                cases_x = [combinations['static_x']]
                cases_y = [combinations['static_y']]
            else:  # desplazamientos
                cases_x = [combinations['displacement_x']]
                cases_y = [combinations['displacement_y']]
            
            # Filtrar casos vacíos
            cases_x = [c for c in cases_x if c.strip()]
            cases_y = [c for c in cases_y if c.strip()]
            
            if not cases_x or not cases_y:
                self.show_warning(f"Seleccione combinaciones para {combo_type}")
                return
            
            # Calcular irregularidad torsional
            success = self.sismo.calculate_torsional_irregularity(self.SapModel, cases_x, cases_y)
            
            if success:
                # Actualizar campos de resultados con validación automática
                torsion_data = getattr(self.sismo, 'torsion_results', {})
                
                ratio_x = torsion_data.get('ratio_x', 0.0)
                ratio_y = torsion_data.get('ratio_y', 0.0)
                
                self.ui.le_delta_max_x.setText(f"{torsion_data.get('delta_max_x', 0.0):.4f}")
                self.ui.le_delta_prom_x.setText(f"{torsion_data.get('delta_prom_x', 0.0):.4f}")
                self.ui.le_relacion_x.setText(f"{ratio_x:.3f}")
                
                self.ui.le_delta_max_y.setText(f"{torsion_data.get('delta_max_y', 0.0):.4f}")
                self.ui.le_delta_prom_y.setText(f"{torsion_data.get('delta_prom_y', 0.0):.4f}")
                self.ui.le_relacion_y.setText(f"{ratio_y:.3f}")
                
                # Aplicar validación automática con colores
                self._apply_torsion_validation(ratio_x, ratio_y, torsion_limit)
                
                # Verificar irregularidad
                irregular_x = ratio_x > torsion_limit
                irregular_y = ratio_y > torsion_limit
                
                status = "IRREGULAR" if (irregular_x or irregular_y) else "REGULAR"
                color = "🔴" if (irregular_x or irregular_y) else "🟢"
                self.show_info(f"✅ Irregularidad torsional calculada\n\n{color} Estado: {status}")
                
            else:
                self.show_error("Error calculando irregularidad torsional")
                
        except Exception as e:
            self.show_error(f"Error: {e}")
            
    def _get_torsion_limit(self) -> float:
        """Obtener límite de torsión validado"""
        try:
            limit = float(self.ui.le_torsion_limit.text())
            if 1.0 <= limit <= 2.0:
                self.ui.le_torsion_limit.setStyleSheet("")
                return limit
            else:
                self.ui.le_torsion_limit.setStyleSheet("QLineEdit { border: 2px solid orange; }")
                self.show_warning("Límite debe estar entre 1.0 y 2.0")
                return None
        except ValueError:
            self.ui.le_torsion_limit.setStyleSheet("QLineEdit { border: 2px solid red; }")
            return None
        
    def _validate_torsion_limit(self):
        """Validar entrada de límite torsional"""
        self._get_torsion_limit()  # Solo para validación visual

    def _apply_torsion_validation(self, ratio_x: float, ratio_y: float, limit: float):
        """Aplicar validación automática con colores"""
        # Validar dirección X
        if ratio_x > limit:
            self.ui.le_relacion_x.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
        else:
            self.ui.le_relacion_x.setStyleSheet("QLineEdit { background-color: #ccffcc; }")
        
        # Validar dirección Y
        if ratio_y > limit:
            self.ui.le_relacion_y.setStyleSheet("QLineEdit { background-color: #ffcccc; font-weight: bold; }")
        else:
            self.ui.le_relacion_y.setStyleSheet("QLineEdit { background-color: #ccffcc; }")

    def show_torsion_table(self):
        """Mostrar tabla detallada de irregularidad torsional"""
        if not hasattr(self.sismo, 'torsion_table_data') or self.sismo.torsion_table_data is None:
            self.show_warning("Primero calcule la irregularidad torsional")
            return
        
        from shared.dialogs.table_dialog import show_dataframe_dialog
        
        show_dataframe_dialog(
            parent=self,
            dataframe=self.sismo.torsion_table_data,
            title="Irregularidad Torsional - Datos Detallados",
            info_text="Análisis detallado de irregularidad torsional por piso y dirección"
        )

    def update_all_data(self):
        """Actualizar todos los datos desde ETABS"""
        if not self._connect_etabs():
            return
        
        # Actualizar combinaciones
        self.refresh_all_combinations()
        
        # Actualizar datos modales
        self.show_modal_data()
        
        self.show_info("Datos actualizados desde ETABS")

    def _get_required_seismic_params(self) -> list:
        """Obtener lista de parámetros sísmicos requeridos según el país"""
        country = self.config.get('country', '').lower()
        
        if country == 'bolivia':
            return ['Fa', 'Fv', 'So', 'I', 'R']  # Bolivia usa I (Ie)
        elif country == 'peru':
            return ['Z', 'U', 'S', 'R']  # Perú usa U, no I
        else:
            return ['R']  # Parámetro mínimo común

    
