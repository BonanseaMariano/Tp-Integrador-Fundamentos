"""
Sistema de logging y mensajes con iconos para el procesador de autómatas.

Proporciona utilidades para mostrar mensajes informativos, advertencias y errores con iconos y niveles de detalle configurables.
"""

from enum import Enum


class LogLevel(Enum):
    """
    Niveles de logging disponibles.
    """
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Iconos:
    """
    Iconos Unicode para diferentes tipos de mensajes y estados del sistema.
    """

    # Iconos principales
    AUTOMATA = "\U0001F504"
    AFD = "\u2699\ufe0f"
    AFND = "\U0001F500"
    MINIMIZADO = "\U0001F3AF"
    GRAFICO = "\U0001F3A8"

    # Procesos
    CONVERSION = "\U0001F504"
    MINIMIZACION = "\u26A1"
    VALIDACION = "\u2705"
    ERROR = "\u274C"
    ADVERTENCIA = "\u26A0\ufe0f"
    INFO = "\u2139\ufe0f"

    # Estados de operación
    CARGANDO = "\U0001F4C2"
    GUARDANDO = "\U0001F4BE"
    PROCESANDO = "\u2699\ufe0f"
    COMPLETADO = "\u2705"
    FALLO = "\u274C"

    # Navegación y UI
    FLECHA_DERECHA = "\u27A4"
    CADENA = "\U0001F517"
    ARCHIVO = "\U0001F4C4"
    DIRECTORIO = "\U0001F4C1"
    REPORTE = "\U0001F4CB"

    # Iconos adicionales para validación
    ESTADOS = "\U0001F535"
    TRANSICIONES = "\u27A1\ufe0f"
    ALFABETO = "\U0001F524"
    INICIAL = "\U0001F7E2"
    FINAL = "\U0001F534"
    ESTADISTICA = "\U0001F4CA"
    PORCENTAJE = "\U0001F4C8"
    REDUCCION = "\U0001F4C9"


class Logger:
    """
    Sistema de logging con iconos y colores para mensajes de depuración, información, advertencia y error.
    Permite configurar el nivel de detalle mostrado.
    """

    def __init__(self, level: LogLevel = LogLevel.INFO):
        """
        Inicializa el logger con un nivel de logging.
        Args:
            level (LogLevel): Nivel de logging inicial.
        """
        self.level = level
        self.separador = "-" * 50  # Separador visual para los mensajes

    def set_level(self, level: str):
        """
        Establece el nivel de logging a partir de un string.
        Args:
            level (str): 'DEBUG', 'INFO', 'WARNING' o 'ERROR'.
        """
        level_map = {
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'WARNING': LogLevel.WARNING,
            'ERROR': LogLevel.ERROR
        }
        self.level = level_map.get(level.upper(), LogLevel.INFO)

    def debug(self, mensaje: str, icono: str = Iconos.INFO):
        """
        Muestra un mensaje de depuración si el nivel lo permite.
        """
        if self.level.value <= LogLevel.DEBUG.value:
            self._print(f"{icono} DEBUG: {mensaje}")

    def info(self, mensaje: str, icono: str = Iconos.INFO):
        """
        Muestra un mensaje informativo si el nivel lo permite.
        """
        if self.level.value <= LogLevel.INFO.value:
            self._print(f"{icono} {mensaje}")

    def warning(self, mensaje: str, icono: str = Iconos.ADVERTENCIA):
        """
        Muestra un mensaje de advertencia si el nivel lo permite.
        """
        if self.level.value <= LogLevel.WARNING.value:
            self._print(f"{icono} {mensaje}")

    def error(self, mensaje: str, icono: str = Iconos.ERROR):
        """
        Muestra un mensaje de error si el nivel lo permite.
        """
        if self.level.value <= LogLevel.ERROR.value:
            self._print(f"{icono} {mensaje}")

    def success(self, mensaje: str, icono: str = Iconos.COMPLETADO):
        """
        Muestra un mensaje de éxito (alias de info con icono de completado).
        """
        self.info(mensaje, icono)

    def _print(self, mensaje: str):
        """
        Imprime el mensaje en la salida estándar.
        """
        print(mensaje, flush=True)

    @staticmethod
    def texto_con_icono(icono: str, texto: str) -> str:
        """Combina un icono con texto."""
        return f"{icono} {texto}"
