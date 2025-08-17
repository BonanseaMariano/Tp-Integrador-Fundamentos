"""
Interfaz de línea de comandos para el procesador de autómatas.
"""

import argparse
import sys
from typing import Any

# Importación directa sin ruta relativa
try:
    from src.graficador import verificar_instalacion
    GRAFICACION_DISPONIBLE = True
except ImportError:
    GRAFICACION_DISPONIBLE = False


class InterfazLineaComandos:
    """Maneja la interfaz de línea de comandos y argumentos."""

    def __init__(self):
        self.parser = self._crear_parser()

    def parse_args(self, args=None):
        """Parsea los argumentos de línea de comandos."""
        return self.parser.parse_args(args)

    def _crear_parser(self):
        """Crea el parser de argumentos de línea de comandos."""
        parser = argparse.ArgumentParser(
            description="Procesador de Autómatas Finitos - Conversión AFND→AFD, Minimización y Graficación",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Ejemplos de uso:
  python main.py archivo.json                          # Procesamiento completo
  python main.py archivo.json -o resultados/           # Especificar directorio de salida
  python main.py archivo.json -g                       # Procesamiento completo + gráficos
  python main.py archivo.json --solo-graficar          # Solo generar gráficos
  python main.py archivo.json -c                       # Solo conversión AFND→AFD
  python main.py archivo.json -m                       # Solo minimización AFD
  python main.py archivo.json -v                       # Modo interactivo validación
  python main.py archivo.json -s "cadena"              # Validar cadena específica
  python main.py archivo.json --validar-archivo test.json  # Validar múltiples cadenas
  python main.py archivo.json -g -f png,pdf,svg        # Múltiples formatos gráficos

Formatos soportados:
  - JSON: Formato estructurado con campos definidos
  - TXT:  Formato de texto plano con secciones

Graficación requiere Graphviz instalado:
  pip install graphviz
  Descargar software desde: https://graphviz.org/download/
            """)

        # Argumentos posicionales
        parser.add_argument('archivo', help='Archivo del autómata (JSON o texto)')

        parser.add_argument('directorio_salida', nargs='?', default='resultados',
                           help='Directorio de salida para los resultados (default: resultados)')

        # Opciones principales
        parser.add_argument('-o', '--output', metavar='DIR',
                           help='Directorio de salida para los resultados (sobrescribe el posicional)')

        # Opciones de procesamiento
        grupo_procesamiento = parser.add_mutually_exclusive_group()
        grupo_procesamiento.add_argument('-c', '--convertir', action='store_true',
                                       help='Solo convertir AFND a AFD (sin minimizar)')

        grupo_procesamiento.add_argument('-m', '--minimizar', action='store_true',
                                       help='Solo minimización AFD (el archivo debe ser un AFD)')

        grupo_procesamiento.add_argument('-v', '--validar', action='store_true',
                                       help='Modo interactivo para validar cadenas')

        grupo_procesamiento.add_argument('-s', '--string', metavar='CADENA',
                                       help='Validar una cadena específica')

        grupo_procesamiento.add_argument('--validar-archivo', metavar='ARCHIVO_JSON',
                                       help='Validar múltiples cadenas desde archivo JSON con el autómata especificado')

        # Opciones de graficación
        parser.add_argument('-g', '--graficar', action='store_true',
                           help='Generar gráficos del autómata y proceso')

        parser.add_argument('--solo-graficar', action='store_true',
                           help='Solo generar gráficos, sin procesamiento')

        parser.add_argument('-f', '--formatos', default='png',
                           help='Formatos de gráficos separados por comas (png,pdf,svg) (default: png)')

        # Opciones de utilidad
        parser.add_argument('--verificar-graphviz', action='store_true',
                           help='Verificar instalación de Graphviz y salir')

        parser.add_argument('-r', '--no-reportes', action='store_true',
                           help='No generar reportes detallados')

        parser.add_argument('--verbose', action='store_true',
                           help='Mostrar información detallada del proceso')

        parser.add_argument('--version', action='version', version='Procesador de Autómatas 2.0')

        return parser

    def verificar_graphviz(self):
        """Verifica la instalación de Graphviz."""
        if GRAFICACION_DISPONIBLE:
            info = verificar_instalacion()
            print("Estado de Graphviz:")
            print(f"  Librería Python: {'✅' if info['libreria_instalada'] else '❌'}")
            print(f"  Ejecutable: {'✅' if info['ejecutable_disponible'] else '❌'}")
            print(f"  Versión: {info.get('version', 'desconocida')}")
            print(f"  Mensaje: {info['mensaje']}")
        else:
            print("❌ Módulo de graficación no disponible")
            print("   Instale con: pip install graphviz")
        return 0

    def ejecutar_operacion(self, args, procesador, ui):
        """Ejecuta la operación correspondiente según los argumentos."""
        # Determinar directorio de salida
        directorio_salida = args.output or args.directorio_salida
        generar_reportes = not args.no_reportes

        # Procesar formatos de gráficos
        formatos_grafico = [f.strip().lower() for f in args.formatos.split(',')]
        self._validar_formatos(formatos_grafico)

        try:
            if args.solo_graficar:
                # Solo generar gráficos
                resultado = procesador.graficar_solo(args.archivo, directorio_salida, formatos_grafico)
                return 0 if resultado else 1

            elif args.convertir:
                # Solo conversión AFND → AFD
                resultado = procesador.convertir_solo(args.archivo, directorio_salida, generar_reportes)
                return 0 if resultado else 1

            elif args.minimizar:
                # Solo minimización AFD
                resultado = procesador.minimizar_solo(args.archivo, directorio_salida, generar_reportes)
                return 0 if resultado else 1

            elif args.validar:
                # Modo interactivo validación
                return ui.validar_cadenas_interactivo(args.archivo)

            elif args.string:
                # Validar cadena específica
                return ui.validar_cadena_especifica(args.archivo, args.string)

            elif args.validar_archivo:
                # Validar múltiples cadenas desde archivo JSON
                return ui.validar_cadenas_desde_archivo(args.archivo, args.validar_archivo)

            else:
                # Procesamiento completo (default)
                resultados = procesador.procesar_completo(
                    args.archivo,
                    directorio_salida,
                    generar_reportes,
                    generar_graficos=args.graficar
                )

                if resultados:
                    # Opción interactiva para validar cadenas
                    if ui.preguntar_validacion_interactiva():
                        return ui.menu_seleccion_automata(resultados, args.archivo, directorio_salida)
                    return 0
                else:
                    return 1

        except Exception as e:
            ui.mostrar_error(f"Error durante la operación: {e}")
            return 1

    def _validar_formatos(self, formatos):
        """Valida que los formatos de gráficos sean válidos."""
        formatos_validos = ['png', 'pdf', 'svg', 'eps', 'ps']
        for formato in formatos:
            if formato not in formatos_validos:
                print(f"⚠️ Advertencia: Formato '{formato}' no reconocido. Formatos válidos: {', '.join(formatos_validos)}")
