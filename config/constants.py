"""
CONSTANTES DE LA APLICACIÓN
Clases y constantes para configuración centralizada
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
import os
from pathlib import Path


@dataclass
class AppConstants:
    """Clase que contiene todas las constantes de la aplicación"""

    # Cantidad de digitos en el reporte para hacer match
    LONGITUD_CODIGO_BARRAS: int = 13

    # Nombres de columnas esperadas en el reporte
    COLUMNA_CODIGO_BARRA: str = "CODIGO DE BARRA"
    COLUMNA_SUCURSAL: str = "PDV"
    COLUMNA_VENDEDOR_DOC: str = "DOC VENDEDOR"
    COLUMNA_VENDEDOR_NOMBRE: str = "VENDEDOR"
    COLUMNA_FECHA_PAGO: str = "FECHA PAGO"
    COLUMNA_MONTO_PREMIO: str = "TOTAL PREMIO"
    COLUMNA_TIPO_PREMIO: str = "TIPO PREMIO"

    # Estados de escaneo
    ESTADO_ESCANEADO: str = "ESCANEADO"
    ESTADO_NO_ESCANEADO: str = "NO_ESCANEADO"
    ESTADO_DUPLICADO: str = "DUPLICADO"
    ESTADO_NO_REPORTADO: str = "NO_REPORTADO"

    # Códigos de resultado
    RESULTADO_OK: str = "OK"
    RESULTADO_DUPLICADO: str = "DUPLICADO"
    RESULTADO_NO_ENCONTRADO: str = "NO_ENCONTRADO"

    # Configuración de archivos
    EXTENSIONES_PERMITIDAS: List[str] = field(
        default_factory=lambda: [".xls", ".xlsx", ".csv"]
    )
    ENCODING: str = "utf-8"

    # Mensajes de interfaz
    MSG_CARGA_EXITOSA: str = "Reporte cargado exitosamente"
    MSG_BOLETO_ENCONTRADO: str = "Boleto encontrado y marcado"
    MSG_BOLETO_DUPLICADO: str = "Boleto ya fue escaneado"
    MSG_BOLETO_NO_REPORTADO: str = "Boleto no está en el reporte"

    # Configuración de diálogos de archivo
    FILTRO_EXCEL: List[tuple] = field(
        default_factory=lambda: [("Archivos Excel", "*.xlsx *.xls")]
    )
    FILTRO_CSV: List[tuple] = field(default_factory=lambda: [("Archivos CSV", "*.csv")])
    FILTRO_EXCEL_CSV: List[tuple] = field(
        default_factory=lambda: [
            ("Archivos Excel", "*.xlsx *.xls"),
            ("Archivos CSV", "*.csv"),
        ]
    )
    FILTRO_EXPORTACION: List[tuple] = field(
        default_factory=lambda: [
            ("Archivos Excel", "*.xlsx"),
            ("Archivos CSV", "*.csv"),
        ]
    )
    FILTRO_JSON: List[tuple] = field(
        default_factory=lambda: [("Archivos JSON", "*.json")]
    )

    def obtener_columnas_relevantes(self) -> List[str]:
        """Retorna lista de columnas relevantes para el procesamiento"""
        return [
            self.COLUMNA_CODIGO_BARRA,
            self.COLUMNA_SUCURSAL,
            self.COLUMNA_VENDEDOR_DOC,
            self.COLUMNA_VENDEDOR_NOMBRE,
            self.COLUMNA_FECHA_PAGO,
            self.COLUMNA_MONTO_PREMIO,
            self.COLUMNA_TIPO_PREMIO,
        ]

    def validar_nombre_columna(self, nombre_columna: str) -> bool:
        """Valida si un nombre de columna es válido"""
        nombres_validos = self.obtener_columnas_relevantes()
        return nombre_columna in nombres_validos

    # Rutas por defecto (propiedades, no campos de dataclass)
    @property
    def CARPETA_DOCUMENTOS(self) -> str:
        """Retorna la carpeta de Documentos del usuario (solo español)"""
        documentos_path = Path.home() / "Documentos"
        return str(documentos_path)

    @property
    def CARPETA_DESCARGAS(self) -> str:
        """Retorna la carpeta de Descargas del usuario (solo español)"""
        descargas_path = Path.home() / "Descargas"
        return str(descargas_path)

    @property
    def CARPETA_RESULTADOS(self) -> str:
        """Retorna la carpeta sugerida para guardar resultados (solo español)"""
        resultados_path = (
            Path.home() / "Documentos" / "Raspas" / "Resultados Inventario"
        )

        # Crear la carpeta completa incluyendo padres si es necesario
        resultados_path.mkdir(parents=True, exist_ok=True)

        return str(resultados_path)

    @property
    def CARPETA_PROGRESO(self) -> str:
        """Retorna la carpeta sugerida para guardar progresos (solo español)"""
        progreso_path = Path.home() / "Documentos" / "Raspas" / "Progresos Inventario"

        # Crear la carpeta completa incluyendo padres si es necesario
        progreso_path.mkdir(parents=True, exist_ok=True)

        return str(progreso_path)


class AppConfig:
    """Clase de configuración de la aplicación"""

    def __init__(self):
        self.constantes = AppConstants()
        self.debug_mode: bool = False
        self.log_escaneos: bool = True
        self.auto_calcular_faltantes: bool = True

    @property
    def columnas_relevantes(self) -> List[str]:
        """Propiedad que retorna columnas relevantes"""
        return self.constantes.obtener_columnas_relevantes()
