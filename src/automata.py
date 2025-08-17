"""
Módulo para la representación de autómatas finitos.

Este módulo contiene las clases necesarias para representar:
- Autómatas Finitos Deterministas (AFD)
- Autómatas Finitos No Deterministas (AFND)
"""

class Estado:
    """Representa un estado del autómata."""

    def __init__(self, nombre, es_final=False):
        self.nombre = nombre
        self.es_final = es_final

    def __str__(self):
        return f"Estado({self.nombre}, final={self.es_final})"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if isinstance(other, Estado):
            return self.nombre == other.nombre
        return False

    def __hash__(self):
        return hash(self.nombre)


class Automata:
    """Clase base para representar un autómata finito."""

    def __init__(self, estados, alfabeto, estado_inicial, estados_finales, transiciones, descripcion=None):
        """
        Inicializa un autómata.

        Args:
            estados: conjunto de estados
            alfabeto: conjunto de símbolos del alfabeto
            estado_inicial: estado inicial
            estados_finales: conjunto de estados finales
            transiciones: diccionario de transiciones
            descripcion: descripción opcional del lenguaje que acepta
        """
        self.estados = set(estados)
        self.alfabeto = set(alfabeto)
        self.estado_inicial = estado_inicial
        self.estados_finales = set(estados_finales)
        self.transiciones = transiciones
        self.descripcion = descripcion

    def validar_cadena(self, cadena):
        """Valida si una cadena es aceptada por el autómata."""
        raise NotImplementedError("Debe implementarse en las clases derivadas")

    def obtener_estados_alcanzables(self):
        """Retorna el conjunto de estados alcanzables desde el estado inicial."""
        alcanzables = set()
        por_visitar = [self.estado_inicial]

        while por_visitar:
            estado_actual = por_visitar.pop()
            if estado_actual not in alcanzables:
                alcanzables.add(estado_actual)

                # Agregar estados alcanzables desde este estado
                for simbolo in self.alfabeto:
                    if (estado_actual, simbolo) in self.transiciones:
                        destinos = self.transiciones[(estado_actual, simbolo)]
                        if isinstance(destinos, set):
                            for destino in destinos:
                                if destino not in alcanzables:
                                    por_visitar.append(destino)
                        else:
                            if destinos not in alcanzables:
                                por_visitar.append(destinos)

        return alcanzables

    def __str__(self):
        return f"Autómata(estados={len(self.estados)}, alfabeto={self.alfabeto})"


class AFD(Automata):
    """Autómata Finito Determinista."""

    def validar_cadena(self, cadena):
        """
        Valida si una cadena es aceptada por el AFD.

        Args:
            cadena: string a validar

        Returns:
            bool: True si la cadena es aceptada, False en caso contrario
        """
        estado_actual = self.estado_inicial

        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False

            if (estado_actual, simbolo) in self.transiciones:
                estado_actual = self.transiciones[(estado_actual, simbolo)]
            else:
                return False

        return estado_actual in self.estados_finales


class AFND(Automata):
    """Autómata Finito No Determinista."""

    def validar_cadena(self, cadena):
        """
        Valida si una cadena es aceptada por el AFND.

        Args:
            cadena: string a validar

        Returns:
            bool: True si la cadena es aceptada, False en caso contrario
        """
        estados_actuales = {self.estado_inicial}

        # Procesar cada símbolo de la cadena
        for simbolo in cadena:
            if simbolo not in self.alfabeto:
                return False

            nuevos_estados = set()
            for estado in estados_actuales:
                if (estado, simbolo) in self.transiciones:
                    destinos = self.transiciones[(estado, simbolo)]
                    if isinstance(destinos, set):
                        nuevos_estados.update(destinos)
                    else:
                        nuevos_estados.add(destinos)

            estados_actuales = nuevos_estados

            # Si no hay estados alcanzables, la cadena es rechazada
            if not estados_actuales:
                return False

        # Verificar si alguno de los estados finales está entre los estados actuales
        return bool(estados_actuales.intersection(self.estados_finales))

    def clausura_epsilon(self, estados):
        """
        Calcula la clausura-ε de un conjunto de estados.

        Args:
            estados: conjunto de estados

        Returns:
            set: clausura-ε de los estados dados
        """
        clausura = set(estados)
        por_procesar = list(estados)

        while por_procesar:
            estado = por_procesar.pop()
            # Buscar transiciones epsilon (representadas como '')
            if (estado, '') in self.transiciones:
                destinos = self.transiciones[(estado, '')]
                if isinstance(destinos, set):
                    for destino in destinos:
                        if destino not in clausura:
                            clausura.add(destino)
                            por_procesar.append(destino)
                else:
                    if destinos not in clausura:
                        clausura.add(destinos)
                        por_procesar.append(destinos)

        return clausura
