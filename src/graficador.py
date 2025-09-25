"""
Módulo para generar gráficos de autómatas finitos usando Graphviz.

Permite visualizar AFD y AFND con diferentes estilos y opciones de configuración.
Incluye métodos para graficar autómatas individuales, comparaciones y procesos de minimización.
"""

try:
    import graphviz

    GRAPHVIZ_DISPONIBLE = True
except ImportError:
    GRAPHVIZ_DISPONIBLE = False

import os
from .automata import AFD, AFND


class GraficadorAutomatas:
    """
    Clase para generar visualizaciones de autómatas finitos (AFD y AFND) usando Graphviz.
    Permite personalizar estilos, exportar en varios formatos y comparar autómatas.
    """

    def __init__(self):
        if not GRAPHVIZ_DISPONIBLE:
            raise ImportError(
                "Graphviz no está instalado. Instálelo con: pip install graphviz\n"
                "También necesita el software Graphviz: https://graphviz.org/download/"
            )

        # Configuración por defecto
        self.configuracion = {
            'formato': 'png',
            'motor': 'dot',
            'dpi': '300',
            'tamaño_nodo': '0.8',
            'color_nodo_normal': 'lightblue',
            'color_nodo_inicial': 'lightgreen',
            'color_nodo_final': 'lightcoral',
            'color_nodo_inicial_final': 'gold',
            'color_transicion': 'black',
            'grosor_transicion': '1.0',
            'fuente': 'Arial',
            'tamaño_fuente': '12'
        }

    def verificar_dependencias(self):
        """
        Verifica si las dependencias necesarias están instaladas.

        Returns:
            tuple: (graphviz_instalado, ejecutable_encontrado)
        """
        if not GRAPHVIZ_DISPONIBLE:
            return False, False

        try:
            # Intentar crear un gráfico simple para verificar el ejecutable
            dot = graphviz.Digraph()
            dot.node('test')
            dot.render('test_graphviz', cleanup=True, format='png')
            os.remove('test_graphviz.png') if os.path.exists('test_graphviz.png') else None
            return True, True
        except Exception:
            return True, False

    def configurar_estilo(self, **kwargs):
        """
        Configura el estilo de los gráficos generados.

        Args:
            formato (str): Formato de salida ('png', 'pdf', 'svg', etc.).
            motor (str): Motor de renderizado ('dot', 'neato', etc.).
            dpi (str): Resolución en DPI.
            color_nodo_normal (str): Color de nodos normales.
            color_nodo_inicial (str): Color del nodo inicial.
            color_nodo_final (str): Color de nodos finales.
            color_nodo_inicial_final (str): Color si es inicial y final.
            ...otros parámetros de configuración.
        """
        self.configuracion.update(kwargs)

    def generar_grafico(self, automata, nombre_archivo, directorio="", incluir_titulo=True):
        """
        Genera un gráfico visual del autómata especificado y lo guarda en el formato elegido.

        Args:
            automata: AFD o AFND a graficar.
            nombre_archivo (str): Nombre base del archivo de salida.
            directorio (str): Carpeta donde guardar el archivo.
            incluir_titulo (bool): Si se incluye un título en el gráfico.
        Returns:
            str: Ruta del archivo generado.
        """
        if not GRAPHVIZ_DISPONIBLE:
            raise ImportError("Graphviz no está disponible")

        # Crear directorio si no existe
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        # Configurar el gráfico
        dot = graphviz.Digraph(
            name=nombre_archivo,
            engine=self.configuracion['motor'],
            format=self.configuracion['formato']
        )

        # Configuración global del gráfico
        dot.attr(
            dpi=self.configuracion['dpi'],
            fontname=self.configuracion['fuente'],
            fontsize=self.configuracion['tamaño_fuente'],
            rankdir='LR'  # Izquierda a derecha
        )

        # Configuración de nodos por defecto
        dot.attr('node',
                 shape='circle',
                 style='filled',
                 fontname=self.configuracion['fuente'],
                 fontsize=self.configuracion['tamaño_fuente'],
                 width=self.configuracion['tamaño_nodo'],
                 height=self.configuracion['tamaño_nodo'])

        # Configuración de transiciones por defecto
        dot.attr('edge',
                 fontname=self.configuracion['fuente'],
                 fontsize=str(int(self.configuracion['tamaño_fuente']) - 2),
                 color=self.configuracion['color_transicion'],
                 penwidth=self.configuracion['grosor_transicion'])

        # Título del gráfico
        if incluir_titulo:
            tipo = "AFD" if isinstance(automata, AFD) else "AFND"
            titulo = f"{tipo}"
            if hasattr(automata, 'descripcion') and automata.descripcion:
                titulo += f"\\n{automata.descripcion}"

            dot.attr(label=titulo, labelloc='t', fontsize='16')

        # Nodo invisible para la flecha de inicio
        dot.node('__start', '', shape='none', width='0', height='0')

        # Agregar estados
        for estado in automata.estados:
            es_inicial = (estado == automata.estado_inicial)
            es_final = (estado in automata.estados_finales)

            # Determinar color del nodo
            if es_inicial and es_final:
                color = self.configuracion['color_nodo_inicial_final']
            elif es_inicial:
                color = self.configuracion['color_nodo_inicial']
            elif es_final:
                color = self.configuracion['color_nodo_final']
            else:
                color = self.configuracion['color_nodo_normal']

            # Determinar forma del nodo (doble círculo para finales)
            forma = 'doublecircle' if es_final else 'circle'

            dot.node(str(estado), str(estado), shape=forma, fillcolor=color)

        # Flecha al estado inicial
        dot.edge('__start', str(automata.estado_inicial))

        # Agregar transiciones
        transiciones_agrupadas = self._agrupar_transiciones(automata.transiciones)

        for (origen, destino), simbolos in transiciones_agrupadas.items():
            etiqueta = ', '.join(sorted(simbolos)) if simbolos != [''] else 'ε'
            dot.edge(str(origen), str(destino), label=etiqueta)

        # Generar archivo
        ruta_completa = os.path.join(directorio, nombre_archivo) if directorio else nombre_archivo
        archivo_generado = dot.render(ruta_completa, cleanup=True)

        return archivo_generado

    def generar_comparacion(self, automata_original, automata_procesado,
                            nombre_archivo, directorio="",
                            titulo_original="Original", titulo_procesado="Procesado"):
        """
        Genera un gráfico comparativo de dos autómatas lado a lado.

        Args:
            automata_original: primer autómata a comparar
            automata_procesado: segundo autómata a comparar
            nombre_archivo: nombre del archivo
            directorio: directorio de salida
            titulo_original: título del primer autómata
            titulo_procesado: título del segundo autómata

        Returns:
            str: ruta del archivo generado
        """
        if not GRAPHVIZ_DISPONIBLE:
            raise ImportError("Graphviz no está disponible")

        # Crear directorio si no existe
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        # Crear gráfico principal con subgráficos
        dot = graphviz.Digraph(
            name=nombre_archivo,
            engine=self.configuracion['motor'],
            format=self.configuracion['formato']
        )

        dot.attr(rankdir='LR', fontname=self.configuracion['fuente'])

        # Subgráfico para el autómata original
        with dot.subgraph(name='cluster_0') as sub1:
            sub1.attr(label=titulo_original, fontsize='14', style='dashed')
            self._agregar_automata_a_subgrafico(sub1, automata_original, prefijo='orig_')

        # Subgráfico para el autómata procesado
        with dot.subgraph(name='cluster_1') as sub2:
            sub2.attr(label=titulo_procesado, fontsize='14', style='dashed')
            self._agregar_automata_a_subgrafico(sub2, automata_procesado, prefijo='proc_')

        # Generar archivo
        ruta_completa = os.path.join(directorio, nombre_archivo) if directorio else nombre_archivo
        archivo_generado = dot.render(ruta_completa, cleanup=True)

        return archivo_generado

    def generar_proceso_minimizacion(self, minimizador, automata_original, automata_minimizado,
                                     nombre_archivo, directorio=""):
        """
        Genera un gráfico que muestra el proceso de minimización paso a paso.

        Args:
            minimizador: instancia de MinimizadorAFD con historial
            automata_original: AFD original
            automata_minimizado: AFD minimizado
            nombre_archivo: nombre del archivo
            directorio: directorio de salida

        Returns:
            str: ruta del archivo generado
        """
        if not GRAPHVIZ_DISPONIBLE:
            raise ImportError("Graphviz no está disponible")

        # Crear directorio si no existe
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio, exist_ok=True)

        dot = graphviz.Digraph(
            name=nombre_archivo,
            engine='dot',
            format=self.configuracion['formato']
        )

        dot.attr(rankdir='TB', fontname=self.configuracion['fuente'])
        dot.attr(label='Proceso de Minimización', labelloc='t', fontsize='16')

        # Agregar información del proceso
        info_nodos = []
        info_nodos.append(f"Estados originales: {len(automata_original.estados)}")
        info_nodos.append(f"Estados minimizados: {len(automata_minimizado.estados)}")

        if hasattr(minimizador, 'historial_minimizacion'):
            for i, paso in enumerate(minimizador.historial_minimizacion[:5]):  # Limitar a 5 pasos
                info_nodos.append(f"Paso {i + 1}: {paso}")

        # Crear tabla con información
        tabla_html = '<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0">'
        for info in info_nodos:
            tabla_html += f'<TR><TD ALIGN="LEFT">{info}</TD></TR>'
        tabla_html += '</TABLE>'

        dot.node('info', f'<{tabla_html}>', shape='plaintext')

        # Generar comparación lado a lado
        with dot.subgraph(name='cluster_orig') as sub1:
            sub1.attr(label='AFD Original', fontsize='12')
            self._agregar_automata_a_subgrafico(sub1, automata_original, prefijo='orig_')

        with dot.subgraph(name='cluster_min') as sub2:
            sub2.attr(label='AFD Minimizado', fontsize='12')
            self._agregar_automata_a_subgrafico(sub2, automata_minimizado, prefijo='min_')

        # Generar archivo
        ruta_completa = os.path.join(directorio, nombre_archivo) if directorio else nombre_archivo
        archivo_generado = dot.render(ruta_completa, cleanup=True)

        return archivo_generado

    def _agrupar_transiciones(self, transiciones):
        """
        Agrupa transiciones por origen y destino para evitar múltiples flechas.

        Args:
            transiciones: diccionario de transiciones del autómata

        Returns:
            dict: transiciones agrupadas por (origen, destino) -> [símbolos]
        """
        agrupadas = {}

        for (origen, simbolo), destino in transiciones.items():
            if isinstance(destino, set):
                # AFND: múltiples destinos
                for dest in destino:
                    clave = (origen, dest)
                    if clave not in agrupadas:
                        agrupadas[clave] = []
                    agrupadas[clave].append(simbolo)
            else:
                # AFD: un solo destino
                clave = (origen, destino)
                if clave not in agrupadas:
                    agrupadas[clave] = []
                agrupadas[clave].append(simbolo)

        return agrupadas

    def _agregar_automata_a_subgrafico(self, subgrafico, automata, prefijo=''):
        """
        Agrega un autómata a un subgráfico específico.

        Args:
            subgrafico: subgráfico de graphviz
            automata: autómata a agregar
            prefijo: prefijo para evitar conflictos de nombres
        """
        # Configurar subgráfico
        subgrafico.attr('node',
                        shape='circle',
                        style='filled',
                        fontname=self.configuracion['fuente'],
                        fontsize=self.configuracion['tamaño_fuente'],
                        width=self.configuracion['tamaño_nodo'])

        subgrafico.attr('edge',
                        fontname=self.configuracion['fuente'],
                        fontsize=str(int(self.configuracion['tamaño_fuente']) - 2))

        # Nodo de inicio
        subgrafico.node(f'{prefijo}__start', '', shape='none', width='0', height='0')

        # Agregar estados
        for estado in automata.estados:
            es_inicial = (estado == automata.estado_inicial)
            es_final = (estado in automata.estados_finales)

            # Determinar color y forma
            if es_inicial and es_final:
                color = self.configuracion['color_nodo_inicial_final']
            elif es_inicial:
                color = self.configuracion['color_nodo_inicial']
            elif es_final:
                color = self.configuracion['color_nodo_final']
            else:
                color = self.configuracion['color_nodo_normal']

            forma = 'doublecircle' if es_final else 'circle'

            subgrafico.node(f'{prefijo}{estado}', str(estado),
                            shape=forma, fillcolor=color)

        # Flecha inicial
        subgrafico.edge(f'{prefijo}__start', f'{prefijo}{automata.estado_inicial}')

        # Transiciones
        transiciones_agrupadas = self._agrupar_transiciones(automata.transiciones)

        for (origen, destino), simbolos in transiciones_agrupadas.items():
            etiqueta = ', '.join(sorted(simbolos)) if simbolos != [''] else 'ε'
            subgrafico.edge(f'{prefijo}{origen}', f'{prefijo}{destino}', label=etiqueta)

    def exportar_multiples_formatos(self, automata, nombre_base, directorio="",
                                    formatos=['png', 'pdf', 'svg']):
        """
        Exporta el mismo autómata en múltiples formatos.

        Args:
            automata: autómata a exportar
            nombre_base: nombre base del archivo
            directorio: directorio de salida
            formatos: lista de formatos a generar

        Returns:
            list: lista de archivos generados
        """
        archivos_generados = []
        formato_original = self.configuracion['formato']

        for formato in formatos:
            self.configuracion['formato'] = formato
            try:
                archivo = self.generar_grafico(automata, f"{nombre_base}_{formato}",
                                               directorio, incluir_titulo=True)
                archivos_generados.append(archivo)
            except Exception as e:
                print(f"⚠️ Error generando formato {formato}: {e}")

        # Restaurar formato original
        self.configuracion['formato'] = formato_original

        return archivos_generados


