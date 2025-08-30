"""
Utilidades centrales para conexión y manejo de ETABS
Funcionalidad común compartida entre todas las aplicaciones sísmicas
"""

import pandas as pd
import numpy as np


def connect_to_etabs():
    """
    Conectar con instancia existente de ETABS
    
    Returns:
        tuple: (ETABSObject, SapModel) si conexión exitosa, (None, None) si falla
    """
    try:
        import comtypes.client
        
        # Intentar conectar con instancia existente de ETABS
        helper = comtypes.client.CreateObject('ETABSv1.Helper')
        helper = helper.QueryInterface(comtypes.gen.ETABSv1.cHelper)
        
        # Obtener objeto activo de ETABS
        myETABSObject = helper.GetObject("CSI.ETABS.API.ETABSObject")
        SapModel = myETABSObject.SapModel
        
        return myETABSObject, SapModel
        
    except Exception as e:
        print(f"Error conectando con ETABS: {e}")
        return None, None


def set_units(SapModel, unit_system):
    """
    Establecer sistema de unidades en ETABS
    
    Args:
        SapModel: Objeto modelo de ETABS
        unit_system (str): Sistema de unidades ('Ton_m_C', 'Ton_mm_C', 'kN_m_C', 'kN_mm_C')
    """
    unit_map = {
        'Ton_m_C': 6,     # Tonf, m, C
        'Ton_mm_C': 7,    # Tonf, mm, C
        'kN_m_C': 3,      # kN, m, C
        'kN_mm_C': 4,     # kN, mm, C
        'kgf_m_C': 5,     # kgf, m, C
        'kgf_mm_C': 8,    # kgf, mm, C
        'lb_in_F': 1,     # lb, in, F
        'lb_ft_F': 2,     # lb, ft, F
    }
    
    if unit_system in unit_map:
        try:
            SapModel.SetPresentUnits(unit_map[unit_system])
            return True
        except Exception as e:
            print(f"Error estableciendo unidades {unit_system}: {e}")
            return False
    else:
        print(f"Sistema de unidades {unit_system} no reconocido")
        return False


def get_table(SapModel, table_name):
    """
    Obtener tabla de resultados de ETABS como DataFrame
    
    Args:
        SapModel: Objeto modelo de ETABS
        table_name (str): Nombre de la tabla a obtener
        
    Returns:
        tuple: (success: bool, dataframe: pd.DataFrame or None)
    """
    try:
        # Verificar tablas disponibles
        [NumberNames, MyName, MyImport, MyUnit, MyDescription] = SapModel.DatabaseTables.GetAvailableTables()
        
        if table_name not in MyName:
            print(f"Tabla '{table_name}' no encontrada")
            print(f"Tablas disponibles: {MyName[:10]}...")  # Mostrar primeras 10
            return False, None
        
        # Obtener datos de la tabla
        [_, _ ,FieldsKeysIncluded, NumberRecords, TableData,_] = \
           SapModel.DatabaseTables.GetTableForDisplayArray(table_name,FieldKeyList =  "", GroupName = "")
        
        if NumberRecords == 0:
            print(f"Tabla '{table_name}' sin registros")
            return False, None
        
        # Convertir a DataFrame de pandas
        if len(TableData) > 0:
            columns = FieldsKeysIncluded  # Primera fila son los headers
            data = np.array(TableData).reshape(NumberRecords,len(columns))   # Resto son los datos
            df = pd.DataFrame(data, columns=columns)
            
            # Intentar convertir columnas numéricas
            for col in df.columns:
                if col not in ['Case','OutputCase', 'CaseType', 'StepType', 'Story', 'Pier', 'Spandrel', 'Location']:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            return True, df
        else:
            return False, None
            
    except Exception as e:
        print(f"Error obteniendo tabla '{table_name}': {e}")
        return False, None


def get_available_tables(SapModel):
    """
    Obtener lista de todas las tablas disponibles en ETABS
    
    Returns:
        list: Lista de nombres de tablas disponibles
    """
    try:
        [NumberNames, MyName, MyImport, MyUnit, MyDescription] = SapModel.DatabaseTables.GetAvailableTables()
        return MyName
    except Exception as e:
        print(f"Error obteniendo tablas disponibles: {e}")
        return []


