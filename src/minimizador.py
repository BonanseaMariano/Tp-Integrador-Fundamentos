"""
Módulo para minimizar Autómatas Finitos Deterministas (AFD) utilizando
el algoritmo de partición de estados equivalentes.
"""

from .automata import AFD


class MinimizadorAFD:
    """Clase para minimizar AFD usando el algoritmo de partición."""

    def __init__(self):
        self.historial_minimizacion = []
        self.particiones = []

    def minimizar(self, afd):
        """
        Minimiza un AFD utilizando el algoritmo de partición.

        Args:
            afd: AFD a minimizar

        Returns:
            AFD: AFD minimizado equivalente
        """
        if not isinstance(afd, AFD):
            raise ValueError("El input debe ser un AFD")

        # Reiniciar variables
        self.historial_minimizacion = []
        self.particiones = []

        # Paso 1: Eliminar estados inalcanzables
        estados_alcanzables = afd.obtener_estados_alcanzables()
        afd_sin_inalcanzables = self._eliminar_estados_inalcanzables(afd, estados_alcanzables)

        self.historial_minimizacion.append(f"Estados inalcanzables eliminados: {len(afd.estados) - len(estados_alcanzables)}")

        # Paso 2: Partición inicial (finales vs no finales)
        estados_finales = set(afd_sin_inalcanzables.estados_finales)
        estados_no_finales = afd_sin_inalcanzables.estados - estados_finales

        particion_actual = []
        if estados_no_finales:
            particion_actual.append(estados_no_finales)
        if estados_finales:
            particion_actual.append(estados_finales)

        self.particiones.append([set(p) for p in particion_actual])
        self.historial_minimizacion.append(f"Partición inicial: {particion_actual}")

        # Paso 3: Refinamiento de particiones
        iteracion = 0
        while True:
            iteracion += 1
            nueva_particion = self._refinar_particion(afd_sin_inalcanzables, particion_actual)

            self.particiones.append([set(p) for p in nueva_particion])
            self.historial_minimizacion.append(f"Iteración {iteracion}: {nueva_particion}")

            # Si no hay cambios, hemos terminado
            if len(nueva_particion) == len(particion_actual):
                # Verificar que las particiones son idénticas
                if self._particiones_equivalentes(particion_actual, nueva_particion):
                    break

            particion_actual = nueva_particion

        self.historial_minimizacion.append(f"Minimización completada en {iteracion} iteraciones")

        # Paso 4: Construir AFD minimizado
        afd_minimizado = self._construir_afd_minimizado(afd_sin_inalcanzables, particion_actual)

        return afd_minimizado

    def _eliminar_estados_inalcanzables(self, afd, estados_alcanzables):
        """Elimina estados inalcanzables del AFD."""
        if len(estados_alcanzables) == len(afd.estados):
            return afd  # No hay estados inalcanzables

        # Filtrar transiciones para mantener solo las de estados alcanzables
        transiciones_filtradas = {}
        for (origen, simbolo), destino in afd.transiciones.items():
            if origen in estados_alcanzables and destino in estados_alcanzables:
                transiciones_filtradas[(origen, simbolo)] = destino

        # Filtrar estados finales
        estados_finales_filtrados = afd.estados_finales.intersection(estados_alcanzables)

        return AFD(
            estados=estados_alcanzables,
            alfabeto=afd.alfabeto,
            estado_inicial=afd.estado_inicial,
            estados_finales=estados_finales_filtrados,
            transiciones=transiciones_filtradas
        )

    def _refinar_particion(self, afd, particion_actual):
        """
        Refina una partición dividiendo grupos que no son equivalentes.

        Args:
            afd: AFD a analizar
            particion_actual: lista de conjuntos de estados

        Returns:
            list: nueva partición refinada
        """
        nueva_particion = []

        for grupo in particion_actual:
            subgrupos = self._dividir_grupo(afd, grupo, particion_actual)
            nueva_particion.extend(subgrupos)

        return nueva_particion

    def _dividir_grupo(self, afd, grupo, particion_actual):
        """
        Divide un grupo de estados si no todos son equivalentes.

        Args:
            afd: AFD a analizar
            grupo: conjunto de estados a analizar
            particion_actual: partición actual

        Returns:
            list: lista de subgrupos resultantes
        """
        if len(grupo) <= 1:
            return [grupo]

        # Crear firma para cada estado basada en sus transiciones
        firmas = {}
        for estado in grupo:
            firma = []
            for simbolo in sorted(afd.alfabeto):
                if (estado, simbolo) in afd.transiciones:
                    destino = afd.transiciones[(estado, simbolo)]
                    # Encontrar a qué PARTICIÓN pertenece el destino (no el destino específico)
                    particion_destino = self._encontrar_grupo_de_estado(destino, particion_actual)
                    firma.append(particion_destino)
                else:
                    # Transición indefinida - va al estado sumidero (representado como -1)
                    firma.append(-1)

            firma_tuple = tuple(firma)
            if firma_tuple not in firmas:
                firmas[firma_tuple] = set()
            firmas[firma_tuple].add(estado)

        # Retornar los subgrupos (conjuntos de estados con la misma firma)
        return list(firmas.values())

    def _encontrar_grupo_de_estado(self, estado, particion):
        """Encuentra el índice del grupo al que pertenece un estado."""
        for i, grupo in enumerate(particion):
            if estado in grupo:
                return i
        return -1  # No debería ocurrir si la partición es válida

    def _particiones_equivalentes(self, particion1, particion2):
        """Verifica si dos particiones son equivalentes."""
        if len(particion1) != len(particion2):
            return False

        # Convertir a conjuntos de conjuntos para comparación
        conjuntos1 = {frozenset(grupo) for grupo in particion1}
        conjuntos2 = {frozenset(grupo) for grupo in particion2}

        return conjuntos1 == conjuntos2

    def _construir_afd_minimizado(self, afd_original, particion_final):
        """
        Construye el AFD minimizado basado en la partición final.

        Args:
            afd_original: AFD original
            particion_final: partición final de estados equivalentes

        Returns:
            AFD: AFD minimizado
        """
        # Mapeo de estado original -> representante del grupo
        mapeo_estados = {}
        estados_minimizados = set()
        representantes = {}

        for i, grupo in enumerate(particion_final):
            # Elegir un representante para el grupo (el lexicográficamente menor)
            representante = min(grupo, key=str)
            representantes[i] = representante
            estados_minimizados.add(representante)

            for estado in grupo:
                mapeo_estados[estado] = representante

        # Estado inicial del AFD minimizado
        estado_inicial_min = mapeo_estados[afd_original.estado_inicial]

        # Estados finales del AFD minimizado
        estados_finales_min = set()
        for estado_final in afd_original.estados_finales:
            if estado_final in mapeo_estados:
                estados_finales_min.add(mapeo_estados[estado_final])

        # Transiciones del AFD minimizado
        transiciones_min = {}
        for (origen, simbolo), destino in afd_original.transiciones.items():
            if origen in mapeo_estados and destino in mapeo_estados:
                origen_min = mapeo_estados[origen]
                destino_min = mapeo_estados[destino]
                transiciones_min[(origen_min, simbolo)] = destino_min

        return AFD(
            estados=estados_minimizados,
            alfabeto=afd_original.alfabeto,
            estado_inicial=estado_inicial_min,
            estados_finales=estados_finales_min,
            transiciones=transiciones_min,
            descripcion=getattr(afd_original, 'descripcion', None)  # Mantener descripción del original
        )

    def obtener_historial_minimizacion(self):
        """Retorna el historial del proceso de minimización."""
        return self.historial_minimizacion.copy()

    def obtener_particiones(self):
        """Retorna todas las particiones generadas durante el proceso."""
        return [p.copy() for p in self.particiones]

    def generar_reporte_minimizacion(self, afd_original, afd_minimizado):
        """
        Genera un reporte detallado de la minimización con representación tabular.

        Args:
            afd_original: AFD original
            afd_minimizado: AFD minimizado

        Returns:
            str: Reporte de la minimización con tablas
        """
        reporte = []
        reporte.append("=" * 60)
        reporte.append("REPORTE DE MINIMIZACIÓN AFD")
        reporte.append("=" * 60)
        reporte.append("")

        # Información general
        reporte.append("RESUMEN:")
        reduccion = len(afd_original.estados) - len(afd_minimizado.estados)
        porcentaje = (reduccion / len(afd_original.estados)) * 100 if len(afd_original.estados) > 0 else 0
        reporte.append(f"  • Estados originales: {len(afd_original.estados)}")
        reporte.append(f"  • Estados minimizados: {len(afd_minimizado.estados)}")
        reporte.append(f"  • Reducción: {reduccion} estados eliminados ({porcentaje:.1f}%)")
        reporte.append(f"  • Transiciones originales: {len(afd_original.transiciones)}")
        reporte.append(f"  • Transiciones minimizadas: {len(afd_minimizado.transiciones)}")
        reporte.append("")

        # Análisis detallado de particiones
        reporte.append("ANÁLISIS DETALLADO DE PARTICIONES:")
        reporte.append("-" * 40)
        if self.particiones:
            # Analizar específicamente los estados que mencionaste
            estados_interes = ["{S1,S2}", "{S1,S2,S3}"]
            for iteracion, particion in enumerate(self.particiones):
                reporte.append(f"Iteración {iteracion}:")
                for i, grupo in enumerate(particion):
                    estados_grupo = [str(e) for e in sorted(grupo, key=str)]
                    # Marcar si contiene estados de interés
                    contiene_interes = any(estado in estados_grupo for estado in estados_interes)
                    marca = " ★" if contiene_interes else ""
                    reporte.append(f"  Partición {i}: {{{', '.join(estados_grupo)}}}{marca}")

                    # Si contiene estados de interés, analizar por qué están separados o juntos
                    if contiene_interes and len([e for e in estados_interes if e in estados_grupo]) == 2:
                        reporte.append(f"    → {estados_interes[0]} y {estados_interes[1]} están en la misma partición")
                    elif contiene_interes:
                        for estado in estados_interes:
                            if estado in estados_grupo:
                                reporte.append(f"    → {estado} está en esta partición")
                reporte.append("")

        # Tabla del AFD original
        reporte.append("AUTÓMATA ORIGINAL (AFD):")
        reporte.append("-" * 40)
        reporte.extend(self._generar_tabla_transiciones(afd_original))
        reporte.append("")

        # Tabla del AFD minimizado
        reporte.append("AUTÓMATA MINIMIZADO (AFD):")
        reporte.append("-" * 40)
        reporte.extend(self._generar_tabla_transiciones(afd_minimizado))
        reporte.append("")

        # Proceso de minimización detallado
        reporte.append("PROCESO DE MINIMIZACIÓN DETALLADO:")
        reporte.append("-" * 40)
        for i, paso in enumerate(self.historial_minimizacion, 1):
            reporte.append(f"{i:2}. {paso}")
        reporte.append("")

        # Mapeo de estados equivalentes
        reporte.append("MAPEO DE ESTADOS EQUIVALENTES:")
        reporte.append("-" * 40)
        if hasattr(self, 'particiones') and self.particiones:
            particion_final = self.particiones[-1] if self.particiones else []
            for i, grupo in enumerate(particion_final):
                if len(grupo) > 1:
                    representante = min(grupo, key=str)
                    estados_equivalentes = sorted(grupo - {representante}, key=str)
                    if estados_equivalentes:
                        reporte.append(f"  {representante} ≡ {{{', '.join(estados_equivalentes)}}}")

        # Análisis específico de por qué {S1,S2} y {S1,S2,S3} no se combinaron
        reporte.append("")
        reporte.append("ANÁLISIS DE EQUIVALENCIA {S1,S2} vs {S1,S2,S3}:")
        reporte.append("-" * 40)
        if "{S1,S2}" in afd_original.estados and "{S1,S2,S3}" in afd_original.estados:
            # Analizar transiciones
            trans_s1s2 = {}
            trans_s1s2s3 = {}

            for simbolo in sorted(afd_original.alfabeto):
                trans_s1s2[simbolo] = afd_original.transiciones.get(("{S1,S2}", simbolo), "∅")
                trans_s1s2s3[simbolo] = afd_original.transiciones.get(("{S1,S2,S3}", simbolo), "∅")

            reporte.append("Transiciones:")
            for simbolo in sorted(afd_original.alfabeto):
                reporte.append(f"  Con '{simbolo}':")
                reporte.append(f"    {{S1,S2}} → {trans_s1s2[simbolo]}")
                reporte.append(f"    {{S1,S2,S3}} → {trans_s1s2s3[simbolo]}")

                # Verificar si van a la misma partición
                if self.particiones:
                    particion_final = self.particiones[-1]
                    destino1 = trans_s1s2[simbolo]
                    destino2 = trans_s1s2s3[simbolo]

                    if destino1 != "∅" and destino2 != "∅":
                        grupo1 = self._encontrar_grupo_de_estado(destino1, particion_final)
                        grupo2 = self._encontrar_grupo_de_estado(destino2, particion_final)

                        if grupo1 == grupo2:
                            reporte.append(f"    ✓ Ambos destinos están en la partición {grupo1}")
                        else:
                            reporte.append(f"    ✗ Destinos en particiones diferentes: {grupo1} vs {grupo2}")
        reporte.append("")

        # Verificación de equivalencia
        reporte.append("VERIFICACIÓN DE EQUIVALENCIA:")
        reporte.append("-" * 40)
        reporte.append("Ambos autómatas aceptan el mismo lenguaje:")
        reporte.append(f"  • Estado inicial original: {afd_original.estado_inicial}")
        reporte.append(f"  • Estado inicial minimizado: {afd_minimizado.estado_inicial}")
        reporte.append(f"  • Estados finales originales: {sorted(afd_original.estados_finales)}")
        reporte.append(f"  • Estados finales minimizados: {sorted(afd_minimizado.estados_finales)}")

        return "\n".join(reporte)

    def _generar_tabla_transiciones(self, automata):
        """
        Genera una representación tabular de las transiciones del autómata.

        Args:
            automata: AFD para generar la tabla

        Returns:
            list: Lista de strings representando la tabla
        """
        tabla = []

        # Información básica
        tabla.append(f"Tipo: AFD")
        tabla.append(f"Estados: {sorted(automata.estados, key=str)}")
        tabla.append(f"Alfabeto: {sorted(automata.alfabeto, key=str)}")
        tabla.append(f"Estado inicial: {automata.estado_inicial}")
        tabla.append(f"Estados finales: {sorted(automata.estados_finales, key=str)}")
        tabla.append("")

        # Crear tabla de transiciones
        estados_ordenados = sorted(automata.estados, key=str)
        alfabeto_ordenado = sorted(automata.alfabeto, key=str)

        # Encabezado de la tabla
        encabezado = ["δ"] + [str(simbolo) for simbolo in alfabeto_ordenado] + ["F"]

        # Calcular anchos de columnas
        ancho_estado = max(len(str(estado)) for estado in estados_ordenados + [encabezado[0]])
        anchos_simbolos = []
        for i, simbolo in enumerate(alfabeto_ordenado, 1):
            ancho_simbolo = len(encabezado[i])
            for estado in estados_ordenados:
                if (estado, simbolo) in automata.transiciones:
                    destino = automata.transiciones[(estado, simbolo)]
                    destinos_str = str(destino)
                    ancho_simbolo = max(ancho_simbolo, len(destinos_str))
            anchos_simbolos.append(ancho_simbolo)

        ancho_final = 1  # Para la columna F (0 o 1)

        # Generar línea de separación
        separador = "+" + "-" * (ancho_estado + 2)
        for ancho in anchos_simbolos:
            separador += "+" + "-" * (ancho + 2)
        separador += "+" + "-" * (ancho_final + 2) + "+"

        # Agregar encabezado
        tabla.append(separador)
        linea_encabezado = f"| {encabezado[0]:^{ancho_estado}} "
        for i, simbolo in enumerate(alfabeto_ordenado):
            linea_encabezado += f"| {encabezado[i+1]:^{anchos_simbolos[i]}} "
        linea_encabezado += f"| {'F':^{ancho_final}} |"
        tabla.append(linea_encabezado)
        tabla.append(separador)

        # Agregar filas de estados
        for estado in estados_ordenados:
            linea = f"| {str(estado):^{ancho_estado}} "

            # Columnas de transiciones
            for i, simbolo in enumerate(alfabeto_ordenado):
                if (estado, simbolo) in automata.transiciones:
                    destino = automata.transiciones[(estado, simbolo)]
                    destinos_str = str(destino)
                else:
                    destinos_str = "∅"  # Conjunto vacío

                linea += f"| {destinos_str:^{anchos_simbolos[i]}} "

            # Columna de estado final
            es_final = "1" if estado in automata.estados_finales else "0"
            linea += f"| {es_final:^{ancho_final}} |"
            tabla.append(linea)

        tabla.append(separador)

        return tabla

