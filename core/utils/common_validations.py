"""
Validaciones comunes para parámetros sísmicos
Centralizadas para evitar duplicación entre países
"""

from typing import Dict, List, Any, Tuple


class SeismicParameterValidator:
    """Validador centralizado para parámetros sísmicos"""
    
    def __init__(self, country_config: Dict[str, Any]):
        self.config = country_config
        self.country = country_config.get('pais', 'Generic').lower()
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validar parámetros sísmicos según el país
        
        Returns:
            Tuple (es_valido, lista_advertencias)
        """
        warnings = []
        
        if self.country == 'bolivia':
            warnings.extend(self._validate_bolivia_params(parameters))
        elif self.country == 'perú':
            warnings.extend(self._validate_peru_params(parameters))
        
        # Validaciones comunes
        warnings.extend(self._validate_common_params(parameters))
        
        return len(warnings) == 0, warnings
    
    def _validate_bolivia_params(self, params: Dict[str, Any]) -> List[str]:
        """Validaciones específicas para Bolivia (CNBDS 2023)"""
        warnings = []
        espectro_config = self.config.get('espectro_config', {})
        
        # Validar Fa
        if 'Fa' in params:
            fa = float(params['Fa'])
            rangos_fa = espectro_config.get('rangos_fa', (0.8, 3.0))
            if fa < rangos_fa[0] or fa > rangos_fa[1]:
                warnings.append(
                    f"Factor Fa ({fa:.2f}) fuera del rango CNBDS 2023 ({rangos_fa[0]}-{rangos_fa[1]})"
                )
        
        # Validar Fv
        if 'Fv' in params:
            fv = float(params['Fv'])
            rangos_fv = espectro_config.get('rangos_fv', (0.6, 2.5))
            if fv < rangos_fv[0] or fv > rangos_fv[1]:
                warnings.append(
                    f"Factor Fv ({fv:.2f}) fuera del rango CNBDS 2023 ({rangos_fv[0]}-{rangos_fv[1]})"
                )
        
        # Validar So
        if 'So' in params:
            so = float(params['So'])
            rangos_so = espectro_config.get('rangos_so', (0.1, 4.0))
            if so < rangos_so[0] or so > rangos_so[1]:
                warnings.append(
                    f"Parámetro So ({so:.2f}) fuera del rango típico ({rangos_so[0]}-{rangos_so[1]})"
                )
        
        return warnings
    
    def _validate_peru_params(self, params: Dict[str, Any]) -> List[str]:
        """Validaciones específicas para Perú (E.030)"""
        warnings = []
        espectro_config = self.config.get('espectro_config', {})
        
        # Validar Z
        if 'Z' in params:
            z = float(params['Z'])
            rangos_z = espectro_config.get('rangos_z', (0.10, 0.45))
            if z < rangos_z[0] or z > rangos_z[1]:
                warnings.append(
                    f"Factor Z ({z:.3f}) fuera del rango E.030 ({rangos_z[0]}-{rangos_z[1]})"
                )
        
        # Validar S
        if 'S' in params:
            s = float(params['S'])
            rangos_s = espectro_config.get('rangos_s', (0.80, 2.00))
            if s < rangos_s[0] or s > rangos_s[1]:
                warnings.append(
                    f"Factor S ({s:.2f}) fuera del rango típico ({rangos_s[0]}-{rangos_s[1]})"
                )
        
        # Validar períodos Tp y Tl
        if 'Tp' in params and 'Tl' in params:
            tp = float(params['Tp'])
            tl = float(params['Tl'])
            
            if tp >= tl:
                warnings.append(f"Tp ({tp:.2f}s) debe ser menor que Tl ({tl:.2f}s)")
            
            rangos_tp = espectro_config.get('rangos_tp', (0.4, 1.0))
            rangos_tl = espectro_config.get('rangos_tl', (1.5, 3.0))
            
            if tp < rangos_tp[0] or tp > rangos_tp[1]:
                warnings.append(f"Tp ({tp:.2f}s) fuera del rango típico ({rangos_tp[0]}-{rangos_tp[1]}s)")
            
            if tl < rangos_tl[0] or tl > rangos_tl[1]:
                warnings.append(f"Tl ({tl:.2f}s) fuera del rango típico ({rangos_tl[0]}-{rangos_tl[1]}s)")
        
        return warnings
    
    def _validate_common_params(self, params: Dict[str, Any]) -> List[str]:
        """Validaciones comunes a todos los países"""
        warnings = []
        
        # Validar que no haya valores negativos en parámetros principales
        numeric_params = ['Fa', 'Fv', 'So', 'Z', 'U', 'S', 'Tp', 'Tl']
        
        for param_name in numeric_params:
            if param_name in params:
                try:
                    value = float(params[param_name])
                    if value <= 0:
                        warnings.append(f"El parámetro {param_name} debe ser positivo (actual: {value})")
                except (ValueError, TypeError):
                    warnings.append(f"El parámetro {param_name} debe ser numérico")
        
        return warnings


def validate_project_data(project_data: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validar datos básicos del proyecto
    
    Returns:
        Tuple (es_valido, lista_errores)
    """
    errors = []
    required_fields = ['proyecto', 'ubicacion', 'autor']
    
    for field in required_fields:
        if not project_data.get(field, '').strip():
            errors.append(f"El campo '{field}' es requerido")
    
    # Validar fecha si está presente
    if 'fecha' in project_data:
        fecha = project_data['fecha'].strip()
        if fecha and not _is_valid_date_format(fecha):
            errors.append("Formato de fecha inválido (use DD/MM/AAAA)")
    
    return len(errors) == 0, errors


def _is_valid_date_format(date_string: str) -> bool:
    """Validar formato de fecha DD/MM/AAAA"""
    try:
        from datetime import datetime
        datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def validate_combinations(combinations: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validar que las combinaciones seleccionadas no estén vacías
    
    Returns:
        Tuple (es_valido, lista_advertencias)
    """
    warnings = []
    
    combination_types = {
        'dynamic': 'Combinación Dinámica',
        'static': 'Combinación Estática', 
        'displacement': 'Combinación Desplazamientos'
    }
    
    for key, description in combination_types.items():
        if not combinations.get(key, '').strip():
            warnings.append(f"{description} no seleccionada")
    
    return len(warnings) == 0, warnings


# Factory function para crear validador según país
def create_validator(country_config: Dict[str, Any]) -> SeismicParameterValidator:
    """Crear validador específico para el país"""
    return SeismicParameterValidator(country_config)