"""
VENTANA PRINCIPAL DE LA APLICACIÓN
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from datetime import datetime
import sys

from inventario_boletos.core.entities import SesionInventario, EstadoBoleto
from inventario_boletos.core.report_processor import ReporteProcessor
from inventario_boletos.ui.styles import AppStyles, AppColors
from inventario_boletos.ui.widgets import CampoEscaneo, PanelEstadisticas, ListaEscaneos
from inventario_boletos.core.entities import SesionInventario, EstadoBoleto
from inventario_boletos.ui.sound_manager import SoundManager, TipoSonido


class MainWindow:
    """Ventana principal de la aplicación"""

    def __init__(self):
        self.root = tk.Tk()
        self.sesion: SesionInventario = None
        self.reporte_processor: ReporteProcessor = None
        self.ruta_reporte_actual: str = None

        # AÑADIR ESTA LÍNEA
        self.sound_manager = SoundManager()

        # Mostrar estado de sonidos (opcional, para debug)
        sound_status = self.sound_manager.get_sounds_status()
        print(f"Estado de sonidos: {sound_status}")

        self._configurar_ventana()
        self._construir_widgets()
        self._configurar_estilos()
        self._configurar_eventos()

    def _configurar_ventana(self):
        """Configura las propiedades de la ventana"""
        self.root.title("Inventario de Boletos - Raspa y Gane")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Icono (opcional)
        # try:
        #     self.root.iconbitmap('icono.ico')
        # except:
        #     pass

        # Configurar el grid de la ventana
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(2, weight=1)  # Fila de lista escaneos expandible

    def _configurar_estilos(self):
        """Configura los estilos de la aplicación"""
        AppStyles.configurar_estilos()

        # Configurar color de fondo
        self.root.configure(background=AppStyles.COLOR_FONDO)

    def _construir_widgets(self):
        """Construye todos los widgets de la interfaz"""
        # Título
        self.lbl_titulo = ttk.Label(
            self.root, text="INVENTARIO DE BOLETOS - RASPA Y GANE", style="Title.TLabel"
        )
        self.lbl_titulo.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Frame superior (controles)
        self.frame_controles = AppStyles.crear_frame_con_borde(self.root)
        self.frame_controles.grid(row=1, column=0, padx=20, pady=(0, 10), sticky="ew")

        self._construir_panel_controles()

        # Frame de escaneo
        self.frame_escaneo = AppStyles.crear_frame_con_borde(self.root)
        self.frame_escaneo.grid(row=2, column=0, padx=20, pady=(0, 10), sticky="nsew")

        self._construir_panel_escaneo()

        # Frame inferior (botones)
        self.frame_botones = ttk.Frame(self.root)
        self.frame_botones.grid(row=3, column=0, padx=20, pady=10, sticky="ew")

        self._construir_panel_botones()

        # Barra de estado
        self.barra_estado = ttk.Label(
            self.root, text="Listo para cargar reporte", relief=tk.SUNKEN, anchor="w"
        )
        self.barra_estado.grid(row=4, column=0, padx=20, pady=(0, 10), sticky="ew")

    def _construir_panel_controles(self):
        """Construye el panel de controles superiores"""
        self.frame_controles.grid_columnconfigure(1, weight=1)

        # Frame para botones de carga
        frame_botones_carga = ttk.Frame(self.frame_controles)
        frame_botones_carga.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # Botón para cargar reporte NUEVO
        self.btn_cargar_nuevo = ttk.Button(
            frame_botones_carga,
            text="📂 NUEVO REPORTE",
            command=self._cargar_reporte,
            style="Primary.TButton",
            width=18,
        )
        self.btn_cargar_nuevo.pack(side="left", padx=(0, 5))

        # Botón para continuar progreso
        self.btn_continuar = ttk.Button(
            frame_botones_carga,
            text="↻ CONTINUAR",
            command=self._cargar_continuar,
            style="Secondary.TButton",
            width=15,
        )
        self.btn_continuar.pack(side="left")

        # Label de archivo cargado
        self.lbl_archivo = ttk.Label(
            self.frame_controles,
            text="No hay archivo cargado",
            foreground=AppColors.PENDIENTE,
        )
        self.lbl_archivo.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Panel de estadísticas
        self.panel_estadisticas = PanelEstadisticas(self.frame_controles)
        self.panel_estadisticas.grid(row=0, column=2, padx=10, pady=10, sticky="e")

    def _construir_panel_escaneo(self):
        """Construye el panel principal de escaneo"""
        # Configurar grid
        self.frame_escaneo.grid_columnconfigure(0, weight=1)
        self.frame_escaneo.grid_rowconfigure(1, weight=1)

        # Campo de escaneo
        self.campo_escaneo = CampoEscaneo(
            self.frame_escaneo, on_escaneo=self._procesar_escaneo
        )
        self.campo_escaneo.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        # Lista de escaneos
        self.lista_escaneos = ListaEscaneos(self.frame_escaneo, max_items=15)
        self.lista_escaneos.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")

    def _construir_panel_botones(self):
        """Construye el panel de botones inferiores"""
        # 5 columnas ahora
        for i in range(5):
            self.frame_botones.grid_columnconfigure(i, weight=1)

        # Botón para guardar progreso rápido
        self.btn_guardar_progreso = ttk.Button(
            self.frame_botones,
            text="💾 GUARDAR PROGRESO",
            command=self._guardar_progreso_rapido,
            style="Secondary.TButton",
            state="disabled",
        )
        self.btn_guardar_progreso.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # Botón para calcular faltantes (CREAR PRIMERO)
        self.btn_calcular_faltantes = ttk.Button(
            self.frame_botones,
            text="🔍 CALCULAR FALTANTES",
            command=self._calcular_faltantes,
            style="Secondary.TButton",
            state="disabled",
        )
        # Botón para calcular faltantes (original, ahora columna 1)
        self.btn_calcular_faltantes.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Botón para ver boletos faltantes (CREAR PRIMERO)
        self.btn_ver_faltantes = ttk.Button(
            self.frame_botones,
            text="📋 VER FALTANTES",
            command=self._ver_faltantes,
            style="Secondary.TButton",
            state="disabled",
        )
        self.btn_ver_faltantes.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        self.btn_exportar = ttk.Button(
            self.frame_botones,
            text="📤 EXPORTAR RESULTADOS",
            command=self._exportar_resultados,
            style="Primary.TButton",
            state="disabled",
        )
        self.btn_exportar.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        # Botón para limpiar (CREAR PRIMERO)
        self.btn_limpiar = ttk.Button(
            self.frame_botones,
            text="🗑️ LIMPIAR TODO",
            command=self._limpiar_todo,
            style="Danger.TButton",
            state="disabled",
        )
        self.btn_limpiar.grid(row=0, column=4, padx=5, pady=5, sticky="ew")

    def _configurar_eventos(self):
        """Configura eventos de la ventana"""
        # Evento al cerrar la ventana
        self.root.protocol("WM_DELETE_WINDOW", self._on_cerrar)

        # Atajo de teclado Ctrl+O para cargar archivo
        self.root.bind("<Control-o>", lambda e: self._cargar_reporte())

        # Atajo de teclado Ctrl+E para exportar
        self.root.bind("<Control-e>", lambda e: self._exportar_resultados())

        # Atajo de teclado Ctrl+L para limpiar
        self.root.bind("<Control-l>", lambda e: self._limpiar_todo())

        # Atajo de teclado F5 para calcular faltantes
        self.root.bind("<F5>", lambda e: self._calcular_faltantes())

    def _cargar_reporte(self):
        """Carga un archivo de reporte Excel/CSV"""
        tipos_archivo = [
            ("Excel files", "*.xlsx *.xls"),
            ("CSV files", "*.csv"),
            ("All files", "*.*"),
        ]

        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar reporte de boletos", filetypes=tipos_archivo
        )

        if not ruta_archivo:
            return

        try:
            # Crear nuevo procesador y cargar archivo
            self.reporte_processor = ReporteProcessor()
            exito, mensaje = self.reporte_processor.cargar_archivo(ruta_archivo)

            if not exito:
                messagebox.showerror("Error", mensaje)
                return

            # Crear nueva sesión
            self.sesion = SesionInventario()
            boletos = self.reporte_processor.obtener_boletos()
            self.sesion.agregar_boletos(boletos)

            # Actualizar interfaz
            self.ruta_reporte_actual = ruta_archivo
            nombre_archivo = os.path.basename(ruta_archivo)
            self.lbl_archivo.config(
                text=f"📄 {nombre_archivo} ({len(boletos)} boletos)",
                foreground=AppColors.EXITO,
            )

            # Habilitar botones
            self.btn_calcular_faltantes.config(state="normal")
            self.btn_ver_faltantes.config(state="normal")
            self.btn_exportar.config(state="normal")

            # Habilitar también el botón de guardar progreso
            self.btn_guardar_progreso.config(state="normal")

            # Actualizar estadísticas
            self._actualizar_estadisticas()

            # Limpiar lista de escaneos
            self.lista_escaneos.limpiar()

            # Actualizar barra de estado
            self.barra_estado.config(text=f"Reporte cargado: {len(boletos)} boletos")

            # Enfocar campo de escaneo
            self.campo_escaneo.entry.focus_set()

            messagebox.showinfo(
                "Éxito",
                f"Reporte cargado exitosamente.\n{len(boletos)} boletos cargados.",
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar el reporte:\n{str(e)}")

    def _procesar_escaneo(self, codigo: str):
        """Procesa un código escaneado"""
        if not self.sesion:
            messagebox.showwarning("Advertencia", "Primero cargue un reporte.")
            self.campo_escaneo.limpiar()
            return

        try:
            # Procesar el escaneo
            resultado = self.sesion.procesar_escaneo(codigo)
            boleto = resultado["boleto"]

            # Determinar estado y mensaje
            if resultado["resultado"] == "EXITO":
                estado = boleto.estado.value
                mensaje = f"✅ {boleto.vendedor_nombre}"
                self._reproducir_sonido("exito")
            elif resultado["resultado"] == "DUPLICADO":
                estado = "DUPLICADO"
                mensaje = f"⚠️ Ya escaneado - {boleto.vendedor_nombre}"
                self._reproducir_sonido("advertencia")
            else:  # NO_ENCONTRADO
                estado = "NO_REPORTADO"
                mensaje = "❌ No encontrado en reporte"
                self._reproducir_sonido("error")
                # Para NO_REPORTADO, no hay objeto boleto
                boleto = None

            # Agregar a la lista (solo si hay boleto o es NO_REPORTADO)
            timestamp = resultado["timestamp"].strftime("%H:%M:%S")
            if boleto or resultado["resultado"] == "NO_ENCONTRADO":
                self.lista_escaneos.agregar_escaneo(codigo, estado, mensaje, timestamp)

            # Actualizar estadísticas SOLO si fue escaneo exitoso
            if resultado["resultado"] == "EXITO":
                self._actualizar_estadisticas()

            # Actualizar barra de estado
            self.barra_estado.config(text=f"Último escaneo: {codigo} - {mensaje}")

        except Exception as e:
            messagebox.showerror("Error", f"Error al procesar escaneo:\n{str(e)}")
        finally:
            self.campo_escaneo.limpiar()

    def _actualizar_estadisticas(self):
        """Actualiza las estadísticas en el panel"""
        if self.sesion:
            self.sesion.actualizar_estadisticas()
            stats = self.sesion.estadisticas

            self.panel_estadisticas.actualizar(
                total=stats.total_boletos,
                escaneados=stats.escaneados,
                faltantes=stats.pendientes,
                duplicados=stats.duplicados,
            )

    def _calcular_faltantes(self):
        """Calcula y muestra los boletos faltantes"""
        if not self.sesion:
            messagebox.showwarning("Advertencia", "Primero cargue un reporte.")
            return

        faltantes = self.sesion.obtener_boletos_faltantes()
        total = self.sesion.estadisticas.total_boletos
        escaneados = self.sesion.estadisticas.escaneados

        mensaje = f"✅ {escaneados} de {total} boletos escaneados\n"
        mensaje += f"📋 {len(faltantes)} boletos faltantes por escanear"

        if faltantes:
            mensaje += "\n\nBoletos faltantes:\n"
            for boleto in faltantes[:10]:  # Mostrar solo primeros 10
                mensaje += f"• {boleto.codigo} - {boleto.vendedor_nombre}\n"

            if len(faltantes) > 10:
                mensaje += f"\n... y {len(faltantes) - 10} más"

        messagebox.showinfo("Resultado del Cálculo", mensaje)

        # Actualizar barra de estado
        self.barra_estado.config(text=f"Cálculo completado: {len(faltantes)} faltantes")

    def _ver_faltantes(self):
        """Muestra una ventana con la lista completa de boletos faltantes"""
        if not self.sesion:
            messagebox.showwarning("Advertencia", "Primero cargue un reporte.")
            return

        faltantes = self.sesion.obtener_boletos_faltantes()

        if not faltantes:
            messagebox.showinfo("Faltantes", "¡Excelente! No hay boletos faltantes.")
            return

        # Crear ventana de diálogo
        ventana_faltantes = tk.Toplevel(self.root)
        ventana_faltantes.title("Boletos Faltantes")
        ventana_faltantes.geometry("600x400")

        # Frame con scroll
        frame_principal = ttk.Frame(ventana_faltantes)
        frame_principal.pack(fill="both", expand=True, padx=10, pady=10)

        # Canvas con scrollbar
        canvas = tk.Canvas(frame_principal)
        scrollbar = ttk.Scrollbar(
            frame_principal, orient="vertical", command=canvas.yview
        )
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Empaquetar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Mostrar boletos faltantes
        ttk.Label(
            scrollable_frame,
            text=f"📋 {len(faltantes)} BOLETOS FALTANTES",
            style="Title.TLabel",
        ).pack(pady=(0, 10))

        for boleto in faltantes:
            frame_boleto = ttk.Frame(scrollable_frame)
            frame_boleto.pack(fill="x", padx=5, pady=2)

            ttk.Label(
                frame_boleto,
                text=f"• {boleto.codigo}",
                font=AppStyles.FUENTE_MONOSPACE,
                width=15,
            ).pack(side="left")

            ttk.Label(
                frame_boleto,
                text=f"Vendedor: {boleto.vendedor_nombre}",
                font=AppStyles.FUENTE_NORMAL,
            ).pack(side="left", padx=(10, 0))

            ttk.Label(
                frame_boleto,
                text=f"Sucursal: {boleto.sucursal}",
                font=AppStyles.FUENTE_NORMAL,
                foreground=AppColors.PENDIENTE,
            ).pack(side="left", padx=(10, 0))

    def _exportar_resultados(self):
        """Exporta los resultados a un archivo Excel"""
        if not self.sesion or not self.reporte_processor:
            messagebox.showwarning(
                "Advertencia", "Primero cargue un reporte y realice escaneos."
            )
            return

        # Sugerir nombre de archivo
        nombre_base = os.path.splitext(os.path.basename(self.ruta_reporte_actual))[0]
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"{nombre_base}_RESULTADOS_{fecha}.xlsx"

        ruta_guardar = filedialog.asksaveasfilename(
            title="Guardar resultados como",
            defaultextension=".xlsx",
            initialfile=nombre_sugerido,
            filetypes=[
                ("Excel files", "*.xlsx"),
                ("CSV files", "*.csv"),
                ("All files", "*.*"),
            ],
        )

        if not ruta_guardar:
            return

        try:
            exito, mensaje = self.reporte_processor.exportar_con_resultados(
                self.sesion, ruta_guardar
            )

            if exito:
                messagebox.showinfo("Éxito", mensaje)
                self.barra_estado.config(
                    text=f"Resultados exportados: {os.path.basename(ruta_guardar)}"
                )
            else:
                messagebox.showerror("Error", mensaje)

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{str(e)}")

    def _cargar_continuar(self):
        """Carga un reporte exportado para continuar el escaneo"""
        tipos_archivo = [
            ("Reportes exportados", "*.xlsx *.xls *.csv"),
            ("Todos los archivos", "*.*"),
        ]

        ruta_archivo = filedialog.askopenfilename(
            title="Seleccionar reporte para continuar", filetypes=tipos_archivo
        )

        if not ruta_archivo:
            return

        self._cargar_reporte_con_estados(ruta_archivo)

    def _cargar_reporte_con_estados(self, ruta_archivo: str):
        """Carga un reporte Excel/CSV que ya tiene estados"""
        try:
            # Crear nuevo procesador
            self.reporte_processor = ReporteProcessor()

            # Cargar reporte con estados
            exito, mensaje, boletos = self.reporte_processor.cargar_reporte_con_estados(
                ruta_archivo
            )

            if not exito:
                messagebox.showerror("Error", mensaje)
                return

            # Crear nueva sesión con los boletos cargados
            self.sesion = SesionInventario()
            self.sesion.agregar_boletos(boletos)

            # Actualizar interfaz
            self.ruta_reporte_actual = ruta_archivo
            nombre_archivo = os.path.basename(ruta_archivo)

            # Contar estados
            # escaneados = sum(1 for b in boletos if b.estado.value == "ESCANEADO")
            escaneados = sum(1 for b in boletos if b.estado == EstadoBoleto.ESCANEADO)
            total = len(boletos)

            self.lbl_archivo.config(
                text=f"↻ {nombre_archivo} ({escaneados}/{total} escaneados)",
                foreground=AppColors.DUPLICADO,
            )

            # Habilitar botones
            self.btn_calcular_faltantes.config(state="normal")
            self.btn_ver_faltantes.config(state="normal")
            self.btn_exportar.config(state="normal")
            self.btn_guardar_progreso.config(state="normal")

            # Actualizar estadísticas
            self._actualizar_estadisticas()

            # Limpiar lista de escaneos
            self.lista_escaneos.limpiar()

            # Añadir mensaje informativo
            self.lista_escaneos.agregar_escaneo(
                "INFO",
                "ESCANEADO",
                f"Reporte cargado con {escaneados} boletos ya escaneados",
                datetime.now().strftime("%H:%M:%S"),
            )

            # Actualizar barra de estado
            self.barra_estado.config(
                text=f"Continuando escaneo: {escaneados}/{total} boletos ya procesados"
            )

            # Enfocar campo de escaneo
            self.campo_escaneo.entry.focus_set()

            messagebox.showinfo(
                "Continuar escaneo",
                f"Reporte cargado para continuar.\n\n"
                f"• Total boletos: {total}\n"
                f"• Ya escaneados: {escaneados}\n"
                f"• Pendientes: {total - escaneados}",
            )

        except Exception as e:
            messagebox.showerror(
                "Error", f"Error al cargar reporte para continuar:\n{str(e)}"
            )

    def _guardar_progreso_rapido(self):
        """Guarda el progreso actual en un archivo .json rápido"""
        if not self.sesion:
            messagebox.showwarning("Advertencia", "No hay sesión activa para guardar.")
            return

        # Sugerir nombre de archivo
        nombre_base = "progreso_inventario"
        if self.ruta_reporte_actual:
            nombre_base = os.path.splitext(os.path.basename(self.ruta_reporte_actual))[
                0
            ]

        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"{nombre_base}_PROGRESO_{fecha}.json"

        ruta_guardar = filedialog.asksaveasfilename(
            title="Guardar progreso rápido",
            defaultextension=".json",
            initialfile=nombre_sugerido,
            filetypes=[("Archivos JSON", "*.json")],
        )

        if not ruta_guardar:
            return

        try:
            exito, mensaje = self.sesion.guardar_progreso_rapido(ruta_guardar)

            if exito:
                messagebox.showinfo(
                    "Éxito", f"Progreso guardado:\n{os.path.basename(ruta_guardar)}"
                )
                self.barra_estado.config(
                    text=f"Progreso guardado: {os.path.basename(ruta_guardar)}"
                )
            else:
                messagebox.showerror("Error", mensaje)

        except Exception as e:
            messagebox.showerror("Error", f"Error al guardar progreso:\n{str(e)}")

    def _limpiar_todo(self):
        """Limpia toda la sesión actual"""
        if self.sesion and messagebox.askyesno(
            "Confirmar",
            "¿Está seguro de que desea limpiar todo?\nSe perderán todos los escaneos actuales.",
        ):
            # Crear nueva sesión vacía
            self.sesion = SesionInventario()
            self.reporte_processor = None
            self.ruta_reporte_actual = None

            # Actualizar interfaz
            self.lbl_archivo.config(
                text="No hay archivo cargado", foreground=AppColors.PENDIENTE
            )

            self.panel_estadisticas.actualizar(0, 0, 0, 0)
            self.lista_escaneos.limpiar()
            self.campo_escaneo.limpiar()

            # Deshabilitar botones
            self.btn_calcular_faltantes.config(state="disabled")
            self.btn_ver_faltantes.config(state="disabled")
            self.btn_exportar.config(state="disabled")

            # Deshabilitar botón de guardar progreso
            self.btn_guardar_progreso.config(state="disabled")

            # Actualizar barra de estado
            self.barra_estado.config(
                text="Sesión limpiada. Listo para cargar nuevo reporte."
            )

            # Enfocar campo de escaneo
            self.campo_escaneo.entry.focus_set()

    def _reproducir_sonido(self, tipo: str):
        """Reproduce un sonido según el tipo de resultado"""
        try:
            # Mapear tipos de resultado a TiposSonido
            mapeo_sonidos = {
                "exito": TipoSonido.EXITO,
                "advertencia": TipoSonido.ADVERTENCIA,
                "error": TipoSonido.ERROR,
            }

            if tipo in mapeo_sonidos:
                self.sound_manager.play(mapeo_sonidos[tipo])

        except Exception as e:
            # Fallback silencioso - no mostrar error al usuario
            # Solo imprimir en consola para debug
            print(f"Nota: No se pudo reproducir sonido '{tipo}': {e}")

    def _on_cerrar(self):
        """Maneja el cierre de la ventana de manera segura"""
        if self.sesion:
            respuesta = messagebox.askyesnocancel(
                "Salir",
                "¿Desea guardar los resultados antes de salir?\n\n"
                + "• Sí: Exportar y salir\n"
                + "• No: Salir sin guardar\n"
                + "• Cancelar: Volver a la aplicación",
            )

            if respuesta is None:  # Cancelar
                return
            elif respuesta:  # Sí (guardar y salir)
                self._exportar_antes_de_salir()

        # Forzar cierre limpio
        self.root.quit()
        self.root.destroy()
        sys.exit(0)  # Asegurar salida completa

    def _exportar_antes_de_salir(self):
        """Exporta automáticamente antes de salir"""
        if not self.sesion or not self.reporte_processor:
            return

        try:
            # Crear nombre de archivo automático
            nombre_base = (
                os.path.splitext(os.path.basename(self.ruta_reporte_actual))[0]
                if self.ruta_reporte_actual
                else "resultados"
            )
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            ruta_auto = os.path.join(
                os.path.expanduser("~"), f"{nombre_base}_AUTO_{fecha}.xlsx"
            )

            exito, mensaje = self.reporte_processor.exportar_con_resultados(
                self.sesion, ruta_auto
            )

            if exito:
                messagebox.showinfo(
                    "Exportado automáticamente",
                    f"Resultados guardados en:\n{ruta_auto}",
                )
        except Exception as e:
            print(f"Error al exportar automáticamente: {e}")

    def run(self):
        """Ejecuta la aplicación"""
        # Enfocar campo de escaneo al iniciar
        self.root.after(100, lambda: self.campo_escaneo.entry.focus_set())

        # Iniciar el loop principal
        self.root.mainloop()
