#!/usr/bin/env python3
"""
Script para construir ambos ejecutables: Bolivia y Perú
"""

import os
import sys
import time
import shutil
import subprocess
from pathlib import Path

def clean_all_build_dirs():
    """Limpia todos los directorios de build"""
    dirs_to_clean = ['build', 'dist', '__pycache__']
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            print(f"Limpiando directorio: {dir_name}")
            shutil.rmtree(dir_name)

def build_application(country: str, spec_file: Path):
    """
    Construye una aplicación específica
    
    Args:
        country: 'bolivia' o 'peru'
        spec_file: Ruta al archivo .spec
    """
    print(f"\n{'='*60}")
    print(f"CONSTRUYENDO APLICACIÓN - {country.upper()}")
    print(f"{'='*60}")
    
    start_time = time.time()
    
    try:
        # Ejecutar PyInstaller
        cmd = ['pyinstaller', '--clean', str(spec_file)]
        print(f"Ejecutando: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        elapsed = time.time() - start_time
        print(f"✅ BUILD EXITOSO para {country.upper()} ({elapsed:.1f}s)")
        
        # Verificar ejecutable
        exe_name = f'AnalisisSismico{country.capitalize()}'
        exe_path = Path('dist') / exe_name / f'{exe_name}.exe'
        
        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024*1024)
            print(f"✅ Ejecutable verificado: {exe_path}")
            print(f"   Tamaño: {size_mb:.1f} MB")
            return True
        else:
            print(f"⚠️  Advertencia: No se encontró {exe_path}")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ ERROR EN BUILD para {country.upper()}:")
        print(f"Código de salida: {e.returncode}")
        if e.stdout:
            print("STDOUT:")
            print(e.stdout[-1000:])  # Últimas 1000 chars
        if e.stderr:
            print("STDERR:")
            print(e.stderr[-1000:])  # Últimas 1000 chars
        return False
    
    except Exception as e:
        print(f"❌ ERROR INESPERADO para {country.upper()}: {e}")
        return False

def create_dist_structure():
    """Crea la estructura de directorios en dist/"""
    dist_dir = Path('dist')
    dist_dir.mkdir(exist_ok=True)
    
    # Crear subdirectorios
    (dist_dir / 'bolivia').mkdir(exist_ok=True)
    (dist_dir / 'peru').mkdir(exist_ok=True)

def organize_executables():
    """Organiza los ejecutables en subdirectorios por país"""
    dist_dir = Path('dist')
    
    # Mover ejecutable de Bolivia
    bolivia_src = dist_dir / 'AnalisisSismicoBolivia'
    bolivia_dst = dist_dir / 'bolivia' / 'AnalisisSismicoBolivia'
    if bolivia_src.exists() and bolivia_src.is_dir():
        if bolivia_dst.exists():
            shutil.rmtree(bolivia_dst)
        shutil.move(str(bolivia_src), str(bolivia_dst))
        print(f"📁 Movido a: {bolivia_dst}")
    
    # Mover ejecutable de Perú
    peru_src = dist_dir / 'AnalisisSismicoPeru'
    peru_dst = dist_dir / 'peru' / 'AnalisisSismicoPeru'
    if peru_src.exists() and peru_src.is_dir():
        if peru_dst.exists():
            shutil.rmtree(peru_dst)
        shutil.move(str(peru_src), str(peru_dst))
        print(f"📁 Movido a: {peru_dst}")

def print_summary(bolivia_success: bool, peru_success: bool, total_time: float):
    """Imprime resumen final del build"""
    print(f"\n{'='*60}")
    print("RESUMEN DE BUILD")
    print(f"{'='*60}")
    print(f"Bolivia: {'✅ EXITOSO' if bolivia_success else '❌ FALLÓ'}")
    print(f"Perú:    {'✅ EXITOSO' if peru_success else '❌ FALLÓ'}")
    print(f"Tiempo total: {total_time:.1f}s")
    
    if bolivia_success and peru_success:
        print("\n🎉 AMBAS APLICACIONES CONSTRUIDAS EXITOSAMENTE")
        print("\nEjecutables disponibles en:")
        print("  dist/bolivia/AnalisisSismicoBolivia/AnalisisSismicoBolivia.exe")
        print("  dist/peru/AnalisisSismicoPeru/AnalisisSismicoPeru.exe")
    elif bolivia_success or peru_success:
        print(f"\n⚠️  CONSTRUCCIÓN PARCIAL COMPLETADA")
    else:
        print(f"\n💥 FALLÓ LA CONSTRUCCIÓN DE AMBAS APLICACIONES")

def main():
    """Función principal"""
    print("🚀 INICIANDO BUILD DE TODAS LAS APLICACIONES")
    start_time = time.time()
    
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
    
    # Verificar archivos spec
    bolivia_spec = Path('build_scripts/bolivia.spec')
    peru_spec = Path('build_scripts/peru.spec')
    
    if not bolivia_spec.exists():
        print(f"❌ ERROR: No se encuentra {bolivia_spec}")
        sys.exit(1)
    
    if not peru_spec.exists():
        print(f"❌ ERROR: No se encuentra {peru_spec}")
        sys.exit(1)
    
    # Limpiar directorios anteriores
    print("\n🧹 LIMPIANDO DIRECTORIOS DE BUILD ANTERIORES")
    clean_all_build_dirs()
    
    # Crear estructura de directorios
    create_dist_structure()
    
    # Construir aplicaciones
    bolivia_success = build_application('bolivia', bolivia_spec)
    peru_success = build_application('peru', peru_spec)
    
    # Organizar ejecutables en subdirectorios
    if bolivia_success or peru_success:
        print(f"\n📂 ORGANIZANDO EJECUTABLES")
        organize_executables()
    
    # Resumen final
    total_time = time.time() - start_time
    print_summary(bolivia_success, peru_success, total_time)
    
    # Código de salida
    if bolivia_success and peru_success:
        sys.exit(0)
    elif bolivia_success or peru_success:
        sys.exit(1)  # Parcialmente exitoso
    else:
        sys.exit(2)  # Falló completamente

if __name__ == '__main__':
    main()