"""
Interfaz de usuario para interacciones con el usuario.
"""

from typing import Dict, Any
from pathlib import Path

from src.automata import AFD, AFND
from src.manejador_archivos import ManejadorArchivos
from src.utils.logger import Logger, Iconos


class InterfazUsuario:
    """Maneja las interacciones con el usuario."""

    def __init__(self, logger: Logger):
        self.logger = logger
        self.manejador_archivos = ManejadorArchivos()

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error."""
        self.logger.error(mensaje)

    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo."""
        self.logger.info(mensaje)

    def preguntar_validacion_interactiva(self) -> bool:
        """Pregunta al usuario si desea validar cadenas interactivamente."""
        try:
            respuesta = input("\n¿Deseas validar cadenas interactivamente? (s/N): ").strip().lower()
            return respuesta == 's'
        except (KeyboardInterrupt, EOFError):
            return False

    def menu_seleccion_automata(self, resultados: Dict[str, Any], archivo_original: str, directorio_salida: str) -> int:
        """Muestra menú para seleccionar qué autómata usar para validación."""
        print("Elige qué autómata usar:")
        print("1. Original")
        print("2. AFD (después de conversión)")
        print("3. Minimizado")

        try:
            opcion = int(input("Opción (1-3): "))
            if opcion == 1:
                return self.validar_cadenas_interactivo(archivo_original)
            elif opcion == 2:
                temp_afd = Path(directorio_salida) / "temp_afd.json"
                self.manejador_archivos.guardar_automata_como_json(resultados['afd'], str(temp_afd))
                return self.validar_cadenas_interactivo(str(temp_afd))
            elif opcion == 3:
                temp_min = Path(directorio_salida) / "temp_minimizado.json"
                self.manejador_archivos.guardar_automata_como_json(resultados['minimizado'], str(temp_min))
                return self.validar_cadenas_interactivo(str(temp_min))
            else:
                self.mostrar_error("Opción inválida")
                return 1
        except ValueError:
            self.mostrar_error("Entrada inválida")
            return 1
        except (KeyboardInterrupt, EOFError):
            print("\nOperación cancelada")
            return 1

    def validar_cadenas_interactivo(self, ruta_entrada: str) -> int:
        """Modo interactivo para validar cadenas en un autómata."""
        try:
            automata = self._cargar_automata(ruta_entrada)
            self._mostrar_info_automata(automata)

            self.logger.info(f"\n{Iconos.CADENA} Ingresa cadenas para validar (o 'salir' para terminar):")

            while True:
                try:
                    cadena = input(f"\n{Iconos.FLECHA_DERECHA} Cadena: ").strip()

                    if cadena.lower() == 'salir':
                        self.logger.success("¡Hasta luego!", Iconos.COMPLETADO)
                        break

                    resultado = automata.validar_cadena(cadena)
                    icono_resultado = Iconos.CHECK if resultado else Iconos.CRUZ
                    estado = "ACEPTADA" if resultado else "RECHAZADA"
                    self.logger.info(f"'{cadena}' -> {estado}", icono_resultado)

                except KeyboardInterrupt:
                    self.logger.info(f"\n{Iconos.COMPLETADO} Saliendo...")
                    break
                except Exception as e:
                    self.logger.error(f"Error: {e}")

            return 0

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1

    def validar_cadena_especifica(self, ruta_entrada: str, cadena: str) -> int:
        """Valida una cadena específica en un autómata."""
        try:
            automata = self._cargar_automata(ruta_entrada)
            resultado = automata.validar_cadena(cadena)
            icono_resultado = Iconos.CHECK if resultado else Iconos.CRUZ
            estado = "ACEPTADA" if resultado else "RECHAZADA"

            self.logger.info(f"Cadena '{cadena}'", Iconos.CADENA)
            self.logger.info(estado, icono_resultado)

            tipo_icono = Iconos.AFND if isinstance(automata, AFND) else Iconos.AFD
            self.logger.info(f"Autómata: {type(automata).__name__} con {len(automata.estados)} estados", tipo_icono)

            return 0

        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1

    def _cargar_automata(self, ruta_archivo: str):
        """Carga un autómata detectando automáticamente el formato."""
        formato = self.manejador_archivos.validar_formato_archivo(ruta_archivo)
        self.logger.info(f"Formato detectado: {formato}")

        if formato == 'json':
            return self.manejador_archivos.cargar_automata_desde_json(ruta_archivo)
        else:
            return self.manejador_archivos.cargar_automata_desde_texto(ruta_archivo)

    def _mostrar_info_automata(self, automata):
        """Muestra información detallada del autómata."""
        self.logger.separador("VALIDADOR DE CADENAS")

        tipo_icono = Iconos.AFND if isinstance(automata, AFND) else Iconos.AFD
        self.logger.info(f"Autómata: {type(automata).__name__}", tipo_icono)
        self.logger.info(f"Estados: {len(automata.estados)} ({', '.join(sorted(automata.estados, key=str))})", Iconos.ESTADOS)
        self.logger.info(f"Alfabeto: {automata.alfabeto}", Iconos.ALFABETO)
        self.logger.info(f"Estado inicial: {automata.estado_inicial}", Iconos.INICIAL)
        self.logger.info(f"Estados finales: {', '.join(sorted(automata.estados_finales, key=str))}", Iconos.FINAL)

        # Mostrar descripción si está disponible
        if hasattr(automata, 'descripcion') and automata.descripcion:
            self.logger.info(f"Descripción: {automata.descripcion}")
        else:
            self.logger.warning("Descripción: No disponible")
