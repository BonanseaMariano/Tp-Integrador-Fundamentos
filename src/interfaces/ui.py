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

    def validar_cadenas_desde_archivo(self, archivo_automata: str, archivo_cadenas: str) -> int:
        """Valida múltiples cadenas desde un archivo JSON usando un autómata específico."""
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

            # Cargar autómata
            self.logger.info(f"📂 Cargando autómata desde: {archivo_automata}", Iconos.CARGANDO)
            automata = self._cargar_automata(archivo_automata)

            # Mostrar información del autómata con descripción
            tipo_icono = Iconos.AFND if isinstance(automata, AFND) else Iconos.AFD
            self.logger.info(f"Autómata: {type(automata).__name__} con {len(automata.estados)} estados", tipo_icono)

            # Mostrar descripción si está disponible
            if hasattr(automata, 'descripcion') and automata.descripcion:
                self.logger.info(f"📝 Descripción: {automata.descripcion}", Iconos.INFO)
            else:
                self.logger.warning("📝 Sin descripción disponible", Iconos.ADVERTENCIA)

            # Validar todas las cadenas
            self.logger.separador("VALIDACIÓN DE MÚLTIPLES CADENAS")
            self.logger.info(f"📋 Validando {len(cadenas)} cadenas desde: {archivo_cadenas}", Iconos.ARCHIVO)

            resultados = []
            cadenas_aceptadas = 0
            cadenas_rechazadas = 0

            for i, cadena in enumerate(cadenas, 1):
                cadena_str = str(cadena)  # Asegurar que es string
                resultado = automata.validar_cadena(cadena_str)

                icono_resultado = Iconos.CHECK if resultado else Iconos.CRUZ
                estado = "✅ ACEPTADA" if resultado else "❌ RECHAZADA"

                # Mostrar cadena vacía como λ para mejor visualización
                cadena_mostrar = "λ" if cadena_str == "" else f"'{cadena_str}'"

                self.logger.info(f"{i:2d}. {cadena_mostrar:15s} → {estado}")

                resultados.append({
                    'cadena': cadena_str,
                    'resultado': resultado,
                    'posicion': i
                })

                if resultado:
                    cadenas_aceptadas += 1
                else:
                    cadenas_rechazadas += 1

            # Eliminar el resumen de validación - ya no se mostrará

            # Ofrecer guardar reporte si hay muchas cadenas
            if len(cadenas) >= 10:
                guardar, ruta_personalizada = self._preguntar_guardar_reporte()
                if guardar:
                    self._guardar_reporte_validacion(archivo_cadenas, archivo_automata, resultados, automata, ruta_personalizada)

            return 0

        except FileNotFoundError as e:
            if archivo_cadenas in str(e):
                self.logger.error(f"Archivo de cadenas no encontrado: {archivo_cadenas}")
            else:
                self.logger.error(f"Archivo de autómata no encontrado: {archivo_automata}")
            return 1
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing JSON: {e}")
            self.logger.info("Verifique que el archivo tenga formato JSON válido")
            return 1
        except KeyError as e:
            self.logger.error(f"Campo requerido no encontrado en JSON: {e}")
            return 1
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

    def _preguntar_guardar_reporte(self) -> tuple[bool, str]:
        """Pregunta al usuario si desea guardar un reporte de validación y dónde."""
        try:
            respuesta = input("\n¿Deseas guardar un reporte detallado? (s/N): ").strip().lower()
            if respuesta == 's':
                ruta_reporte = input("Ingresa la ruta y nombre del archivo (sin extensión): ").strip()
                if not ruta_reporte:
                    self.logger.warning("Ruta vacía, usando nombre por defecto")
                    return True, ""
                return True, ruta_reporte
            return False, ""
        except (KeyboardInterrupt, EOFError):
            return False, ""

    def _guardar_reporte_validacion(self, archivo_cadenas: str, ruta_automata: str, resultados: list, automata, ruta_personalizada: str = ""):
        """Guarda un reporte detallado de la validación."""
        try:
            from datetime import datetime
            from pathlib import Path

            # Determinar nombre y ruta del reporte
            if ruta_personalizada:
                # Usar ruta personalizada del usuario
                ruta_path = Path(ruta_personalizada)

                # Crear directorios padre si no existen
                if ruta_path.parent != Path('.'):
                    ruta_path.parent.mkdir(parents=True, exist_ok=True)

                # Asegurar extensión .txt
                nombre_reporte = str(ruta_path) + ".txt"
            else:
                # Usar nombre por defecto con timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nombre_base = Path(archivo_cadenas).stem
                nombre_reporte = f"reporte_validacion_{nombre_base}_{timestamp}.txt"

            # Generar contenido del reporte
            reporte = []
            reporte.append("=" * 80)
            reporte.append("REPORTE DE VALIDACIÓN DE MÚLTIPLES CADENAS")
            reporte.append("=" * 80)
            reporte.append("")
            reporte.append(f"Fecha y hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            reporte.append("")

            # 1. RUTA DEL AUTÓMATA
            reporte.append("AUTÓMATA UTILIZADO:")
            reporte.append("-" * 40)
            reporte.append(f"Ruta: {ruta_automata}")
            reporte.append("")

            # 2. DESCRIPCIÓN DEL AUTÓMATA
            reporte.append("DESCRIPCIÓN:")
            reporte.append("-" * 40)
            if hasattr(automata, 'descripcion') and automata.descripcion:
                reporte.append(f"{automata.descripcion}")
            else:
                reporte.append("Sin descripción disponible")
            reporte.append("")

            # 3. TABLA CON TODAS LAS CADENAS
            reporte.append("TABLA DE RESULTADOS:")
            reporte.append("-" * 40)

            # Crear encabezado de la tabla
            reporte.append("+-----+----------------------+------------+")
            reporte.append("| No. |        Cadena        |  Resultado |")
            reporte.append("+-----+----------------------+------------+")

            # Agregar todas las cadenas en formato tabular
            for resultado in resultados:
                cadena = resultado['cadena']
                acepta = resultado['resultado']
                posicion = resultado['posicion']

                # Formatear la cadena para mostrar
                if cadena == "":
                    cadena_mostrar = "λ (vacía)"
                else:
                    cadena_mostrar = f"'{cadena}'"

                # Truncar cadena si es muy larga para que quepa en la tabla
                if len(cadena_mostrar) > 20:
                    cadena_mostrar = cadena_mostrar[:17] + "..."

                estado = "ACEPTADA" if acepta else "RECHAZADA"

                reporte.append(f"| {posicion:3d} | {cadena_mostrar:<20} | {estado:<10} |")

            reporte.append("+-----+----------------------+------------+")
            reporte.append("")
            reporte.append("=" * 80)

            # Guardar el archivo
            with open(nombre_reporte, 'w', encoding='utf-8') as f:
                f.write('\n'.join(reporte))

            self.logger.success(f"📄 Reporte guardado: {nombre_reporte}", Iconos.ARCHIVO)

        except Exception as e:
            self.logger.error(f"Error guardando reporte: {e}")
