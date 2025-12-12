"""
WIDGETS PERSONALIZADOS PARA LA INTERFAZ
"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Optional, Callable

from inventario_boletos.ui.styles import AppStyles, AppColors


class CampoEscaneo(ttk.Frame):
    """Widget personalizado para el campo de escaneo"""
    
    def __init__(self, parent, on_escaneo: Callable[[str], None], **kwargs):
        super().__init__(parent, **kwargs)
        self.on_escaneo = on_escaneo
        self.ultimo_escaneo = None
        self.ultimo_escaneo_time = None
        
        self._construir_widgets()
        self._configurar_eventos()
    
    def _construir_widgets(self):
        """Construye los widgets internos"""
        # Label
        self.label = ttk.Label(
            self,
            text="ESCANEE O ESCRIBA EL CÓDIGO:",
            style='Subtitle.TLabel'
        )
        self.label.pack(pady=(0, 5))
        
        # Campo de entrada
        self.entry_var = tk.StringVar()
        self.entry = ttk.Entry(
            self,
            textvariable=self.entry_var,
            style='Scan.TEntry',
            font=AppStyles.FUENTE_MONOSPACE,
            justify='center'
        )
        self.entry.pack(fill='x', padx=20, pady=(0, 10))
        
        # Configurar el campo para que tenga un placeholder
        self.placeholder = "Pase el código de barras por el lector..."
        self.mostrar_placeholder()
        
        # Label de ayuda
        self.help_label = ttk.Label(
            self,
            text="El lector de códigos actuará como teclado. Presione Enter después de escribir manualmente.",
            style='TLabel',
            foreground=AppColors.PENDIENTE,
            font=("Helvetica", 8)
        )
        self.help_label.pack(pady=(0, 5))
    
    def _configurar_eventos(self):
        """Configura los eventos del widget"""
        # Enfocar automáticamente el campo de entrada
        self.entry.focus_set()
        
        # Evento cuando se presiona Enter
        self.entry.bind('<Return>', self._procesar_entrada)
        
        # Evento cuando el campo gana foco
        self.entry.bind('<FocusIn>', self._on_focus_in)
        
        # Evento cuando el campo pierde foco
        self.entry.bind('<FocusOut>', self._on_focus_out)
        
        # Capturar todas las teclas para detectar escaneo rápido
        self.entry.bind('<Key>', self._on_key_press)
    
    def mostrar_placeholder(self):
        """Muestra el texto de placeholder"""
        self.entry.configure(foreground=AppColors.PENDIENTE)
        self.entry_var.set(self.placeholder)
    
    def ocultar_placeholder(self):
        """Oculta el texto de placeholder"""
        self.entry.configure(foreground=AppColors.NORMAL)
        if self.entry_var.get() == self.placeholder:
            self.entry_var.set("")
    
    def _on_focus_in(self, event=None):
        """Cuando el campo recibe foco"""
        self.ocultar_placeholder()
    
    def _on_focus_out(self, event=None):
        """Cuando el campo pierde foco"""
        if not self.entry_var.get():
            self.mostrar_placeholder()
    
    def _on_key_press(self, event):
        """Detecta presión de teclas para manejar escaneo rápido"""
        # Si el usuario empieza a escribir, ocultar placeholder
        if self.entry_var.get() == self.placeholder:
            self.ocultar_placeholder()
        
        # Detectar si es un escaneo rápido (múltiples caracteres rápidos)
        ahora = datetime.now()
        if self.ultimo_escaneo_time:
            diferencia = (ahora - self.ultimo_escaneo_time).total_seconds()
            if diferencia > 0.5:  # Más de 0.5 segundos entre teclas = escritura manual
                self.ultimo_escaneo = None
        
        self.ultimo_escaneo_time = ahora
    
    def _procesar_entrada(self, event=None):
        """Procesa la entrada del usuario"""
        codigo = self.entry_var.get().strip()
        
        # Ignorar si está vacío o es el placeholder
        if not codigo or codigo == self.placeholder:
            return
        
        # Limpiar el campo
        self.entry_var.set("")
        self.entry.focus_set()
        
        # Llamar al callback de escaneo
        if self.on_escaneo:
            self.on_escaneo(codigo)
    
    def forzar_escaneo(self, codigo: str):
        """Fuerza el procesamiento de un código (para testing)"""
        self.entry_var.set(codigo)
        self._procesar_entrada()
    
    def limpiar(self):
        """Limpia el campo de entrada"""
        self.entry_var.set("")
        self.mostrar_placeholder()
        self.entry.focus_set()


class PanelEstadisticas(ttk.LabelFrame):
    """Widget para mostrar estadísticas en tiempo real"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, text="ESTADÍSTICAS", **kwargs)
        self._construir_widgets()
        self.actualizar(0, 0, 0, 0)
    
    def _construir_widgets(self):
        """Construye los widgets del panel"""
        # Crear grid para las estadísticas
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        # Total de boletos
        self.lbl_total_text = ttk.Label(self, text="Total reportados:")
        self.lbl_total_text.grid(row=0, column=0, padx=5, pady=2, sticky='w')
        
        self.lbl_total_val = ttk.Label(self, text="0", font=AppStyles.FUENTE_SUBTITULO)
        self.lbl_total_val.grid(row=0, column=1, padx=5, pady=2, sticky='e')
        
        # Escaneados
        self.lbl_escaneados_text = ttk.Label(self, text="Escaneados:")
        self.lbl_escaneados_text.grid(row=1, column=0, padx=5, pady=2, sticky='w')
        
        self.lbl_escaneados_val = ttk.Label(self, text="0", foreground=AppColors.EXITO)
        self.lbl_escaneados_val.grid(row=1, column=1, padx=5, pady=2, sticky='e')
        
        # Faltantes
        self.lbl_faltantes_text = ttk.Label(self, text="Faltantes:")
        self.lbl_faltantes_text.grid(row=2, column=0, padx=5, pady=2, sticky='w')
        
        self.lbl_faltantes_val = ttk.Label(self, text="0", foreground=AppColors.PENDIENTE)
        self.lbl_faltantes_val.grid(row=2, column=1, padx=5, pady=2, sticky='e')
        
        # Duplicados
        self.lbl_duplicados_text = ttk.Label(self, text="Duplicados:")
        self.lbl_duplicados_text.grid(row=3, column=0, padx=5, pady=2, sticky='w')
        
        self.lbl_duplicados_val = ttk.Label(self, text="0", foreground=AppColors.DUPLICADO)
        self.lbl_duplicados_val.grid(row=3, column=1, padx=5, pady=2, sticky='e')
        
        # Porcentaje
        self.lbl_porcentaje_text = ttk.Label(self, text="Progreso:")
        self.lbl_porcentaje_text.grid(row=4, column=0, padx=5, pady=2, sticky='w')
        
        self.lbl_porcentaje_val = ttk.Label(self, text="0%")
        self.lbl_porcentaje_val.grid(row=4, column=1, padx=5, pady=2, sticky='e')
        
        # Barra de progreso
        self.progress_bar = ttk.Progressbar(
            self,
            length=200,
            mode='determinate'
        )
        self.progress_bar.grid(row=5, column=0, columnspan=2, padx=5, pady=5, sticky='ew')
    
    def actualizar(self, total: int, escaneados: int, faltantes: int, duplicados: int):
        """Actualiza las estadísticas mostradas"""
        self.lbl_total_val.config(text=str(total))
        self.lbl_escaneados_val.config(text=str(escaneados))
        self.lbl_faltantes_val.config(text=str(faltantes))
        self.lbl_duplicados_val.config(text=str(duplicados))
        
        # Calcular porcentaje
        if total > 0:
            porcentaje = (escaneados / total) * 100
            self.lbl_porcentaje_val.config(text=f"{porcentaje:.1f}%")
            self.progress_bar['value'] = porcentaje
        else:
            self.lbl_porcentaje_val.config(text="0%")
            self.progress_bar['value'] = 0


