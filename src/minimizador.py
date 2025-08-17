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
                    # Encontrar a qué grupo pertenece el destino
                    grupo_destino = self._encontrar_grupo_de_estado(destino, particion_actual)
                    firma.append(grupo_destino)
                else:
                    firma.append(None)  # No hay transición

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
        Genera un reporte detallado de la minimización.

        Args:
            afd_original: AFD original
            afd_minimizado: AFD minimizado

        Returns:
            str: Reporte de la minimización
        """
        reporte = []
        reporte.append("=== REPORTE DE MINIMIZACIÓN AFD ===")
        reporte.append("")

        reporte.append("AFD ORIGINAL:")
        reporte.append(f"  Estados: {afd_original.estados}")
        reporte.append(f"  Alfabeto: {afd_original.alfabeto}")
        reporte.append(f"  Estado inicial: {afd_original.estado_inicial}")
        reporte.append(f"  Estados finales: {afd_original.estados_finales}")
        reporte.append(f"  Número de transiciones: {len(afd_original.transiciones)}")
        reporte.append("")

        reporte.append("AFD MINIMIZADO:")
        reporte.append(f"  Estados: {afd_minimizado.estados}")
        reporte.append(f"  Alfabeto: {afd_minimizado.alfabeto}")
        reporte.append(f"  Estado inicial: {afd_minimizado.estado_inicial}")
        reporte.append(f"  Estados finales: {afd_minimizado.estados_finales}")
        reporte.append(f"  Número de transiciones: {len(afd_minimizado.transiciones)}")
        reporte.append("")

        reporte.append("PROCESO DE MINIMIZACIÓN:")
        for paso in self.historial_minimizacion:
            reporte.append(f"  {paso}")

        reporte.append("")
        reporte.append("PARTICIONES POR ITERACIÓN:")
        for i, particion in enumerate(self.particiones):
            reporte.append(f"  Iteración {i}: {particion}")

        reporte.append("")
        reporte.append("ANÁLISIS:")
        reduccion = len(afd_original.estados) - len(afd_minimizado.estados)
        porcentaje = (reduccion / len(afd_original.estados)) * 100 if len(afd_original.estados) > 0 else 0
        reporte.append(f"  Reducción de estados: {len(afd_original.estados)} → {len(afd_minimizado.estados)} ({reduccion} estados eliminados)")
        reporte.append(f"  Porcentaje de reducción: {porcentaje:.1f}%")
        reporte.append(f"  Cambio en transiciones: {len(afd_original.transiciones)} → {len(afd_minimizado.transiciones)}")

        return "\n".join(reporte)
