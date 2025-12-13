"""
ENTIDADES DEL DOMINIO
Clases principales que representan los objetos de negocio
"""

from datetime import datetime
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum
from inventario_boletos.config.constants import AppConstants


class EstadoBoleto(str, Enum):
    """Enumeración de estados posibles de un boleto"""

    PENDIENTE = "PENDIENTE"
    ESCANEADO = "ESCANEADO"
    DUPLICADO = "DUPLICADO"
    NO_REPORTADO = "NO_REPORTADO"


class ResultadoEscaneo(str, Enum):
    """Enumeración de resultados posibles de un escaneo"""

    EXITO = "EXITO"
    DUPLICADO = "DUPLICADO"
    NO_ENCONTRADO = "NO_ENCONTRADO"
    ERROR = "ERROR"


@dataclass
class Boleto:
    """
    Entidad que representa un boleto físico/digital.
    Corresponde a una fila del reporte Excel.
    """

    codigo: str
    sucursal: str = ""
    vendedor_documento: str = ""
    vendedor_nombre: str = ""
    fecha_pago: str = ""
    monto_premio: float = 0.0
    tipo_premio: str = ""

    # Estado interno
    estado: EstadoBoleto = EstadoBoleto.PENDIENTE
    fecha_escaneo: Optional[datetime] = None
    escaneos_realizados: int = 0
    datos_originales: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validaciones después de la inicialización"""
        self.codigo = str(self.codigo).strip()
        if not self.codigo:
            raise ValueError("El código del boleto no puede estar vacío")

    def marcar_escaneado(self) -> "Boleto":
        """
        Marca el boleto como escaneado.
        SOLO aumenta contador si es primera vez.
        """
        if self.estado == EstadoBoleto.ESCANEADO:
            # Ya estaba escaneado - marcar como duplicado PERO NO aumentar contador
            self.estado = EstadoBoleto.DUPLICADO
            # NO aumentar self.escaneos_realizados
        elif self.estado == EstadoBoleto.DUPLICADO:
            # Ya era duplicado - mantener estado y NO aumentar contador
            pass  # No hacer nada
        else:
            # Primera vez - marcar como escaneado y aumentar contador
            self.estado = EstadoBoleto.ESCANEADO
            self.escaneos_realizados = 1  # Siempre 1 para primer escaneo

        self.fecha_escaneo = datetime.now()
        return self

    def marcar_no_reportado(self) -> "Boleto":
        """Marca el boleto como no reportado"""
        self.estado = EstadoBoleto.NO_REPORTADO
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el boleto a diccionario para exportación"""
        return {
            "CODIGO_DE_BARRA": self.codigo,
            "PDV": self.sucursal,
            "DOC_VENDEDOR": self.vendedor_documento,
            "VENDEDOR": self.vendedor_nombre,
            "FECHA_PAGO": self.fecha_pago,
            "TOTAL_PREMIO": self.monto_premio,
            "TIPO_PREMIO": self.tipo_premio,
            "ESTADO_ESCANEO": self.estado.value,
            "FECHA_ESCANEO": self.fecha_escaneo.isoformat()
            if self.fecha_escaneo
            else "",
            "ESCANEOS_REALIZADOS": self.escaneos_realizados,
        }

    @property
    def fue_escaneado(self) -> bool:
        """Propiedad que indica si el boleto fue escaneado"""
        return self.estado == EstadoBoleto.ESCANEADO

    @property
    def es_duplicado(self) -> bool:
        """Propiedad que indica si el boleto es duplicado"""
        return self.estado == EstadoBoleto.DUPLICADO

    def __str__(self) -> str:
        return f"Boleto({self.codigo}, {self.vendedor_nombre}, {self.estado.value})"


