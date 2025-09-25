"""
Interfaz de usuario para interacciones con el usuario.

Permite mostrar mensajes, preguntar opciones y validar cadenas de manera interactiva o desde archivos, facilitando la comunicación entre el usuario y el sistema.
"""

from typing import Dict, Any
from pathlib import Path

from src.automata import AFD, AFND
from src.manejador_archivos import ManejadorArchivos
from src.utils.logger import Logger, Iconos


class InterfazUsuario:
    """
    Maneja las interacciones con el usuario para mostrar mensajes, menús y validaciones.
    """

    def __init__(self, logger: Logger):
        """Inicializa la interfaz con un logger y manejador de archivos."""
        self.logger = logger
        self.manejador_archivos = ManejadorArchivos()

    def mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error al usuario."""
        self.logger.error(mensaje)

    def mostrar_info(self, mensaje: str):
        """Muestra un mensaje informativo al usuario."""
        self.logger.info(mensaje)

    def preguntar_validacion_interactiva(self) -> bool:
        """
        Pregunta al usuario si desea validar cadenas interactivamente.
        Returns:
            bool: True si el usuario responde 's', False en caso contrario o interrupción.
        """
        try:
            respuesta = input("\n¿Deseas validar cadenas interactivamente? (s/N): ").strip().lower()
            return respuesta == 's'
        except (KeyboardInterrupt, EOFError):
            return False

    def menu_seleccion_automata(self, resultados: Dict[str, Any], archivo_original: str, directorio_salida: str) -> int:
        """
        Muestra un menú para seleccionar qué autómata usar para validación de cadenas.
        Returns:
            int: Código de salida según la opción elegida o error.
        """
        while True:
            print("Elige qué autómata usar:")
            print("1. Original")
            print("2. AFD (después de conversión)")
            print("3. Minimizado")
            try:
                opcion = int(input("Opción (1-3): "))
                if opcion == 1:
                    resultado = self.validar_cadenas_interactivo(archivo_original)
                elif opcion == 2:
                    temp_afd = Path(directorio_salida) / "temp_afd.json"
                    self.manejador_archivos.guardar_automata_como_json(resultados['afd'], str(temp_afd))
                    resultado = self.validar_cadenas_interactivo(str(temp_afd))
                elif opcion == 3:
                    temp_min = Path(directorio_salida) / "temp_minimizado.json"
                    self.manejador_archivos.guardar_automata_como_json(resultados['minimizado'], str(temp_min))
                    resultado = self.validar_cadenas_interactivo(str(temp_min))
                else:
                    self.mostrar_error("Opción inválida")
                    continue
                if resultado == 'volver_menu':
                    continue  # Volver a mostrar el menú
                return resultado
            except ValueError:
                self.mostrar_error("Entrada inválida")
            except (KeyboardInterrupt, EOFError):
                print("\nOperación cancelada")
                return 1

    def validar_cadenas_interactivo(self, ruta_entrada: str):
        """
        Modo interactivo para validar cadenas en un autómata.
        Permite ingresar cadenas por consola y muestra si son aceptadas o rechazadas.
        """
        import os
        from pathlib import Path
        temp_min_path = Path(ruta_entrada)
        es_temp_min = temp_min_path.name == "temp_minimizado.json"
        try:
            automata = self._cargar_automata(ruta_entrada)
            self._mostrar_info_automata(automata)
            self.logger.info(f"\n{Iconos.CADENA} Ingresa cadenas para validar (o 'salir' para volver al menú):")
            while True:
                try:
                    cadena = input(f"\n{Iconos.FLECHA_DERECHA} Cadena: ").strip()
                    if cadena.lower() == 'salir':
                        self.logger.info("Volviendo al menú de selección de autómata...", Iconos.INFO)
                        return 'volver_menu'
                    resultado = automata.validar_cadena(cadena)
                    icono_resultado = Iconos.COMPLETADO if resultado else Iconos.FALLO
                    estado = "ACEPTADA" if resultado else "RECHAZADA"
                    self.logger.info(f"'{cadena}' -> {estado}", icono_resultado)
                except KeyboardInterrupt:
                    self.logger.info(f"\n{Iconos.COMPLETADO} Saliendo...")
                    raise  # Propaga la excepción para terminar el programa
                except Exception as e:
                    self.logger.error(f"Error: {e}")
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1
        finally:
            # Eliminar archivo temporal si corresponde
            if es_temp_min and temp_min_path.exists():
                try:
                    os.remove(temp_min_path)
                except Exception as e:
                    self.logger.error(f"No se pudo eliminar el archivo temporal: {e}")

    def validar_cadena_especifica(self, ruta_entrada: str, cadena: str) -> int:
        """
        Valida una cadena específica en un autómata y muestra el resultado.
        Returns:
            int: 0 si la cadena es válida, 1 si hay error.
        """
        try:
            automata = self._cargar_automata(ruta_entrada)
            resultado = automata.validar_cadena(cadena)
            icono_resultado = Iconos.COMPLETADO if resultado else Iconos.FALLO
            estado = "ACEPTADA" if resultado else "RECHAZADA"
            self.logger.info(f"Cadena '{cadena}'", Iconos.CADENA)
            self.logger.info(estado, icono_resultado)
            tipo_icono = Iconos.AFND if isinstance(automata, AFND) else Iconos.AFD
            self.logger.info(f"Autómata: {type(automata).__name__} con {len(automata.estados)} estados", tipo_icono)
            return 0
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1

    def validar_cadenas_desde_archivo(self, archivo_automata: str, archivo_cadenas: str) -> int:
        """
        Valida múltiples cadenas desde un archivo JSON usando un autómata específico.
        Returns:
            int: 0 si todas las cadenas se validan correctamente, 1 si hay error.
        """
        try:
            import json
            # Cargar cadenas desde archivo JSON
            with open(archivo_cadenas, 'r', encoding='utf-8') as f:
                datos = json.load(f)
            # Validar estructura del archivo JSON
            if 'cadenas' not in datos:
                self.logger.error("El archivo JSON debe contener el campo 'cadenas'")
                self.logger.info("Formato esperado: {'cadenas': ['cadena1', 'cadena2', ...]}")
                return 1
            cadenas = datos['cadenas']
            if not isinstance(cadenas, list):
                self.logger.error("El campo 'cadenas' debe ser una lista")
                return 1
            automata = self._cargar_automata(archivo_automata)
            self._mostrar_info_automata(automata)
            for cadena in cadenas:
                resultado = automata.validar_cadena(cadena)
                icono_resultado = Iconos.COMPLETADO if resultado else Iconos.FALLO
                estado = "ACEPTADA" if resultado else "RECHAZADA"
                self.logger.info(f"'{cadena}' -> {estado}", icono_resultado)
            return 0
        except Exception as e:
            self.logger.error(f"Error: {e}")
            return 1

    def _cargar_automata(self, ruta_entrada: str):
        """Carga un autómata desde un archivo, detectando el formato automáticamente."""
        formato = self.manejador_archivos.validar_formato_archivo(ruta_entrada)
        if formato == 'json':
            return self.manejador_archivos.cargar_automata_desde_json(ruta_entrada)
        else:
            return self.manejador_archivos.cargar_automata_desde_texto(ruta_entrada)

    def _mostrar_info_automata(self, automata):
        """Muestra información básica del autómata cargado."""
        tipo = type(automata).__name__
        self.logger.info(f"Tipo: {tipo} | Estados: {len(automata.estados)} | Alfabeto: {automata.alfabeto}")
