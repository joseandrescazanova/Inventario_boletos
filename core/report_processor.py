"""
PROCESADOR DE REPORTES EXCEL
Clase para cargar y procesar archivos Excel/CSV con reportes de boletos
"""

import pandas as pd
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from inventario_boletos.core.entities import Boleto
from inventario_boletos.config.constants import AppConstants, AppConfig
from inventario_boletos.core.entities import Boleto, EstadoBoleto  # Añadir EstadoBoleto


class ReporteProcessorError(Exception):
    """Excepción personalizada para errores en el procesamiento de reportes"""

    pass


class ReporteProcessor:
    """
    Clase responsable de cargar y procesar archivos de reporte Excel/CSV.
    Convierte los datos del archivo en objetos Boleto.
    """

    def __init__(self, config: Optional[AppConfig] = None):
        """Inicializa el procesador de reportes"""
        self.config = config or AppConfig()
        self.constantes = self.config.constantes
        self.df = None  # DataFrame de pandas
        self.columnas_detectadas = {}
        self.errores = []

    def cargar_archivo(self, ruta_archivo: str) -> Tuple[bool, str]:
        """
        Carga un archivo Excel o CSV.

        Args:
            ruta_archivo: Ruta completa al archivo

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            # Validar que el archivo existe
            if not os.path.exists(ruta_archivo):
                raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")

            # Validar extensión
            extension = os.path.splitext(ruta_archivo)[1].lower()
            if extension not in self.constantes.EXTENSIONES_PERMITIDAS:
                extensiones = ", ".join(self.constantes.EXTENSIONES_PERMITIDAS)
                raise ValueError(f"Extensión no permitida. Use: {extensiones}")

            # Cargar archivo según extensión
            if extension == ".csv":
                self.df = pd.read_csv(
                    ruta_archivo, encoding=self.constantes.ENCODING, dtype=str
                )
            else:  # .xls o .xlsx
                # Leer manteniendo los tipos originales como string
                self.df = pd.read_excel(ruta_archivo, dtype=str)

            # Validar que el DataFrame no esté vacío
            if self.df.empty:
                raise ValueError("El archivo está vacío o no contiene datos")

            # Detectar columnas relevantes
            self._detectar_columnas()

            # Validar columnas mínimas requeridas
            if not self._validar_columnas_minimas():
                columnas_req = self.constantes.COLUMNA_CODIGO_BARRA
                raise ValueError(f"Columna requerida no encontrada: '{columnas_req}'")

            # Limpiar datos
            self._limpiar_datos()

            return True, self.constantes.MSG_CARGA_EXITOSA

        except Exception as e:
            self.errores.append(str(e))
            return False, f"Error al cargar archivo: {str(e)}"

    def _detectar_columnas(self) -> None:
        """Detecta automáticamente las columnas relevantes en el DataFrame"""
        if self.df is None or self.df.empty:
            return

        # Mapeo de nombres posibles para cada columna
        mapeo_posibles_nombres = {
            self.constantes.COLUMNA_CODIGO_BARRA: [
                "CODIGO DE BARRA",
                "CODIGO_DE_BARRA",
                "CODIGO",
                "CÓDIGO DE BARRAS",
                "CODIGO_BARRAS",
                "BARCODE",
                "CÓDIGO",
            ],
            self.constantes.COLUMNA_SUCURSAL: [
                "PDV",
                "SUCURSAL",
                "PUNTO DE VENTA",
                "PUNTO_VENTA",
                "PUNTOVENTA",
                "PTO VENTA",
                "PUNTO",
            ],
            self.constantes.COLUMNA_VENDEDOR_DOC: [
                "DOC VENDEDOR",
                "DOC_VENDEDOR",
                "DOCUMENTO VENDEDOR",
                "DOCUMENTO_VENDEDOR",
                "CEDULA VENDEDOR",
                "VENDEDOR_DOC",
                "DOC",
                "DOCUMENTO",
            ],
            self.constantes.COLUMNA_VENDEDOR_NOMBRE: [
                "VENDEDOR",
                "NOMBRE VENDEDOR",
                "NOMBRE_VENDEDOR",
                "VENDEDOR_NOMBRE",
                "CAJERO",
                "NOMBRE",
            ],
            self.constantes.COLUMNA_FECHA_PAGO: [
                "FECHA PAGO",
                "FECHA_PAGO",
                "FECHA",
                "FECHA DE PAGO",
                "FECHA_DE_PAGO",
                "FECHAPAGO",
            ],
            self.constantes.COLUMNA_MONTO_PREMIO: [
                "TOTAL PREMIO",
                "TOTAL_PREMIO",
                "MONTO PREMIO",
                "MONTO_PREMIO",
                "PREMIO",
                "VALOR PREMIO",
                "VALOR",
            ],
            self.constantes.COLUMNA_TIPO_PREMIO: [
                "TIPO PREMIO",
                "TIPO_PREMIO",
                "TIPO",
                "TIPO DE PREMIO",
            ],
        }

        # Detectar cada columna
        self.columnas_detectadas = {}

        for columna_estandar, posibles_nombres in mapeo_posibles_nombres.items():
            for nombre_posible in posibles_nombres:
                if nombre_posible.upper() in [col.upper() for col in self.df.columns]:
                    # Encontrar el nombre exacto en el DataFrame
                    for col_real in self.df.columns:
                        if col_real.upper() == nombre_posible.upper():
                            self.columnas_detectadas[columna_estandar] = col_real
                            break
                    break

        # Si no detectamos algunas columnas, usar las disponibles
        for columna in self.df.columns:
            col_upper = columna.upper()
            # Buscar coincidencia parcial para columnas no detectadas
            for col_estandar in mapeo_posibles_nombres.keys():
                if col_estandar not in self.columnas_detectadas:
                    # Buscar palabras clave en el nombre de la columna
                    palabras_clave = col_estandar.split()
                    if any(palabra in col_upper for palabra in palabras_clave):
                        self.columnas_detectadas[col_estandar] = columna
                        break

    def _validar_columnas_minimas(self) -> bool:
        """Valida que existan las columnas mínimas requeridas"""
        if not self.columnas_detectadas:
            return False

        # Columna absolutamente requerida: código de barras
        columna_clave = self.constantes.COLUMNA_CODIGO_BARRA
        if columna_clave not in self.columnas_detectadas:
            return False

        return True

    def _limpiar_datos(self) -> None:
        """Limpia y normaliza los datos del DataFrame"""
        if self.df is None:
            return

        # 1. Eliminar filas completamente vacías
        self.df = self.df.dropna(how="all")

        # 2. Limpiar código de barras (columna clave) - PRESERVANDO CEROS A LA IZQUIERDA
        col_codigo = self.columnas_detectadas.get(self.constantes.COLUMNA_CODIGO_BARRA)
        if col_codigo:
            # Convertir a string, preservando ceros a la izquierda
            self.df[col_codigo] = self.df[col_codigo].apply(
                lambda x: str(x).strip() if pd.notna(x) else ""
            )
            # Eliminar filas con código vacío
            self.df = self.df[self.df[col_codigo] != ""]
            self.df = self.df[self.df[col_codigo].astype(str) != "nan"]
            self.df = self.df[self.df[col_codigo].astype(str) != "None"]

        # 3. Limpiar otras columnas de texto
        columnas_texto = [
            self.columnas_detectadas.get(self.constantes.COLUMNA_SUCURSAL),
            self.columnas_detectadas.get(self.constantes.COLUMNA_VENDEDOR_NOMBRE),
            self.columnas_detectadas.get(self.constantes.COLUMNA_TIPO_PREMIO),
            self.columnas_detectadas.get(self.constantes.COLUMNA_VENDEDOR_DOC),
            self.columnas_detectadas.get(self.constantes.COLUMNA_FECHA_PAGO),
        ]

        for col in columnas_texto:
            if col and col in self.df.columns:
                self.df[col] = self.df[col].apply(
                    lambda x: str(x).strip() if pd.notna(x) else ""
                )

        # 4. Limpiar columna de monto premio
        col_monto = self.columnas_detectadas.get(self.constantes.COLUMNA_MONTO_PREMIO)
        if col_monto and col_monto in self.df.columns:
            # Convertir a numérico, errores a NaN
            self.df[col_monto] = pd.to_numeric(self.df[col_monto], errors="coerce")
            # Reemplazar NaN por 0
            self.df[col_monto] = self.df[col_monto].fillna(0)

        # 5. Eliminar duplicados por código de barras
        if col_codigo:
            self.df = self.df.drop_duplicates(subset=[col_codigo], keep="first")

    def obtener_boletos(self) -> List[Boleto]:
        """
        Convierte los datos del reporte en objetos Boleto.

        Returns:
            Lista de objetos Boleto
        """
        if self.df is None or self.df.empty:
            return []

        boletos = []

        for idx, fila in self.df.iterrows():
            try:
                # Obtener valores de las columnas detectadas
                datos_boleto = {}

                for col_estandar, col_real in self.columnas_detectadas.items():
                    if col_real in fila:
                        valor = fila[col_real]
                        # Convertir a string preservando el formato
                        if pd.isna(valor):
                            datos_boleto[col_estandar] = ""
                        else:
                            # Para código de barras, preservar exactamente como está
                            if col_estandar == self.constantes.COLUMNA_CODIGO_BARRA:
                                # Preservar ceros a la izquierda y formato original
                                datos_boleto[col_estandar] = str(valor).strip()
                            else:
                                datos_boleto[col_estandar] = str(valor).strip()
                    else:
                        datos_boleto[col_estandar] = ""

                # Asegurar que el código sea string y tenga ceros a la izquierda
                codigo = datos_boleto[self.constantes.COLUMNA_CODIGO_BARRA]

                # Convertir monto premio a float seguro
                monto_str = datos_boleto.get(self.constantes.COLUMNA_MONTO_PREMIO, "0")
                try:
                    monto = float(monto_str)
                except (ValueError, TypeError):
                    monto = 0.0

                # Crear boleto
                boleto = Boleto(
                    codigo=codigo,
                    sucursal=datos_boleto.get(self.constantes.COLUMNA_SUCURSAL, ""),
                    vendedor_documento=datos_boleto.get(
                        self.constantes.COLUMNA_VENDEDOR_DOC, ""
                    ),
                    vendedor_nombre=datos_boleto.get(
                        self.constantes.COLUMNA_VENDEDOR_NOMBRE, ""
                    ),
                    fecha_pago=datos_boleto.get(self.constantes.COLUMNA_FECHA_PAGO, ""),
                    monto_premio=monto,
                    tipo_premio=datos_boleto.get(
                        self.constantes.COLUMNA_TIPO_PREMIO, ""
                    ),
                    datos_originales=fila.to_dict(),
                )

                boletos.append(boleto)

            except Exception as e:
                error_msg = f"Error procesando fila {idx}: {str(e)}"
                self.errores.append(error_msg)
                if self.config.debug_mode:
                    print(f"DEBUG: {error_msg}")

        return boletos

    def obtener_resumen(self) -> Dict[str, Any]:
        """
        Obtiene un resumen estadístico del reporte cargado.

        Returns:
            Diccionario con resumen estadístico
        """
        if self.df is None:
            return {"error": "No hay datos cargados"}

        try:
            # Columna de código de barras
            col_codigo = self.columnas_detectadas.get(
                self.constantes.COLUMNA_CODIGO_BARRA
            )

            resumen = {
                "total_filas": len(self.df),
                "total_boletos_unicos": len(self.df[col_codigo].unique())
                if col_codigo
                else 0,
                "columnas_detectadas": self.columnas_detectadas,
                "errores_procesamiento": len(self.errores),
                "fecha_carga": datetime.now().isoformat(),
            }

            # Estadísticas por sucursal si existe la columna
            col_sucursal = self.columnas_detectadas.get(
                self.constantes.COLUMNA_SUCURSAL
            )
            if col_sucursal and col_sucursal in self.df.columns:
                sucursales = self.df[col_sucursal].value_counts().to_dict()
                resumen["distribucion_sucursales"] = sucursales
                resumen["total_sucursales"] = len(sucursales)

            # Estadísticas por vendedor si existe la columna
            col_vendedor = self.columnas_detectadas.get(
                self.constantes.COLUMNA_VENDEDOR_NOMBRE
            )
            if col_vendedor and col_vendedor in self.df.columns:
                vendedores = self.df[col_vendedor].value_counts().head(10).to_dict()
                resumen["top_vendedores"] = vendedores

            # Estadísticas de montos si existe la columna
            col_monto = self.columnas_detectadas.get(
                self.constantes.COLUMNA_MONTO_PREMIO
            )
            if col_monto and col_monto in self.df.columns:
                resumen["monto_total"] = float(self.df[col_monto].sum())
                resumen["monto_promedio"] = float(self.df[col_monto].mean())
                resumen["monto_maximo"] = float(self.df[col_monto].max())
                resumen["monto_minimo"] = float(self.df[col_monto].min())

            return resumen

        except Exception as e:
            return {"error": f"Error generando resumen: {str(e)}"}

    def exportar_con_resultados(self, sesion, ruta_salida: str) -> Tuple[bool, str]:
        """
        Exporta el reporte original con columnas adicionales de resultados.

        Args:
            sesion: SesionInventario con los resultados de escaneo
            ruta_salida: Ruta donde guardar el archivo

        Returns:
            Tuple (éxito, mensaje)
        """
        try:
            if self.df is None:
                raise ValueError("No hay datos cargados para exportar")

            # Crear copia del DataFrame original
            df_export = self.df.copy()

            # Agregar columnas de resultados
            resultados = []

            # Columna de código de barras detectada
            col_codigo = self.columnas_detectadas.get(
                self.constantes.COLUMNA_CODIGO_BARRA
            )
            if not col_codigo:
                raise ValueError("No se detectó columna de código de barras")

            # Para cada fila en el DataFrame original
            for _, fila in df_export.iterrows():
                codigo = str(fila[col_codigo]).strip()
                boleto = sesion.buscar_boleto(codigo)

                if boleto:
                    resultados.append(
                        {
                            "ESTADO_ESCANEO": boleto.estado.value,
                            "FECHA_ESCANEO": boleto.fecha_escaneo.isoformat()
                            if boleto.fecha_escaneo
                            else "",
                            "ESCANEOS_REALIZADOS": boleto.escaneos_realizados,
                        }
                    )
                else:
                    resultados.append(
                        {
                            "ESTADO_ESCANEO": self.constantes.ESTADO_NO_ESCANEADO,
                            "FECHA_ESCANEO": "",
                            "ESCANEOS_REALIZADOS": 0,
                        }
                    )

            # Convertir resultados a DataFrame y unir
            df_resultados = pd.DataFrame(resultados)
            df_export = pd.concat([df_export, df_resultados], axis=1)

            # Guardar archivo según extensión
            extension = os.path.splitext(ruta_salida)[1].lower()

            if extension == ".csv":
                df_export.to_csv(
                    ruta_salida, index=False, encoding=self.constantes.ENCODING
                )
            else:
                df_export.to_excel(ruta_salida, index=False)

            return True, f"Archivo exportado exitosamente: {ruta_salida}"

        except Exception as e:
            return False, f"Error al exportar: {str(e)}"

    def cargar_reporte_con_estados(self, ruta_archivo: str):
        """
        Carga un reporte que ya contiene columnas de estado de escaneo.

        Returns:
            Tuple (éxito, mensaje, lista_de_boletos)
        """
        try:
            # Cargar archivo normalmente
            exito, mensaje = self.cargar_archivo(ruta_archivo)
            if not exito:
                return False, mensaje, []

            # Verificar que tenga columnas de estado
            tiene_estados = "ESTADO_ESCANEO" in self.df.columns
            if not tiene_estados:
                return False, "El archivo no contiene columna 'ESTADO_ESCANEO'", []

            # Obtener boletos con sus estados
            boletos_con_estado = self._obtener_boletos_con_estado()

            return True, "Reporte con estados cargado exitosamente", boletos_con_estado

        except Exception as e:
            return False, f"Error al cargar reporte con estados: {str(e)}", []

    def _obtener_boletos_con_estado(self):
        """Obtiene boletos desde un reporte que ya tiene estados"""
        if self.df is None or self.df.empty:
            return []

        boletos = []

        for idx, fila in self.df.iterrows():
            try:
                # Obtener datos básicos
                datos_boleto = {}
                for col_estandar, col_real in self.columnas_detectadas.items():
                    if col_real in fila:
                        valor = fila[col_real]
                        datos_boleto[col_estandar] = (
                            str(valor).strip() if pd.notna(valor) else ""
                        )
                    else:
                        datos_boleto[col_estandar] = ""

                # Obtener estado si existe
                estado_str = str(fila.get("ESTADO_ESCANEO", "")).strip()
                fecha_escaneo_str = str(fila.get("FECHA_ESCANEO", "")).strip()
                escaneos_realizados = 0
                try:
                    escaneos_realizados = int(fila.get("ESCANEOS_REALIZADOS", 0))
                except:
                    pass

                # Asegurar que el código sea string
                codigo = datos_boleto[self.constantes.COLUMNA_CODIGO_BARRA]

                # Convertir monto premio
                monto_str = datos_boleto.get(self.constantes.COLUMNA_MONTO_PREMIO, "0")
                try:
                    monto = float(monto_str)
                except:
                    monto = 0.0

                # Crear boleto
                boleto = Boleto(
                    codigo=codigo,
                    sucursal=datos_boleto.get(self.constantes.COLUMNA_SUCURSAL, ""),
                    vendedor_documento=datos_boleto.get(
                        self.constantes.COLUMNA_VENDEDOR_DOC, ""
                    ),
                    vendedor_nombre=datos_boleto.get(
                        self.constantes.COLUMNA_VENDEDOR_NOMBRE, ""
                    ),
                    fecha_pago=datos_boleto.get(self.constantes.COLUMNA_FECHA_PAGO, ""),
                    monto_premio=monto,
                    tipo_premio=datos_boleto.get(
                        self.constantes.COLUMNA_TIPO_PREMIO, ""
                    ),
                    datos_originales=fila.to_dict(),
                )

                # Aplicar estado si existe - CORREGIDO: convertir string a EstadoBoleto
                if estado_str:
                    try:
                        # Importar EstadoBoleto aquí o al inicio del archivo
                        from inventario_boletos.core.entities import EstadoBoleto

                        # Intentar convertir el string a EstadoBoleto
                        # Primero intentar coincidencia exacta con value
                        estado_encontrado = None
                        for estado_enum in EstadoBoleto:
                            if estado_enum.value == estado_str:
                                estado_encontrado = estado_enum
                                break

                        # Si no coincide con value, intentar con name
                        if estado_encontrado is None:
                            for estado_enum in EstadoBoleto:
                                if estado_enum.name == estado_str:
                                    estado_encontrado = estado_enum
                                    break

                        # Si aún no encuentra, usar PENDIENTE como default
                        if estado_encontrado is None:
                            estado_encontrado = EstadoBoleto.PENDIENTE
                            # También podemos intentar crear desde string directamente
                            try:
                                estado_encontrado = EstadoBoleto(estado_str)
                            except ValueError:
                                pass  # Ya tenemos PENDIENTE como fallback

                        boleto.estado = estado_encontrado

                    except Exception as e:
                        # En caso de error, usar PENDIENTE
                        from inventario_boletos.core.entities import EstadoBoleto

                        boleto.estado = EstadoBoleto.PENDIENTE
                        if self.config.debug_mode:
                            print(
                                f"DEBUG: Error convirtiendo estado '{estado_str}': {e}"
                            )

                # Manejar fecha de escaneo
                if fecha_escaneo_str and fecha_escaneo_str not in [
                    "",
                    "nan",
                    "NaT",
                    "None",
                ]:
                    try:
                        from datetime import datetime

                        boleto.fecha_escaneo = datetime.fromisoformat(
                            fecha_escaneo_str.replace("Z", "+00:00")
                        )
                    except:
                        pass  # Ignorar error de fecha

                boleto.escaneos_realizados = escaneos_realizados

                boletos.append(boleto)

            except Exception as e:
                error_msg = f"Error procesando fila {idx}: {str(e)}"
                self.errores.append(error_msg)

        return boletos

    def __str__(self) -> str:
        """Representación en string del procesador"""
        if self.df is None:
            return "ReporteProcessor: Sin datos cargados"

        total = len(self.df)
        columnas = len(self.columnas_detectadas)
        return f"ReporteProcessor: {total} registros, {columnas} columnas detectadas"