@dataclass
class Estadisticas:
    """Entidad que representa las estadísticas de una sesión"""

    total_boletos: int = 0
    escaneados: int = 0
    duplicados: int = 0
    no_encontrados: int = 0
    pendientes: int = 0

    def actualizar_desde_boletos(self, boletos: List[Boleto]) -> "Estadisticas":
        """Actualiza estadísticas desde una lista de boletos"""
        self.total_boletos = len(boletos)

        # Escaneados: solo boletos con estado ESCANEADO
        self.escaneados = sum(1 for b in boletos if b.estado == EstadoBoleto.ESCANEADO)

        # Duplicados: solo boletos con estado DUPLICADO
        self.duplicados = sum(1 for b in boletos if b.estado == EstadoBoleto.DUPLICADO)

        # No reportados: NO se cuentan aquí (no están en la lista de boletos)
        self.no_encontrados = (
            0  # Siempre 0 porque no se crean objetos para no reportados
        )

        # Pendientes: PENDIENTE o cualquier otro estado
        self.pendientes = sum(1 for b in boletos if b.estado == EstadoBoleto.PENDIENTE)

        return self

    def to_dict(self) -> Dict[str, int]:
        """Convierte las estadísticas a diccionario"""
        return {
            "total_boletos": self.total_boletos,
            "escaneados": self.escaneados,
            "duplicados": self.duplicados,
            "no_encontrados": self.no_encontrados,
            "pendientes": self.pendientes,
            "porcentaje_escaneados": self.porcentaje_escaneados,
        }

    @property
    def porcentaje_escaneados(self) -> float:
        """Calcula el porcentaje de boletos escaneados"""
        if self.total_boletos == 0:
            return 0.0
        return round((self.escaneados / self.total_boletos) * 100, 2)

    def __str__(self) -> str:
        return (
            f"Estadísticas: {self.escaneados}/{self.total_boletos} "
            f"({self.porcentaje_escaneados}%) escaneados"
        )


