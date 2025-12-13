"""
GESTOR DE DIÁLOGOS DE ARCHIVOS
Centraliza la gestión de diálogos de apertura/guardado de archivos
"""

import os
from datetime import datetime
from pathlib import Path
from tkinter import filedialog
from typing import Optional, Tuple, List

from inventario_boletos.config.constants import AppConstants, AppConfig


class FileDialogManager:
    """Gestor centralizado de diálogos de archivos"""

    def __init__(self, config: Optional[AppConfig] = None):
        """Inicializa el gestor de diálogos"""
        self.config = config or AppConfig()
        self.constantes = self.config.constantes
        self._ultima_ruta = None  # Para recordar la última ubicación

    def seleccionar_reporte_nuevo(
        self, titulo: str = "Seleccionar reporte de boletos"
    ) -> Optional[str]:
        """
        Abre diálogo para seleccionar un reporte nuevo (Excel/CSV)

        Args:
            titulo: Título del diálogo

        Returns:
            Ruta del archivo seleccionado o None
        """
        # Usar carpeta de Documentos como ubicación inicial
        initialdir = self._obtener_ubicacion_inicial("cargar")

        # Usar filtro estricto SIN opción "Todos los archivos"
        ruta = filedialog.askopenfilename(
            title=titulo,
            filetypes=self.constantes.FILTRO_EXCEL_CSV,  # Solo Excel y CSV
            initialdir=initialdir,
        )

        if ruta:
            self._ultima_ruta = os.path.dirname(ruta)

        return ruta if ruta else None

    def seleccionar_reporte_continuar(
        self, titulo: str = "Seleccionar reporte para continuar"
    ) -> Optional[str]:
        """
        Abre diálogo para seleccionar un reporte Excel/CSV para continuar escaneo

        Args:
            titulo: Título del diálogo

        Returns:
            Ruta del archivo seleccionado o None
        """
        # Usar carpeta de resultados como ubicación inicial
        initialdir = self.constantes.CARPETA_RESULTADOS

        # SOLO Excel y CSV (sin JSON)
        ruta = filedialog.askopenfilename(
            title=titulo,
            filetypes=self.constantes.FILTRO_EXCEL_CSV,
            initialdir=initialdir,
        )

        if ruta:
            self._ultima_ruta = os.path.dirname(ruta)

        return ruta if ruta else None

    def seleccionar_progreso_json(
        self, titulo: str = "Seleccionar progreso guardado"
    ) -> str:  # Cambiar a str en lugar de Optional[str]
        """
        Abre diálogo específico para seleccionar archivos de progreso JSON

        Args:
            titulo: Título del diálogo

        Returns:
            Ruta del archivo JSON seleccionado o cadena vacía si se cancela
        """
        # Usar carpeta de progreso como ubicación inicial
        initialdir = self.constantes.CARPETA_PROGRESO

        # Solo archivos JSON
        ruta = filedialog.askopenfilename(
            title=titulo, filetypes=self.constantes.FILTRO_JSON, initialdir=initialdir
        )

        if ruta:
            self._ultima_ruta = os.path.dirname(ruta)
            return ruta

        return ""  # Retornar cadena vacía en lugar de None

    def guardar_resultados(
        self, nombre_base: str = "reporte", titulo: str = "Guardar resultados como"
    ) -> Optional[str]:
        """
        Abre diálogo para guardar resultados de exportación

        Args:
            nombre_base: Nombre base para sugerir
            titulo: Título del diálogo

        Returns:
            Ruta donde guardar o None
        """
        # Usar carpeta de resultados como ubicación inicial
        initialdir = self.constantes.CARPETA_RESULTADOS

        # GARANTIZAR QUE LA CARPETA EXISTA
        os.makedirs(initialdir, exist_ok=True)

        # Generar nombre sugerido automático
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"{nombre_base}_RESULTADOS_{fecha}.xlsx"

        # Filtro para exportación (solo Excel y CSV, Excel por defecto)
        ruta = filedialog.asksaveasfilename(
            title=titulo,
            defaultextension=".xlsx",
            initialfile=nombre_sugerido,
            filetypes=self.constantes.FILTRO_EXPORTACION,  # Solo Excel y CSV
            initialdir=initialdir,
        )

        if ruta:
            self._ultima_ruta = os.path.dirname(ruta)

        return ruta if ruta else None

    def guardar_progreso_json(
        self, nombre_base: str = "progreso", titulo: str = "Guardar progreso rápido"
    ) -> Optional[str]:
        """
        Abre diálogo para guardar progreso en JSON

        Args:
            nombre_base: Nombre base para sugerir
            titulo: Título del diálogo

        Returns:
            Ruta donde guardar o None
        """
        # Usar carpeta de progreso como ubicación inicial
        initialdir = self.constantes.CARPETA_PROGRESO

        # GARANTIZAR QUE LA CARPETA EXISTA
        os.makedirs(initialdir, exist_ok=True)

        # Generar nombre sugerido automático
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_sugerido = f"{nombre_base}_PROGRESO_{fecha}.json"

        # Solo JSON permitido
        ruta = filedialog.asksaveasfilename(
            title=titulo,
            defaultextension=".json",
            initialfile=nombre_sugerido,
            filetypes=self.constantes.FILTRO_JSON,  # Solo JSON
            initialdir=initialdir,
        )

        if ruta:
            self._ultima_ruta = os.path.dirname(ruta)

        return ruta if ruta else None

    def _obtener_ubicacion_inicial(self, tipo: str) -> str:
        """
        Obtiene la ubicación inicial inteligente para diálogos
        """
        # Prioridad 1: Última ruta usada
        if self._ultima_ruta and os.path.exists(self._ultima_ruta):
            return self._ultima_ruta

        # Prioridad 2: Carpeta específica según tipo
        if tipo == "cargar":
            # Para cargar, usar Documentos (en español)
            documentos_path = self.constantes.CARPETA_DOCUMENTOS
            if os.path.exists(documentos_path):
                return documentos_path
            # Si no existe Documentos, usar el directorio actual
            return os.getcwd()

        elif tipo == "guardar":
            # Para guardar, usar carpeta de resultados
            return self.constantes.CARPETA_RESULTADOS

        elif tipo == "continuar":
            # Para continuar, usar carpeta de resultados
            return self.constantes.CARPETA_RESULTADOS

        # Fallback: directorio actual
        return os.getcwd()

    def crear_nombre_autoexport(self, nombre_base: str) -> str:
        """
        Crea un nombre automático para exportación al cerrar

        Args:
            nombre_base: Nombre base del archivo original

        Returns:
            Ruta completa para guardado automático
        """
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"{nombre_base}_AUTO_{fecha}.xlsx"

        # Guardar en carpeta de resultados
        carpeta_resultados = Path(self.constantes.CARPETA_RESULTADOS)
        carpeta_resultados.mkdir(exist_ok=True)

        return str(carpeta_resultados / nombre_archivo)

    def obtener_ruta_autoexport(self, ruta_reporte_actual: Optional[str] = None) -> str:
        """
        Obtiene ruta para exportación automática al cerrar

        Args:
            ruta_reporte_actual: Ruta del reporte actual (opcional)

        Returns:
            Ruta para guardado automático
        """
        if ruta_reporte_actual:
            nombre_base = os.path.splitext(os.path.basename(ruta_reporte_actual))[0]
        else:
            nombre_base = "resultados"

        return self.crear_nombre_autoexport(nombre_base)

    # def _crear_carpetas_necesarias(self):
    #     """Crea todas las carpetas necesarias si no existen"""
    #     carpetas_necesarias = [
    #         self.constantes.CARPETA_PROGRESO,
    #         self.constantes.CARPETA_RESULTADOS,
    #     ]

    #     for carpeta in carpetas_necesarias:
    #         try:
    #             os.makedirs(carpeta, exist_ok=True)
    #             print(f"Directorio creado/verificado: {carpeta}")
    #         except Exception as e:
    #             print(f"Error al crear directorio {carpeta}: {e}")
