"""
Sistema de logging y mensajes con iconos para el procesador de autómatas.
"""

import sys
from enum import Enum
from typing import Optional


class LogLevel(Enum):
    """Niveles de logging."""
    DEBUG = 0
    INFO = 1
    WARNING = 2
    ERROR = 3


class Iconos:
    """Iconos Unicode para diferentes tipos de mensajes."""

    # Iconos principales
    AUTOMATA = "🔄"
    AFD = "⚙️"
    AFND = "🔀"
    MINIMIZADO = "🎯"
    GRAFICO = "🎨"

    # Procesos
    CONVERSION = "🔄"
    MINIMIZACION = "⚡"
    VALIDACION = "✅"
    ERROR = "❌"
    ADVERTENCIA = "⚠️"
    INFO = "ℹ️"

    # Estados de operación
    CARGANDO = "📂"
    GUARDANDO = "💾"
    PROCESANDO = "⚙️"
    COMPLETADO = "✅"
    FALLÓ = "❌"

    # Navegación y UI
    FLECHA_DERECHA = "➤"
    CADENA = "🔗"
    ARCHIVO = "📄"
    DIRECTORIO = "📁"
    REPORTE = "📋"

    # Iconos adicionales para validación
    ESTADOS = "🔵"
    TRANSICIONES = "➡️"
    ALFABETO = "🔤"
    INICIAL = "🟢"
    FINAL = "🔴"
    ESTADISTICA = "📊"
    PORCENTAJE = "📈"
    REDUCCION = "📉"


class Logger:
    """Sistema de logging con iconos y colores."""

    def __init__(self, level: LogLevel = LogLevel.INFO):
        self.level = level

    def set_level(self, level: str):
        """Establece el nivel de logging."""
        level_map = {
            'DEBUG': LogLevel.DEBUG,
            'INFO': LogLevel.INFO,
            'WARNING': LogLevel.WARNING,
            'ERROR': LogLevel.ERROR
        }
        self.level = level_map.get(level.upper(), LogLevel.INFO)

    def debug(self, mensaje: str, icono: str = Iconos.INFO):
        """Mensaje de debug."""
        if self.level.value <= LogLevel.DEBUG.value:
            self._print(f"{icono} DEBUG: {mensaje}")

    def info(self, mensaje: str, icono: str = Iconos.INFO):
        """Mensaje informativo."""
        if self.level.value <= LogLevel.INFO.value:
            self._print(f"{icono} {mensaje}")

    def warning(self, mensaje: str, icono: str = Iconos.ADVERTENCIA):
        """Mensaje de advertencia."""
        if self.level.value <= LogLevel.WARNING.value:
            self._print(f"{icono} {mensaje}")

    def error(self, mensaje: str, icono: str = Iconos.ERROR):
        """Mensaje de error."""
        if self.level.value <= LogLevel.ERROR.value:
            self._print(f"{icono} {mensaje}")

    def success(self, mensaje: str, icono: str = Iconos.COMPLETADO):
        """Mensaje de éxito."""
        self.info(mensaje, icono)

    def separador(self, titulo: str = ""):
        """Imprime un separador visual."""
        if titulo:
            self._print(f"\n{'='*5} {titulo} {'='*5}\n")
        else:
            self._print("\n" + "="*50 + "\n")

    def _print(self, mensaje: str):
        """Imprime el mensaje."""
        print(mensaje, flush=True)

    @staticmethod
    def texto_con_icono(icono: str, texto: str) -> str:
        """Combina un icono con texto."""
        return f"{icono} {texto}"
