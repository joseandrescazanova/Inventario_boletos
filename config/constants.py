"""
CONSTANTES DE LA APLICACIÓN
Clases y constantes para configuración centralizada
"""

from dataclasses import dataclass
from typing import List, Dict, Any


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
    EXTENSIONES_PERMITIDAS: List[str] = (".xls", ".xlsx", ".csv")
    ENCODING: str = "utf-8"

    # Mensajes de interfaz
    MSG_CARGA_EXITOSA: str = "Reporte cargado exitosamente"
    MSG_BOLETO_ENCONTRADO: str = "Boleto encontrado y marcado"
    MSG_BOLETO_DUPLICADO: str = "Boleto ya fue escaneado"
    MSG_BOLETO_NO_REPORTADO: str = "Boleto no está en el reporte"

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