def get_unique_cases(SapModel, combo_name):
    """
    Obtener casos de carga únicos de una combinación
    
    Args:
        SapModel: Objeto modelo de ETABS
        combo_name (str): Nombre de la combinación
        
    Returns:
        list: Lista de casos únicos en la combinación
    """
    unique_cases = []
    try:
        _,case_types,case_names,*_ = SapModel.RespCombo.GetCaseList(combo_name)
        if not case_types:
            return [combo_name]
        for case_type,case_name in zip(case_types,case_names):
            if case_type == 0:
                unique_cases += [case_name]
            elif case_type == 1:
                unique_cases += get_unique_cases(SapModel,case_name)
        return list(set(unique_cases))
    except Exception as e:
        print(f"Error obteniendo casos de combinación '{combo_name}': {e}")
        return unique_cases


def get_load_cases(SapModel, case_type=None):
    """
    Obtener lista de casos de carga
    
    Args:
        SapModel: Objeto modelo de ETABS
        case_type (int, optional): Filtrar por tipo (5=sismo, 1=muerta, 2=viva, etc.)
        
    Returns:
        list: Lista de nombres de casos de carga
    """
    try:
        [ret, load_cases, NumberNames] = SapModel.LoadCases.GetNameList()
        
        if case_type is None:
            # Filtrar casos que no empiecen con ~ y no contengan Modal
            filtered_cases = [case for case in load_cases 
                            if case[0] != '~' and 'Modal' not in case]
        else:
            # Filtrar por tipo específico
            filtered_cases = []
            for case in load_cases:
                if case[0] != '~' and 'Modal' not in case:
                    try:
                        [ret, current_type] = SapModel.LoadCases.GetTypeOAPI_1(case)
                        if current_type == case_type:
                            filtered_cases.append(case)
                    except:
                        continue
        
        return filtered_cases
        
    except Exception as e:
        print(f"Error obteniendo casos de carga: {e}")
        return []


def get_seismic_load_cases(SapModel):
    """
    Obtener casos de carga sísmicos específicamente
    
    Returns:
        list: Lista de casos sísmicos
    """
    return get_load_cases(SapModel, case_type=5)  # Tipo 5 = sísmico


def get_load_combinations(SapModel, seismic_only=False):
    """
    Obtener combinaciones de carga
    
    Args:
        SapModel: Objeto modelo de ETABS
        seismic_only (bool): Si True, solo combinaciones que contengan casos sísmicos
        
    Returns:
        list: Lista de nombres de combinaciones
    """
    try:
        [ret, load_combos, NumberNames] = SapModel.RespCombo.GetNameList()
        
        # Filtrar combinaciones válidas
        filtered_combos = [combo for combo in load_combos 
                         if combo[0] != '~' and 'Modal' not in combo]
        
        if seismic_only:
            # Filtrar solo combinaciones sísmicas
            seismic_cases = set(get_seismic_load_cases(SapModel))
            seismic_combos = []
            
            for combo in filtered_combos:
                unique_cases = set(get_unique_cases(SapModel, combo))
                # Si la intersección no está vacía, contiene casos sísmicos
                if unique_cases.intersection(seismic_cases):
                    seismic_combos.append(combo)
            
            return seismic_combos
        
        return filtered_combos
        
    except Exception as e:
        print(f"Error obteniendo combinaciones de carga: {e}")
        return []


# Funciones específicas para obtener datos comunes

def get_story_data(SapModel):
    """Obtener información general de pisos"""
    success, data = get_table(SapModel, 'Story Definitions')
    return data if success else None


def get_modal_data(SapModel):
    """Obtener datos del análisis modal"""
    success, data = get_table(SapModel, 'Modal Participating Mass Ratios')
    if success and data is not None:
        # Filtrar solo resultados modales
        modal_data = data[data['Case'] == 'Modal'].copy()
        return modal_data
    return None


def get_drift_data(SapModel):
    """Obtener datos de derivas de entrepiso"""
    success, data = get_table(SapModel, 'Story Drifts')
    return data if success else None


def get_displacement_data(SapModel):
    """Obtener datos de desplazamientos"""
    success, data = get_table(SapModel, 'Story Max Over Avg Displacements')
    return data if success else None


