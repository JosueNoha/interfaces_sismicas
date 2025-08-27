"""
Clase de análisis sísmico específica para Perú - E.030
"""

import sys
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
from matplotlib.figure import Figure

from core.base.seismic_base import SeismicBase
from core.utils import unit_tool

# Importar utilidades ETABS centralizadas
try:
    from core.utils import etabs_utils as etb
    from apps.peru import etabs_utils as peru_etb  # Utilidades específicas de Perú
except ImportError:
    # Fallback si no están disponibles
    etb = None
    peru_etb = None

u = unit_tool.Units()


class SeismicPeru(SeismicBase):
    """Clase de análisis sísmico específica para Perú - E.030"""
    
    def __init__(self, config=None):
        super().__init__(config)
        
        # Parámetros sísmicos específicos de E.030
        self.Z = 0.25  # Factor de zona
        self.U = 1.00  # Factor de uso
        self.S = 1.20  # Factor de suelo
        self.Tp = 0.60  # Período TP
        self.Tl = 2.00  # Período TL
        
        # Configuración de unidades
        self.u_h = 'm'    # Unidad altura
        self.u_d = 'mm'   # Unidad desplazamiento
        self.u_f = 'kN'   # Unidad fuerza
        
        # Clases internas para organización
        self.loads = self.Loads()
        self.tables = self.Tables()
        
        # Inicializar con parámetros de configuración
        if config and 'parametros_defecto' in config:
            defaults = config['parametros_defecto']
            self.Z = defaults.get('Z', self.Z)
            self.U = defaults.get('U', self.U)
            self.S = defaults.get('S', self.S)
            self.Tp = defaults.get('Tp', self.Tp)
            self.Tl = defaults.get('Tl', self.Tl)

    class Loads:
        """Clase para manejo de cargas sísmicas"""
        def __init__(self):
            self.seism_loads = {}
            
        def set_seism_loads(self, seism_loads):
            """Establecer cargas sísmicas"""
            self.seism_loads = seism_loads

    class Tables:
        """Clase para manejo de tablas de resultados"""
        def __init__(self):
            self.modal = None
            self.drift_table = None
            self.displacements = None
            self.torsion_table = None
            self.shear_table = None

    def set_base_story(self, base_story):
        """Establecer piso base para análisis"""
        self.base_story = base_story

    # Análisis Modal
    def ana_modal(self, SapModel):
        """
        Análisis modal - extraer períodos y masas participativas
        Devuelve datos del análisis modal y períodos fundamentales
        """
        if not etb:
            return None
            
        try:
            etb.set_units(SapModel, 'Ton_m_C')
            _, modal_table = etb.get_table(SapModel, 'Modal Participating Mass Ratios')
            
            # Filtrar y procesar tabla modal
            modal_table = modal_table[modal_table['OutputCase'] == 'MODAL']
            modal_table = modal_table[['Mode', 'Period', 'UX', 'UY', 'SumUX', 'SumUY']]
            
            self.tables.modal = modal_table
            return modal_table
            
        except Exception as e:
            print(f"Error en análisis modal: {e}")
            return None

    def get_fundamental_periods(self):
        """Obtener períodos fundamentales en X e Y"""
        if self.tables.modal is None:
            return None, None
            
        # Buscar el primer modo con participación significativa en cada dirección
        modal_x = self.tables.modal[self.tables.modal['UX'] > 0.1]
        modal_y = self.tables.modal[self.tables.modal['UY'] > 0.1]
        
        Tx = modal_x.iloc[0]['Period'] if not modal_x.empty else None
        Ty = modal_y.iloc[0]['Period'] if not modal_y.empty else None
        
        return Tx, Ty

    # Espectro de Respuesta E.030
    def get_C(self, T):
        """Calcular factor de amplificación C según E.030"""
        if T <= self.Tp:
            return 2.5
        elif T <= self.Tl:
            return 2.5 * (self.Tp / T)
        else:
            return 2.5 * (self.Tp * self.Tl) / (T**2)

    def get_ZUCS_R(self, direction, R):
        """Calcular aceleración espectral ZUCS/R"""
        return (self.Z * self.U * self.S * 9.81) / R

    def espectro_peru(self):
        """Generar espectro de respuesta para Perú según E.030"""
        T = np.arange(0, 4+0.01, 0.01)
        Sa = np.zeros_like(T)

        # Calcular espectro por tramos
        idx1 = T <= self.Tp
        idx2 = (T > self.Tp) & (T <= self.Tl)  
        idx3 = T >= self.Tl

        # Tramo 1: T ≤ Tp
        Sa[idx1] = 2.5 * self.Z * self.U * self.S
        
        # Tramo 2: Tp < T ≤ Tl
        Sa[idx2] = 2.5 * self.Tp / T[idx2] * self.Z * self.U * self.S
        
        # Tramo 3: T ≥ Tl
        Sa[idx3] = 2.5 * self.Tp * self.Tl / (T[idx3]**2) * self.Z * self.U * self.S
        
        self.Sa_max = max(Sa) * 1.2
        
        return T, Sa

    def dinamic_spectrum(self):
        """Generar gráfico del espectro dinámico"""
        T, Sa = self.espectro_peru()
        
        fig = Figure(figsize=(10, 6), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(T, Sa, 'r-', linewidth=2, label='Espectro E.030')
        ax.axvline(x=self.Tp, color='g', linestyle='--', alpha=0.7)
        ax.axvline(x=self.Tl, color='b', linestyle='--', alpha=0.7)
        
        ax.text(self.Tp, max(Sa)*0.9, f'Tp={self.Tp}s', fontsize=10)
        ax.text(self.Tl, max(Sa)*0.8, f'Tl={self.Tl}s', fontsize=10)
        
        ax.set_xlabel('Período T (s)')
        ax.set_ylabel('Sa (m/s²)')
        ax.set_title('Espectro de Respuesta E.030')
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        fig.tight_layout()
        self.fig_spectrum = fig

    # Métodos de análisis (implementación básica - se puede expandir)
    def show_modal_analysis(self):
        """Mostrar análisis modal"""
        print("Mostrando análisis modal para Perú")
        # Implementar lógica específica

    def show_irregularity_analysis(self):
        """Mostrar análisis de irregularidades"""
        print("Mostrando análisis de irregularidades para Perú")
        # Implementar lógica específica

    def show_torsion_irregularity(self, direction):
        """Mostrar irregularidad por torsión"""
        print(f"Mostrando irregularidad por torsión en {direction}")
        # Implementar lógica específica

    def show_soft_story(self, direction):
        """Mostrar irregularidad de piso blando"""
        print(f"Mostrando piso blando en {direction}")
        # Implementar lógica específica

    def show_mass_irregularity(self):
        """Mostrar irregularidad de masa"""
        print("Mostrando irregularidad de masa")
        # Implementar lógica específica

    def show_shear_forces(self, analysis_type):
        """Mostrar fuerzas cortantes"""
        print(f"Mostrando cortantes {analysis_type}")
        # Implementar lógica específica

    def show_drift_analysis(self):
        """Mostrar análisis de derivas"""
        print("Mostrando análisis de derivas")
        # Implementar lógica específica

    def show_displacement_analysis(self):
        """Mostrar análisis de desplazamientos"""
        print("Mostrando análisis de desplazamientos")
        # Implementar lógica específica

    def update_shear_data(self):
        """Actualizar datos de cortante"""
        print("Actualizando datos de cortante")
        # Implementar lógica específica

    def update_displacement_data(self):
        """Actualizar datos de desplazamiento"""
        print("Actualizando datos de desplazamiento")
        # Implementar lógica específica

    def update_stiffness_data(self):
        """Actualizar datos de rigidez"""
        print("Actualizando datos de rigidez")
        # Implementar lógica específica