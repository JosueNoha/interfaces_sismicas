"""
Utilidades específicas de ETABS para Perú - Wrapper sobre utilidades centrales
Solo contiene adaptaciones específicas para E.030
"""

from core.utils.etabs_utils import *
from apps.peru.config_peru import PERU_CONFIG


def get_seismic_parameters_peru(SapModel):
    """Obtener parámetros sísmicos específicos de Perú desde ETABS"""
    try:
        # Obtener datos específicos de E.030 si están configurados en ETABS
        seismic_data = {}
        
        # Intentar obtener configuración sísmica del modelo
        # (Implementación específica para parámetros de E.030)
        
        return seismic_data
    except:
        return {}


def validate_e030_requirements(modal_data):
    """Validar requisitos específicos de E.030 para análisis modal"""
    if modal_data is None:
        return False, "No hay datos modales disponibles"
    
    # Verificar que se incluyan al menos 90% de masa participativa
    sum_ux = modal_data['SumUX'].max() if 'SumUX' in modal_data.columns else 0
    sum_uy = modal_data['SumUY'].max() if 'SumUY' in modal_data.columns else 0
    
    if sum_ux < 90 or sum_uy < 90:
        return False, f"Masa participativa insuficiente: X={sum_ux:.1f}%, Y={sum_uy:.1f}%"
    
    # Verificar al menos 3 modos
    num_modes = len(modal_data)
    if num_modes < 3:
        return False, f"Se requieren al menos 3 modos, encontrados: {num_modes}"
    
    return True, "Requisitos E.030 cumplidos"


def get_peru_drift_limits():
    """Obtener límites de deriva según E.030"""
    return {
        'concrete': 0.007,      # 0.7% para concreto armado
        'steel': 0.010,         # 1.0% para estructuras de acero
        'masonry': 0.005        # 0.5% para albañilería
    }


def check_e030_irregularities(SapModel):
    """Verificar irregularidades según criterios de E.030"""
    irregularities = {
        'torsion': False,
        'soft_story': False,
        'mass': False,
        'geometry': False
    }
    
    try:
        # Verificar irregularidad torsional
        torsion_data = get_torsion_data(SapModel)
        if torsion_data is not None:
            # Criterio E.030: desplazamiento máximo > 1.2 * desplazamiento promedio
            irregularities['torsion'] = check_torsional_irregularity_e030(torsion_data)
        
        # Verificar piso blando
        stiffness_data = get_story_stiffness(SapModel)
        if stiffness_data is not None:
            irregularities['soft_story'] = check_soft_story_e030(stiffness_data)
        
        # Verificar irregularidad de masa
        mass_data = get_story_mass(SapModel)
        if mass_data is not None:
            irregularities['mass'] = check_mass_irregularity_e030(mass_data)
            
    except Exception as e:
        print(f"Error verificando irregularidades E.030: {e}")
    
    return irregularities


def check_torsional_irregularity_e030(torsion_data):
    """Verificar irregularidad torsional según E.030"""
    # Implementar criterio específico de E.030
    # Δmax > 1.2 * Δprom en cualquier piso
    try:
        for _, row in torsion_data.iterrows():
            if 'MaxDrift' in row and 'AvgDrift' in row:
                ratio = row['MaxDrift'] / row['AvgDrift']
                if ratio > 1.2:
                    return True
        return False
    except:
        return False


def check_soft_story_e030(stiffness_data):
    """Verificar piso blando según E.030"""
    # Ki < 0.8 * Ki+1 (rigidez del piso i menor a 80% del superior)
    try:
        for i in range(len(stiffness_data) - 1):
            current_stiff = stiffness_data.iloc[i]['Stiffness']
            upper_stiff = stiffness_data.iloc[i+1]['Stiffness']
            
            if current_stiff < 0.8 * upper_stiff:
                return True
        return False
    except:
        return False


def check_mass_irregularity_e030(mass_data):
    """Verificar irregularidad de masa según E.030"""
    # mi > 1.5 * mi+1 (masa del piso i mayor a 150% del superior)
    try:
        for i in range(len(mass_data) - 1):
            current_mass = mass_data.iloc[i]['Mass']
            upper_mass = mass_data.iloc[i+1]['Mass']
            
            if current_mass > 1.5 * upper_mass:
                return True
        return False
    except:
        return False


# Funciones auxiliares específicas para E.030
def get_story_stiffness(SapModel):
    """Obtener rigidez de piso (implementación simplificada)"""
    try:
        [ret, stiff_table] = get_table(SapModel, 'Story Stiffness')
        return stiff_table if ret else None
    except:
        return None


def get_story_mass(SapModel):
    """Obtener masas de piso"""
    try:
        [ret, mass_table] = get_table(SapModel, 'Story Mass')
        return mass_table if ret else None
    except:
        return None