"""
Clase base para análisis sísmico - Funcionalidad común entre Bolivia y Perú
"""

class SeismicBase:
    """Clase base para cálculos sísmicos comunes"""
    
    def __init__(self, config=None):
        """
        Inicializar con configuración específica del país
        config: diccionario con configuración del país
        """
        self.config = config or {}
        self.dynamic_attrs = {}  # ✅ Simple y sin recursión
        
        # Propiedades comunes del proyecto
        self.proyecto = "Edificación de Concreto Reforzado"
        self.ubicacion = self.config.get('ubicacion_defecto', "")
        self.autor = self.config.get('autor_defecto', "Yabar Ingenieros")
        self.fecha = ""
        
        # URLs o paths de imágenes
        self.urls_imagenes = {
            'portada': None,
            'planta': None,
            '3d': None,
            'defX': None,
            'defY': None
        }
        
        # Descripciones por defecto
        self.descriptions = {
            'descripcion': '''
            El edificio se considera empotrado en la base, la planta y el 3D del edificio se muestra en la siguiente figura.
            ''',
            'modelamiento': '''
            El edificio se modela en 3D considerando todos los elementos estructurales: columnas, vigas, losas y muros de corte si existen.
            Se considera el efecto de diafragma rígido en cada nivel.
            ''',
            'cargas': '''
            Se consideró 220 kgf/m2 de sobrecarga muerta (tabiquería y piso terminado) y 250 kgf/m2 de sobrecarga viva aplicado al área en planta del edificio.
            '''
        }

        # Clases internas para organizar datos
        self.loads = self.Loads()
        self.tables = self.Tables()
        self.data = self.Data()

    def set_dynamic_attr(self, name, value):
        """Establecer atributo dinámico"""
        self.dynamic_attrs[name] = value

    def get_dynamic_attr(self, name, default=None):
        """Obtener atributo dinámico"""
        return self.dynamic_attrs.get(name, default)

    def has_dynamic_attr(self, name):
        """Verificar si existe atributo dinámico"""
        return name in self.dynamic_attrs
    
    class Loads:
            """Manejo de cargas sísmicas"""
            def __init__(self):
                self.seism_loads = {}
                
            def set_seism_loads(self, seism_loads):
                self.seism_loads = seism_loads

    class Tables:
        """Manejo de tablas de resultados"""
        def __init__(self):
            pass

    class Data:
        """Almacenamiento de datos sísmicos - genérico"""
        def __init__(self):
            # Períodos fundamentales (común a todas las normas)
            self.Tx = 0.0
            self.Ty = 0.0
            
            # Peso sísmico (común)
            self.Ps = 0.0
            
            # Cortantes basales
            self.Vsx = 0.0
            self.Vsy = 0.0
            self.Vdx = 0.0
            self.Vdy = 0.0
            
            # Factores de escala
            self.FEx = 0.0
            self.FEy = 0.0