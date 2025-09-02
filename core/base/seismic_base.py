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
        
        # Parámetros de deriva por defecto
        self.max_drift = 0.007  # Límite por defecto para concreto armado
        self.is_regular = True  # Regularidad estructural por defecto

        # Unidades por defecto
        self.u_f = 'tonf'
        self.u_d = 'mm'
        self.u_h = 'm'
        
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

    def set_units(self, units_dict):
        """Establecer unidades de trabajo"""
        self.u_h = units_dict.get('alturas', 'm')
        self.u_d = units_dict.get('desplazamientos', 'mm')  
        self.u_f = units_dict.get('fuerzas', 'tonf')

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
            # Cortantes basales por dirección
            self.Vdx = 0.0  # Dinámico X
            self.Vdy = 0.0  # Dinámico Y  
            self.Vsx = 0.0  # Estático X
            self.Vsy = 0.0  # Estático Y
            
            # Factores de escala
            self.FEx = 0.0
            self.FEy = 0.0


    def _create_shear_figure(self, table, sx, sy, analysis_type):
        """Crear figura de cortantes siguiendo lógica original"""
        from matplotlib.figure import Figure
        import numpy as np
        from core.utils.unit_tool import Units
        u = Units()
        
        try:
            # Configurar unidades por defecto si no existen
            u_f = getattr(self, 'u_f', 'tonf')
            u_h = getattr(self, 'u_h', 'm')
            # Separar cortantes X e Y
            shear_x_data = table[table['OutputCase'].isin(sx)]['V'].values
            shear_y_data = table[table['OutputCase'].isin(sy)]['V'].values

            
            # Agregar cero en la base
            shear_x = np.append([0.], np.abs(shear_x_data))
            shear_y = np.append([0.], np.abs(shear_y_data))
            
            # Obtener alturas (de Top locations)
            heights_data = table[table['OutputCase'].isin(sx) & (table['Location']=='Top')]['Height'][::-1].cumsum()
            
            # Crear array extendido para escalones
            heights_extended = []
            for h in heights_data[::-1]:
                heights_extended.extend([h, h])
            heights_extended.append(0)
            heights_extended = np.array(heights_extended)
            
            # Convertir unidades
            shear_x *= u.to_unit(1,u_f)
            shear_y *= u.to_unit(1,u_f)
            heights_extended *= u.to_unit(1,u_h)
            
            # Crear figura
            fig = Figure(figsize=(6, 4), dpi=100)
            ax = fig.add_subplot(111)
            
            # Límites del gráfico
            max_height = max(heights_extended) * 1.05 if len(heights_extended) > 0 else 10
            max_shear = max(max(shear_x), max(shear_y)) * 1.02
            
            ax.set_ylim(0, max_height)
            ax.set_xlim(0, max_shear)
            
            # Plotear líneas
            ax.plot(shear_x, heights_extended, 'r-', label='$V_x$', linewidth=2)
            ax.plot(shear_y, heights_extended, 'b-', label='$V_y$', linewidth=2)
            
            # Marcadores
            ax.scatter(shear_x, heights_extended, color='r', marker='x', s=30)
            ax.scatter(shear_y, heights_extended, color='b', marker='x', s=30)
            
            # Labels y formato
            ax.set_xlabel(f'Fuerza cortante ({u_f})')
            ax.set_ylabel(f'Altura ({u_h})')
            ax.grid(True, linestyle='--', alpha=0.7)
            ax.legend(loc='upper right')
            
            title = 'Cortantes Dinámicos' if analysis_type == 'dynamic' else 'Cortantes Estáticos'
            ax.set_title(title)
            
            return fig
            
        except Exception as e:
            print(f"Error creando figura {analysis_type}: {e}")
            return None
        
    def calculate_displacements(self, SapModel, use_displacement_combo=False):
        """Calcular desplazamientos laterales desde ETABS"""
        from core.utils.etabs_utils import set_units, get_table, get_story_data, get_unique_cases
        from core.utils.unit_tool import Units
        from matplotlib.figure import Figure
        import numpy as np
        
        try:
            set_units(SapModel, 'Ton_mm_C')
            u = Units()
            
            # Determinar casos de carga
            if use_displacement_combo:
                # Usar combinaciones directas
                x_cases = [self.loads.seism_loads.get('dx', '')]
                y_cases = [self.loads.seism_loads.get('dy', '')]
            else:
                # Usar casos únicos de las combinaciones dinámicas
                sdx = self.loads.seism_loads.get('SDX', '')
                sdy = self.loads.seism_loads.get('SDY', '')
                
                x_cases = get_unique_cases(SapModel, sdx) if sdx else [sdx]
                y_cases = get_unique_cases(SapModel, sdy) if sdy else [sdy]
            
            # Filtrar casos vacíos
            x_cases = [c for c in x_cases if c]
            y_cases = [c for c in y_cases if c]
            
            if not x_cases or not y_cases:
                return False
            
            # Configurar visualización
            all_cases = x_cases + y_cases
            SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(all_cases)
            SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(all_cases)
            
            # Obtener datos
            success, table = get_table(SapModel, 'Story Max Over Avg Displacements')
            stories = get_story_data(SapModel)
            
            if not success or table is None or stories is None:
                return False
            
            # Procesar tabla según lógica original
            table = table[['Story','OutputCase','Direction','Maximum']]
            table = table[
                ((table['OutputCase'].isin(x_cases)) & (table['Direction']=='X')) |
                ((table['OutputCase'].isin(y_cases)) & (table['Direction']=='Y'))
            ]
            
            table = table.merge(stories[['Story','Height']], on='Story',sort=False)
            table[['Maximum','Height']] = table[['Maximum','Height']].astype(float)
            
            # Agrupar por piso y dirección
            story_order = stories['Story'].unique()
            table = table.groupby(['Story','Direction'], as_index=False, sort=False)[['Maximum','Height']].max()
            
            # Pivot X e Y
            disp_x = table[table['Direction']=='X']
            disp_y = table[table['Direction']=='Y']
            table = disp_x.merge(disp_y, on=['Story','Height'], how='outer', suffixes=('_x', '_y'),sort=False)
            table[['Maximum_x','Maximum_y']] = table[['Maximum_x','Maximum_y']].fillna(0)
            
            # Ordenar por pisos
            table = table.sort_values(by='Story', 
                                    key=lambda x: x.map({v: i for i, v in enumerate(story_order)}))
            table = table[['Story','Height','Maximum_x','Maximum_y']]
            
            # Aplicar unidades
            table[['Height','Maximum_x','Maximum_y']] *= u.mm
            self.tables.displacements = table
            
            # Preparar arrays para gráfico
            disp_x_raw = np.array(table['Maximum_x'])[::-1]
            disp_x_raw = np.append([0.], disp_x_raw)
            
            disp_y_raw = np.array(table['Maximum_y'])[::-1] 
            disp_y_raw = np.append([0.], disp_y_raw)
            
            heights = np.array(table['Height'])[::-1].cumsum()
            heights = np.append([0.], heights)
            
            # Aplicar factores de amplificación si no es combo directo
            if not use_displacement_combo:
                is_regular = getattr(self, 'is_regular', True)
                Rx = getattr(self, 'Rx', 8.0)
                Ry = getattr(self, 'Ry', 8.0)
                
                factor = 0.75 if is_regular else 0.85
                disp_x_raw *= factor * Rx
                disp_y_raw *= factor * Ry
            
            # Almacenar para otras funciones
            self.disp_x = disp_x_raw
            self.disp_y = disp_y_raw  
            self.disp_h = heights
            
            
            # Almacenar resultados para la UI
            if hasattr(self, 'tables') and hasattr(self.tables, 'displacements'):
                disp_data = self.tables.displacements
                if disp_data is not None and not disp_data.empty:
                    # Encontrar máximos en cada dirección
                    # Las columnas pueden variar, buscar las correctas
                    x_cols = [col for col in disp_data.columns if 'x' in col.lower() and ('max' in col.lower() or 'disp' in col.lower())]
                    y_cols = [col for col in disp_data.columns if 'y' in col.lower() and ('max' in col.lower() or 'disp' in col.lower())]
                    
                    # Si no encontramos columnas específicas, usar genéricas
                    if not x_cols and 'Maximum_x' in disp_data.columns:
                        x_cols = ['Maximum_x']
                    if not y_cols and 'Maximum_y' in disp_data.columns:
                        y_cols = ['Maximum_y']
                        
                    max_x = disp_data[x_cols[0]].max() if x_cols else 0.0
                    max_y = disp_data[y_cols[0]].max() if y_cols else 0.0
                    
                    self.displacement_results = {
                        'max_displacement_x': max_x,
                        'max_displacement_y': max_y
                    }
                else:
                    # Fallback usando arrays si la tabla no está disponible
                    max_x = max(abs(x) for x in self.disp_x) if hasattr(self, 'disp_x') and len(self.disp_x) > 0 else 0.0
                    max_y = max(abs(y) for y in self.disp_y) if hasattr(self, 'disp_y') and len(self.disp_y) > 0 else 0.0
                    
                    self.displacement_results = {
                        'max_displacement_x': max_x,
                        'max_displacement_y': max_y
                    }
                    
            # Recordar si se usó combo para poder regenerar después
            self._used_displacement_combo = use_displacement_combo
                        
            return True
            
        except Exception as e:
            print(f"Error calculando desplazamientos: {e}")
            return False

    def _create_displacement_figure(self, disp_x, disp_y, heights, use_combo):
        """Crear figura de desplazamientos"""
        from matplotlib.figure import Figure
        from core.utils.unit_tool import Units
        u = Units()
        
        u_d = getattr(self, 'u_d', 'mm')
        u_h = getattr(self, 'u_h', 'm')
        
        # Convertir a unidades de display
        disp_x_plot = u.to_unit(disp_x,u_d)
        disp_y_plot = u.to_unit(disp_y,u_d)
        heights_plot = u.to_unit(heights,u_h)
        
        fig = Figure(figsize=(6,4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.set_ylim(0, max(heights_plot)*1.05)
        ax.set_xlim(0, max(max(disp_x_plot), max(disp_y_plot))*1.1)
        
        if not use_combo:
            Rx = getattr(self, 'Rx', 8.0)
            Ry = getattr(self, 'Ry', 8.0)
            ax.plot(disp_x_plot, heights_plot, 'r', label=f'X (R={Rx:.2f})')
            ax.plot(disp_y_plot, heights_plot, 'b', label=f'Y (R={Ry:.2f})')
        else:
            ax.plot(disp_x_plot, heights_plot, 'r', label='Desplazamientos en X')
            ax.plot(disp_y_plot, heights_plot, 'b', label='Desplazamientos en Y')
        
        ax.scatter(disp_x_plot, heights_plot, color='r', marker='x')
        ax.scatter(disp_y_plot, heights_plot, color='b', marker='x')
        
        ax.set_xlabel(f'Desplazamientos ({u_d})')
        ax.set_ylabel(f'h ({u_h})')
        ax.grid(linestyle='dotted', linewidth=1)
        ax.legend()
        
        return fig
    
    def calculate_drifts(self, SapModel, use_displacement_combo=False):
        """Calcular desplazamientos laterales desde ETABS"""
        from core.utils.etabs_utils import set_units, get_table, get_story_data, get_unique_cases
        from core.utils.unit_tool import Units
        from matplotlib.figure import Figure
        import numpy as np
        
        try:
            set_units(SapModel, 'Ton_mm_C')
            u = Units()
            
            # Determinar casos de carga
            if use_displacement_combo:
                # Usar combinaciones directas
                x_cases = [self.loads.seism_loads.get('dx', '')]
                y_cases = [self.loads.seism_loads.get('dy', '')]
            else:
                # Usar casos únicos de las combinaciones dinámicas
                sdx = self.loads.seism_loads.get('SDX', '')
                sdy = self.loads.seism_loads.get('SDY', '')
                
                x_cases = get_unique_cases(SapModel, sdx) if sdx else [sdx]
                y_cases = get_unique_cases(SapModel, sdy) if sdy else [sdy]
            
            # Filtrar casos vacíos
            x_cases = [c for c in x_cases if c]
            y_cases = [c for c in y_cases if c]
            
            if not x_cases or not y_cases:
                return False
            
            # Configurar visualización
            all_cases = x_cases + y_cases
            SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(all_cases)
            SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(all_cases)
            
            # Obtener datos
            success, table = get_table(SapModel, 'Diaphragm Max Over Avg Drifts')
            stories = get_story_data(SapModel)
            story_order = stories['Story'].unique() 
            
            if not success or table is None or stories is None:
                return False
            # Procesar tabla
            table[['Max Drift']] = table[['Max Drift']].astype(float)
            table = table[
                ((table['OutputCase'].isin(x_cases)) & table['Item'].str.contains('x',case=False)) |
                ((table['OutputCase'].isin(y_cases)) & table['Item'].str.contains('y',case=False))
            ]
            
            if use_displacement_combo:
                table['OutputCase'] = table['OutputCase']+table['StepType']
                table['Drifts'] = table['Max Drift']
            else:
                if self.is_regular:
                    table['Drifts'] = table['Max Drift']*0.75
                else:
                    table['Drifts'] = table['Max Drift']*0.85
                table['Drifts'] = table.apply((lambda row: row['Drifts']*self.Ry if row['OutputCase'].isin(y_cases) else row['Drifts']*self.Rx),axis=1)
                
            table = table[['Story','OutputCase','Item','Drifts']]
            table = table.assign(Drift_Check = (table['Drifts'] < self.max_drift).apply(lambda x: 'Cumple' if x else 'No Cumple'))
            
            stories['Height'] = stories['Height'] .astype(float)
            table = table.merge(stories[['Story','Height']], on='Story',sort=False)
            
            # Agrupar por piso y dirección
            table = table.groupby(['Story','Item'], as_index=False, sort=False)[['Drifts','Height']].max()

            
            # Pivot X e Y
            drifts_x = table[table['Item'].str.contains(r'^Diaph .* X$')]
            drifts_y = table[table['Item'].str.contains(r'^Diaph .* Y$')]
            table = drifts_x.merge(drifts_y, on=['Story','Height'], how='outer', suffixes=('_x', '_y'),sort=False)
            table[['Drifts_x','Drifts_y']] = table[['Drifts_x','Drifts_y']].fillna(0)
            
            # Ordenar por pisos
            table = table[['Story','Height','Drifts_x','Drifts_y']]
            table = table.sort_values(by='Story', 
                         key=lambda x: x.map({v: i for i, v in enumerate(story_order)}))
            
            # Aplicar unidades
            table[['Height']] *= u.mm
            self.tables.drifts = table
            
            # Preparar arrays para gráfico
            drift_x_raw = np.array(table['Drifts_x'])[::-1]
            drift_x_raw = np.append([0.], drift_x_raw)
            
            drift_y_raw = np.array(table['Drifts_y'])[::-1] 
            drift_y_raw = np.append([0.], drift_y_raw)
            
            heights = np.array(table['Height'])[::-1].cumsum()
            heights = np.append([0.], heights)
            
            
            # Almacenar para otras funciones
            self.drift_x = drift_x_raw
            self.drift_y = drift_y_raw  
            self.drift_h = heights
            
            # Crear gráfico
            self.fig_drifts = self._create_drift_figure(
                drift_x_raw, drift_y_raw, heights, use_displacement_combo
            )
            
            # Almacenar resultados para la UI con información del piso
            if hasattr(self, 'tables') and hasattr(self.tables, 'drifts'):
                drift_data = self.tables.drifts
                
            if drift_data is not None and not drift_data.empty:
                # Encontrar máximos y sus pisos correspondientes
                max_x = drift_data['Drifts_x'].max()
                max_y = drift_data['Drifts_y'].max()
                
                max_x_idx = drift_data['Drifts_x'].idxmax()
                max_y_idx = drift_data['Drifts_y'].idxmax()
                
                story_x = drift_data.loc[max_x_idx, 'Story'] if not drift_data.empty else 'N/A'
                story_y = drift_data.loc[max_y_idx, 'Story'] if not drift_data.empty else 'N/A'
                
                # Obtener límite desde la instancia o usar por defecto
                limit = getattr(self, 'max_drift', 0.007)
                
                self.drift_results = {
                    'max_drift_x': max_x,
                    'max_drift_y': max_y,
                    'story_max_x': story_x,
                    'story_max_y': story_y,
                    'limit': limit,
                    'complies_x': max_x <= limit,
                    'complies_y': max_y <= limit,
                    'complies_overall': (max_x <= limit) and (max_y <= limit)}
                    
            # Recordar si se usó combo para poder regenerar después  
            self._used_drift_combo = use_displacement_combo
            
            return True
            
        except Exception as e:
            print(f"Error calculando desplazamientos: {e}")
            return False
        
    def _create_drift_figure(self, drift_x, drift_y, heights, use_combo):
        """Crear figura de desplazamientos"""
        from matplotlib.figure import Figure
        from core.utils.unit_tool import Units
        u = Units()
        
        u_h = getattr(self, 'u_h', 'm')
        
        # Convertir a unidades de display
        disp_x_plot = drift_x
        disp_y_plot = drift_y
        heights_plot = u.to_unit(heights,u_h)
        
        fig = Figure(figsize=(6,4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.set_ylim(0, max(heights_plot)*1.05)
        ax.set_xlim(0, max(max(disp_x_plot), max(disp_y_plot))*1.1)
        
        if not use_combo:
            Rx = getattr(self, 'Rx', 8.0)
            Ry = getattr(self, 'Ry', 8.0)
            ax.plot(disp_x_plot, heights_plot, 'r', label=f'X (R={Rx:.2f})')
            ax.plot(disp_y_plot, heights_plot, 'b', label=f'Y (R={Ry:.2f})')
        else:
            ax.plot(disp_x_plot, heights_plot, 'r', label='Desplazamientos en X')
            ax.plot(disp_y_plot, heights_plot, 'b', label='Desplazamientos en Y')
        
        ax.scatter(disp_x_plot, heights_plot, color='r', marker='x')
        ax.scatter(disp_y_plot, heights_plot, color='b', marker='x')
        
        ax.set_xlabel(f'Desplazamientos Relativos')
        ax.set_ylabel(f'h ({u_h})')
        ax.grid(linestyle='dotted', linewidth=1)
        ax.legend()
        
        return fig

    def calculate_torsional_irregularity(self, SapModel, cases_x, cases_y, half_condition=True, ratio_max=1.2):
        """
        Calcula irregularidad torsional según norma
        
        Parameters
        ----------
        SapModel : objeto ETABS
        cases_x : list - Casos de carga en dirección X
        cases_y : list - Casos de carga en dirección Y  
        half_condition : bool - Aplicar condición Dmax/2
        ratio_max : float - Ratio máximo permitido
        
        Returns
        -------
        bool : True si el cálculo fue exitoso
        """
        try:
            # Configurar casos para visualización
            all_cases = cases_x + cases_y
            SapModel.DatabaseTables.SetLoadCasesSelectedForDisplay(all_cases)
            SapModel.DatabaseTables.SetLoadCombinationsSelectedForDisplay(all_cases)
            from core.utils.etabs_utils import get_table, set_units
            from core.utils.unit_tool import Units
            set_units(SapModel, 'Ton_mm_C')
            
            # Obtener tabla de derivas
            success, drift_table = get_table(SapModel, 'Diaphragm Max Over Avg Drifts')
            if not success or drift_table is None:
                return False
            
            # Procesar y almacenar resultados
            drift_table[['Max Drift', 'Avg Drift', 'Ratio']] = \
                drift_table[['Max Drift', 'Avg Drift', 'Ratio']].astype(float)
            drift_table = drift_table[
                (drift_table['OutputCase'].isin(cases_x) & 
                drift_table['Item'].str.contains('x',case=False)) |
                (drift_table['OutputCase'].isin(cases_y) & 
                drift_table['Item'].str.contains('y',case=False))
                ]
            torsion_table_data = drift_table[
                ['Story', 'OutputCase', 'Item', 'Max Drift', 'Avg Drift', 'Ratio']].copy()
            self.torsion_table_data = torsion_table_data
            self.torsion_results = self._process_torsion_data(torsion_table_data, cases_x, cases_y, half_condition, ratio_max)
            
            return True
            
        except Exception as e:
            print(f"Error calculando irregularidad torsional: {e}")
            return False
        
    def _process_torsion_data(self, drift_table, cases_x, cases_y, half_condition=True, ratio_max=1.2):
        """Procesar datos de torsión con validaciones de norma"""
        
        results = {
            'delta_max_x': 0.0, 'delta_prom_x': 0.0, 'ratio_x': 0.0,
            'delta_max_y': 0.0, 'delta_prom_y': 0.0, 'ratio_y': 0.0,
            'is_irregular_x': False, 'is_irregular_y': False
        }
        
        try:
            # Procesar por dirección
            for direction, cases in [('x', cases_x), ('y', cases_y)]:
                dir_data = drift_table[
                    (drift_table['OutputCase'].isin(cases)) & 
                    (drift_table['Item'].str.contains(direction, case=False))
                ]
                
                if not dir_data.empty:
                    idx_max = dir_data['Ratio'].idxmax()
                    max_drift = dir_data['Max Drift'].loc[idx_max]
                    avg_drift = dir_data['Avg Drift'].loc[idx_max]
                    ratio = dir_data['Ratio'].loc[idx_max]
                    
                    results[f'delta_max_{direction}'] = max_drift
                    results[f'delta_prom_{direction}'] = avg_drift
                    results[f'ratio_{direction}'] = ratio
                    
                    # Evaluar irregularidad
                    is_irregular = ratio > ratio_max
                    if half_condition and hasattr(self, 'max_drift_x'):
                        max_allowed = getattr(self, f'max_drift_{direction}', 0.007) / 2
                        is_irregular = is_irregular and (max_drift >= max_allowed)
                    
                    results[f'is_irregular_{direction}'] = is_irregular
                    
        except Exception as e:
            print(f"Error procesando datos de torsión: {e}")
        
        return results
    
    
    def _create_spectrum_figure(self, T, Sa, country='generic'):
        """Crear figura del espectro de respuesta"""
        from matplotlib.figure import Figure
        
        fig = Figure(figsize=(6, 4), dpi=100)
        ax = fig.add_subplot(111)
        
        ax.plot(T, Sa, 'r-', linewidth=2, label='Espectro Elástico')
        ax.set_xlabel('Período T (s)')
        ax.set_ylabel('Sa (g)')
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend()
        
        titles = {
            'bolivia': 'Espectro CNBDS 2023',
            'peru': 'Espectro E.030',
            'generic': 'Espectro de Respuesta'
        }
        ax.set_title(titles.get(country, titles['generic']))
        
        return fig
    
    def update_all_data(self):
        """Actualizar todos los datos - Usar método completo"""
        if not self.SapModel:
            if not self._connect_etabs():
                return
        
        try:
            print("🔄 Actualizando todos los datos...")
            
            # Usar método completo que incluye modal y cortantes
            self._auto_update_modal_analysis()
            
            print("✅ Actualización completa")
            
        except Exception as e:
            print(f"Error actualizando datos: {e}")
            self.show_warning(f"Error actualizando datos: {str(e)}")