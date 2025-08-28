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