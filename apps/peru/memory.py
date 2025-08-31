"""
Generación de memoria LaTeX para Perú - E.030
Renombrado desde memory_peru.py y simplificado usando MemoryBase
"""

import numpy as np
from pathlib import Path
import shutil

from core.base.memory_base import MemoryBase
from core.utils.table_generator import PeruTableGenerator
from core.utils.latex_utils import replace_template_variables
from core.utils.file_utils import ensure_directory_exists


class PeruMemoryGenerator(MemoryBase):
    """Generador de memorias LaTeX para análisis sísmico Perú - E.030"""
    
    def __init__(self, seismic_instance, output_dir):
        super().__init__(seismic_instance, output_dir)
        self.country = 'peru'
        
        # Path al template específico de Perú
        self.templates_dir = Path(__file__).parent / 'resources' / 'templates'
        
        # Variables específicas de Perú para el template
        self.template_variables = self._get_peru_variables()

    def get_default_template_path(self) -> str:
        """Obtener path del template por defecto de Perú"""
        return str(self.templates_dir / 'plantilla_peru.ltx')

    def generate_memory(self) -> Path:
        """Generar memoria completa para Perú - E.030"""
        # Validar datos mínimos
        if not self.validate_seismic_data():
            raise ValueError("Datos sísmicos incompletos para generar memoria")
        
        # Preparar estructura de salida
        self.setup_output_structure()
        
        # Cargar template
        content = self.load_template()
        
        # Reemplazar contenido
        content = self.replace_basic_parameters(content)
        content = self._replace_peru_specific_content(content)
        content = self.insert_content_sections(content)
        
        # Generar recursos
        self.actualize_images_and_tables()
        self.generate_spectrum_data()
        
        # Generar tablas usando generador centralizado
        content = self.insert_tables(content)
        
        # Guardar archivo final
        tex_file = self.save_memory(content, 'memoria_peru.tex')
        
        # Compilar a PDF
        self.compile_latex(tex_file, run_twice=True)
        
        return tex_file

    def _get_peru_variables(self) -> dict:
        """Obtener variables específicas de Perú para el template"""
        variables = {}
        
        # Parámetros sísmicos E.030
        for param in ['Z', 'U', 'S', 'Tp', 'Tl']:  # U en lugar de I
            if hasattr(self.seismic, param):
                variables[param] = getattr(self.seismic, param)
        
        # Factor de reducción
        if hasattr(self.seismic, 'R'):
            variables['R'] = getattr(self.seismic, 'R')
        
        # Sa máxima para gráficos (usa U en lugar de I)
        if hasattr(self.seismic, 'Sa_max'):
            variables['Samax'] = self.seismic.Sa_max
        elif all(hasattr(self.seismic, param) for param in ['Z', 'U', 'S', 'R']):
            # C = 2.5 (factor del espectro)
            variables['Samax'] = round(2.5 * self.seismic.Z * self.seismic.U * self.seismic.S / self.seismic.R, 3)
        
        # Cortantes y otros datos
        if hasattr(self.seismic, 'data'):
            data = self.seismic.data
            variables.update({
                'Vdx': getattr(data, 'Vdx', 0.0),
                'Vdy': getattr(data, 'Vdy', 0.0),
                'Vsx': getattr(data, 'Vsx', 0.0),
                'Vsy': getattr(data, 'Vsy', 0.0),
                'FEx': getattr(data, 'FEx', 1.0),
                'FEy': getattr(data, 'FEy', 1.0)
            })
        
        return variables

    def replace_country_variables(self, content: str) -> str:
        """Reemplazar variables específicas de Perú en el template"""
        return replace_template_variables(content, self.template_variables)

    def _create_table_generator(self):
        """Crear generador de tablas específico para Perú"""
        return PeruTableGenerator(self.seismic)

    def _replace_peru_specific_content(self, content: str) -> str:
        """Reemplazar contenido específico de Perú"""
        
        # Reemplazar variables específicas de E.030
        for var_name, var_value in self.template_variables.items():
            patterns = [
                f'@{var_name}.0nn',
                f'@{var_name}.2nu',
                f'@{var_name}.2F4',
                f'@{var_name}'
            ]
            
            for pattern in patterns:
                if pattern in content:
                    if '.0nn' in pattern:
                        replacement = str(var_value)
                    elif '.2nu' in pattern or '.2F4' in pattern:
                        replacement = f'{float(var_value):.2f}' if isinstance(var_value, (int, float)) else str(var_value)
                    else:
                        replacement = str(var_value)
                    
                    content = content.replace(pattern, replacement)
        
        return content

    def generate_spectrum_data(self):
        """Generar datos del espectro específico de Perú"""
        try:
            if hasattr(self.seismic, 'espectro_peru'):
                T, Sa = self.seismic.espectro_peru()
            else:
                # Generar espectro básico con parámetros E.030
                T = np.linspace(0.1, 4.0, 100)
                Z = getattr(self.seismic, 'Z', 0.25)
                U = getattr(self.seismic, 'U', 1.0)
                S = getattr(self.seismic, 'S', 1.2)
                Sa = 2.5 * Z * U * S * np.ones_like(T)  # Simplificado
            
            data = np.column_stack((T, Sa))
            np.savetxt(self.output_dir / 'espectro_peru.txt', data, fmt="%.4f")
            
        except Exception as e:
            print(f"Error generando datos espectro Perú: {e}")
            super().generate_spectrum_data()  # Fallback al método base


    def generate_memory(self) -> Path:
        """
        Generar memoria de cálculo con validación previa para Perú
        
        Returns:
            Path al archivo LaTeX generado
            
        Raises:
            ValueError: Si faltan datos requeridos
        """
        print("\n🔍 VALIDANDO DATOS PARA PERÚ (E.030)...")
        
        # Validar datos antes de proceder
        is_valid, errors = self.validate_required_data()
        
        if not is_valid:
            error_msg = "❌ No se puede generar la memoria para Perú. Faltan los siguientes elementos:\n\n"
            error_msg += "\n".join(errors)
            error_msg += "\n\n💡 Solución: Complete los elementos faltantes antes de generar la memoria."
            
            print(error_msg)
            raise ValueError(error_msg)
        
        print("✅ Validación exitosa. Generando memoria Perú...")
        
        try:
            # 1. Configurar estructura de salida
            self.setup_output_structure()
            
            # 2. Cargar template de Perú
            content = self.load_template()
            
            # 3. Reemplazar parámetros básicos
            content = self.replace_basic_parameters(content)
            
            # 4. Reemplazar variables específicas de Perú
            content = self.replace_country_variables(content)
            
            # 5. Insertar secciones de contenido
            content = self.insert_content_sections(content)
            
            # 6. Generar datos del espectro Perú
            print("📈 GENERANDO ESPECTRO PERÚ (E.030)...")
            self.generate_spectrum_data()
            
            # 7. Generar todos los graficos
            self._force_generate_missing_plots()
            
            # 8. Actualizar imágenes y tablas existentes
            print("\n📁 PROCESANDO IMÁGENES Y TABLAS PERÚ...")
            self.actualize_images_and_tables()
            
            # 9. Insertar tablas en memoria
            print("📊 INSERTANDO TABLAS PERÚ...")
            content = self.insert_existing_tables_in_memory(content)
            
            # 10. Guardar archivo LaTeX
            print("💾 GUARDANDO MEMORIA PERÚ...")
            tex_file = self.save_memory(content, 'memoria_peru.tex')
            
            print(f"✅ Memoria Perú generada exitosamente: {tex_file}")
            
            # 11. Compilar a PDF si es posible
            try:
                print("\n🔄 COMPILANDO PDF PERÚ...")
                self.compile_latex(tex_file, run_twice=True)
                print("✅ PDF Perú generado exitosamente")
            except Exception as pdf_error:
                print(f"⚠️ Advertencia: Error compilando PDF Perú: {pdf_error}")
                print("📄 Archivo LaTeX disponible, compile manualmente si es necesario")
            
            return tex_file
            
        except Exception as e:
            error_msg = f"❌ Error generando memoria Perú: {e}"
            print(error_msg)
            raise Exception(error_msg)

    def _copy_static_resources(self):
        """Copiar recursos estáticos específicos de Perú"""
        print("  🇵🇪 Copiando recursos Perú...")
        
        # 1. Recursos del directorio del país
        peru_resources = Path(__file__).parent / 'resources' / 'images'
        if peru_resources.exists():
            self._copy_from_directory(peru_resources, "recursos Perú")
        else:
            print(f"    ℹ️ Directorio no encontrado: {peru_resources}")
        
        # 2. Recursos compartidos (si existen)
        shared_resources = Path(__file__).parent.parent.parent / 'shared' / 'resources' / 'images'
        if shared_resources.exists():
            self._copy_from_directory(shared_resources, "recursos compartidos")
        else:
            print(f"    ℹ️ Directorio compartido no encontrado: {shared_resources}")
            
    def _copy_from_directory(self, source_dir: Path, description: str):
        """Copiar imágenes desde un directorio"""
        copied_count = 0
        extensions = ['*.png', '*.jpg', '*.jpeg', '*.pdf', '*.bmp']
        
        for ext in extensions:
            for image_file in source_dir.glob(ext):
                try:
                    dest_path = self.images_dir / image_file.name
                    shutil.copy2(image_file, dest_path)
                    print(f"    ✓ {image_file.name} ({description})")
                    copied_count += 1
                except Exception as e:
                    print(f"    ❌ Error copiando {image_file.name}: {e}")
        
        if copied_count == 0:
            print(f"    ℹ️ No se encontraron imágenes en {description}")
