# 📋 Inventario de Boletos - Raspa y Gane
Sistema de gestión y control de inventario de boletos de lotería

🚀 Descripción
Aplicación de escritorio para el control, seguimiento y gestión de inventario de boletos de lotería "Raspa y Gane". Permite cargar reportes de boletos, escanear códigos de barras, llevar estadísticas en tiempo real y exportar resultados.

✨ Características Principales
📊 Gestión de Reportes
Carga de archivos Excel (.xlsx, .xls) y CSV con reportes de boletos

Detección automática de columnas (código de barras, vendedor, sucursal, etc.)

Continuar progreso desde reportes exportados previamente

🔍 Sistema de Escaneo
Campo de escaneo optimizado para lectura rápida de códigos de barras

Validación en tiempo real contra el reporte cargado

Sonidos distintivos para diferentes resultados (éxito, advertencia, error)

Lista de últimos escaneos con información detallada

📈 Estadísticas y Monitoreo
Panel de estadísticas en tiempo real:

Total de boletos reportados

Escaneados correctamente

Faltantes por escanear

Duplicados detectados

Progreso general (%)

Visualización inmediata de resultados

📤 Exportación de Resultados
Exportar a Excel con columnas adicionales de estado

Guardar progreso rápido en formato JSON

Nombres automáticos con timestamps

Estructura organizada de archivos exportados

🛠️ Tecnologías Utilizadas
Python 3.8+

Tkinter - Interfaz gráfica de usuario

Pandas - Procesamiento de datos Excel/CSV

PyGame - Reproducción de sonidos (opcional)

Sistema multiplataforma - Windows, Linux, macOS

📁 Estructura del Proyecto
text
inventario_boletos/
├── assets/                 # Recursos multimedia
│   └── sounds/            # Archivos de sonido
│       ├── exito.mp3      # Sonido para escaneo exitoso
│       ├── advertencia.mp3 # Sonido para duplicados
│       └── error.mp3      # Sonido para errores
├── config/                # Configuración
│   ├── __init__.py
│   └── constants.py      # Constantes de la aplicación
├── core/                  # Lógica principal
│   ├── __init__.py
│   ├── entities.py       # Entidades (Boleto, Sesion, etc.)
│   └── report_processor.py # Procesador de archivos
├── img/                   # Imágenes e iconos
│   └── icon.png          # Icono de la aplicación
├── ui/                    # Interfaz de usuario
│   ├── __init__.py
│   ├── main_window.py    # Ventana principal
│   ├── widgets.py        # Componentes personalizados
│   ├── styles.py         # Estilos y temas
│   ├── sound_manager.py  # Gestor de sonidos
│   └── file_dialog_manager.py # Gestor de diálogos
├── requirements.txt       # Dependencias
└── README.md             # Este archivo

⚙️ Instalación
Prerrequisitos
Python 3.8 o superior

pip (gestor de paquetes de Python)

Pasos de instalación
Clonar o descargar el proyecto:

bash
git clone https://github.com/joseandrescazanova/Inventario_boletos.git
cd inventario_boletos
Crear entorno virtual (recomendado):

bash
python -m venv venv
# En Linux:
source venv/bin/activate


bash
pip install -r requirements.txt
Dependencias principales
pandas - Para procesamiento de Excel/CSV

openpyxl - Soporte para archivos Excel

pygame - Para reproducción de sonidos (opcional)

🎮 Uso de la Aplicación
1. Iniciar la aplicación
bash
python -m inventario_boletos.ui.main_window
2. Flujo de trabajo típico
📥 Cargar Reporte
Hacer clic en "NUEVO REPORTE"

Seleccionar archivo Excel/CSV con los boletos

La aplicación detectará automáticamente las columnas

🔍 Escanear Boletos
Enfocar el campo de escaneo (selección automática)

Escanear código de barras del boleto

Escuchar sonido de confirmación:

