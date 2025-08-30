# ui/widgets/units_widget.py
"""
Widget para selección de unidades centralizada
"""

from PyQt5.QtWidgets import (QWidget, QGridLayout, QLabel, QComboBox, 
                             QGroupBox, QHBoxLayout)
from PyQt5.QtCore import pyqtSignal
from core.config.units_config import UNITS_CONFIG, get_unit_options, get_default_unit

class UnitsWidget(QWidget):
    """Widget para selección de unidades"""
    
    units_changed = pyqtSignal(dict)  # Señal cuando cambian las unidades
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Configurar interfaz"""
        layout = QHBoxLayout(self)
        
        # Group box para unidades
        group_box = QGroupBox("Unidades de Trabajo")
        group_layout = QGridLayout(group_box)
        
        # Crear combo boxes para cada categoría
        self.combos = {}
        
        # Alturas
        group_layout.addWidget(QLabel("Alturas:"), 0, 0)
        self.combos['alturas'] = QComboBox()
        self.combos['alturas'].addItems(get_unit_options('alturas'))
        self.combos['alturas'].setCurrentText(get_default_unit('alturas'))
        group_layout.addWidget(self.combos['alturas'], 0, 1)
        
        # Desplazamientos
        group_layout.addWidget(QLabel("Desplazamientos:"), 0, 2)
        self.combos['desplazamientos'] = QComboBox()
        self.combos['desplazamientos'].addItems(get_unit_options('desplazamientos'))
        self.combos['desplazamientos'].setCurrentText(get_default_unit('desplazamientos'))
        group_layout.addWidget(self.combos['desplazamientos'], 0, 3)
        
        # Fuerzas
        group_layout.addWidget(QLabel("Fuerzas:"), 0, 4)
        self.combos['fuerzas'] = QComboBox()
        self.combos['fuerzas'].addItems(get_unit_options('fuerzas'))
        self.combos['fuerzas'].setCurrentText(get_default_unit('fuerzas'))
        group_layout.addWidget(self.combos['fuerzas'], 0, 5)
        
        layout.addWidget(group_box)
        
    def connect_signals(self):
        """Conectar señales"""
        for categoria, combo in self.combos.items():
            combo.currentTextChanged.connect(self._on_unit_changed)
    
    def _on_unit_changed(self):
        """Cuando cambia una unidad"""
        units = self.get_current_units()
        self.units_changed.emit(units)
    
    def get_current_units(self):
        """Obtener unidades actuales seleccionadas"""
        return {categoria: combo.currentText() 
                for categoria, combo in self.combos.items()}
    
    def set_units(self, units_dict):
        """Establecer unidades específicas"""
        for categoria, unidad in units_dict.items():
            if categoria in self.combos:
                combo = self.combos[categoria]
                if unidad in [combo.itemText(i) for i in range(combo.count())]:
                    combo.setCurrentText(unidad)