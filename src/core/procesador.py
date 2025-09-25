"""
Procesador central para autómatas finitos.

Este módulo orquesta la conversión, minimización, validación y graficación de autómatas,
coordinando los distintos componentes del sistema y gestionando la entrada/salida de archivos.
"""

from pathlib import Path
from typing import Dict, Optional, Any
import os

from src.automata import AFD, AFND
from src.conversor import ConversorTabular
from src.minimizador import MinimizadorAFD
from src.manejador_archivos import ManejadorArchivos
from src.utils.equivalencia import equivalencia_afd_producto

# Importar graficador solo si está disponible
try:
    from src.graficador import GraficadorAutomatas, verificar_instalacion

    GRAFICACION_DISPONIBLE = True
except ImportError:
    GRAFICACION_DISPONIBLE = False


    class GraficadorAutomatas:
        def exportar_multiples_formatos(self, *args, **kwargs):
            return []

        def generar_comparacion(self, *args, **kwargs):
            return None


    def verificar_instalacion():
        return {'libreria_instalada': False, 'ejecutable_disponible': False, 'version': None,
                'mensaje': 'No disponible'}

from src.utils.logger import Logger, Iconos


class ProcesadorAutomatas:
    """
    Procesador principal para operaciones con autómatas finitos.
    Se encarga de la conversión AFND→AFD, minimización, validación de equivalencia y graficación.
    """

    def __init__(self, logger: Logger):
        """
        Inicializa el procesador con los componentes necesarios.

        Args:
            logger (Logger): Instancia de logger para mensajes.
        """
        self.logger = logger
        self.conversor = ConversorTabular()  # Usa el conversor tabular como predeterminado
        self.minimizador = MinimizadorAFD()
        self.manejador_archivos = ManejadorArchivos()
        self._graficador = None

    def procesar_completo(self, archivo_entrada: str, directorio_salida: str = "resultados",
                          generar_reportes: bool = True, generar_graficos: bool = False) -> Dict[str, Any]:
        """
        Procesa un autómata completo: conversión AFND→AFD, minimización, validación de equivalencia y generación de reportes/gráficos.

        Args:
            archivo_entrada (str): Ruta al archivo del autómata.
            directorio_salida (str): Directorio donde guardar resultados.
            generar_reportes (bool): Si generar reportes detallados.
            generar_graficos (bool): Si generar gráficos del proceso.
        Returns:
            dict: Diccionario con los autómatas en cada etapa y resultados intermedios.
        """
        self.logger.separador("PROCESADOR DE AUTÓMATAS FINITOS")
        self.logger.info(f"Cargando autómata desde: {archivo_entrada}", Iconos.CARGANDO)

        try:
            # Cargar autómata original
            automata_original = self._cargar_automata(archivo_entrada)
            tipo_icono = Iconos.AFND if isinstance(automata_original, AFND) else Iconos.AFD
            self.logger.info(f"Autómata cargado: {type(automata_original).__name__}", tipo_icono)
            self.logger.info(f"Estados: {len(automata_original.estados)}", Iconos.ESTADOS)
            self.logger.info(f"Transiciones: {len(automata_original.transiciones)}", Iconos.TRANSICIONES)

            resultados = {
                'original': automata_original,
                'afd': None,
                'minimizado': None
            }

            # Configurar graficador si es necesario
            graficador = None
            if generar_graficos:
                graficador = self._inicializar_graficador(directorio_salida)

            # Conversión AFND -> AFD (si es necesario)
            if isinstance(automata_original, AFND):
                afd = self._convertir_a_afd(automata_original, graficador, directorio_salida)
                resultados['afd'] = afd
            else:
                self.logger.info("El autómata ya es AFD, saltando conversión...", Iconos.INFO)
                afd = automata_original
                resultados['afd'] = afd

            # Minimización del AFD
            afd_minimizado = self._minimizar_afd(afd, graficador, directorio_salida)
            resultados['minimizado'] = afd_minimizado

            # Mostrar estadísticas finales
            self._mostrar_estadisticas(automata_original, afd_minimizado)

            # Guardar resultados
            if directorio_salida:
                self._guardar_resultados(resultados, directorio_salida)

            # Generar reportes
            if generar_reportes:
                self._generar_reportes(resultados, directorio_salida)

            # Validar equivalencia tras conversión/minimización
            self._validar_equivalencia(resultados)

            self.logger.separador("PROCESAMIENTO COMPLETADO")
            return resultados

        except Exception as e:
            self.logger.error(f"Error durante el procesamiento: {e}")
            return None

    def convertir_solo(self, archivo_entrada: str, directorio_salida: str = "resultados",
                       generar_reporte: bool = True) -> Optional[AFD]:
        """
        Solo convierte AFND a AFD sin minimizar.

        Args:
            archivo_entrada (str): Ruta al archivo del autómata.
            directorio_salida (str): Directorio donde guardar resultados.
            generar_reporte (bool): Si generar reporte de la conversión.

        Returns:
            AFD convertido o None si falla.
        """
        self.logger.separador("CONVERSIÓN AFND → AFD")
        self.logger.info(f"Cargando AFND desde: {archivo_entrada}", Iconos.CARGANDO)

        try:
            automata_original = self._cargar_automata(archivo_entrada)

            if not isinstance(automata_original, AFND):
                self.logger.warning(f"El autómata ya es {type(automata_original).__name__}")
                return automata_original

            self.logger.info(f"AFND cargado: {len(automata_original.estados)} estados", Iconos.AFND)

            # Conversión
            self.logger.info("Ejecutando algoritmo de construcción de subconjuntos...", Iconos.PROCESANDO)
            afd = self.conversor.convertir(automata_original)
            self.logger.success(f"Conversión completada: {len(afd.estados)} estados", Iconos.AFD)

            # Guardar resultado
            if directorio_salida:
                self._guardar_conversion(automata_original, afd, archivo_entrada, directorio_salida, generar_reporte)

            return afd

        except Exception as e:
            self.logger.error(f"Error durante la conversión: {e}")
            return None

    def minimizar_solo(self, archivo_entrada: str, directorio_salida: str = "resultados",
                       generar_reporte: bool = True) -> Optional[AFD]:
        """
        Solo minimiza un AFD sin conversión previa.

        Args:
            archivo_entrada (str): Ruta al archivo del autómata.
            directorio_salida (str): Directorio donde guardar resultados.
            generar_reporte (bool): Si generar reporte de la minimización.

        Returns:
            AFD minimizado o None si falla.
        """
        self.logger.separador("MINIMIZACIÓN DE AFD")
        self.logger.info(f"Cargando AFD desde: {archivo_entrada}", Iconos.CARGANDO)

        try:
            automata_original = self._cargar_automata(archivo_entrada)

            if isinstance(automata_original, AFND):
                self.logger.warning("El archivo no corresponde a un AFD. No se puede minimizar.")
                return None

            self.logger.info(f"AFD cargado: {len(automata_original.estados)} estados", Iconos.AFD)

            self.logger.info("Ejecutando algoritmo de minimización...", Iconos.PROCESANDO)
            afd_min = self.minimizador.minimizar(automata_original)
            self.logger.success(f"Minimización completada: {len(afd_min.estados)} estados", Iconos.MINIMIZADO)

            if directorio_salida:
                self._guardar_minimizacion(automata_original, afd_min, archivo_entrada, directorio_salida,
                                           generar_reporte)

            return afd_min

        except Exception as e:
            self.logger.error(f"Error durante la minimización: {e}")
            return None

    def graficar_solo(self, archivo_entrada: str, directorio_salida: str = "graficos",
                      formatos: list = None) -> bool:
        """Genera solo gráficos de un autómata sin procesamiento adicional."""
        if formatos is None:
            formatos = ['png']
        if not GRAFICACION_DISPONIBLE:
            self.logger.error("Módulo de graficación no disponible. Instale: pip install graphviz")
            return False

        self.logger.separador("GRAFICACIÓN DE AUTÓMATA")
        self.logger.info(f"Cargando autómata desde: {archivo_entrada}", Iconos.CARGANDO)

        try:
            automata = self._cargar_automata(archivo_entrada)
            tipo_icono = Iconos.AFND if isinstance(automata, AFND) else Iconos.AFD
            self.logger.info(f"Autómata cargado: {type(automata).__name__}", tipo_icono)

            # Verificar instalación de Graphviz
            info_instalacion = verificar_instalacion()
            if not info_instalacion['ejecutable_disponible']:
                self.logger.error("Graphviz no está disponible:")
                self.logger.info(info_instalacion['mensaje'])
                return False

            # Crear directorio y graficador
            Path(directorio_salida).mkdir(parents=True, exist_ok=True)
            graficador = GraficadorAutomatas()

            # Generar gráficos
            nombre_base = Path(archivo_entrada).stem
            archivos_generados = graficador.exportar_multiples_formatos(
                automata=automata,
                nombre_base=nombre_base,
                directorio=directorio_salida,
                formatos=formatos
            )

            self.logger.info("Gráficos generados:", Iconos.GRAFICO)
            for archivo in archivos_generados:
                self.logger.info(f"   - {archivo}")

            self.logger.success("Graficación completada exitosamente!")
            return True

        except Exception as e:
            self.logger.error(f"Error durante la graficación: {e}")
            return False

    def _cargar_automata(self, ruta_archivo: str):
        """Carga un autómata detectando automáticamente el formato."""
        formato = self.manejador_archivos.validar_formato_archivo(ruta_archivo)
        self.logger.info(f"Formato detectado: {formato}")

        if formato == 'json':
            return self.manejador_archivos.cargar_automata_desde_json(ruta_archivo)
        else:
            return self.manejador_archivos.cargar_automata_desde_texto(ruta_archivo)

    def _inicializar_graficador(self, directorio_salida: str):
        """Inicializa el graficador si está disponible."""
        if not GRAFICACION_DISPONIBLE:
            self.logger.warning("Módulo de graficación no disponible. Instale: pip install graphviz")
            return None

        try:
            info_instalacion = verificar_instalacion()
            if info_instalacion['ejecutable_disponible']:
                Path(directorio_salida).mkdir(parents=True, exist_ok=True)
                self.logger.info("Graficador inicializado correctamente", Iconos.GRAFICO)
                return GraficadorAutomatas()
            else:
                self.logger.warning("Graphviz no está disponible para graficación")
                self.logger.info(info_instalacion['mensaje'])
                return None
        except Exception as e:
            self.logger.warning(f"Error inicializando graficador: {e}")
            return None

    def _convertir_a_afd(self, afnd, graficador, directorio_salida):
        """Convierte AFND a AFD con graficación opcional."""
        self.logger.info("Convirtiendo AFND a AFD...", Iconos.CONVERSION)
        afd = self.conversor.convertir(afnd)
        self.logger.success(f"Conversión completada: {len(afd.estados)} estados")

        # Generar gráfico de conversión si está disponible
        if graficador:
            try:
                archivo_comparacion = graficador.generar_comparacion(
                    automata_original=afnd,
                    automata_procesado=afd,
                    nombre_archivo="conversion_afnd_afd",
                    directorio=directorio_salida,
                    titulo_original="AFND Original",
                    titulo_procesado="AFD Convertido"
                )
                self.logger.info(f"Gráfico de conversión: {archivo_comparacion}", Iconos.GRAFICO)
            except Exception as e:
                self.logger.warning(f"Error generando gráfico de conversión: {e}")

        return afd

    def _minimizar_afd(self, afd, graficador, directorio_salida):
        """Minimiza AFD con graficación opcional."""
        self.logger.info("Minimizando AFD...", Iconos.MINIMIZACION)
        afd_minimizado = self.minimizador.minimizar(afd)
        self.logger.success(f"Minimización completada: {len(afd_minimizado.estados)} estados", Iconos.MINIMIZADO)

        # Generar gráficos de minimización si está disponible
        if graficador:
            try:
                # Gráfico comparativo
                archivo_minimizacion = graficador.generar_comparacion(
                    automata_original=afd,
                    automata_procesado=afd_minimizado,
                    nombre_archivo="minimizacion_afd",
                    directorio=directorio_salida,
                    titulo_original="AFD Original",
                    titulo_procesado="AFD Minimizado"
                )
                self.logger.info(f"Gráfico de minimización: {archivo_minimizacion}", Iconos.GRAFICO)

            except Exception as e:
                self.logger.warning(f"Error generando gráficos de minimización: {e}")

        return afd_minimizado

    def _mostrar_estadisticas(self, original, minimizado):
        """Muestra estadísticas del procesamiento."""
        reduccion = len(original.estados) - len(minimizado.estados)
        porcentaje = (reduccion / len(original.estados)) * 100 if len(original.estados) > 0 else 0
        self.logger.info(f"Reducción total: {reduccion} estados ({porcentaje:.1f}%)", Iconos.REDUCCION)

    def _guardar_resultados(self, resultados, directorio_salida):
        """Guarda todos los autómatas resultantes."""
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)
        self.logger.info("Guardando resultados...", Iconos.GUARDANDO)

        # Ya no se guarda el autómata original porque es innecesario
        # nombre_original = os.path.join(directorio_salida, "automata_original.json")
        # self.manejador_archivos.guardar_automata_como_json(resultados['original'], nombre_original)
        # self.logger.info(f"Guardado: {nombre_original}", Iconos.ARCHIVO)

        # Guardar AFD (si es diferente del original)
        if resultados['afd'] != resultados['original']:
            nombre_afd = os.path.join(directorio_salida, "automata_afd.json")
            self.manejador_archivos.guardar_automata_como_json(resultados['afd'], nombre_afd)
            self.logger.info(f"Guardado: {nombre_afd}", Iconos.ARCHIVO)

        # Guardar AFD minimizado
        nombre_minimizado = os.path.join(directorio_salida, "automata_minimizado.json")
        self.manejador_archivos.guardar_automata_como_json(resultados['minimizado'], nombre_minimizado)
        self.logger.info(f"Guardado: {nombre_minimizado}", Iconos.ARCHIVO)

    def _generar_reportes(self, resultados, directorio_salida):
        """Genera reportes detallados del procesamiento."""
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)
        self.logger.info("Generando reportes detallados...", Iconos.REPORTE)

        reportes = []

        # Reporte de conversión (si aplica)
        if isinstance(resultados['original'], AFND):
            reporte_conversion = self.conversor.generar_reporte(
                resultados['original'], resultados['afd']
            )
            ruta_reporte = os.path.join(directorio_salida, "reporte_conversion.txt")
            with open(ruta_reporte, 'w', encoding='utf-8') as f:
                f.write(reporte_conversion)
            reportes.append(ruta_reporte)

        # Reporte de minimización
        reporte_minimizacion = self.minimizador.generar_reporte_minimizacion(
            resultados['afd'], resultados['minimizado']
        )
        ruta_reporte = os.path.join(directorio_salida, "reporte_minimizacion.txt")
        with open(ruta_reporte, 'w', encoding='utf-8') as f:
            f.write(reporte_minimizacion)
        reportes.append(ruta_reporte)

        self.logger.success(f"Reportes generados: {len(reportes)} archivos")
        for reporte in reportes:
            self.logger.info(f"  {reporte}", Iconos.REPORTE)

    def _guardar_conversion(self, afnd, afd, archivo_entrada, directorio_salida, generar_reporte):
        """Guarda los resultados de la conversión."""
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)

        nombre_base = Path(archivo_entrada).stem
        archivo_afd = os.path.join(directorio_salida, f"{nombre_base}_convertido.json")

        self.manejador_archivos.guardar_automata_como_json(afd, archivo_afd)
        self.logger.info(f"AFD guardado en: {archivo_afd}", Iconos.GUARDANDO)

        if generar_reporte:
            reporte = self.conversor.generar_reporte(afnd, afd)  # Usa el conversor tabular
            archivo_reporte = os.path.join(directorio_salida, f"{nombre_base}_reporte_conversion.txt")
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                f.write(reporte)
            self.logger.info(f"Reporte guardado en: {archivo_reporte}", Iconos.REPORTE)

    def _guardar_minimizacion(self, afd_original, afd_minimizado, archivo_entrada, directorio_salida, generar_reporte):
        """Guarda los resultados de la minimización."""
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)

        nombre_base = Path(archivo_entrada).stem
        archivo_min = os.path.join(directorio_salida, f"{nombre_base}_minimizado.json")

        self.manejador_archivos.guardar_automata_como_json(afd_minimizado, archivo_min)
        self.logger.info(f"AFD minimizado guardado en: {archivo_min}", Iconos.GUARDANDO)

        if generar_reporte:
            reporte = self.minimizador.generar_reporte_minimizacion(afd_original, afd_minimizado)
            archivo_reporte = os.path.join(directorio_salida, f"{nombre_base}_reporte_minimizacion.txt")
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                f.write(reporte)
            self.logger.info(f"Reporte guardado en: {archivo_reporte}", Iconos.REPORTE)

    def convertir_tabular(self, archivo_entrada: str, directorio_salida: str = "resultados",
                          generar_reporte: bool = True) -> Optional[AFD]:
        """Convierte AFND a AFD usando el algoritmo tabular optimizado."""
        self.logger.separador("CONVERSIÓN TABULAR AFND → AFD")
        self.logger.info(f"Cargando AFND desde: {archivo_entrada}", Iconos.CARGANDO)

        try:
            automata_original = self._cargar_automata(archivo_entrada)

            if not isinstance(automata_original, AFND):
                self.logger.warning(f"El autómata ya es {type(automata_original).__name__}")
                return automata_original

            self.logger.info(f"AFND cargado: {len(automata_original.estados)} estados", Iconos.AFND)

            # Conversión tabular
            self.logger.info("Ejecutando algoritmo tabular optimizado...", Iconos.PROCESANDO)
            afd = self.conversor.convertir(automata_original)
            self.logger.success(f"Conversión tabular completada: {len(afd.estados)} estados", Iconos.AFD)

            # Mostrar comparación de eficiencia
            reduccion = len(automata_original.estados) - len(afd.estados)
            eficiencia = (reduccion / len(automata_original.estados)) * 100 if len(automata_original.estados) > 0 else 0
            self.logger.info(f"Eficiencia del algoritmo tabular: {eficiencia:.1f}% reducción", Iconos.REDUCCION)

            # Guardar resultado
            if directorio_salida:
                self._guardar_conversion_tabular(automata_original, afd, archivo_entrada, directorio_salida,
                                                 generar_reporte)

            return afd

        except Exception as e:
            self.logger.error(f"Error durante la conversión tabular: {e}")
            return None

    def _guardar_conversion_tabular(self, afnd, afd, archivo_entrada, directorio_salida, generar_reporte):
        """Guarda los resultados de la conversión tabular."""
        Path(directorio_salida).mkdir(parents=True, exist_ok=True)

        nombre_base = Path(archivo_entrada).stem
        archivo_afd = os.path.join(directorio_salida, f"{nombre_base}_tabular.json")

        self.manejador_archivos.guardar_automata_como_json(afd, archivo_afd)
        self.logger.info(f"AFD tabular guardado en: {archivo_afd}", Iconos.GUARDANDO)

        if generar_reporte:
            reporte = self.conversor.generar_reporte(afnd, afd)
            archivo_reporte = os.path.join(directorio_salida, f"{nombre_base}_reporte_tabular.txt")
            with open(archivo_reporte, 'w', encoding='utf-8') as f:
                f.write(reporte)
            self.logger.info(f"Reporte tabular guardado en: {archivo_reporte}", Iconos.REPORTE)

    def _validar_equivalencia(self, resultados):
        """Valida que los autómatas sean equivalentes usando el método formal del autómata producto y deja el log aquí."""
        original = resultados['original']
        minimizado = resultados['minimizado']
        equivalentes = equivalencia_afd_producto(original, minimizado)
        if equivalentes:
            self.logger.success(
                "Los autómatas son equivalentes",
                Iconos.COMPLETADO
            )
        else:
            self.logger.error(
                "Los autómatas NO son equivalentes (existe una cadena aceptada por uno y rechazada por el otro)",
                Iconos.FALLÓ
            )
