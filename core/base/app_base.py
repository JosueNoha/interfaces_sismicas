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
from core.utils import unit_tool
u = unit_tool.Units()

class AppBase(QMainWindow):
    """Clase base mejorada para aplicaciones sísmicas"""
    
    # Inicialización y configuración 
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
        
        # Atributos a guardar
        self.modal_data = None
        self.modal_results = None
        
        # Configurar funcionalidad común
        self._setup_icon()
        self._init_default_values()
        
        # Actualizar widgets al inicio
        self.refresh_all_combinations(silent=True)
        self.process_modal_data()
        self._update_shear_displays()
        self._update_displacement_results()
        self._update_drift_results()
        self._update_torsion_results()
        
        # Conectar señales
        self._connect_common_signals()

    def _setup_icon(self):
        """Configurar icono de la aplicación"""
        icon_path = self.config.get('icon_path')
        if icon_path and os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def _connect_common_signals(self):
        """Conectar señales comunes"""
        # Botones de análisis sísmico
        self.ui.b_modal.clicked.connect(self.show_modal_table) 
        self.ui.b_desplazamiento.clicked.connect(self._show_displacements_plot)
        self.ui.b_derivas.clicked.connect(self._show_drifts_plot)
        self.ui.b_actualizar.clicked.connect(self.update_all_data)
        
        # Gráfico de cortantes
        self.ui.b_view_dynamic.clicked.connect(lambda: self._show_shear_plot('dynamic'))
        self.ui.b_view_static.clicked.connect(lambda: self._show_shear_plot('static'))
        
        # Validacion de deriva maxima
        self.ui.le_max_drift.textChanged.connect(self._validate_max_drift)

        # Botón irregularidad torsional
        self.ui.b_torsion.clicked.connect(self.calculate_torsion)
        self.ui.b_torsion_table.clicked.connect(self.show_torsion_table)
        self.ui.le_torsion_limit.textChanged.connect(self._update_torsion_results)
        
        # AGREGAR: Actualización automática de cortantes cuando cambien las combinaciones
        self.ui.cb_comb_dynamic_x.currentTextChanged.connect(self._on_combination_changed)
        self.ui.cb_comb_dynamic_y.currentTextChanged.connect(self._on_combination_changed)
        self.ui.cb_comb_static_x.currentTextChanged.connect(self._on_combination_changed)
        self.ui.cb_comb_static_y.currentTextChanged.connect(self._on_combination_changed)
            
        # Actualiza Factores de escala
        self.ui.le_scale_factor.textChanged.connect(self._on_scale_factor_changed)
        
        # Validación de masa participativa mínima
        self.ui.le_modal.textChanged.connect(self.process_modal_data)
        
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
            
    # Descripciones y Ui
    def _update_description_ui(self, desc_type: str, description_text: str):
        """Actualizar elementos de UI relacionados con la descripción"""
        # Usar el nuevo método de la interfaz si existe
        if hasattr(self.ui, '_update_text_status'):
            self.ui._update_text_status(desc_type, bool(description_text.strip()))
        else:
            # Fallback al método anterior por compatibilidad
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
            # Guardar path en el objeto sismo
            self.sismo.urls_imagenes[image_type] = file_path
            
            self.ui._update_image_status(image_type, file_path)
            
            print(f"✅ Imagen {image_type} cargada: {file_path}")

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
        
    def show_error(self, message: str):
        """Mostrar mensaje de error"""
        QMessageBox.critical(self, "Error", message)

    def show_info(self, message: str):
        """Mostrar mensaje de información"""
        QMessageBox.information(self, "Información", message)

    def show_warning(self, message: str):
        """Mostrar mensaje de advertencia"""
        QMessageBox.warning(self, "Advertencia", message)

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
            
    # Conexión a etabs
    
    def _connect_etabs(self) -> bool:
        """Conectar con ETABS"""
        from core.utils.etabs_utils import connect_to_etabs, validate_model_connection
        
        self.ETABSObject, self.SapModel = connect_to_etabs()
        
        if self.SapModel:
            # Validar conexión
            model_info = validate_model_connection(self.SapModel)
            
            if model_info['connected']:
                print(f"✅ Conectado a ETABS: {model_info['model_name']}")
                
                return True
            else:
                self.show_warning(f"Error en conexión: {model_info.get('error', 'Desconocido')}")
        else:
            self.show_warning("No se pudo conectar con ETABS. Verifique que esté abierto.")
        
        return False
                
              
    # Selección de combinaciones desde ETABS  
    def refresh_all_combinations(self, silent=False):
        """Actualizar todas las combinaciones desde ETABS"""
        if not self._connect_etabs():
            if not silent:
                self.show_warning("No se pudo conectar con ETABS")
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
                selections = self._auto_select_combinations_by_pattern()
                if not silent:
                    self.show_info(f"✅ Combinaciones actualizadas\n🎯 {selections} selecciones automáticas")
                else:
                    print("✅ Combinaciones actualizadas automáticamente")
            else:
                self._set_disconnected_message()
                if not silent:
                    self.show_warning("⚠️ Actualización parcial")
                    
        except Exception as e:
            self._set_disconnected_message()
            if not silent:
                self.show_error(f"Error: {e}")
            else:
                print(f"Error en actualización automática: {e}")
                
    def _auto_select_combinations_by_pattern(self):
        """Seleccionar automáticamente combinaciones que cumplan patrones comunes"""
        try:
            # Patrones base (sin X/Y, se añaden automáticamente)
            base_patterns = {
                'static': ['SE', 'SS', 'S', 'Estat', 'Estatico', 'Static'],
                'dynamic': ['SD', 'SDin', 'Dinamico', 'Dynamic', 'Modal', 'Sdin'],
                'displacement': ['Despl', 'Drift', 'Deriva', 'Displacement', 'Desp']
            }
            
            
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
        
    def _connect_combination_signals(self):
        """Conectar señales relacionadas con combinaciones"""
        if hasattr(self.ui, 'b_refresh_combinations'):
            self.ui.b_refresh_combinations.clicked.connect(self.refresh_all_combinations)
            
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
                
    # Analisis Modal
    def process_modal_data(self):
        """Guardar y procesar los datos modales"""
        # Si no está conectado, conectar automáticamente
        if not self.SapModel:
            self._connect_etabs()
            
        from core.utils.etabs_utils import get_modal_data,process_modal_data
        modal_data = get_modal_data(self.SapModel)
        if modal_data is not None and len(modal_data) > 0:
            results = process_modal_data(modal_data)
            if results:
                self.modal_data = modal_data
                self.modal_results = results
                self._update_modal_fields(results)
        else:
            self.show_warning("⚠️ No hay datos modales disponibles.")
        
    def show_modal_table(self):
        """Mostrar tabla de datos modales""" #tabla
        # Si no está conectado, conectar automáticamente
        if not self.SapModel:
            self._connect_etabs()
        
        try:
            if self.modal_data is None:
                self.process_modal_data()
            
            if self.modal_data is not None and self.modal_results is not None:
                filtered_modal_data = self._filter_modal_columns(self.modal_data)
                # Mostrar tabla directamente
                from shared.dialogs.table_dialog import show_dataframe_dialog
                
                show_dataframe_dialog(
                    parent=self,
                    dataframe=filtered_modal_data,
                    title="Análisis Modal - Períodos y Masas Participativas"
                )
        
            else:
                self.show_warning("⚠️ No hay datos modales disponibles.\nEjecute el análisis modal en ETABS primero.")
                
        except Exception as e:
            print(f"Error obteniendo datos modales: {e}")
            self.show_warning(f"Error obteniendo datos modales: {str(e)}")
            
    def _filter_modal_columns(self, dataframe):
        """Filtrar columnas específicas para análisis modal"""
        desired_columns = ['Mode', 'Period', 'UX', 'UY', 'RZ', 'SumUX', 'SumUY', 'SumRZ']
        
        # Verificar columnas disponibles
        available_columns = [col for col in desired_columns if col in dataframe.columns]
        
        # Filtrar DataFrame
        filtered_df = dataframe[available_columns].copy()
        
        # Agregar columna Mode si no existe
        if 'Mode' not in filtered_df.columns:
            filtered_df.insert(0, 'Mode', range(1, len(filtered_df) + 1))
    
        return filtered_df
              
    def _update_modal_fields(self, results):
        """Actualizar campos modales y aplicar validación visual consolidada"""
        if self.modal_data is None:
            self.process_modal_data()
        try:
            # 1. Actualizar períodos fundamentales
            if hasattr(self.ui, 'le_tx'):
                self.ui.le_tx.setText(f"{results['Tx']:.4f}" if results['Tx'] else "N/A")
            if hasattr(self.ui, 'le_ty'):
                self.ui.le_ty.setText(f"{results['Ty']:.4f}" if results['Ty'] else "N/A")
                
            
            # 2. Actualizar masa participativa
            if hasattr(self.ui, 'le_participacion_x'):
                self.ui.le_participacion_x.setText(f"{results['total_mass_x']:.1f}")
            if hasattr(self.ui, 'le_participacion_y'):
                self.ui.le_participacion_y.setText(f"{results['total_mass_y']:.1f}")
            
            # 3. Validación visual consolidada
            min_mass = self._get_min_mass_participation()
            cumple_x = results['total_mass_x'] >= min_mass
            cumple_y = results['total_mass_y'] >= min_mass
            
            # Aplicar colores directamente
            color_ok = "QLineEdit { background-color: #d4edda; }"
            color_warning = "QLineEdit { background-color: #fff3cd; }"
            
            if hasattr(self.ui, 'le_participacion_x'):
                self.ui.le_participacion_x.setStyleSheet(color_ok if cumple_x else color_warning)
            if hasattr(self.ui, 'le_participacion_y'):
                self.ui.le_participacion_y.setStyleSheet(color_ok if cumple_y else color_warning)
            
            print(f"✅ Campos actualizados - Tx: {results['Tx']:.4f}s, Ty: {results['Ty']:.4f}s")
            
        except Exception as e:
            print(f"❌ Error actualizando campos: {e}")

    def _get_min_mass_participation(self) -> float:
        """Obtener porcentaje mínimo de masa participativa validado"""
        try:
            min_percent = float(self.ui.le_modal.text())
            if 70.0 <= min_percent <= 100.0:
                self.ui.le_modal.setStyleSheet("")
                return min_percent
            else:
                self.ui.le_modal.setStyleSheet("QLineEdit { border: 2px solid orange; }")
                return 90.0
        except ValueError:
            self.ui.le_modal.setStyleSheet("QLineEdit { border: 2px solid red; }")
            return 90.0
        
        
    # Fuerzas Cortantes
    def calculate_shear_forces(self):
        """Método principal para calcular cortantes"""
        # Solo conectar si se solicita y no está conectado
        if not self.SapModel:
            self._connect_etabs()
        
        try:
            # Validar combinaciones
            combinations = self.get_selected_combinations()
            required = ['dynamic_x', 'dynamic_y', 'static_x', 'static_y']
            missing = [k for k in required if not combinations[k].strip()]
            
            if missing:
                self.show_warning(f"Faltan combinaciones: {', '.join(missing)}")
                return False
            
            # Filtrar datos por tipo
            dynamic_cases = [combinations['dynamic_x'], combinations['dynamic_y']]
            static_cases = [combinations['static_x'], combinations['static_y']]
            all_cases = dynamic_cases + static_cases
            
            x_cases = [combinations['dynamic_x'], combinations['static_x']]
        
            
            from core.utils.etabs_utils import set_envelopes_for_display
        
            try:
                # 1. Configurar envolventes
                set_envelopes_for_display(self.SapModel, set_envelopes=True)
                
                # 2. Seleccionar casos
                self.SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(all_cases)
                self.SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(all_cases)
                
            except Exception as e:
                print(f"⚠️ Error configurando ETABS: {e}")
            
            # Obtener datos directamente de ETABS
            from core.utils.etabs_utils import get_story_forces, get_story_data, set_units
            set_units(self.SapModel,'Ton_m_C')
            story_forces = get_story_forces(self.SapModel)
            story_data = get_story_data(self.SapModel)
            
            if story_forces is None:
                self.show_error("No se pudieron obtener fuerzas de piso")
                return False
            
            story_forces = story_forces.merge(story_data,on='Story',sort=False)
            
            shear_dynamic = story_forces[story_forces['OutputCase'].isin(dynamic_cases)].copy()
            shear_static = story_forces[story_forces['OutputCase'].isin(static_cases)].copy()
            

            if len(shear_dynamic) == 0 or len(shear_static) == 0:
                self.show_error("No se obtuvieron datos suficientes de Fuerzas Cortantes")
                return False
            
            import numpy as np
            shear_dynamic['V'] = np.where(
                shear_dynamic['OutputCase'].isin(x_cases),
                shear_dynamic['VX'],shear_dynamic['VY'])
            shear_static['V'] = np.where(
                shear_static['OutputCase'].isin(x_cases),
                shear_static['VX'],shear_static['VY'])
            

            shear_dynamic = shear_dynamic[['Story','Height','Location','OutputCase','V']]
            shear_dynamic['Height'] *= u.m
            shear_dynamic['V'] *= u.tonf
            shear_static = shear_static[['Story','Height','Location','OutputCase','V']]
            shear_static['Height'] *= u.m
            shear_static['V'] *= u.tonf

            self.sismo.shear_dynamic = shear_dynamic
            self.sismo.shear_static = shear_static
            
            return True
            
        except Exception as e:
            self.show_error(f"Error: {e}")
            return False

    def _extract_base_shears(self):
        """Extraer cortantes basales de los datos calculados"""
        try:
            self.calculate_shear_forces()
            
            # Filtrar datos de base
            dyn_base = self.sismo.shear_dynamic[self.sismo.shear_dynamic['Location'] == 'Bottom']
            sta_base = self.sismo.shear_static[self.sismo.shear_static['Location'] == 'Bottom']
            
            
            if len(dyn_base) == 0 or len(sta_base) == 0:
                return None
            
            combinations = self.get_selected_combinations()
            x_cases = [combinations['dynamic_x'], combinations['static_x']]
            y_cases = [combinations['dynamic_y'], combinations['static_y']]
            # Extraer valores por dirección
            def get_shear_value(df, direction):
                cases = x_cases if direction == 'X' else y_cases
                filtered = df[df['OutputCase'].isin(cases)].copy()
                return abs(filtered['V'].iloc[-1]) if len(filtered) > 0 else 0.0
            
            return {
                'vdx': get_shear_value(dyn_base, 'X'),
                'vdy': get_shear_value(dyn_base, 'Y'),
                'vsx': get_shear_value(sta_base, 'X'),
                'vsy': get_shear_value(sta_base, 'Y')
            }
            
        except Exception as e:
            print(f"❌ Error extrayendo cortantes: {e}")
            return None

    def _update_shear_displays(self):
        """Actualizar campos de cortantes y factores"""
        from core.config.constants import DEFAULT_UNITS
        try:
            
            base_values = self._extract_base_shears()
            # Actualizar campos de cortantes
            u_f = self.sismo.u_f
            self.ui.le_vdx.setText(f"{u.to_unit(base_values['vdx'],u_f):.2f} ({u_f})")
            self.ui.le_vdy.setText(f"{u.to_unit(base_values['vdy'],u_f):.2f} ({u_f})")
            self.ui.le_vsx.setText(f"{u.to_unit(base_values['vsx'],u_f):.2f} ({u_f})")
            self.ui.le_vsy.setText(f"{u.to_unit(base_values['vsy'],u_f):.2f} ({u_f})")
            
            # Calcular factores de escala
            scale_factors = self._calculate_scale_factors(base_values)
            self.ui.le_fx.setText(f"{scale_factors['fx']:.3f}")
            self.ui.le_fy.setText(f"{scale_factors['fy']:.3f}")
            
            # Almacenar datos
            self.sismo.data.Vdx = base_values['vdx']
            self.sismo.data.Vdy = base_values['vdy']
            self.sismo.data.Vsx = base_values['vsx']
            self.sismo.data.Vsy = base_values['vsy']
            self.sismo.data.FEx = scale_factors['fx']
            self.sismo.data.FEy = scale_factors['fy']
            
            return True
                
        except Exception as e:
            print(f"❌ Error actualizando displays: {e}")
            return False

    def _calculate_scale_factors(self, base_values):
        """Calcular factores de escala basados en porcentaje mínimo"""
        try:
            # Obtener porcentaje mínimo
            try:
                min_percent = float(self.ui.le_scale_factor.text()) / 100.0
            except:
                min_percent = 0.80  # 80% por defecto
            
            # Calcular factores (dinámico debe ser >= min_percent * estático)
            fx = 1.0
            fy = 1.0
            
            if base_values['vdx'] > 0:
                required_vdx = min_percent * base_values['vsx']
                fx = max(1.0, required_vdx / base_values['vdx'])
                
            if base_values['vdy'] > 0:
                required_vdy = min_percent * base_values['vsy'] 
                fy = max(1.0, required_vdy / base_values['vdy'])
            
            return {'fx': fx, 'fy': fy}
            
        except Exception as e:
            print(f"❌ Error calculando factores: {e}")
            return {'fx': 1.0, 'fy': 1.0}
    

    def _on_scale_factor_changed(self):
        """Actualizar factores cuando cambie el porcentaje mínimo"""
        try:
            if (not hasattr(self.sismo, 'data') or not hasattr(self.sismo.data, 'Vdx') or 
                self.sismo.data.Vdx <= 0 or getattr(self, '_updating_shears', False)):
                return
            
            base_values = {
                'vdx': self.sismo.data.Vdx, 'vdy': self.sismo.data.Vdy,
                'vsx': self.sismo.data.Vsx, 'vsy': self.sismo.data.Vsy
            }
            
            # Solo actualizar factores, no cortantes
            scale_factors = self._calculate_scale_factors(base_values)
            self.ui.le_fx.setText(f"{scale_factors['fx']:.3f}")
            self.ui.le_fy.setText(f"{scale_factors['fy']:.3f}")
            
            self.sismo.data.FEx = scale_factors['fx']
            self.sismo.data.FEy = scale_factors['fy']
            
        except Exception as e:
            print(f"⚠️ Error actualizando factores: {e}")
            
        
    def _create_shear_plot(self,plot_type='static'):
        self.calculate_shear_forces()
        shear_data = getattr(self.sismo,f'shear_{plot_type}')
        self.update_seismic_loads()
        prep = 'SS' if plot_type == 'static' else 'SD'
        sx = self.sismo.loads.seism_loads[prep+'X']
        sy = self.sismo.loads.seism_loads[prep+'Y']
        figure = self.sismo._create_shear_figure(shear_data,
                                    [sx],[sy],plot_type)
        setattr(self.sismo,f'{plot_type}_shear_fig',figure)
        return figure

    def _show_shear_plot(self,plot_type):
        """Mostrar gráfico en ventana emergente"""
        fig = getattr(self.sismo, f'{plot_type}_shear_fig', None)
        if not fig:
            fig = self._create_shear_plot(plot_type)
            
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        from PyQt5.QtWidgets import QDialog, QVBoxLayout
        
        dialog = QDialog(self)
        layout = QVBoxLayout(dialog)
        canvas = FigureCanvasQTAgg(fig)
        layout.addWidget(canvas)
        dialog.exec_()
                
   
    # Desplazamientos   
    def calculate_displacements(self):
        """Calcular desplazamientos laterales"""
        if not self.SapModel:
            if not self._connect_etabs():
                return
        try:
            self.update_seismic_loads()
            
            # Decidir si usar combinación de desplazamientos o dinámico directo
            use_combo = bool(self.sismo.loads.seism_loads.get('dx','') and 
                             self.sismo.loads.seism_loads.get('dy',''))
            self.sismo.use_combo = use_combo
            
            # Configurar cargas
            success = self.sismo.calculate_displacements(self.SapModel, use_combo)
            
            if success:
                # Actualizar campos de resultados
                self._update_displacement_results()
            else:
                self.show_error("Error calculando desplazamientos")
                
        except Exception as e:
            self.show_error(f"Error: {e}") 
   
    
    def _update_displacement_results(self):
        """Actualizar campos de resultados de desplazamientos"""
        try:
            if not hasattr(self.sismo,'displacement_results'):
                self.calculate_displacements()
                
            u_d = self.sismo.u_d
            results = self.sismo.displacement_results
            
            max_x = results.get('max_displacement_x', 0.0)
            max_y = results.get('max_displacement_y', 0.0)
            
            # Actualizar campos
            self.ui.le_desp_max_x.setText(f"{u.to_unit(max_x,u_d):.3f} ({u_d})")
            self.ui.le_desp_max_y.setText(f"{u.to_unit(max_y,u_d):.3f} ({u_d})")
            
            print(f"Debug - Desplazamientos: X={u.to_unit(max_x,u_d):.3f} mm, Y={u.to_unit(max_y,u_d):.3f} mm")  
                
        except Exception as e:
            print(f"Error actualizando resultados de desplazamientos: {e}")
            self.ui.le_desp_max_x.setText("N/A")
            self.ui.le_desp_max_y.setText("N/A")
            
    def _show_displacements_plot(self):
        """Mostrar gráfico de desplazamientos"""
        self.calculate_displacements()
        
        if not hasattr(self.sismo, 'fig_displacements') or self.sismo.fig_displacements is None:
            self.sismo.fig_displacements = self.sismo._create_displacement_figure(
                self.sismo.disp_x, self.sismo.disp_y, self.sismo.disp_h, self.sismo.use_combo
            )
            
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
   
   
    #Derivas
    def calculate_drifts(self):
        """Calcular derivas"""
        if not self.SapModel:
            if not self._connect_etabs():
                return
            
        try:
            self.update_seismic_loads()
            
            # Decidir si usar combinación de desplazamientos o dinámico directo
            use_combo = bool(self.sismo.loads.seism_loads.get('dx','') and 
                             self.sismo.loads.seism_loads.get('dy',''))
            self.sismo.use_combo = use_combo
            
            # Obtener límite de deriva
            max_drift_limit = self._get_max_drift_limit()
            self.sismo.max_drift = max_drift_limit
            
            success = self.sismo.calculate_drifts(self.SapModel, use_combo)
            
            if success:
                # Actualizar campos de resultados
                self._update_drift_results()
            else:
                self.show_error("Error calculando derivas")
                
        except Exception as e:
            self.show_error(f"Error: {e}")
        
            
    def _update_drift_results(self):
        """Actualizar campos de resultados de derivas"""
        try:
            if not hasattr(self.sismo,'drift_results'):
                self.calculate_drifts()

            results = self.sismo.drift_results
            
            max_x = results.get('max_drift_x', 0.0)
            max_y = results.get('max_drift_y', 0.0)
            story_x = results.get('story_max_x', 'N/A')
            story_y = results.get('story_max_y', 'N/A')
            
            # Actualizar campos
            self.ui.le_deriva_max_x.setText(f"{max_x:.4f}")
            self.ui.le_deriva_max_y.setText(f"{max_y:.4f}")
            self.ui.le_piso_deriva_x.setText(str(story_x))
            self.ui.le_piso_deriva_y.setText(str(story_y))
            
            
            self._validate_max_drift()
                
        except Exception as e:
            print(f"Error actualizando resultados de derivas: {e}")
            
            
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
        
    def _validate_max_drift(self):
        try:
            if not hasattr(self.sismo,'drift_results'):
                self.calculate_drifts()
                
            limit = getattr(self.sismo,'max_drift', 0.007)
            results = self.sismo.drift_results
            max_x = results.get('max_drift_x', 0.0)
            max_y = results.get('max_drift_y', 0.0)
            
            complies_x = max_x <= limit
            complies_y = max_y <= limit
            
            self._drift_validation(complies_x,complies_y)
        except:
            pass #excepcion silenciosa
        
    def _drift_validation(self,complies_x, complies_y):
        """Validar deriva máxima y aplicar colores"""
        try:
            # Aplicar colores directamente
            color_ok = "QLineEdit { background-color: #ccffcc; }"
            color_error = "QLineEdit { background-color: #ffcccc; font-weight: bold; }"
            
            # Validación dirección X
            x_style = color_ok if complies_x else color_error
            self.ui.le_deriva_max_x.setStyleSheet(x_style)
            if hasattr(self.ui, 'le_piso_deriva_x'):
                self.ui.le_piso_deriva_x.setStyleSheet(x_style)
            
            # Validación dirección Y
            y_style = color_ok if complies_y else color_error
            self.ui.le_deriva_max_y.setStyleSheet(y_style)
            if hasattr(self.ui, 'le_piso_deriva_y'):
                self.ui.le_piso_deriva_y.setStyleSheet(y_style)
                     
        except ValueError:
            # Si el valor de deriva máxima no es válido, limpiar estilos
            default_style = ""
            for field in [self.ui.le_deriva_max_x, self.ui.le_deriva_max_y]:
                field.setStyleSheet(default_style)
            if hasattr(self.ui, 'le_piso_deriva_x'):
                self.ui.le_piso_deriva_x.setStyleSheet(default_style)
            if hasattr(self.ui, 'le_piso_deriva_y'):
                self.ui.le_piso_deriva_y.setStyleSheet(default_style)


    def _show_drifts_plot(self):
        """Mostrar gráfico de desplazamientos internamente"""
        self.calculate_drifts()
        
        if not hasattr(self.sismo, 'fig_drifts') or self.sismo.fig_drifts is None:
            self.sismo.fig_drifts = self.sismo._create_drift_figure(
                self.sismo.drift_x, self.sismo.drift_y, self.sismo.drift_h, self.sismo.use_combo
            )
            
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


    # Torsiones 
    def calculate_torsion(self):
        """Calcular irregularidad torsional"""
        if not self.SapModel:
            if not self._connect_etabs():
                return
            
        try:
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
                self._update_torsion_results()
                
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
        
    def _validate_torsion(self, ratio_x: float, ratio_y: float, limit: float):
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
            
    def _update_torsion_results(self):
        """Actualizar campos de resultados de torsion"""
        try:
            if not hasattr(self.sismo,'torsion_results'):
                self.calculate_torsion()

            torsion_data = getattr(self.sismo, 'torsion_results', {})
            torsion_limit = self._get_torsion_limit()
            ratio_x = torsion_data.get('ratio_x', 0.0)
            ratio_y = torsion_data.get('ratio_y', 0.0)
            
            # Actualizar camposunits_widge
            self.ui.le_delta_max_x.setText(f"{torsion_data.get('delta_max_x', 0.0):.4f}")
            self.ui.le_delta_prom_x.setText(f"{torsion_data.get('delta_prom_x', 0.0):.4f}")
            self.ui.le_relacion_x.setText(f"{ratio_x:.3f}")
            
            self.ui.le_delta_max_y.setText(f"{torsion_data.get('delta_max_y', 0.0):.4f}")
            self.ui.le_delta_prom_y.setText(f"{torsion_data.get('delta_prom_y', 0.0):.4f}")
            self.ui.le_relacion_y.setText(f"{ratio_y:.3f}")
            
            # Validación con colores
            self._validate_torsion(ratio_x,ratio_y,torsion_limit)
            
            # Verificar irregularidad
            irregular_x = ratio_x > torsion_limit
            irregular_y = ratio_y > torsion_limit
            
            status = "IRREGULAR" if (irregular_x or irregular_y) else "REGULAR"
            color = "🔴" if (irregular_x or irregular_y) else "🟢"
            self.show_info(f"✅ Irregularidad torsional calculada\n\n{color} Estado: {status}")
                
        except Exception as e:
            print(f"Error actualizando resultados de derivas: {e}")

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
        
    # Unidades
    def _on_units_changed(self):
        """Manejar cambio de unidades de trabajo"""        
        # Extraer inidades de la interfaz
        units_dict = self.get_current_units()
        # Actualizar labels de la interfaz
        self._update_interface_units(units_dict)
        
        
    def _update_interface_units(self, units_dict):
        """Actualizar las unidades mostradas en la interfaz"""
        u_f = units_dict.get('fuerzas', 'tonf')
        u_d = units_dict.get('desplazamientos', 'mm')
        u_h = units_dict.get('alturas','m')
        
        if self.sismo.u_f != u_f:
            self.sismo.u_f = u_f    
            self._update_shear_displays()
            setattr(self.sismo, 'static_shear_fig', None)
            setattr(self.sismo, 'dynamic_shear_fig', None)
            
        if self.sismo.u_d != u_d:
            self.sismo.u_d = u_d
            self._update_displacement_results()
            setattr(self.sismo, 'fig_displacements', None)
            setattr(self.sismo, 'fig_drifts', None)
        
        if self.sismo.u_h != u_h:
            self.sismo.u_h = u_h
            setattr(self.sismo, 'static_shear_fig', None)
            setattr(self.sismo, 'dynamic_shear_fig', None)
            setattr(self.sismo, 'fig_displacements', None)
            setattr(self.sismo, 'fig_drifts', None)
        
            
    def get_current_units(self):
        """Obtener unidades actuales"""
        if hasattr(self.ui, 'units_widget'):
            return self.ui.units_widget.get_current_units()
        return {'alturas': 'm', 'desplazamientos': 'mm', 'fuerzas': 'tonf'}


    # Memorias y reportes
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
        
    def get_output_directory(self) -> str:
        """Seleccionar directorio de salida para reportes"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de salida",
            str(Path.home() / "Documents")
        )
        return directory
        
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
            
    
    # Trasversales
    
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
                
    
    def _auto_update_complete(self):
        """Actualización automática completa - Modal Y Cortantes (sin bucle)"""
        if not self.SapModel:
            return
            
        from core.utils.etabs_utils import get_modal_data, process_modal_data
        
        try:
            print("🔄 Actualizando análisis modal y cortantes automáticamente...")
            
            # 1. ANÁLISIS MODAL
            modal_data = get_modal_data(self.SapModel)
            
            if modal_data is not None and len(modal_data) > 0:
                modal_results = process_modal_data(modal_data)
                if modal_results:
                    self._update_modal_fields(modal_results)
                    self.modal_table_data = modal_data
                    print("✅ Campos modales actualizados")
            
            # 2. CORTANTES AUTOMÁTICOS (método directo sin reconectar)
            self.calculate_shear_forces(auto_connect=False)
            
            print("✅ Actualización automática completa")
                
        except Exception as e:
            print(f"Error en actualización automática: {e}")
        
        

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
        
    def update_all_data(self):
        """Actualizar todos los datos"""
        if not self.SapModel:
            if not self._connect_etabs():
                return
        else:
            # Si ya está conectado, actualizar directamente
            self._auto_update_complete()
        
        print("✅ Actualización completa terminada")
        

    def _get_required_seismic_params(self) -> list:
        """Obtener lista de parámetros sísmicos requeridos según el país"""
        country = self.config.get('country', '').lower()
        
        if country == 'bolivia':
            return ['Fa', 'Fv', 'So', 'I', 'R']  # Bolivia usa I (Ie)
        elif country == 'peru':
            return ['Z', 'U', 'S', 'R']  # Perú usa U, no I
        else:
            return ['R']  # Parámetro mínimo común

    def _on_combination_changed(self):
        """Actualizar cortantes cuando cambien las combinaciones"""
        try:
            if  getattr(self, '_updating_combinations', False):
                return
            
            if not self.SapModel:
                self._connect_etabs()
            
            self._updating_combinations = True
            try:
                combinations = self.get_selected_combinations()
                required = ['dynamic_x', 'dynamic_y', 'static_x', 'static_y']
                
                # Solo actualizar si todas las combinaciones están completas
                if all(combinations[k].strip() and not combinations[k].startswith("No conectado") for k in required):
                    self._update_shear_displays()
                    
            finally:
                self._updating_combinations = False
                
        except Exception as e:
            print(f"⚠️ Error en actualización automática: {e}")