def get_story_forces(SapModel):
    """Obtener fuerzas de piso (cortantes, momentos)"""
    success, data = get_table(SapModel, 'Story Forces')
    return data if success else None


def get_base_shear(SapModel, story_name=None):
    """
    Obtener cortante basal
    
    Args:
        SapModel: Objeto modelo de ETABS
        story_name (str, optional): Nombre específico del piso base
        
    Returns:
        pd.DataFrame or None: Datos de cortante basal
    """
    story_forces = get_story_forces(SapModel)
    if story_forces is None:
        return None
    
    try:
        # Si no se especifica piso, usar el último (base)
        if story_name is None:
            base_story = story_forces['Story'].iloc[-1]
        else:
            base_story = story_name
        
        # Filtrar cortante en la base
        base_shear = story_forces[story_forces['Story'] == base_story].copy()
        base_shear = base_shear[base_shear['Location'] == 'Bottom']
        
        return base_shear
        
    except Exception as e:
        print(f"Error obteniendo cortante basal: {e}")
        return None


def get_torsion_data(SapModel):
    """Obtener datos de irregularidad torsional"""
    success, data = get_table(SapModel, 'Story Max Over Avg Drifts')
    return data if success else None


def get_mass_data(SapModel):
    """Obtener datos de masa por piso"""
    success, data = get_table(SapModel, 'Assembled Joint Masses')
    return data if success else None


def get_center_of_mass(SapModel):
    """Obtener centro de masa por piso"""
    success, data = get_table(SapModel, 'Centers Of Mass And Rigidity')
    return data if success else None


def get_diaphragm_data(SapModel):
    """Obtener datos de diafragmas"""
    success, data = get_table(SapModel, 'Diaphragm Center Of Mass Displacements')
    return data if success else None


# Funciones de verificación y validación

def validate_model_connection(SapModel):
    """
    Validar que la conexión con ETABS es funcional
    
    Returns:
        dict: Estado de la conexión y información básica
    """
    try:
        # Obtener información básica del modelo
        model_info = {
            'connected': True,
            'model_name': '',
            'units': '',
            'num_stories': 0,
            'has_modal': False,
            'num_load_cases': 0
        }
        
        # Intentar obtener nombre del modelo
        try:
            [ret, path, name] = SapModel.GetModelFilePath()
            model_info['model_name'] = name
        except:
            pass
        
        # Verificar unidades actuales
        try:
            units = SapModel.GetPresentUnits()
            unit_names = ['', 'lb_in_F', 'lb_ft_F', 'kN_m_C', 'kN_mm_C', 'kgf_m_C', 'Ton_m_C', 'Ton_mm_C', 'kgf_mm_C']
            model_info['units'] = unit_names[units] if units < len(unit_names) else f'Unknown({units})'
        except:
            pass
        
        # Contar pisos
        story_data = get_story_data(SapModel)
        if story_data is not None:
            model_info['num_stories'] = len(story_data)
        
        # Verificar análisis modal
        modal_data = get_modal_data(SapModel)
        model_info['has_modal'] = modal_data is not None and len(modal_data) > 0
        
        # Contar casos de carga
        load_cases = get_load_cases(SapModel)
        model_info['num_load_cases'] = len(load_cases)
        
        return model_info
        
    except Exception as e:
        return {
            'connected': False,
            'error': str(e),
            'model_name': '',
            'units': '',
            'num_stories': 0,
            'has_modal': False,
            'num_load_cases': 0
        }


def check_analysis_complete(SapModel):
    """
    Verificar que el análisis está completo
    
    Returns:
        dict: Estado del análisis
    """
    status = {
        'modal_complete': False,
        'response_complete': False,
        'has_results': False
    }
    
    try:
        # Verificar análisis modal
        modal_data = get_modal_data(SapModel)
        status['modal_complete'] = modal_data is not None and len(modal_data) >= 3
        
        # Verificar resultados de respuesta
        story_forces = get_story_forces(SapModel)
        status['response_complete'] = story_forces is not None and len(story_forces) > 0
        
        # Estado general
        status['has_results'] = status['modal_complete'] and status['response_complete']
        
    except Exception as e:
        print(f"Error verificando análisis: {e}")
    
    return status


# Funciones de procesamiento de datos

