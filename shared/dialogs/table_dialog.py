"""
Diálogo para mostrar DataFrames en formato tabla
"""

from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
                            QTableWidget, QTableWidgetItem, QLabel, QHeaderView)
from PyQt5.QtCore import Qt
import pandas as pd


def show_dataframe_dialog(parent, dataframe, title="Datos", info_text=""):
    """
    Mostrar DataFrame en diálogo de tabla
    
    Args:
        parent: Widget padre
        dataframe: pandas DataFrame
        title: Título del diálogo
        info_text: Texto informativo adicional
    """
    dialog = QDialog(parent)
    dialog.setWindowTitle(title)
    dialog.setMinimumSize(800, 400)
    dialog.setModal(True)
    
    layout = QVBoxLayout(dialog)
    
    # Texto informativo
    if info_text:
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
    
    # Tabla
    table = QTableWidget()
    table.setRowCount(len(dataframe))
    table.setColumnCount(len(dataframe.columns))
    table.setHorizontalHeaderLabels(dataframe.columns.tolist())
    
    # Llenar datos
    for i, (index, row) in enumerate(dataframe.iterrows()):
        for j, value in enumerate(row):
            item = QTableWidgetItem(str(value))
            table.setItem(i, j, item)
    
    # Ajustar columnas
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectRows)
    
    layout.addWidget(table)
    
    # Botón cerrar
    button_layout = QHBoxLayout()
    button_layout.addStretch()
    
    btn_close = QPushButton("Cerrar")
    btn_close.clicked.connect(dialog.accept)
    button_layout.addWidget(btn_close)
    
    layout.addLayout(button_layout)
    
    dialog.exec_()