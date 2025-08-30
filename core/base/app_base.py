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
        """Generar reporte - implementar en clases derivadas"""
        self.show_warning("Función de reporte no implementada para esta aplicación")
            
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

                    # Crear gráficos
                    self._generate_shear_plots()
                    
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
        
    def _generate_shear_plots(self):
        """Generar gráficos de cortantes"""
        try:
            if hasattr(self.sismo, 'dynamic_shear_fig'):
                # Mostrar o guardar gráfico dinámico
                self._save_shear_plot(self.sismo.dynamic_shear_fig, 'cortante_dinamico.png')
            
            if hasattr(self.sismo, 'static_shear_fig'):
                # Mostrar o guardar gráfico estático  
                self._save_shear_plot(self.sismo.static_shear_fig, 'cortante_estatico.png')
                
        except Exception as e:
            print(f"Error generando gráficos: {e}")

    def _save_shear_plot(self, fig, filename):
        """Guardar gráfico en directorio temporal para preview"""
        import tempfile
        import os
        
        temp_dir = tempfile.gettempdir()
        filepath = os.path.join(temp_dir, filename)
        fig.savefig(filepath, dpi=150, bbox_inches='tight')

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