class ListaEscaneos(ttk.LabelFrame):
    """Widget para mostrar la lista de últimos escaneos"""
    
    def __init__(self, parent, max_items: int = 10, **kwargs):
        super().__init__(parent, text="ÚLTIMOS ESCANEOS", **kwargs)
        self.max_items = max_items
        self.escaneos = []
        self._construir_widgets()
    
    def _construir_widgets(self):
        """Construye el widget de lista"""
        # Canvas con scrollbar
        self.canvas = tk.Canvas(self, highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Empaquetar
        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
    
    def agregar_escaneo(self, codigo: str, estado: str, mensaje: str, timestamp=None):
        """Agrega un escaneo a la lista"""
        if timestamp is None:
            timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Crear frame para el item
        item_frame = ttk.Frame(self.scrollable_frame)
        item_frame.pack(fill='x', padx=5, pady=2)
        
        # Icono según estado
        icono = "✅" if estado == "ESCANEADO" else "⚠️" if estado == "DUPLICADO" else "❌"
        
        # Label de icono
        lbl_icono = ttk.Label(
            item_frame,
            text=icono,
            font=("Helvetica", 10)
        )
        lbl_icono.pack(side='left', padx=(0, 5))
        
        # Label de código y mensaje
        texto = f"{codigo} - {mensaje} ({timestamp})"
        lbl_texto = ttk.Label(
            item_frame,
            text=texto,
            font=AppStyles.FUENTE_MONOSPACE,
            foreground=AppColors.obtener_color_estado(estado)
        )
        lbl_texto.pack(side='left', fill='x', expand=True)
        
        # Agregar a la lista y limitar tamaño
        self.escaneos.append(item_frame)
        if len(self.escaneos) > self.max_items:
            # Eliminar el más antiguo
            viejo = self.escaneos.pop(0)
            viejo.destroy()
        
        # Auto-scroll al final
        self.canvas.yview_moveto(1.0)
    
    def limpiar(self):
        """Limpia toda la lista"""
        for item in self.escaneos:
            item.destroy()
        self.escaneos = []