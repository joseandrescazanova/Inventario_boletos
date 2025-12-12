"""
ESTILOS Y CONFIGURACIÓN VISUAL DE LA INTERFAZ
"""
import tkinter as tk
from tkinter import ttk


class AppStyles:
    """Clase que contiene todos los estilos de la aplicación"""
    
    # Colores
    COLOR_PRIMARIO = "#2C3E50"      # Azul oscuro
    COLOR_SECUNDARIO = "#3498DB"    # Azul claro
    COLOR_EXITO = "#27AE60"         # Verde
    COLOR_ADVERTENCIA = "#F39C12"   # Naranja
    COLOR_ERROR = "#E74C3C"         # Rojo
    COLOR_FONDO = "#ECF0F1"         # Gris claro
    COLOR_TEXTO = "#2C3E50"         # Azul oscuro
    
    # Fuentes
    FUENTE_TITULO = ("Helvetica", 16, "bold")
    FUENTE_SUBTITULO = ("Helvetica", 12, "bold")
    FUENTE_NORMAL = ("Helvetica", 10)
    FUENTE_MONOSPACE = ("Courier", 10)
    
    @classmethod
    def configurar_estilos(cls):
        """Configura los estilos de ttk"""
        estilo = ttk.Style()
        
        # Configurar tema
        estilo.theme_use('clam')
        
        # Estilo para botones principales
        estilo.configure(
            'Primary.TButton',
            background=cls.COLOR_SECUNDARIO,
            foreground='white',
            font=cls.FUENTE_NORMAL,
            borderwidth=1,
            focusthickness=3,
            focuscolor='none'
        )
        
        estilo.map(
            'Primary.TButton',
            background=[('active', cls.COLOR_PRIMARIO)],
            relief=[('pressed', 'sunken'), ('!pressed', 'raised')]
        )
        
        # Estilo para botones secundarios
        estilo.configure(
            'Secondary.TButton',
            background=cls.COLOR_FONDO,
            foreground=cls.COLOR_TEXTO,
            font=cls.FUENTE_NORMAL
        )
        
        # Estilo para labels de título
        estilo.configure(
            'Title.TLabel',
            background=cls.COLOR_FONDO,
            foreground=cls.COLOR_PRIMARIO,
            font=cls.FUENTE_TITULO
        )
        
        # Estilo para labels de subtítulo
        estilo.configure(
            'Subtitle.TLabel',
            background=cls.COLOR_FONDO,
            foreground=cls.COLOR_SECUNDARIO,
            font=cls.FUENTE_SUBTITULO
        )
        
        # Estilo para el campo de escaneo
        estilo.configure(
            'Scan.TEntry',
            fieldbackground='white',
            foreground=cls.COLOR_TEXTO,
            font=cls.FUENTE_MONOSPACE,
            borderwidth=2,
            relief='solid'
        )
    
    @classmethod
    def crear_frame_con_borde(cls, parent, **kwargs):
        """Crea un Frame con borde estilizado"""
        frame = tk.Frame(
            parent,
            background=cls.COLOR_FONDO,
            highlightbackground=cls.COLOR_SECUNDARIO,
            highlightthickness=1,
            **kwargs
        )
        return frame


class AppColors:
    """Colores para estados de escaneo"""
    EXITO = "#27AE60"      # Verde
    DUPLICADO = "#F39C12"  # Naranja
    NO_ENCONTRADO = "#E74C3C"  # Rojo
    PENDIENTE = "#95A5A6"  # Gris
    NORMAL = "#2C3E50"     # Azul oscuro
    
    @classmethod
    def obtener_color_estado(cls, estado: str) -> str:
        """Obtiene el color correspondiente a un estado"""
        colores = {
            "ESCANEADO": cls.EXITO,
            "DUPLICADO": cls.DUPLICADO,
            "NO_REPORTADO": cls.NO_ENCONTRADO,
            "PENDIENTE": cls.PENDIENTE,
            "NO_ESCANEADO": cls.PENDIENTE
        }
        return colores.get(estado, cls.NORMAL)