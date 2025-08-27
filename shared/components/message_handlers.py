"""Manejadores de mensajes compartidos"""
from PyQt5.QtWidgets import QMessageBox

class MessageHandler:
    @staticmethod
    def show_info(parent, title, message):
        QMessageBox.information(parent, title, message)
    
    @staticmethod
    def show_warning(parent, title, message):
        QMessageBox.warning(parent, title, message)
    
    @staticmethod
    def show_error(parent, title, message):
        QMessageBox.critical(parent, title, message)
    
    @staticmethod
    def show_question(parent, title, message):
        reply = QMessageBox.question(parent, title, message,
                                   QMessageBox.Yes | QMessageBox.No,
                                   QMessageBox.No)
        return reply == QMessageBox.Yes