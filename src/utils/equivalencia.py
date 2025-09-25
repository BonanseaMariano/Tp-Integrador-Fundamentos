def son_afd_equivalentes(afd1, afd2):
    """
    Compara dos AFD minimizados para verificar si son equivalentes estructuralmente.
    Retorna True si son equivalentes, False en caso contrario.
    """
    return (
            set(afd1.estados) == set(afd2.estados) and
            set(afd1.alfabeto) == set(afd2.alfabeto) and
            afd1.estado_inicial == afd2.estado_inicial and
            set(afd1.estados_finales) == set(afd2.estados_finales) and
            afd1.transiciones == afd2.transiciones
    )


def _hashable_state(state):
    # Convierte un set a frozenset si es necesario, si no lo deja igual
    if isinstance(state, set):
        return frozenset(state)
    return state


def equivalencia_afd_producto(afd1, afd2):
    """
    Verifica equivalencia de dos AFD usando el método del autómata producto.
    Retorna True si son equivalentes, False si existe alguna cadena que distingue ambos lenguajes.
    """
    if set(afd1.alfabeto) != set(afd2.alfabeto):
        return False  # No pueden ser equivalentes si el alfabeto difiere
    alfabeto = list(afd1.alfabeto)
    inicial = (_hashable_state(afd1.estado_inicial), _hashable_state(afd2.estado_inicial))
    visitados = set()
    cola = [inicial]
    while cola:
        estado1, estado2 = cola.pop(0)
        h_estado1 = _hashable_state(estado1)
        h_estado2 = _hashable_state(estado2)
        if (h_estado1, h_estado2) in visitados:
            continue
        visitados.add((h_estado1, h_estado2))
        es_final1 = h_estado1 in set(map(_hashable_state, afd1.estados_finales))
        es_final2 = h_estado2 in set(map(_hashable_state, afd2.estados_finales))
        if es_final1 != es_final2:
            return False  # Hay una cadena que distingue ambos lenguajes
        for simbolo in alfabeto:
            dest1 = afd1.transiciones.get((h_estado1, simbolo))
            dest2 = afd2.transiciones.get((h_estado2, simbolo))
            if dest1 is not None and dest2 is not None:
                cola.append((_hashable_state(dest1), _hashable_state(dest2)))
    return True  # No se encontró ninguna diferencia