def process_modal_data(modal_data):
    """
    Procesar datos modales para obtener períodos fundamentales
    
    Returns:
        dict: Períodos fundamentales y masas participativas
    """
    if modal_data is None or len(modal_data) == 0:
        return None
    
    try:
        # Buscar períodos fundamentales
        # Primer modo con participación significativa en X
        mode_x = modal_data[modal_data.UX == max(modal_data.UX)].index[0]
        Tx = modal_data['Period'][mode_x] if not modal_data.empty else None
        
        # Primer modo con participación significativa en Y  
        mode_y = modal_data[modal_data.UY == max(modal_data.UY)].index[0]
        Ty = modal_data['Period'][mode_y] if not modal_data.empty else None
        
        # Masas participativas totales
        sum_ux = modal_data['SumUX'].max()*100
        sum_uy = modal_data['SumUY'].max()*100
        
        return {
            'Tx': Tx,
            'Ty': Ty,
            'total_mass_x': sum_ux,
            'total_mass_y': sum_uy,
            'num_modes': len(modal_data)
        }
        
    except Exception as e:
        print(f"Error procesando datos modales: {e}")
        return None


def process_drift_data(drift_data, max_drift=0.007):
    """
    Procesar datos de deriva y verificar límites
    
    Args:
        drift_data: DataFrame con datos de deriva
        max_drift: Límite máximo de deriva (default 0.7% para concreto)
        
    Returns:
        dict: Resumen del análisis de derivas
    """
    if drift_data is None:
        return None
    
    try:
        # Obtener derivas máximas
        max_drift_x = drift_data['DriftX'].max() if 'DriftX' in drift_data.columns else 0
        max_drift_y = drift_data['DriftY'].max() if 'DriftY' in drift_data.columns else 0
        
        # Verificar cumplimiento
        complies_x = max_drift_x <= max_drift
        complies_y = max_drift_y <= max_drift
        
        return {
            'max_drift_x': max_drift_x,
            'max_drift_y': max_drift_y,
            'limit': max_drift,
            'complies_x': complies_x,
            'complies_y': complies_y,
            'complies_overall': complies_x and complies_y
        }
        
    except Exception as e:
        print(f"Error procesando derivas: {e}")
        return None

def update_seismic_combinations(ui_combo_widgets, SapModel=None):
    """
    Actualizar ComboBoxes con combinaciones sísmicas desde ETABS
    Similar al código original pero centralizado
    
    Args:
        ui_combo_widgets: Lista de widgets QComboBox a actualizar
        SapModel: Modelo ETABS (se conecta automáticamente si es None)
    
    Returns:
        bool: True si se actualizó correctamente
    """
    try:
        # Conectar a ETABS si no se proporciona SapModel
        if SapModel is None:
            _, SapModel = connect_to_etabs()
            if SapModel is None:
                return False
        
        # Obtener casos de carga (siguiendo lógica original)
        _, load_cases, _ = SapModel.LoadCases.GetNameList()
        load_cases = [load for load in load_cases if load[0] != '~' and 'Modal' not in load]
        
        # Filtrar casos sísmicos (tipo 5)
        seism_cases = []
        for case in load_cases:
            try:
                case_type = SapModel.LoadCases.GetTypeOAPI_1(case)[2]
                if case_type == 5:
                    seism_cases.append(case)
            except:
                continue
        
        # Obtener combinaciones de carga
        _, load_combos, _ = SapModel.RespCombo.GetNameList()
        load_combos = [combo for combo in load_combos if combo[0] != '~' and 'Modal' not in combo]
        
        # Filtrar combinaciones sísmicas
        seism_combos = []
        for combo in load_combos:
            try:
                unique_cases = set(get_unique_cases(SapModel, combo))
                if unique_cases.intersection(set(seism_cases)):
                    seism_combos.append(combo)
            except:
                continue
        
        # Actualizar todos los ComboBoxes
        all_seismic = seism_cases + seism_combos
        
        for cbox in ui_combo_widgets:
            if cbox is not None:
                current_selection = cbox.currentText()
                cbox.clear()
                cbox.addItems(all_seismic)
                
                # Restaurar selección si aún existe
                if current_selection in all_seismic:
                    cbox.setCurrentText(current_selection)
        
        return True
        
    except Exception as e:
        print(f"Error actualizando combinaciones sísmicas: {e}")
        return False