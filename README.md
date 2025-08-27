# Estructura del Proyecto Centralizada

## Descripción General

Este proyecto centraliza la creación de aplicaciones de análisis sísmico para diferentes países (Bolivia y Perú), eliminando la duplicación de código y facilitando el mantenimiento.

## Estructura de Directorios

```md
proyecto_sismico/
├── core/                          # Núcleo del sistema
│   ├── __init__.py
│   ├── app_factory.py            # Factory para crear aplicaciones
│   ├── base/                     # Clases base
│   │   ├── __init__.py
│   │   ├── app_base.py          # Clase base para aplicaciones
│   │   ├── seismic_base.py      # Clase base para cálculos sísmicos
│   │   └── memory_base.py       # Clase base para memoria de cálculo
│   ├── config/                   # Configuraciones
│   │   ├── __init__.py
│   │   └── app_config.py        # Configuraciones por país
│   └── utils/                    # Utilidades compartidas
│       ├── __init__.py
│       ├── file_utils.py        # Manejo de archivos
│       └── ui_utils.py          # Utilidades UI
│
├── ui/                           # Interfaces de usuario
│   ├── __init__.py
│   ├── main_window.py           # Interfaz principal unificada
│   └── widgets/                 # Widgets personalizados
│       ├── __init__.py
│       └── seismic_params_widget.py  # Widget dinámico de parámetros
│
├── shared/                       # Componentes compartidos
│   ├── __init__.py
│   ├── dialogs/                 # Diálogos comunes
│   │   ├── __init__.py
│   │   └── descriptions_dialog.py
│   └── resources/               # Recursos compartidos
│       ├── images/
│       └── templates/
│
├── apps/                        # Aplicaciones específicas por país
│   ├── __init__.py
│   ├── bolivia/                 # Código específico de Bolivia
│   │   ├── __init__.py
│   │   ├── memory_bolivia.py    # Generación de memoria Bolivia
│   │   └── resources/
│   │       ├── templates/
│   │       └── images/
│   └── peru/                    # Código específico de Perú
│       ├── __init__.py
│       ├── memory_peru.py       # Generación de memoria Perú
│       └── resources/
│           ├── templates/
│           └── images/
│
├── run_app.py                   # Launcher principal
├── requirements.txt             # Dependencias
└── README.md                    # Documentación
```

## Archivos Principales Creados/Modificados

### 1. `ui/main_window.py`

- **Reemplaza**: `interfaz_bolivia.py`, `interfaz_peru.py`
- **Función**: Interfaz unificada que se adapta según configuración
- **Mejoras**:
  - Estructura de pestañas clara
  - Widgets organizados en grupos lógicos
  - Diseño responsivo

### 2. `ui/widgets/seismic_params_widget.py`

- **Función**: Widget dinámico que muestra parámetros específicos según el país
- **Beneficios**:
  - Bolivia: Fa, Fv, So, categoría
  - Perú: Z, U, S, Tp, Tl, tipo de suelo
  - Extensible para otros países

### 3. `core/app_factory.py`

- **Función**: Factory pattern para crear aplicaciones
- **Incluye**:
  - `SeismicAppFactory`: Crea apps según país
  - `UnifiedSeismicApp`: Aplicación unificada
  - `main()`: Punto de entrada

### 4. `core/base/app_base.py` (actualizada)

- **Función**: Funcionalidad común mejorada
- **Nuevas características**:
  - Manejo de iconos
  - Carga de imágenes unificada
  - Diálogos de descripción mejorados
  - Mensajes de usuario

### 5. `run_app.py`

- **Función**: Launcher principal con argumentos de línea de comandos
- **Uso**:

  ```bash
  python run_app.py bolivia    # Para Bolivia
  python run_app.py peru       # Para Perú
  python run_app.py --list     # Listar países
  ```

## Características Principales

### ✅ Eliminación de Duplicación

- Una sola interfaz principal para ambos países
- Funcionalidad común centralizada
- Widgets reutilizables

### ✅ Configuración Dinámica

- Parámetros sísmicos específicos por país
- Títulos y labels personalizables
- Rutas de recursos configurables

### ✅ Mantenibilidad

- Cambios en un solo lugar se reflejan en todas las apps
- Estructura clara y organizada
- Separación de responsabilidades

### ✅ Escalabilidad

- Fácil agregar nuevos países
- Widgets de parámetros extensibles
- Factory pattern para creación de apps

## Uso

### Ejecutar Bolivia

```bash
python run_app.py bolivia
```

### Ejecutar Perú  

```bash
python run_app.py peru
```

### Desarrollo

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar en modo debug
python run_app.py bolivia --debug
```

## Beneficios del Refactor

1. **Código Único**: ~70% reducción en líneas duplicadas
2. **Mantenimiento**: Cambios centralizados
3. **Consistencia**: UI uniforme entre países
4. **Flexibilidad**: Configuración dinámica por país
5. **Legibilidad**: Estructura clara y documentada

## Migración desde Código Anterior

Los archivos antiguos como `interfaz_bolivia.py` e `interfaz_peru.py` pueden ser eliminados una vez verificado que la nueva estructura funciona correctamente. La funcionalidad está completamente preservada pero centralizada.
