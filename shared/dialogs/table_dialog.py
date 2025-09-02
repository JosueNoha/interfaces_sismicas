"""
Diálogo ultra simplificado para mostrar solo tabla modal filtrada
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, 
                           QTableWidgetItem, QHeaderView, QPushButton)
from PyQt5.QtCore import Qt
import pandas as pd


def show_dataframe_dialog(parent, dataframe, title="Datos ETABS", info_text=""):
    """
    Mostrar DataFrame en diálogo ultra simple - solo tabla
    
    Args:
        parent: Widget padre
        dataframe: pandas DataFrame con los datos
        title: Título del diálogo
        info_text: No se usa (para compatibilidad)
    """
    dialog = DataFrameDialog(parent, dataframe, title)
    dialog.exec_()


class DataFrameDialog(QDialog):
    """Diálogo ultra simplificado - solo tabla modal filtrada"""
    
    def __init__(self, parent, dataframe, title="Datos ETABS"):
        super().__init__(parent)
        self.df = dataframe
        
        self.setWindowTitle(title)
        self.resize(600, 600)  # Más compacto
        
        self._setup_ui()
        self._populate_table()
        self._setup_connections()
    
    def _populate_table(self):
        """Llenar tabla con datos - formateo genérico"""
        self.table.setRowCount(len(self.df))
        self.table.setColumnCount(len(self.df.columns))
        
        # Headers
        headers = [str(col) for col in self.df.columns]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Datos con formateo automático
        for i, (index, row) in enumerate(self.df.iterrows()):
            for j, (col_name, value) in enumerate(row.items()):
                if pd.isna(value):
                    text = "N/A"
                elif isinstance(value, float):
                    # Formateo genérico para flotantes
                    text = f"{value:.4f}"
                else:
                    text = str(value)
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                self.table.setItem(i, j, item)
        
        # Ajustar tabla
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def _setup_ui(self):
        """Configurar interfaz ultra simplificada"""
        layout = QVBoxLayout()
        
        # Solo la tabla - sin paneles laterales ni grupos
        self.table = QTableWidget()
        self.table.setSortingEnabled(True)
        layout.addWidget(self.table)
        
        # Botones inferiores
        buttons_layout = QHBoxLayout()
        
        self.btn_export = QPushButton("Exportar CSV")
        self.btn_close = QPushButton("Cerrar")
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.btn_export)
        buttons_layout.addWidget(self.btn_close)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def _populate_table(self):
        """Llenar tabla con datos filtrados - SIN RESALTADO"""
        self.table.setRowCount(len(self.df))
        self.table.setColumnCount(len(self.df.columns))
        
        # Headers
        headers = [str(col) for col in self.df.columns]
        self.table.setHorizontalHeaderLabels(headers)
        
        # Datos
        for i, (index, row) in enumerate(self.df.iterrows()):
            for j, (col_name, value) in enumerate(row.items()):
                if pd.isna(value):
                    text = "N/A"
                elif isinstance(value, float):
                    # Formateo específico por columna
                    if col_name == 'Period':
                        text = f"{value:.4f}"
                    elif col_name in ['UX', 'UY', 'RZ']:
                        text = f"{value:.6f}"
                    elif col_name.startswith('Sum'):
                        text = f"{value:.4f}"
                    else:
                        text = f"{value:.6f}"
                else:
                    text = str(value)
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignCenter)
                
                # ELIMINADO: Resaltado de modos significativos
                
                self.table.setItem(i, j, item)
        
        # Ajustar tabla a todo el espacio disponible
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    
    def _setup_connections(self):
        """Conectar señales"""
        self.btn_close.clicked.connect(self.accept)
        self.btn_export.clicked.connect(self._export_csv)
    
    def _export_csv(self):
        """Exportar datos filtrados a CSV"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Exportar Datos Modales", 
            "analisis_modal_filtrado.csv", 
            "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                self.df.to_csv(file_path, index=False)
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(self, "Éxito", f"Datos exportados a:\n{file_path}")
            except Exception as e:
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", f"Error exportando datos:\n{str(e)}")