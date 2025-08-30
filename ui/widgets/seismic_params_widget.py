"""
Widget dinámico para parámetros sísmicos según configuración del país
"""

from PyQt5 import QtCore, QtWidgets
from typing import Dict, Any


class SeismicParamsWidget(QtWidgets.QWidget):
    """Widget que se adapta a los parámetros sísmicos de cada país"""
    
    def __init__(self, config: Dict[str, Any], parent=None):
        super().__init__(parent)
        
        self.config = config
        self.param_widgets = {}
        
        self.setupUi()

    def setupUi(self):
        """Configurar interfaz según el país"""
        self.layout = QtWidgets.QGridLayout(self)
        
        # Obtener parámetros específicos del país
        params_config = self.config.get('parametros_ui', {})
        
        if self.config.get('pais') == 'Bolivia':
            self._setup_bolivia_params()
        elif self.config.get('pais') == 'Perú':
            self._setup_peru_params()
        else:
            self._setup_generic_params()
    
    def _setup_bolivia_params(self):
        """Configurar parámetros específicos de Bolivia (CNBDS 2023)"""
        row = 0
        
        # Factor de amplificación Fa
        self.label_fa = QtWidgets.QLabel("Factor Fa:")
        self.sb_fa = QtWidgets.QDoubleSpinBox()
        self.sb_fa.setRange(0.1, 5.0)
        self.sb_fa.setSingleStep(0.1)
        self.sb_fa.setDecimals(2)
        self.sb_fa.setValue(1.86)
        
        self.layout.addWidget(self.label_fa, row, 0)
        self.layout.addWidget(self.sb_fa, row, 1)
        self.param_widgets['Fa'] = self.sb_fa
        
        # Factor de amplificación Fv
        self.label_fv = QtWidgets.QLabel("Factor Fv:")
        self.sb_fv = QtWidgets.QDoubleSpinBox()
        self.sb_fv.setRange(0.1, 5.0)
        self.sb_fv.setSingleStep(0.1)
        self.sb_fv.setDecimals(2)
        self.sb_fv.setValue(0.63)
        
        self.layout.addWidget(self.label_fv, row, 2)
        self.layout.addWidget(self.sb_fv, row, 3)
        self.param_widgets['Fv'] = self.sb_fv
        
        row += 1
        
        # So (aceleración espectral)
        self.label_so = QtWidgets.QLabel("So:")
        self.sb_so = QtWidgets.QDoubleSpinBox()
        self.sb_so.setRange(0.1, 5.0)
        self.sb_so.setSingleStep(0.1)
        self.sb_so.setDecimals(2)
        self.sb_so.setValue(2.9)
        
        self.layout.addWidget(self.label_so, row, 0)
        self.layout.addWidget(self.sb_so, row, 1)
        self.param_widgets['So'] = self.sb_so
        
        # Categoría de edificación
        self.label_categoria = QtWidgets.QLabel("Categoría:")
        self.cb_categoria = QtWidgets.QComboBox()
        self.cb_categoria.addItems(['A', 'B', 'C', 'D'])
        self.cb_categoria.setCurrentText('B')
        
        self.layout.addWidget(self.label_categoria, row, 2)
        self.layout.addWidget(self.cb_categoria, row, 3)
        self.param_widgets['categoria'] = self.cb_categoria

    def _setup_peru_params(self):
        """Configurar parámetros específicos de Perú (E.030)"""
        row = 0
        
        # Factor de zona Z
        self.sb_z.setRange(0.1, 1.0)
        self.sb_z.setSingleStep(0.05)
        self.sb_z.setDecimals(3)
        self.sb_z.setValue(0.25)
        
        self.layout.addWidget(self.label_z, row, 0)
        self.layout.addWidget(self.sb_z, row, 1)
        self.param_widgets['Z'] = self.sb_z
        
        self.layout.addWidget(self.label_u, row, 2)
        self.layout.addWidget(self.cb_u, row, 3)
        self.param_widgets['U'] = self.cb_u
        
        row += 1
        
        # Factor de suelo S
        self.label_s = QtWidgets.QLabel("Factor S:")
        self.sb_s = QtWidgets.QDoubleSpinBox()
        self.sb_s.setRange(0.8, 2.0)
        self.sb_s.setSingleStep(0.1)
        self.sb_s.setDecimals(2)
        self.sb_s.setValue(1.20)
        
        self.layout.addWidget(self.label_s, row, 0)
        self.layout.addWidget(self.sb_s, row, 1)
        self.param_widgets['S'] = self.sb_s
        
        # Períodos Tp y Tl
        self.label_tp = QtWidgets.QLabel("Tp (s):")
        self.sb_tp = QtWidgets.QDoubleSpinBox()
        self.sb_tp.setRange(0.1, 2.0)
        self.sb_tp.setSingleStep(0.1)
        self.sb_tp.setDecimals(2)
        self.sb_tp.setValue(0.6)
        
        self.layout.addWidget(self.label_tp, row, 2)
        self.layout.addWidget(self.sb_tp, row, 3)
        self.param_widgets['Tp'] = self.sb_tp
        
        row += 1
        
        self.label_tl = QtWidgets.QLabel("Tl (s):")
        self.sb_tl = QtWidgets.QDoubleSpinBox()
        self.sb_tl.setRange(1.0, 5.0)
        self.sb_tl.setSingleStep(0.1)
        self.sb_tl.setDecimals(2)
        self.sb_tl.setValue(2.0)
        
        self.layout.addWidget(self.label_tl, row, 0)
        self.layout.addWidget(self.sb_tl, row, 1)
        self.param_widgets['Tl'] = self.sb_tl
        
        # Tipo de suelo
        self.label_suelo = QtWidgets.QLabel("Tipo de Suelo:")
        self.cb_suelo = QtWidgets.QComboBox()
        suelo_tipos = self.config.get('espectro_config', {}).get('tipos_suelo', ['S0', 'S1', 'S2', 'S3'])
        self.cb_suelo.addItems(suelo_tipos)
        self.cb_suelo.setCurrentText('S1')
        
        self.layout.addWidget(self.label_suelo, row, 2)
        self.layout.addWidget(self.cb_suelo, row, 3)
        self.param_widgets['suelo'] = self.cb_suelo

    def _setup_generic_params(self):
        """Configurar parámetros genéricos"""
        row = 0
        
        # Factor sísmico básico
        self.label_factor = QtWidgets.QLabel("Factor Sísmico:")
        self.sb_factor = QtWidgets.QDoubleSpinBox()
        self.sb_factor.setRange(0.1, 2.0)
        self.sb_factor.setSingleStep(0.1)
        self.sb_factor.setDecimals(3)
        self.sb_factor.setValue(1.0)
        
        self.layout.addWidget(self.label_factor, row, 0)
        self.layout.addWidget(self.sb_factor, row, 1)
        self.param_widgets['factor'] = self.sb_factor

    def get_parameters(self) -> Dict[str, Any]:
        """Obtener todos los parámetros actuales"""
        params = {}
        
        for name, widget in self.param_widgets.items():
            if isinstance(widget, QtWidgets.QDoubleSpinBox):
                params[name] = widget.value()
            elif isinstance(widget, QtWidgets.QComboBox):
                try:
                    # Intentar convertir a float si es posible
                    params[name] = float(widget.currentText())
                except ValueError:
                    # Si no es numérico, mantener como string
                    params[name] = widget.currentText()
            elif isinstance(widget, QtWidgets.QLineEdit):
                params[name] = widget.text()
                
        return params

    def set_parameters(self, params: Dict[str, Any]):
        """Establecer parámetros"""
        for name, value in params.items():
            if name in self.param_widgets:
                widget = self.param_widgets[name]
                
                if isinstance(widget, QtWidgets.QDoubleSpinBox):
                    widget.setValue(float(value))
                elif isinstance(widget, QtWidgets.QComboBox):
                    index = widget.findText(str(value))
                    if index >= 0:
                        widget.setCurrentIndex(index)
                elif isinstance(widget, QtWidgets.QLineEdit):
                    widget.setText(str(value))

    def connect_param_changed(self, callback):
        """Conectar cambios de parámetros a callback"""
        for widget in self.param_widgets.values():
            if isinstance(widget, QtWidgets.QDoubleSpinBox):
                widget.valueChanged.connect(callback)
            elif isinstance(widget, QtWidgets.QComboBox):
                widget.currentTextChanged.connect(callback)
            elif isinstance(widget, QtWidgets.QLineEdit):
                widget.textChanged.connect(callback)