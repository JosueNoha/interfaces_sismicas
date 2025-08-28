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

    def __setattr__(self, name, value):
        """Permitir asignación dinámica de atributos"""
        if not hasattr(self, '_dynamic_attrs'):
            super().__setattr__('_dynamic_attrs', {})
        
        # Atributos fijos van normalmente
        fixed_attrs = {'config', 'proyecto', 'ubicacion', 'autor', 'fecha', 
                    'urls_imagenes', 'descriptions', 'loads', 'tables', 'data', '_dynamic_attrs'}
        
        if name in fixed_attrs or name.startswith('_'):
            super().__setattr__(name, value)
        else:
            self._dynamic_attrs[name] = value

    def __getattr__(self, name):
        """Recuperar atributos dinámicos"""
        if hasattr(self, '_dynamic_attrs') and name in self._dynamic_attrs:
            return self._dynamic_attrs[name]
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
    
    def get_modal_analysis(self):
        """Obtener análisis modal desde ETABS"""
        try:
            from core.utils import etabs_utils as etb
            # Intentar conectar con ETABS
            EtabsObject, SapModel = etb.connect_to_etabs()
            if not SapModel:
                return None
                
            # Obtener datos modales
            modal_data = etb.get_modal_data(SapModel)
            if modal_data is not None and not modal_data.empty:
                # Buscar períodos fundamentales
                modal_x = modal_data[modal_data['UX'] > 0.1] if 'UX' in modal_data.columns else modal_data
                modal_y = modal_data[modal_data['UY'] > 0.1] if 'UY' in modal_data.columns else modal_data
                
                Tx = modal_x.iloc[0]['Period'] if not modal_x.empty and 'Period' in modal_x.columns else 1.0
                Ty = modal_y.iloc[0]['Period'] if not modal_y.empty and 'Period' in modal_y.columns else 1.2
                
                # Guardar datos en el objeto
                self.data.Tx = float(Tx)
                self.data.Ty = float(Ty)
                self.tables.modal = modal_data
                
                return {'Tx': self.data.Tx, 'Ty': self.data.Ty}
            return None
        except Exception as e:
            print(f"Error en análisis modal: {e}")
            return None

    def calculate_shear_forces(self):
        """Calcular fuerzas cortantes desde ETABS"""
        try:
            from core.utils import etabs_utils as etb
            EtabsObject, SapModel = etb.connect_to_etabs()
            if not SapModel:
                return None
                
            # Obtener fuerzas de piso (cortantes basales)
            base_shear = etb.get_base_shear(SapModel)
            if base_shear is not None and not base_shear.empty:
                # Extraer cortantes en X e Y
                Vx = base_shear['VX'].abs().max() if 'VX' in base_shear.columns else 0.0
                Vy = base_shear['VY'].abs().max() if 'VY' in base_shear.columns else 0.0
                
                # Guardar datos
                self.data.Vdx = float(Vx)
                self.data.Vdy = float(Vy)
                
                return {'Vx': self.data.Vdx, 'Vy': self.data.Vdy}
            return None
        except Exception as e:
            print(f"Error calculando cortantes: {e}")
            return None

    def calculate_displacements(self):
        """Calcular desplazamientos desde ETABS"""
        try:
            from core.utils import etabs_utils as etb
            EtabsObject, SapModel = etb.connect_to_etabs()
            if not SapModel:
                return None
                
            # Obtener desplazamientos de piso
            displacements = etb.get_displacement_data(SapModel)
            if displacements is not None and not displacements.empty:
                # Extraer desplazamientos máximos
                max_x = displacements['UX'].abs().max() if 'UX' in displacements.columns else 0.0
                max_y = displacements['UY'].abs().max() if 'UY' in displacements.columns else 0.0
                
                self.tables.displacements = displacements
                return {'max_x': float(max_x), 'max_y': float(max_y)}
            return None
        except Exception as e:
            print(f"Error calculando desplazamientos: {e}")
            return None

    def calculate_drifts(self):
        """Calcular derivas desde ETABS"""
        try:
            from core.utils import etabs_utils as etb
            EtabsObject, SapModel = etb.connect_to_etabs()
            if not SapModel:
                return None
                
            # Obtener derivas de entrepiso
            drifts = etb.get_drift_data(SapModel)
            if drifts is not None and not drifts.empty:
                # Extraer derivas máximas
                max_drift_x = drifts['DriftX'].abs().max() if 'DriftX' in drifts.columns else 0.0
                max_drift_y = drifts['DriftY'].abs().max() if 'DriftY' in drifts.columns else 0.0
                
                self.tables.drift_table = drifts
                return {'max_drift_x': float(max_drift_x), 'max_drift_y': float(max_drift_y)}
            return None
        except Exception as e:
            print(f"Error calculando derivas: {e}")
            return None

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

    def set_descripcion(self, tipo, texto):
        """Establecer descripción personalizada"""
        if tipo in self.descriptions:
            self.descriptions[tipo] = texto.strip()

    def get_descripcion(self, tipo):
        """Obtener descripción (personalizada o por defecto)"""
        return self.descriptions.get(tipo, '')

    def set_imagen(self, tipo, url_path):
        """Establecer URL/path de imagen"""
        if tipo in self.urls_imagenes:
            self.urls_imagenes[tipo] = url_path

    def get_imagen(self, tipo):
        """Obtener URL/path de imagen"""
        return self.urls_imagenes.get(tipo)

    def get_configuracion(self, key, default=None):
        """Obtener valor de configuración específica del país"""
        return self.config.get(key, default)