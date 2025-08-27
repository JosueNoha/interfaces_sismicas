"""
Clase base para generación de memorias de cálculo LaTeX
"""

from pathlib import Path
from abc import ABC, abstractmethod


class MemoryBase(ABC):
    """Clase base para generadores de memoria de cálculo"""
    
    def __init__(self, seismic_instance, output_dir):
        self.seismic = seismic_instance
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def generate_memory(self):
        """Generar memoria - implementar en clases derivadas"""
        pass

    def load_template(self, template_path):
        """Cargar template LaTeX"""
        with open(template_path, 'r', encoding='utf-8') as file:
            return file.read()

    def save_memory(self, content, filename='memoria.tex'):
        """Guardar memoria LaTeX"""
        with open(self.output_dir / filename, 'w', encoding='utf-8') as file:
            file.write(content)