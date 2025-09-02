from . import config

class Units:
    
    m : float
    cm : float
    mm : float
    inch : float
    N : float
    kN : float
    kg : float
    g : float
    kgf : float
    tonf : float
    Pa : float
    MPa : float
    s : float
    
    def __init__(self):
        self.system = config.units_system
        self.set_units(self.system)
        
    def get_system(self):
        return self.system
    
    def set_units(self,u_system='SI'):
        '''
        Establece los factores de conversion de acuerdo al sistema de unidades definido
        
        Parameters:
        u_system: str, default='SI'
            Sistema de unidades puede ser: 'SI'(Internacional),'MKS'(m-kg-s),'FPS'(ft-lb-s)
        '''
        if u_system == 'SI':
            self.m = 1.
            self.kg = 1.
            self.s = 1
        elif u_system == 'MKS':
            self.m = 1.
            self.kg = 1/9.8106
            self.s = 1.
        elif u_system == 'FPS':
            self.m = 100/(2.54*12)
            self.kg = 1/2.20462
            self.s = 1.
         
        self.lb = 2.20462*self.kg
        self.g = self.kg/1000
        self.cm = self.m/100
        self.mm = self.m/1000
        self.inch = 2.54*self.cm
        self.ft = self.inch*12
        self.N = self.kg*self.m/self.s**2
        self.kN = 1000*self.N
        self.kgf = self.N*9.8106
        self.tonf = 1000*self.kgf
        self.Pa = self.N/self.m**2
        self.MPa = 1e6*self.Pa

    def to_unit(self, value, target_unit):
        """
        Convertir valor desde unidades base hacia unidad objetivo
        
        Examples: u.to_unit(1000, 'kN') → 1.0
                u.to_unit(1.0, 'kg/(m*s**2)') → presión en Pa
        """
        normalized = self._normalize(target_unit)
        factor = self._parse(normalized)
        return value / factor  # Dividir para convertir A la unidad

    def from_unit(self, value, source_unit):
        """
        Convertir desde unidad específica hacia unidades base
        
        Examples: u.from_unit(1, 'kN') → 1000.0 N
        """
        normalized = self._normalize(source_unit) 
        factor = self._parse(normalized)
        return value * factor  # Multiplicar para convertir DESDE la unidad
            
    
    def _normalize(self, unit_str):
        """Normalizar términos españoles y espacios"""
        import re
        replacements = {
            'pulg': 'inch', 'pulgada': 'inch', 'pulgadas': 'inch',
            'pie': 'ft', 'pies': 'ft', 'fts':'ft'
        }
        
        result = unit_str
        for spanish, english in replacements.items():
            result = result.replace(spanish, english)
    
        return re.sub(r'\s+', '', result)
    
    def _parse(self, expr):
        """Parser principal con soporte de paréntesis"""
        # Sin paréntesis → método simple
        if '(' not in expr:
            return self._eval_simple(expr)
        
        # Con paréntesis → resolver de adentro hacia afuera
        import re
        while '(' in expr:
            match = re.search(r'\([^()]+\)', expr)
            if not match:
                raise ValueError(f"Paréntesis mal balanceados: {expr}")
            
            # Evaluar contenido del paréntesis
            inner = match.group(0)[1:-1]  # Quitar ( )
            inner_result = self._eval_simple(inner)
            
            # Reemplazar con placeholder
            placeholder = f"_R{id(inner_result)}_"
            if not hasattr(self, '_temp'):
                self._temp = {}
            self._temp[placeholder] = inner_result
            
            expr = expr.replace(match.group(0), placeholder)
        
        # Evaluar expresión final
        result = self._eval_simple(expr)
        
        # Limpiar
        if hasattr(self, '_temp'):
            delattr(self, '_temp')
        
        return result

    
    def _eval_simple(self, expr):
        """Evaluar expresión simple: multiplicaciones y divisiones"""
        factor = 1.0
        
        # Manejar divisiones
        if '/' in expr:
            parts = expr.split('/')
            # Numerador
            factor *= self._eval_mult(parts[0]) if parts[0] else 1.0
            # Denominadores
            for part in parts[1:]:
                if part:
                    factor /= self._eval_mult(part)
        else:
            factor = self._eval_mult(expr)
        
        return factor
    
    
    def _eval_mult(self, expr):
        """Evaluar multiplicaciones: kN*m**2"""
        factor = 1.0
        
        # Preservar exponentes **
        expr = expr.replace('**', '^^^')
        
        # Dividir por *
        parts = [p.strip() for p in expr.split('*') if p.strip()]
        
        for part in parts:
            part = part.replace('^^^', '**')  # Restaurar **
            
            # ¿Es placeholder temporal?
            if part.startswith('_R') and hasattr(self, '_temp') and part in self._temp:
                factor *= self._temp[part]
            else:
                factor *= self._get_factor(part)
        
        return factor


    def _get_factor(self, unit_str):
        """Obtener factor de unidad simple con exponentes"""
        import re
        
        exponent = 1
        base_unit = unit_str
        
        # Detectar exponentes: m**2, m², m2
        if '**' in unit_str:
            parts = unit_str.split('**')
            base_unit = parts[0]
            exponent = int(parts[1])
        elif unit_str.endswith('²'):
            base_unit = unit_str[:-1]
            exponent = 2
        elif unit_str.endswith('³'):
            base_unit = unit_str[:-1]
            exponent = 3
        elif re.search(r'\d+$', unit_str):
            match = re.search(r'([a-zA-Z]+)(\d+)$', unit_str)
            if match:
                base_unit = match.group(1)
                exponent = int(match.group(2))
        
        # Obtener factor base usando atributos de la clase
        factors = {
            'm': self.m, 'cm': self.cm, 'mm': self.mm, 'inch': self.inch, 'ft': self.ft,
            'N': self.N, 'kN': self.kN, 'kgf': self.kgf, 'tonf': self.tonf, 'lb': self.lb,
            'kg': self.kg, 'g': self.g, 's': self.s, 'Pa': self.Pa, 'MPa': self.MPa
        }
        
        if base_unit not in factors:
            available = ', '.join(sorted(factors.keys()))
            raise ValueError(f"Unidad '{base_unit}' no reconocida. Disponibles: {available}")
        
        return factors[base_unit] ** exponent