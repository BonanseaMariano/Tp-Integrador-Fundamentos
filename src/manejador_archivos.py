"""
Módulo para lectura y escritura de archivos de autómatas finitos.

Soporta formatos JSON y texto plano. Permite cargar y guardar autómatas deterministas y no deterministas,
validando la estructura y consistencia de los datos.
"""

import json
from .automata import AFD, AFND


class ManejadorArchivos:
    """
    Clase para manejar la entrada y salida de archivos de autómatas.
    Permite cargar y guardar autómatas en formato JSON o texto plano, validando la estructura y los datos.
    """

    @staticmethod
    def cargar_automata_desde_json(ruta_archivo):
        """
        Carga un autómata desde un archivo JSON, validando su estructura y consistencia.

        Args:
            ruta_archivo (str): Ruta al archivo JSON.
        Returns:
            AFD o AFND: Autómata cargado desde el archivo.
        Raises:
            FileNotFoundError, PermissionError, ValueError: Si hay errores de acceso o formato.
        """
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                datos = json.load(archivo)

        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Archivo no encontrado: {ruta_archivo}")
        except PermissionError:
            raise PermissionError(f"❌ Sin permisos para leer el archivo: {ruta_archivo}")
        except json.JSONDecodeError as e:
            raise ValueError(f"❌ Error al parsear JSON en línea {e.lineno}: {e.msg}")
        except UnicodeDecodeError:
            raise ValueError(f"❌ Error de codificación. El archivo debe estar en UTF-8: {ruta_archivo}")
        except Exception as e:
            raise ValueError(f"❌ Error inesperado al cargar archivo JSON: {e}")

        try:
            # Validar estructura del archivo
            campos_requeridos = ['estados', 'alfabeto', 'estado_inicial', 'estados_finales', 'transiciones']
            for campo in campos_requeridos:
                if campo not in datos:
                    raise ValueError(f"❌ Campo requerido '{campo}' no encontrado en el archivo JSON")

            # Validar que los campos no estén vacíos
            if not datos['estados']:
                raise ValueError("❌ El conjunto de estados no puede estar vacío")
            if not datos['alfabeto']:
                raise ValueError("❌ El alfabeto no puede estar vacío")
            if not datos['estado_inicial']:
                raise ValueError("❌ El estado inicial no puede estar vacío")
            if not isinstance(datos['transiciones'], list):
                raise ValueError("❌ Las transiciones deben ser una lista")

            # Extraer datos
            estados = set(datos['estados'])
            alfabeto = set(datos['alfabeto'])
            estado_inicial = datos['estado_inicial']
            estados_finales = set(datos['estados_finales'])
            descripcion = datos.get('descripcion', None)

            # Validar consistencia
            if estado_inicial not in estados:
                raise ValueError(f"❌ Estado inicial '{estado_inicial}' no está en el conjunto de estados")

            for estado_final in estados_finales:
                if estado_final not in estados:
                    raise ValueError(f"❌ Estado final '{estado_final}' no está en el conjunto de estados")

            # Procesar transiciones
            transiciones = {}
            for i, transicion in enumerate(datos['transiciones']):
                try:
                    # Validar estructura de transición
                    if not isinstance(transicion, dict):
                        raise ValueError(f"❌ Transición {i + 1} debe ser un objeto")

                    campos_transicion = ['origen', 'simbolo', 'destino']
                    for campo in campos_transicion:
                        if campo not in transicion:
                            raise ValueError(f"❌ Campo '{campo}' faltante en transición {i + 1}")

                    origen = transicion['origen']
                    simbolo = transicion['simbolo']
                    destino = transicion['destino']

                    # Validar que origen esté en el conjunto de estados
                    if origen not in estados:
                        raise ValueError(
                            f"❌ Estado origen '{origen}' en transición {i + 1} no está en el conjunto de estados")

                    # Validar que símbolo esté en el alfabeto (excepto epsilon)
                    if simbolo != '' and simbolo not in alfabeto:
                        raise ValueError(f"❌ Símbolo '{simbolo}' en transición {i + 1} no está en el alfabeto")

                    # Crear clave para la transición
                    clave = (origen, simbolo)

                    # Validar destinos
                    if isinstance(destino, list):
                        if not destino:
                            raise ValueError(f"❌ Lista de destinos vacía en transición {i + 1}")
                        for dest in destino:
                            if dest not in estados:
                                raise ValueError(
                                    f"❌ Estado destino '{dest}' en transición {i + 1} no está en el conjunto de estados")

                        # Si ya existe la transición, agregar los destinos al conjunto existente
                        if clave in transiciones:
                            if isinstance(transiciones[clave], set):
                                transiciones[clave].update(destino)
                            else:
                                # Convertir destino único existente a conjunto y agregar nuevos destinos
                                transiciones[clave] = {transiciones[clave]} | set(destino)
                        else:
                            transiciones[clave] = set(destino)
                    else:
                        if destino not in estados:
                            raise ValueError(
                                f"❌ Estado destino '{destino}' en transición {i + 1} no está en el conjunto de estados")

                        # Si ya existe la transición, convertir a conjunto y agregar el nuevo destino
                        if clave in transiciones:
                            if isinstance(transiciones[clave], set):
                                transiciones[clave].add(destino)
                            else:
                                # Convertir a conjunto con el destino existente y el nuevo
                                transiciones[clave] = {transiciones[clave], destino}
                        else:
                            transiciones[clave] = destino

                except Exception as e:
                    raise ValueError(f"❌ Error en transición {i + 1}: {e}")

            # Determinar si es AFD o AFND
            es_afnd = any(isinstance(destino, set) for destino in transiciones.values())
            es_afnd = es_afnd or '' in alfabeto  # También si tiene transiciones epsilon

            if es_afnd:
                return AFND(estados, alfabeto, estado_inicial, estados_finales, transiciones, descripcion)
            else:
                return AFD(estados, alfabeto, estado_inicial, estados_finales, transiciones, descripcion)

        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            raise ValueError(f"❌ Error procesando datos del archivo JSON: {e}")

    @staticmethod
    def guardar_automata_como_json(automata, ruta_archivo, incluir_metadatos=True):
        """
        Guarda un autómata en formato JSON, permitiendo incluir metadatos opcionales.

        Args:
            automata: AFD o AFND a guardar.
            ruta_archivo (str): Ruta donde guardar el archivo.
            incluir_metadatos (bool): Si incluir información adicional.
        """
        try:
            # Preparar transiciones para JSON
            transiciones_json = []
            for (origen, simbolo), destino in automata.transiciones.items():
                if isinstance(destino, set):
                    destino_json = list(destino)
                else:
                    destino_json = destino

                transiciones_json.append({
                    'origen': origen,
                    'simbolo': simbolo,
                    'destino': destino_json
                })

            # Estructura del JSON
            datos = {
                'estados': list(automata.estados),
                'alfabeto': list(automata.alfabeto),
                'estado_inicial': automata.estado_inicial,
                'estados_finales': list(automata.estados_finales),
                'transiciones': transiciones_json
            }

            # Agregar descripción si existe
            if hasattr(automata, 'descripcion') and automata.descripcion:
                datos['descripcion'] = automata.descripcion

            if incluir_metadatos:
                # datos['tipo'] = 'AFD' if isinstance(automata, AFD) else 'AFND'  # Eliminado
                datos['num_estados'] = len(automata.estados)
                datos['num_transiciones'] = len(automata.transiciones)

            # Guardar archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)

        except Exception as e:
            raise IOError(f"Error al guardar archivo: {e}")

    @staticmethod
    def cargar_automata_desde_texto(ruta_archivo):
        """
        Carga un autómata desde un archivo de texto con formato específico.

        Formato esperado:
        ESTADOS: q0,q1,q2
        ALFABETO: a,b
        ESTADO_INICIAL: q0
        ESTADOS_FINALES: q2
        DESCRIPCION: Descripción opcional del autómata
        TIPO: AFD o AFND (opcional)
        TRANSICIONES:
        q0,a,q1
        q1,b,q2
        """
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                lineas = [linea.strip() for linea in archivo.readlines() if linea.strip()]

        except FileNotFoundError:
            raise FileNotFoundError(f"❌ Archivo no encontrado: {ruta_archivo}")
        except PermissionError:
            raise PermissionError(f"❌ Sin permisos para leer el archivo: {ruta_archivo}")
        except UnicodeDecodeError:
            raise ValueError(f"❌ Error de codificación. El archivo debe estar en UTF-8: {ruta_archivo}")
        except Exception as e:
            raise ValueError(f"❌ Error inesperado al cargar archivo de texto: {e}")

        if not lineas:
            raise ValueError("❌ El archivo está vacío")

        try:
            datos = {}
            transiciones = []
            seccion_transiciones = False
            numero_linea = 0

            for numero_linea, linea in enumerate(lineas, 1):
                if linea.startswith('TRANSICIONES:'):
                    seccion_transiciones = True
                    continue

                if seccion_transiciones:
                    # Procesar transición: origen,simbolo,destino(s)
                    if ',' not in linea:
                        raise ValueError(
                            f"❌ Formato inválido en transición línea {numero_linea}: '{linea}'. Formato esperado: origen,simbolo,destino")

                    partes = linea.split(',')
                    if len(partes) < 3:
                        raise ValueError(f"❌ Transición incompleta en línea {numero_linea}: '{linea}'. Faltan campos.")

                    origen = partes[0].strip()
                    simbolo = partes[1].strip()
                    destinos = [parte.strip() for parte in partes[2:] if parte.strip()]

                    if not origen:
                        raise ValueError(f"❌ Estado origen vacío en línea {numero_linea}")
                    if not destinos:
                        raise ValueError(f"❌ Estado destino vacío en línea {numero_linea}")

                    if len(destinos) == 1:
                        transiciones.append((origen, simbolo, destinos[0]))
                    else:
                        transiciones.append((origen, simbolo, destinos))
                else:
                    # Procesar metadatos
                    if ':' not in linea:
                        raise ValueError(
                            f"❌ Formato inválido en línea {numero_linea}: '{linea}'. Se esperaba formato 'CAMPO: valor'")

                    clave, valor = linea.split(':', 1)
                    clave = clave.strip().upper()
                    valor = valor.strip()

                    if not clave:
                        raise ValueError(f"❌ Campo vacío en línea {numero_linea}")
                    if not valor:
                        raise ValueError(f"❌ Valor vacío para campo '{clave}' en línea {numero_linea}")

                    if clave in ['ESTADOS', 'ALFABETO', 'ESTADOS_FINALES']:
                        elementos = [item.strip() for item in valor.split(',') if item.strip()]
                        if not elementos:
                            raise ValueError(f"❌ Lista vacía para campo '{clave}' en línea {numero_linea}")
                        datos[clave] = elementos
                    else:
                        # Aceptar cualquier campo adicional (DESCRIPCION, TIPO, etc.)
                        datos[clave] = valor

            # Validar datos requeridos
            campos_requeridos = ['ESTADOS', 'ALFABETO', 'ESTADO_INICIAL', 'ESTADOS_FINALES']
            for campo in campos_requeridos:
                if campo not in datos:
                    raise ValueError(f"❌ Campo requerido '{campo}' no encontrado en el archivo")

            # Validar que no haya duplicados
            if len(set(datos['ESTADOS'])) != len(datos['ESTADOS']):
                raise ValueError("❌ Estados duplicados en el conjunto de estados")
            if len(set(datos['ALFABETO'])) != len(datos['ALFABETO']):
                raise ValueError("❌ Símbolos duplicados en el alfabeto")

            if not transiciones:
                raise ValueError("❌ No se encontraron transiciones. Debe incluir la sección 'TRANSICIONES:'")

            # Construir estructuras del autómata
            estados = set(datos['ESTADOS'])
            alfabeto = set(datos['ALFABETO'])
            estado_inicial = datos['ESTADO_INICIAL']
            estados_finales = set(datos['ESTADOS_FINALES'])

            # Validar consistencia
            if estado_inicial not in estados:
                raise ValueError(f"❌ Estado inicial '{estado_inicial}' no está en el conjunto de estados")

            for estado_final in estados_finales:
                if estado_final not in estados:
                    raise ValueError(f"❌ Estado final '{estado_final}' no está en el conjunto de estados")

            # Extraer descripción si existe
            descripcion = datos.get('DESCRIPCION', None)

            # Procesar transiciones con validación
            transiciones_dict = {}
            es_afnd = False

            for i, transicion in enumerate(transiciones, 1):
                try:
                    origen, simbolo, destino = transicion

                    # Validar origen
                    if origen not in estados:
                        raise ValueError(f"❌ Estado origen '{origen}' no está en el conjunto de estados")

                    # Validar símbolo (permitir epsilon como cadena vacía)
                    if simbolo != '' and simbolo not in alfabeto:
                        raise ValueError(f"❌ Símbolo '{simbolo}' no está en el alfabeto")

                    # Clave de la transición
                    clave = (origen, simbolo)

                    if isinstance(destino, list):
                        # Destino múltiple explícito (formato: q0,a,q1,q2)
                        for dest in destino:
                            if dest not in estados:
                                raise ValueError(f"❌ Estado destino '{dest}' no está en el conjunto de estados")
                        transiciones_dict[clave] = set(destino)
                        es_afnd = True
                    else:
                        # Validar destino único
                        if destino not in estados:
                            raise ValueError(f"❌ Estado destino '{destino}' no está en el conjunto de estados")

                        # Verificar si ya existe esta transición (no determinismo)
                        if clave in transiciones_dict:
                            # Ya existe una transición para este (estado, símbolo)
                            # Convertir a conjunto y agregar el nuevo destino
                            if isinstance(transiciones_dict[clave], set):
                                transiciones_dict[clave].add(destino)
                            else:
                                # Convertir de destino único a conjunto
                                destino_anterior = transiciones_dict[clave]
                                transiciones_dict[clave] = {destino_anterior, destino}
                            es_afnd = True
                        else:
                            # Primera vez que vemos esta transición
                            transiciones_dict[clave] = destino

                except Exception as e:
                    raise ValueError(f"❌ Error en transición {i}: {e}")

            # Determinar tipo (usar campo TIPO si existe, sino detectar automáticamente)
            tipo_especificado = datos.get('TIPO', '').upper()
            if tipo_especificado in ['AFD', 'AFND']:
                es_afnd = (tipo_especificado == 'AFND')
            # Si no se especifica tipo, detectar por las transiciones

            # Crear autómata apropiado
            if es_afnd:
                return AFND(estados, alfabeto, estado_inicial, estados_finales, transiciones_dict, descripcion)
            else:
                return AFD(estados, alfabeto, estado_inicial, estados_finales, transiciones_dict, descripcion)

        except ValueError:
            # Re-lanzar errores de validación
            raise
        except Exception as e:
            raise ValueError(f"❌ Error procesando archivo de texto: {e}")

    @staticmethod
    def guardar_automata_como_texto(automata, ruta_archivo):
        """
        Guarda un autómata en formato de texto plano.

        Args:
            automata: AFD o AFND a guardar
            ruta_archivo: ruta donde guardar el archivo
        """
        try:
            with open(ruta_archivo, 'w', encoding='utf-8') as archivo:
                # Escribir metadatos básicos
                archivo.write(f"ESTADOS: {','.join(sorted(automata.estados, key=str))}\n")
                archivo.write(f"ALFABETO: {','.join(sorted(automata.alfabeto, key=str))}\n")
                archivo.write(f"ESTADO_INICIAL: {automata.estado_inicial}\n")
                archivo.write(f"ESTADOS_FINALES: {','.join(sorted(automata.estados_finales, key=str))}\n")

                # Escribir descripción si existe
                if hasattr(automata, 'descripcion') and automata.descripcion:
                    archivo.write(f"DESCRIPCION: {automata.descripcion}\n")

                # Escribir tipo
                # tipo = 'AFD' if isinstance(automata, AFD) else 'AFND'  # Eliminado
                # archivo.write(f"TIPO: {tipo}\n")  # Eliminado

                archivo.write("TRANSICIONES:\n")

                # Escribir transiciones
                for (origen, simbolo), destino in sorted(automata.transiciones.items()):
                    if isinstance(destino, set):
                        destinos_str = ','.join(sorted(destino, key=str))
                        archivo.write(f"{origen},{simbolo},{destinos_str}\n")
                    else:
                        archivo.write(f"{origen},{simbolo},{destino}\n")

        except Exception as e:
            raise IOError(f"Error al guardar archivo: {e}")

    @staticmethod
    def validar_formato_archivo(ruta_archivo):
        """
        Valida el formato de un archivo de autómata.

        Args:
            ruta_archivo: ruta al archivo

        Returns:
            str: 'json' o 'texto' según el formato detectado
        """
        try:
            with open(ruta_archivo, 'r', encoding='utf-8') as archivo:
                contenido = archivo.read().strip()

            # Intentar parsear como JSON
            try:
                json.loads(contenido)
                return 'json'
            except json.JSONDecodeError:
                pass

            # Verificar formato de texto
            if any(palabra in contenido for palabra in ['ESTADOS:', 'ALFABETO:', 'TRANSICIONES:']):
                return 'texto'

            raise ValueError("Formato de archivo no reconocido")

        except FileNotFoundError:
            raise FileNotFoundError(f"Archivo no encontrado: {ruta_archivo}")
        except Exception as e:
            raise ValueError(f"Error al validar formato: {e}")