def verificar_instalacion():
    """
    Verifica si Graphviz está correctamente instalado.

    Returns:
        dict: información sobre la instalación
    """
    info = {
        'libreria_instalada': GRAPHVIZ_DISPONIBLE,
        'ejecutable_disponible': False,
        'version': None,
        'mensaje': ''
    }

    if not GRAPHVIZ_DISPONIBLE:
        info['mensaje'] = (
            "La librería graphviz no está instalada.\n"
            "Instálela con: pip install graphviz\n"
            "También necesita el software Graphviz: https://graphviz.org/download/"
        )
        return info

    try:
        # Verificar si el ejecutable está disponible
        dot = graphviz.Digraph()
        dot.node('test')
        dot.render('test_verificacion', cleanup=True, format='png')

        if os.path.exists('test_verificacion.png'):
            os.remove('test_verificacion.png')

        info['ejecutable_disponible'] = True
        info['mensaje'] = "✅ Graphviz está correctamente instalado y configurado"

        # Intentar obtener versión
        try:
            import subprocess
            resultado = subprocess.run(['dot', '-V'], capture_output=True, text=True, timeout=5)
            info['version'] = resultado.stderr.split()[4] if resultado.stderr else "desconocida"
        except:
            pass

    except Exception as e:
        info['mensaje'] = (
            f"❌ La librería graphviz está instalada pero el ejecutable no está disponible.\n"
            f"Error: {e}\n"
            f"Instale el software Graphviz desde: https://graphviz.org/download/\n"
            f"Y asegúrese de que esté en el PATH del sistema."
        )

    return info
