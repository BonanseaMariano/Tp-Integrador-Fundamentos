"""
Módulo para convertir AFND a AFD.
"""

from .automata import AFD, AFND


class ConversorTabular:
    """
    Conversor AFND → AFD que opera directamente sobre tablas de transiciones.
    """

    def __init__(self):
        self.tabla_afnd = {}  # Tabla original del AFND
        self.tabla_afd = {}  # Tabla resultante del AFD
        self.mapeo_estados = {}  # Conjuntos de estados AFND -> estado AFD
        self.estados_procesados = set()
        self.historial = []

    def convertir(self, afnd):
        """
        Convierte AFND a AFD usando representación tabular.

        Args:
            afnd: AFND a convertir

        Returns:
            AFD: AFD equivalente
        """
        if not isinstance(afnd, AFND):
            raise ValueError("El input debe ser un AFND")

        # Reiniciar estructuras
        self.tabla_afnd = {}
        self.tabla_afd = {}
        self.mapeo_estados = {}
        self.estados_procesados = set()
        self.historial = []

        # Paso 1: Construir tabla del AFND
        self._construir_tabla_afnd(afnd)

        # Paso 2: Generar tabla del AFD
        self._generar_tabla_afd(afnd)

        # Paso 3: Optimizar eliminando estados inútiles
        self._optimizar_tabla_afd(afnd)

        # Paso 4: Construir AFD desde la tabla optimizada
        return self._construir_afd_desde_tabla(afnd)

    def _construir_tabla_afnd(self, afnd):
        """Construye la representación tabular del AFND eliminando estados inútiles."""
        self.historial.append("=== TABLA DE TRANSICIONES ORIGINAL SIN ESTADOS SUMIDERO ===")

        # Paso 1: Identificar estados que pueden alcanzar estados finales
        estados_utiles = set()
        for estado in afnd.estados:
            if self._puede_alcanzar_final({estado}, afnd):
                estados_utiles.add(estado)

        estados_inutiles = afnd.estados - estados_utiles

        # Paso 2: Crear tabla solo con estados útiles
        for estado in sorted(estados_utiles):
            self.tabla_afnd[estado] = {}
            for simbolo in sorted(afnd.alfabeto):
                if simbolo == '':  # Ignorar epsilon por ahora
                    continue

                # Obtener destinos para esta transición
                destinos = set()
                if (estado, simbolo) in afnd.transiciones:
                    trans = afnd.transiciones[(estado, simbolo)]
                    if isinstance(trans, set):
                        destinos = trans.copy()
                    else:
                        destinos = {trans}

                # Aplicar clausura epsilon y filtrar solo estados útiles
                destinos_con_epsilon = set()
                for destino in destinos:
                    clausura = afnd.clausura_epsilon({destino})
                    # Solo incluir estados que pueden alcanzar finales
                    destinos_con_epsilon.update(clausura.intersection(estados_utiles))

                self.tabla_afnd[estado][simbolo] = destinos_con_epsilon

        # Mostrar tabla construida
        self._agregar_tabla_a_historial(self.tabla_afnd, afnd.estados_finales, "AFND")
        if estados_inutiles:
            self.historial.append(f"Estados sumidero eliminados desde el AFND: {sorted(estados_inutiles)}")

    def _generar_tabla_afd(self, afnd):
        """Genera la tabla del AFD usando el algoritmo de construcción de subconjuntos."""
        self.historial.append("\n=== GENERACIÓN DE TABLA AFD ===")

        # Estado inicial: clausura epsilon del estado inicial del AFND
        estado_inicial_conjunto = afnd.clausura_epsilon({afnd.estado_inicial})
        estado_inicial_nombre = self._obtener_nombre_estado(estado_inicial_conjunto)

        # Cola de estados por procesar
        por_procesar = [estado_inicial_conjunto]
        self.estados_procesados = set()

        self.historial.append(f"Estado inicial AFD: {estado_inicial_nombre} = {sorted(estado_inicial_conjunto)}")

        while por_procesar:
            conjunto_actual = por_procesar.pop(0)
            conjunto_key = frozenset(conjunto_actual)

            if conjunto_key in self.estados_procesados:
                continue

            # Verificar si este conjunto puede alcanzar estados finales
            if not self._puede_alcanzar_final(conjunto_actual, afnd):
                self.historial.append(
                    f"Omitiendo conjunto {sorted(conjunto_actual)} - no puede alcanzar estados finales")
                continue

            self.estados_procesados.add(conjunto_key)
            nombre_estado = self._obtener_nombre_estado(conjunto_actual)

            # Agregar fila a la tabla del AFD
            self.tabla_afd[nombre_estado] = {}

            self.historial.append(f"\nProcesando estado {nombre_estado} = {sorted(conjunto_actual)}")

            # Para cada símbolo del alfabeto
            for simbolo in sorted(afnd.alfabeto):
                if simbolo == '':
                    continue

                # Calcular el conjunto destino
                conjunto_destino = set()
                for estado_afnd in conjunto_actual:
                    if estado_afnd in self.tabla_afnd and simbolo in self.tabla_afnd[estado_afnd]:
                        conjunto_destino.update(self.tabla_afnd[estado_afnd][simbolo])

                if conjunto_destino:
                    # Verificar si el conjunto destino puede alcanzar estados finales
                    if self._puede_alcanzar_final(conjunto_destino, afnd):
                        nombre_destino = self._obtener_nombre_estado(conjunto_destino)
                        self.tabla_afd[nombre_estado][simbolo] = nombre_destino

                        self.historial.append(f"  δ({nombre_estado}, {simbolo}) = {nombre_destino}")

                        # Agregar a la cola si no ha sido procesado
                        conjunto_destino_key = frozenset(conjunto_destino)
                        if (conjunto_destino_key not in self.estados_procesados and
                                conjunto_destino not in por_procesar):
                            por_procesar.append(conjunto_destino)
                    else:
                        # El destino no puede alcanzar estados finales, no crear transición
                        self.tabla_afd[nombre_estado][simbolo] = None
                        self.historial.append(f"  δ({nombre_estado}, {simbolo}) = ∅ (destino inútil)")
                else:
                    # No hay transición (va al estado sumidero implícito)
                    self.tabla_afd[nombre_estado][simbolo] = None

        # Mostrar tabla generada
        estados_finales_afd = self._calcular_estados_finales_afd(afnd)

    def _optimizar_tabla_afd(self, afnd):
        """Elimina estados inútiles de la tabla del AFD."""
        self.historial.append("\n=== OPTIMIZACIÓN DE TABLA AFD ===")

        estados_finales_afd = self._calcular_estados_finales_afd(afnd)
        estados_a_eliminar = set()

        # Identificar estados sumidero no aceptadores
        for estado in self.tabla_afd:
            if estado not in estados_finales_afd:
                es_sumidero = True

                # Verificar si todas las transiciones van al mismo estado o son nulas
                for simbolo in afnd.alfabeto:
                    if simbolo == '':
                        continue
                    destino = self.tabla_afd[estado].get(simbolo)
                    if destino is not None and destino != estado:
                        es_sumidero = False
                        break

                if es_sumidero:
                    estados_a_eliminar.add(estado)

        # Eliminar estados sumidero
        if estados_a_eliminar:
            self.historial.append(f"Eliminando estados sumidero: {sorted(estados_a_eliminar)}")

            for estado in estados_a_eliminar:
                del self.tabla_afd[estado]

            # Actualizar transiciones que apuntan a estados eliminados
            for estado in self.tabla_afd:
                for simbolo in list(self.tabla_afd[estado].keys()):
                    destino = self.tabla_afd[estado][simbolo]
                    if destino in estados_a_eliminar:
                        self.tabla_afd[estado][simbolo] = None  # Transición al vacío

        # Mostrar tabla optimizada
        if estados_a_eliminar:
            self.historial.append("\nTabla AFD optimizada:")
            estados_finales_optimizados = estados_finales_afd - estados_a_eliminar
            self._agregar_tabla_a_historial(self.tabla_afd, estados_finales_optimizados, "AFD Optimizado")

    def _construir_afd_desde_tabla(self, afnd):
        """Construye el objeto AFD desde la tabla optimizada."""
        # Estados del AFD
        estados_afd = set(self.tabla_afd.keys())

        # Estado inicial
        conjunto_inicial = afnd.clausura_epsilon({afnd.estado_inicial})
        estado_inicial_afd = self._obtener_nombre_estado(conjunto_inicial)

        # Estados finales
        estados_finales_afd = set()
        for estado_afd in estados_afd:
            conjunto_afnd = self._obtener_conjunto_afnd(estado_afd)
            if any(estado in afnd.estados_finales for estado in conjunto_afnd):
                estados_finales_afd.add(estado_afd)

        # Transiciones
        transiciones_afd = {}
        for estado in self.tabla_afd:
            for simbolo, destino in self.tabla_afd[estado].items():
                if destino is not None:  # Ignorar transiciones al vacío
                    transiciones_afd[(estado, simbolo)] = destino

        # Crear AFD
        afd = AFD(
            estados=estados_afd,
            alfabeto=afnd.alfabeto - {''},
            estado_inicial=estado_inicial_afd,
            estados_finales=estados_finales_afd,
            transiciones=transiciones_afd,
            descripcion=f"AFD convertido desde AFND - {getattr(afnd, 'descripcion', '')}"
        )

        # Personalización del historial para el reporte
        self.historial.append("\n=== TABLA DE TRANSICIONES DEL AFD CONSTRUIDO ===")
        self._agregar_tabla_a_historial(self.tabla_afd, estados_finales_afd, "AFD Construido")
        self.historial.append(f"Estados: {len(estados_afd)}")
        self.historial.append(f"Transiciones: {len(transiciones_afd)}")

        return afd

    def _obtener_nombre_estado(self, conjunto_estados):
        """Obtiene el nombre para un conjunto de estados."""
        conjunto_key = frozenset(conjunto_estados)

        if conjunto_key not in self.mapeo_estados:
            if len(conjunto_estados) == 1:
                nombre = list(conjunto_estados)[0]
            else:
                estados_ordenados = sorted(str(e) for e in conjunto_estados)
                nombre = "{" + ",".join(estados_ordenados) + "}"
            self.mapeo_estados[conjunto_key] = nombre

        return self.mapeo_estados[conjunto_key]

    def _obtener_conjunto_afnd(self, nombre_estado_afd):
        """Obtiene el conjunto de estados AFND que representa un estado AFD."""
        for conjunto, nombre in self.mapeo_estados.items():
            if nombre == nombre_estado_afd:
                return set(conjunto)
        return {nombre_estado_afd}  # Si es un estado simple

    def _puede_alcanzar_final(self, conjunto_estados, afnd):
        """Verifica si un conjunto puede alcanzar estados finales."""
        # Si ya contiene estados finales, puede alcanzar
        if any(estado in afnd.estados_finales for estado in conjunto_estados):
            return True

        # BFS para verificar alcanzabilidad
        visitados = set()
        por_visitar = list(conjunto_estados)

        while por_visitar:
            estado = por_visitar.pop(0)

            if estado in visitados:
                continue
            visitados.add(estado)

            for simbolo in afnd.alfabeto:
                if simbolo == '':
                    continue

                if (estado, simbolo) in afnd.transiciones:
                    destinos = afnd.transiciones[(estado, simbolo)]
                    if isinstance(destinos, set):
                        for destino in destinos:
                            if destino in afnd.estados_finales:
                                return True
                            if destino not in visitados:
                                por_visitar.append(destino)
                    else:
                        if destinos in afnd.estados_finales:
                            return True
                        if destinos not in visitados:
                            por_visitar.append(destinos)

        return False

    def _calcular_estados_finales_afd(self, afnd):
        """Calcula los estados finales del AFD."""
        estados_finales = set()

        for estado_afd in self.tabla_afd:
            conjunto_afnd = self._obtener_conjunto_afnd(estado_afd)
            if any(estado in afnd.estados_finales for estado in conjunto_afnd):
                estados_finales.add(estado_afd)

        return estados_finales

    def _agregar_tabla_a_historial(self, tabla, estados_finales, tipo):
        """Agrega una representación tabular al historial."""
        if not tabla:
            self.historial.append("(Tabla vacía)")
            return

        # Obtener símbolos ordenados
        simbolos = set()
        for estado_dict in tabla.values():
            simbolos.update(estado_dict.keys())
        simbolos = sorted(simbolos)

        # Calcular anchos de columnas
        estados_ordenados = sorted(tabla.keys(), key=str)
        ancho_estado = max(len(str(estado)) for estado in estados_ordenados + ["δ"])

        anchos_simbolos = []
        for simbolo in simbolos:
            ancho = len(str(simbolo))
            for estado in estados_ordenados:
                destino = tabla[estado].get(simbolo, "∅")
                if destino is None:
                    destino_str = "-"  # Transición eliminada (no apunta a ningún estado)
                elif isinstance(destino, set):
                    destino_str = "{" + ",".join(sorted(str(d) for d in destino)) + "}"
                else:
                    destino_str = str(destino)
                ancho = max(ancho, len(destino_str))
            anchos_simbolos.append(ancho)

        # Generar tabla
        separador = "+" + "-" * (ancho_estado + 2)
        for ancho in anchos_simbolos:
            separador += "+" + "-" * (ancho + 2)
        separador += "+" + "-" * 3 + "+"

        self.historial.append(separador)

        # Encabezado
        linea = f"| {'δ':^{ancho_estado}} "
        for i, simbolo in enumerate(simbolos):
            linea += f"| {simbolo:^{anchos_simbolos[i]}} "
        linea += "| F |"
        self.historial.append(linea)
        self.historial.append(separador)

        # Filas de estados
        for estado in estados_ordenados:
            linea = f"| {estado:^{ancho_estado}} "

            for i, simbolo in enumerate(simbolos):
                destino = tabla[estado].get(simbolo, "∅")
                if destino is None:
                    destino_str = "-"  # Transición eliminada (no apunta a ningún estado)
                elif isinstance(destino, set):
                    destino_str = "{" + ",".join(sorted(str(d) for d in destino)) + "}"
                else:
                    destino_str = str(destino)
                linea += f"| {destino_str:^{anchos_simbolos[i]}} "

            es_final = "1" if estado in estados_finales else "0"
            linea += f"| {es_final} |"
            self.historial.append(linea)

        self.historial.append(separador)

    def obtener_historial(self):
        """Retorna el historial completo del proceso."""
        return self.historial.copy()

    def generar_reporte(self, afnd, afd):
        """Genera un reporte completo de la conversión tabular."""
        reporte = []
        reporte.append("=" * 69)
        reporte.append("REPORTE DE ELIMINACIÓN DE NO DETERMINISMO")
        reporte.append("=" * 69)
        reporte.append("")
        reporte.append("RESUMEN:")
        reporte.append(f"  • Estados AFND: {len(afnd.estados)}")
        reporte.append(f"  • Estados AFD: {len(afd.estados)}")
        reporte.append("")
        reporte.append("PROCESO DETALLADO:")
        reporte.append("-" * 50)
        for linea in self.historial:
            if "=== OPTIMIZACIÓN DE TABLA AFD ===" in linea:
                continue
            if "=== AFD CONSTRUIDO ===" in linea:
                reporte.append(linea)
                continue
            if linea.startswith("Estados:") or linea.startswith("Transiciones:"):
                continue
            if "Estados:" in linea and "reducción" in linea:
                partes = linea.split("(")
                reporte.append(partes[0].strip())
                continue
            reporte.append(linea)
        return "\n".join(reporte)
