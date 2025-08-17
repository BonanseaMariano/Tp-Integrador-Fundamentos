#!/usr/bin/env python3
"""
Programa principal para el Trabajo Práctico Integrador:
Eliminación de no determinismo y minimización de autómatas finitos.

Autor: Bonansea Camaño Mariano Nicolas
"""

import sys
import os
from pathlib import Path

# Agregar el directorio src al path de forma más robusta
src_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Intentar importar los módulos con manejo de errores
try:
    from interfaces.cli import InterfazLineaComandos
    from interfaces.ui import InterfazUsuario
    from core.procesador import ProcesadorAutomatas
    from utils.logger import Logger
except ImportError as e:
    print(f"Error al importar módulos: {e}")
    print("Asegúrate de que la estructura de directorios esté correcta.")
    sys.exit(1)


def main():
    """Función principal del programa."""
    args = None  # Inicializar args para evitar error de referencia
    try:
        # Configurar logging
        logger = Logger()

        # Crear interfaz de línea de comandos
        cli = InterfazLineaComandos()
        args = cli.parse_args()

        # Configurar logger basado en argumentos
        if hasattr(args, 'verbose') and args.verbose:
            logger.set_level('DEBUG')

        # Crear procesador principal
        procesador = ProcesadorAutomatas(logger)

        # Crear interfaz de usuario
        ui = InterfazUsuario(logger)

        # Ejecutar según los argumentos
        if hasattr(args, 'verificar_graphviz') and args.verificar_graphviz:
            return cli.verificar_graphviz()

        # Validar archivo de entrada
        if not Path(args.archivo).exists():
            ui.mostrar_error(f"Archivo no encontrado: {args.archivo}")
            return 1

        # Procesar según la operación solicitada
        resultado = cli.ejecutar_operacion(args, procesador, ui)
        return resultado

    except KeyboardInterrupt:
        print("\n🚫 Operación cancelada por el usuario")
        return 1
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        if args is not None and hasattr(args, 'verbose') and args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