@dataclass
class SesionInventario:
    """
    Entidad que representa una sesión completa de inventario.
    Agrega y coordina todos los boletos de una sesión.
    """

    id_sesion: str = field(
        default_factory=lambda: datetime.now().strftime("%Y%m%d_%H%M%S")
    )
    fecha_inicio: datetime = field(default_factory=datetime.now)
    fecha_fin: Optional[datetime] = None

    ruta_reporte_original: Optional[str] = None

    # Colecciones
    boletos: Dict[str, Boleto] = field(default_factory=dict)  # código -> Boleto
    escaneos: List[Dict[str, Any]] = field(default_factory=list)

    # Estadísticas
    estadisticas: Estadisticas = field(default_factory=Estadisticas)

    def __post_init__(self):
        """Inicialización después de crear la instancia"""
        self.constantes = AppConstants()

    def agregar_boleto(self, boleto: Boleto) -> "SesionInventario":
        """Agrega un boleto a la sesión"""
        if boleto.codigo in self.boletos:
            raise ValueError(f"Boleto {boleto.codigo} ya existe en la sesión")

        self.boletos[boleto.codigo] = boleto
        self.estadisticas.total_boletos = len(self.boletos)
        return self

    def agregar_boletos(self, boletos: List[Boleto]) -> "SesionInventario":
        """Agrega múltiples boletos a la sesión"""
        for boleto in boletos:
            self.agregar_boleto(boleto)
        return self

    def buscar_boleto(self, codigo: str) -> Optional[Boleto]:
        """Busca un boleto por su código"""
        return self.boletos.get(str(codigo).strip())

    def procesar_escaneo(self, codigo_escaneado: str) -> Dict[str, Any]:
        from inventario_boletos.config.constants import AppConstants

        constantes = AppConstants()

        # Procesar código: solo dígitos, últimos N caracteres
        solo_digitos = "".join(filter(str.isdigit, codigo_escaneado))
        if len(solo_digitos) >= constantes.LONGITUD_CODIGO_BARRAS:
            codigo_buscado = solo_digitos[-constantes.LONGITUD_CODIGO_BARRAS :]
        else:
            codigo_buscado = solo_digitos

        # Resto del método igual, usando codigo_buscado en lugar de codigo_escaneado
        codigo = str(codigo_buscado).strip()
        ###########################################################

        timestamp = datetime.now()

        # Buscar boleto
        boleto = self.buscar_boleto(codigo)

        if boleto:
            if boleto.fue_escaneado or boleto.es_duplicado:
                # Boleto duplicado - NO aumentar contador
                resultado = {
                    "resultado": ResultadoEscaneo.DUPLICADO,
                    "boleto": boleto,
                    "mensaje": f"Boleto {codigo} ya fue escaneado anteriormente",
                    "timestamp": timestamp,
                    "fue_duplicado": True,
                }
                # NO llamar a marcar_escaneado() - mantener contador actual
            else:
                # Boleto encontrado por primera vez
                boleto.marcar_escaneado()  # Esto sí aumenta contador a 1
                resultado = {
                    "resultado": ResultadoEscaneo.EXITO,
                    "boleto": boleto,
                    "mensaje": f"Boleto {codigo} escaneado correctamente",
                    "timestamp": timestamp,
                    "fue_duplicado": False,
                }
        else:
            # Boleto no encontrado - NO crear objeto Boleto ni contar
            resultado = {
                "resultado": ResultadoEscaneo.NO_ENCONTRADO,
                "boleto": None,  # En lugar de crear boleto fantasma
                "mensaje": f"Boleto {codigo} no encontrado en el reporte",
                "timestamp": timestamp,
                "fue_duplicado": False,
            }

        # Registrar escaneo
        self.escaneos.append(resultado)

        # Actualizar estadísticas
        self.actualizar_estadisticas()

        return resultado

    def actualizar_estadisticas(self) -> "SesionInventario":
        """Actualiza las estadísticas de la sesión"""
        self.estadisticas.actualizar_desde_boletos(list(self.boletos.values()))
        return self

    def obtener_boletos_faltantes(self) -> List[Boleto]:
        """Retorna lista de boletos pendientes de escanear"""
        return [b for b in self.boletos.values() if b.estado == EstadoBoleto.PENDIENTE]

    def finalizar_sesion(self) -> "SesionInventario":
        """Marca la sesión como finalizada"""
        self.fecha_fin = datetime.now()
        self.actualizar_estadisticas()
        return self

    @property
    def duracion(self) -> Optional[float]:
        """Calcula la duración de la sesión en segundos"""
        if self.fecha_fin and self.fecha_inicio:
            return (self.fecha_fin - self.fecha_inicio).total_seconds()
        elif self.fecha_inicio:
            return (datetime.now() - self.fecha_inicio).total_seconds()
        return None

    @classmethod
    def cargar_progreso_rapido(cls, ruta_json: str):
        """
        Carga una sesión desde un archivo JSON guardado previamente

        Args:
            ruta_json: Ruta al archivo JSON

        Returns:
            Tuple (éxito, mensaje, sesion_cargada)
        """
        try:
            import json
            from datetime import datetime
            import os

            # Verificar que el archivo existe
            if not os.path.exists(ruta_json):
                return False, f"Archivo no encontrado: {ruta_json}", None

            # Leer el archivo JSON
            with open(ruta_json, "r", encoding="utf-8") as f:
                datos = json.load(f)

            # Crear nueva sesión
            sesion = SesionInventario()

            # Restaurar campos básicos
            sesion.id_sesion = datos.get("id_sesion", sesion.id_sesion)
            sesion.ruta_reporte_original = datos.get("ruta_reporte_original")

            # Restaurar fecha_inicio si está en los datos
            fecha_inicio_str = datos.get("fecha_inicio")
            if fecha_inicio_str:
                try:
                    sesion.fecha_inicio = datetime.fromisoformat(fecha_inicio_str)
                except:
                    pass  # Mantener la fecha_inicio por defecto

            # Restaurar fecha_fin si está en los datos
            fecha_fin_str = datos.get("fecha_fin")
            if fecha_fin_str:
                try:
                    sesion.fecha_fin = datetime.fromisoformat(fecha_fin_str)
                except:
                    sesion.fecha_fin = None

            # Restaurar boletos
            if "boletos" in datos and isinstance(datos["boletos"], list):
                for boleto_data in datos["boletos"]:
                    # Crear boleto
                    boleto = Boleto(
                        codigo=boleto_data.get("codigo", ""),
                        sucursal=boleto_data.get("sucursal", ""),
                        vendedor_documento=boleto_data.get("vendedor_documento", ""),
                        vendedor_nombre=boleto_data.get("vendedor_nombre", ""),
                        fecha_pago=boleto_data.get("fecha_pago", ""),
                        monto_premio=float(boleto_data.get("monto_premio", 0.0)),
                        tipo_premio=boleto_data.get("tipo_premio", ""),
                        datos_originales=boleto_data.get("datos_originales", {}),
                    )

                    # Restaurar estado
                    estado_str = boleto_data.get("estado", "PENDIENTE")
                    try:
                        boleto.estado = EstadoBoleto[estado_str]
                    except:
                        boleto.estado = EstadoBoleto.PENDIENTE

                    # Restaurar fecha de escaneo
                    fecha_escaneo_str = boleto_data.get("fecha_escaneo")
                    if fecha_escaneo_str:
                        try:
                            boleto.fecha_escaneo = datetime.fromisoformat(
                                fecha_escaneo_str
                            )
                        except:
                            boleto.fecha_escaneo = None

                    # Restaurar escaneos realizados
                    boleto.escaneos_realizados = boleto_data.get(
                        "escaneos_realizados", 0
                    )

                    # Agregar a la sesión (como diccionario)
                    sesion.boletos[boleto.codigo] = boleto

            # Restaurar estadísticas
            if "estadisticas" in datos:
                stats_data = datos["estadisticas"]
                sesion.estadisticas = Estadisticas(
                    total_boletos=stats_data.get("total_boletos", 0),
                    escaneados=stats_data.get("escaneados", 0),
                    pendientes=stats_data.get("pendientes", 0),
                    duplicados=stats_data.get("duplicados", 0),
                    no_encontrados=stats_data.get("no_encontrados", 0),
                )
            else:
                # Si no hay estadísticas guardadas, calcularlas
                sesion.actualizar_estadisticas()

            return True, "Progreso cargado exitosamente", sesion

        except json.JSONDecodeError as e:
            return False, f"Error al leer archivo JSON: {str(e)}", None
        except Exception as e:
            return False, f"Error al cargar progreso: {str(e)}", None

    def guardar_progreso_rapido(self, ruta_archivo: str):
        """
        Guarda el progreso actual en un archivo JSON simple.

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            import json
            import os

            # Preparar datos para guardar
            datos = {
                "id_sesion": self.id_sesion,
                "fecha_inicio": self.fecha_inicio.isoformat()
                if self.fecha_inicio
                else None,
                "fecha_fin": self.fecha_fin.isoformat() if self.fecha_fin else None,
                "ruta_reporte_original": self.ruta_reporte_original,
                "boletos": [],  # Lista de objetos boleto completos
            }

            # Guardar todos los boletos completos
            for boleto in self.boletos.values():
                datos["boletos"].append(
                    {
                        "codigo": boleto.codigo,
                        "sucursal": boleto.sucursal,
                        "vendedor_documento": boleto.vendedor_documento,
                        "vendedor_nombre": boleto.vendedor_nombre,
                        "fecha_pago": boleto.fecha_pago,
                        "monto_premio": boleto.monto_premio,
                        "tipo_premio": boleto.tipo_premio,
                        "estado": boleto.estado.value,
                        "fecha_escaneo": boleto.fecha_escaneo.isoformat()
                        if boleto.fecha_escaneo
                        else None,
                        "escaneos_realizados": boleto.escaneos_realizados,
                        "datos_originales": boleto.datos_originales,
                    }
                )

            # Guardar estadísticas
            datos["estadisticas"] = self.estadisticas.to_dict()

            # Asegurar que el directorio existe
            directorio = os.path.dirname(ruta_archivo)
            if directorio and not os.path.exists(directorio):
                os.makedirs(directorio)

            # Guardar en archivo
            with open(ruta_archivo, "w", encoding="utf-8") as f:
                json.dump(datos, f, indent=2, ensure_ascii=False)

            return True, f"Progreso guardado en {ruta_archivo}"

        except Exception as e:
            return False, f"Error al guardar progreso: {str(e)}"

    def __str__(self) -> str:
        estado = "ACTIVA" if self.fecha_fin is None else "FINALIZADA"
        return f"Sesión {self.id_sesion} - {estado} - {self.estadisticas}"
