"""
Módulo para convertir Autómatas Finitos No Deterministas (AFND) a
Autómatas Finitos Deterministas (AFD) utilizando el algoritmo de construcción de subconjuntos.
"""

from .automata import AFD, AFND


class ConversorAFNDaAFD:
    """Clase para convertir AFND a AFD usando el algoritmo de construcción de subconjuntos."""

    def __init__(self):
        self.estados_AFD = {}  # Mapeo de conjuntos de estados AFND -> estado AFD
        self.contador_estados = 0
        self.historial_conversion = []  # Para documentar el proceso

    def convertir(self, afnd):
        """
        Convierte un AFND a AFD equivalente.

        Args:
            afnd: Instancia de AFND a convertir

        Returns:
            AFD: Autómata finito determinista equivalente
        """
        if not isinstance(afnd, AFND):
            raise ValueError("El input debe ser un AFND")

        # Reiniciar variables de conversión
        self.estados_AFD = {}
        self.contador_estados = 0
        self.historial_conversion = []

        # Paso 1: Calcular el estado inicial del AFD
        estado_inicial_afnd = {afnd.estado_inicial}
        clausura_inicial = afnd.clausura_epsilon(estado_inicial_afnd)
        estado_inicial_afd = self._obtener_nombre_estado_afd(clausura_inicial)

        # Estructuras para el AFD
        estados_afd = set()
        transiciones_afd = {}
        estados_finales_afd = set()
        estados_por_procesar = [clausura_inicial]
        estados_procesados = set()

        self.historial_conversion.append(f"Estado inicial AFD: {estado_inicial_afd} = {clausura_inicial}")

        # Paso 2: Construcción de subconjuntos
        while estados_por_procesar:
            conjunto_actual = estados_por_procesar.pop(0)

            # Convertir conjunto a tupla para usarlo como clave
            clave_conjunto = frozenset(conjunto_actual)
            if clave_conjunto in estados_procesados:
                continue

            estados_procesados.add(clave_conjunto)
            nombre_estado_afd = self._obtener_nombre_estado_afd(conjunto_actual)
            estados_afd.add(nombre_estado_afd)

            # Verificar si es estado final
            if any(estado in afnd.estados_finales for estado in conjunto_actual):
                estados_finales_afd.add(nombre_estado_afd)

            self.historial_conversion.append(f"Procesando estado AFD {nombre_estado_afd} = {conjunto_actual}")

            # Para cada símbolo del alfabeto
            for simbolo in afnd.alfabeto:
                if simbolo == '':  # Ignorar transiciones epsilon
                    continue

                # Calcular el conjunto de estados alcanzables
                conjunto_destino = set()
                for estado in conjunto_actual:
                    if (estado, simbolo) in afnd.transiciones:
                        destinos = afnd.transiciones[(estado, simbolo)]
                        if isinstance(destinos, set):
                            conjunto_destino.update(destinos)
                        else:
                            conjunto_destino.add(destinos)

                if conjunto_destino:
                    # Aplicar clausura epsilon
                    clausura_destino = afnd.clausura_epsilon(conjunto_destino)
                    nombre_destino_afd = self._obtener_nombre_estado_afd(clausura_destino)

                    # Agregar transición al AFD
                    transiciones_afd[(nombre_estado_afd, simbolo)] = nombre_destino_afd

                    self.historial_conversion.append(
                        f"  δ({nombre_estado_afd}, {simbolo}) = {nombre_destino_afd} = {clausura_destino}"
                    )

                    # Agregar nuevo estado para procesar si no ha sido procesado
                    clave_destino = frozenset(clausura_destino)
                    if clave_destino not in estados_procesados and clausura_destino not in estados_por_procesar:
                        estados_por_procesar.append(clausura_destino)

        # Crear el AFD resultante
        afd_resultado = AFD(
            estados=estados_afd,
            alfabeto=afnd.alfabeto - {''},  # Remover epsilon si existe
            estado_inicial=estado_inicial_afd,
            estados_finales=estados_finales_afd,
            transiciones=transiciones_afd,
            descripcion=getattr(afnd, 'descripcion', None)  # Mantener descripción del original
        )

        self.historial_conversion.append(f"Conversión completada. AFD con {len(estados_afd)} estados.")

        return afd_resultado

    def _obtener_nombre_estado_afd(self, conjunto_estados):
        """
        Obtiene o crea un nombre para un estado del AFD basado en un conjunto de estados del AFND.

        Args:
            conjunto_estados: conjunto de estados del AFND

        Returns:
            str: nombre del estado en el AFD
        """
        clave = frozenset(conjunto_estados)

        if clave not in self.estados_AFD:
            # Crear nombre basado en los estados del conjunto
            if len(conjunto_estados) == 1:
                nombre = list(conjunto_estados)[0]
            else:
                estados_ordenados = sorted([str(e) for e in conjunto_estados])
                nombre = "{" + ",".join(estados_ordenados) + "}"

            self.estados_AFD[clave] = nombre

        return self.estados_AFD[clave]

    def obtener_historial_conversion(self):
        """
        Retorna el historial del proceso de conversión para documentación.

        Returns:
            list: Lista de strings describiendo cada paso de la conversión
        """
        return self.historial_conversion.copy()

    def generar_reporte_conversion(self, afnd, afd):
        """
        Genera un reporte detallado de la conversión.

        Args:
            afnd: AFND original
            afd: AFD resultante

        Returns:
            str: Reporte de la conversión
        """
        reporte = []
        reporte.append("=== REPORTE DE CONVERSIÓN AFND → AFD ===")
        reporte.append("")
        reporte.append("AUTÓMATA ORIGINAL (AFND):")
        reporte.append(f"  Estados: {afnd.estados}")
        reporte.append(f"  Alfabeto: {afnd.alfabeto}")
        reporte.append(f"  Estado inicial: {afnd.estado_inicial}")
        reporte.append(f"  Estados finales: {afnd.estados_finales}")
        reporte.append(f"  Número de transiciones: {len(afnd.transiciones)}")
        reporte.append("")

        reporte.append("AUTÓMATA RESULTANTE (AFD):")
        reporte.append(f"  Estados: {afd.estados}")
        reporte.append(f"  Alfabeto: {afd.alfabeto}")
        reporte.append(f"  Estado inicial: {afd.estado_inicial}")
        reporte.append(f"  Estados finales: {afd.estados_finales}")
        reporte.append(f"  Número de transiciones: {len(afd.transiciones)}")
        reporte.append("")

        reporte.append("PROCESO DE CONVERSIÓN:")
        for paso in self.historial_conversion:
            reporte.append(f"  {paso}")

        reporte.append("")
        reporte.append("ANÁLISIS:")
        reporte.append(f"  Reducción de estados: {len(afnd.estados)} → {len(afd.estados)}")
        reporte.append(f"  Cambio en transiciones: {len(afnd.transiciones)} → {len(afd.transiciones)}")

        return "\n".join(reporte)
