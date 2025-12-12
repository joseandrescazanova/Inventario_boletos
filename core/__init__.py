"""
Módulo core - Núcleo de la aplicación
"""
from .entities import (
    Boleto,
    SesionInventario,
    Estadisticas,
    EstadoBoleto,
    ResultadoEscaneo
)

from .report_processor import ReporteProcessor, ReporteProcessorError

__all__ = [
    'Boleto',
    'SesionInventario',
    'Estadisticas',
    'EstadoBoleto',
    'ResultadoEscaneo',
    'ReporteProcessor',
    'ReporteProcessorError'
]