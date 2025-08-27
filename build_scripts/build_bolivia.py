#!/usr/bin/env python3
"""
Script para construir el ejecutable de la aplicación Bolivia
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def clean_build_dirs():
    """Limpia directorios de build anteriores"""
    dirs_to_clean = ['build', 'dist/bolivia', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"Limpiando directorio: {dir_name}")
            shutil.rmtree(dir_name)

def build_bolivia():
    """Construye el ejecutable de Bolivia usando PyInstaller"""
    print("=" * 60)
    print("CONSTRUYENDO APLICACIÓN ANÁLISIS SÍSMICO - BOLIVIA")
    print("=" * 60)
    
    # Verificar que estamos en el directorio correcto
    project_root = Path().resolve()
    spec_file = project_root / 'build_scripts' / 'bolivia.spec'
    
    if not spec_file.exists():
        print(f"ERROR: No se encuentra el archivo {spec_file}")
        sys.exit(1)
    
    # Limpiar directorios de build
    clean_build_dirs()
    
    try:
        # Ejecutar PyInstaller
        cmd = ['pyinstaller', '--clean', str(spec_file)]
        print(f"Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ BUILD EXITOSO")
        print(f"Ejecutable generado en: {project_root / 'dist' / 'AnalisisSismicoBolivia'}")
        
        # Verificar que el ejecutable se creó
        exe_path = project_root / 'dist' / 'AnalisisSismicoBolivia' / 'AnalisisSismicoBolivia.exe'
        if exe_path.exists():
            print(f"✅ Ejecutable verificado: {exe_path}")
            print(f"Tamaño: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("⚠️  Advertencia: No se encontró el archivo ejecutable")
        
    except subprocess.CalledProcessError as e:
        print("❌ ERROR EN BUILD:")
        print(f"Código de salida: {e.returncode}")
        print("STDOUT:")
        print(e.stdout)
        print("STDERR:")
        print(e.stderr)
        sys.exit(1)
    
    except Exception as e:
        print(f"❌ ERROR INESPERADO: {e}")
        sys.exit(1)

def main():
    """Función principal"""
    # Cambiar al directorio raíz del proyecto
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    
    print(f"Directorio de trabajo: {project_root}")
    
    # Verificar dependencias
    try:
        import PyInstaller
        print(f"PyInstaller versión: {PyInstaller.__version__}")
    except ImportError:
        print("❌ ERROR: PyInstaller no está instalado")
        print("Instalar con: pip install pyinstaller")
        sys.exit(1)
    
    # Construir aplicación
    build_bolivia()
    
    print("\n" + "=" * 60)
    print("BUILD COMPLETADO - BOLIVIA")
    print("=" * 60)

if __name__ == '__main__':
    main()