✅ Éxito - Boleto válido escaneado por primera vez

⚠️ Advertencia - Boleto duplicado

❌ Error - Código no encontrado en el reporte

📊 Monitorear Progreso
Ver estadísticas en tiempo real en el panel superior

Revisar últimos escaneos en la lista central


💾 Exportar Resultados
Hacer clic en "EXPORTAR RESULTADOS"

Elegir ubicación y nombre del archivo

El archivo generado incluirá:

Todos los datos originales

Columna "ESTADO_ESCANEO"

Columna "FECHA_ESCANEO"

Columna "ESCANEOS_REALIZADOS"

📋 Formatos de Archivo Soportados
✅ Formatos de entrada:
Excel: .xlsx, .xls

CSV: .csv

✅ Columnas detectadas automáticamente:
Código de barras (requerido)

Sucursal/PDV

Documento del vendedor

Nombre del vendedor

Fecha de pago

Monto del premio

Tipo de premio

✅ Formatos de salida:
Excel con resultados (.xlsx)

Progreso rápido (.json)

🎯 Casos de Uso
Inventario Físico
Cargar reporte de boletos asignados

Escanear cada boleto físico

Identificar boletos faltantes/extraviados

Exportar reporte de inventario final

Control de Entrega
Cargar reporte de boletos a entregar

Escanear al momento de la entrega

Verificar entregas completas vs pendientes

Generar comprobante de entrega

Auditoría y Reconciliación
Cargar reporte teórico

Escanear existencia física

Identificar discrepancias

Generar reporte de auditoría

🔧 Solución de Problemas
Problemas comunes:
❌ "No se detectan las columnas correctamente"
Verificar que el archivo tenga encabezados

Asegurar que la columna de código de barras tenga datos

Revisar que el archivo no esté dañado

❌ "Los sonidos no funcionan"
Verificar que los archivos estén en assets/sounds/

Instalar pygame: pip install pygame

En Linux, asegurar tener instalados codecs de audio

❌ "Error al exportar a Excel"
Verificar permisos de escritura en la carpeta destino

Cerrar el archivo Excel si está abierto en otro programa

Asegurar espacio suficiente en disco

Modo de diagnóstico:
La aplicación muestra mensajes de diagnóstico en la consola. Para problemas técnicos, revisar la salida de la terminal.

📝 Personalización
Sonidos
Reemplazar archivos en assets/sounds/:

exito.mp3 - Para escaneos exitosos

advertencia.mp3 - Para duplicados

error.mp3 - Para códigos no encontrados

Estilos
Modificar ui/styles.py para:

Cambiar colores de la interfaz

Ajustar fuentes y tamaños

Personalizar apariencia de componentes

Configuración
Editar config/constants.py para:

Cambiar extensiones permitidas

Ajustar límites de visualización

Modificar mensajes del sistema

🤝 Contribución
Reportar problemas
Verificar si el problema ya existe en los issues

Describir detalladamente el error

Incluir pasos para reproducirlo

Adjuntar capturas de pantalla si es relevante

Sugerir mejoras
Describir la funcionalidad deseada

Explicar el beneficio para los usuarios

Proponer implementación si es posible

📄 Licencia
Este proyecto es para uso interno de SuperServicios. Consultar con el departamento de sistemas para información de licencias.

👥 Contacto y Soporte
Departamento de Sistemas: andres.casanova@superservicios.com.co joseandrescazanova@gmail.com

Desarrollador principal: [Nombre del desarrollador]

Versión: 1.0.0

Última actualización: [Fecha]

🔄 Historial de Versiones
v1.0.0 (Actual)
Carga de reportes Excel/CSV

Sistema de escaneo con sonidos

Estadísticas en tiempo real

Exportación de resultados

Interfaz gráfica intuitiva

Próximas características
Exportación a PDF

Reportes gráficos

Autenticación de usuarios

Sincronización en la nube

API para integración con otros sistemas
