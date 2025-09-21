# Trabajo Práctico Integrador Fundamentos de Programación

### Alumno: Bonansea Camaño Mariano Nicolas

**Tema:** Eliminación de no determinismo y minimización de autómatas finitos

### Descripción

Este proyecto implementa algoritmos para:

1. Conversión de Autómatas Finitos No Deterministas (AFND) a Autómatas Finitos Deterministas (AFD)
2. Minimización de AFD mediante el algoritmo de partición
3. Validación de cadenas en autómatas (interactiva, individual y masiva)
4. Graficación visual de autómatas

### Estructura del Proyecto

```
├── src/
│   ├── __init__.py
│   ├── automata.py          # Clases para representar AFD y AFND
│   ├── conversor.py         # Conversión AFND → AFD (algoritmo tabular)
│   ├── minimizador.py       # Minimización de AFD
│   ├── graficador.py        # Generación de gráficos visuales
│   ├── manejador_archivos.py # Lectura/escritura de archivos
│   ├── core/
│   │   └── procesador.py    # Procesador central de operaciones
│   ├── interfaces/
│   │   ├── cli.py           # Interfaz de línea de comandos
│   │   └── ui.py            # Interfaz de usuario
│   └── utils/
│       └── logger.py        # Sistema de logging con iconos
├── ejemplos/                # Archivos de ejemplo
├── tests/                   # Casos de prueba
├── resultados/             # Directorio de salida (generado automáticamente)
├── main.py                 # Programa principal
├── Consignas.md           # Consignas del trabajo práctico
└── README.md              # Este archivo
```

### Instalación

1. Clona el repositorio
2. Crea un entorno virtual: `python -m venv .venv`
3. Activa el entorno virtual:
    - Windows: `.venv\Scripts\activate`
    - Linux/Mac: `source .venv/bin/activate`
4. Instala las dependencias: `pip install -r requirements.txt`
5. Instala Graphviz (software):
    - **Windows**: Descarga desde [graphviz.org](https://graphviz.org/download/) y agrega al PATH
    - **Linux**: `sudo apt-get install graphviz` (Ubuntu/Debian) o `sudo yum install graphviz` (CentOS/RHEL)
    - **macOS**: `brew install graphviz`

#### Verificar instalación de Graphviz

```python
from src.graficador import verificar_instalacion

print(verificar_instalacion())
```

### Uso

### Comandos disponibles

```bash
python main.py <archivo> [directorio_salida] [opciones]
```

**Argumentos posicionales:**

- `<archivo>`: Archivo del autómata (JSON o texto)
- `[directorio_salida]`: Directorio de salida para los resultados (por defecto: resultados)

**Opciones principales:**

- `-o`, `--output DIR`                 Directorio de salida para los resultados (sobrescribe el posicional)

**Opciones de procesamiento (excluyentes):**

- `-c`, `--convertir`                  Solo convertir AFND a AFD (sin minimizar)
- `-m`, `--minimizar`                  Solo minimizar el AFD (el archivo debe ser un AFD)
- `-v`, `--validar`                    Modo interactivo para validar cadenas
- `-s`, `--string CADENA`              Validar una cadena específica
- `--validar-archivo ARCHIVO_JSON`     Validar múltiples cadenas desde un archivo JSON con el autómata especificado

**Opciones de graficación:**

- `-g`, `--graficar`                   Generar gráficos del autómata y del proceso
- `--solo-graficar`                    Solo grafica el autómata proporcionado, sin procesamiento adicional
- `-f`, `--formatos FORMATO(S)`        Formatos de gráficos separados por comas (png,pdf,svg) (por defecto: png)

**Opciones de utilidad:**

- `-h`, `--help`                          Muestra la ayuda y sintaxis de uso
- `--verificar-graphviz`                  Verificar la instalación de Graphviz y salir
- `-r`, `--no-reportes`                   No generar reportes detallados
- `--verbose`                             Mostrar información detallada del proceso
- `--version`                             Muestra el número de versión del programa y sale

---

#### Ejemplos de uso

```bash
# Procesamiento completo (conversión + minimización)
python main.py ejemplos/TP1_Ej9a.json resultados/

# Solo conversión AFND → AFD
python main.py ejemplos/TP1_Ej9a.json -c

# Solo minimización de AFD
python main.py ejemplos/TP1_Ej9a.json -m

# Generar gráficos en varios formatos
python main.py ejemplos/TP1_Ej9a.json -g -f png,pdf,svg

# Validación interactiva de cadenas
python main.py ejemplos/TP1_Ej9a.json -v

# Validar una cadena específica
python main.py ejemplos/TP1_Ej9a.json -s "abba"

# Validar múltiples cadenas desde archivo JSON
python main.py ejemplos/TP1_Ej9a.json --validar-archivo ejemplos/cadenas_prueba.json

# Solo generar gráficos, sin procesamiento
python main.py ejemplos/TP1_Ej9a.json --solo-graficar
```

### Validación de Múltiples Cadenas

Funcionalidad para validar múltiples cadenas desde un archivo JSON:

#### Formato del archivo de cadenas:

```json
{
  "cadenas": [
    "",
    "a",
    "b",
    "aa",
    "ab",
    "ba",
    "bb"
  ]
}
```

#### Características:

- 📝 **Muestra la descripción** del autómata para mejor comprensión
- 📋 **Procesa todas las cadenas** automáticamente
- 📊 **Reporte detallado** con tabla organizada (ruta personalizable)

#### Uso:

```bash
python main.py automata.json --validar-archivo cadenas.json

# El sistema pregunta si generar reporte y dónde guardarlo:
# ¿Deseas guardar un reporte detallado? (s/N): s
# Ingresa la ruta y nombre del archivo (sin extensión): reportes/validacion_automata
# 📄 Reporte guardado: reportes/validacion_automata.txt
```

#### Formatos de archivo soportados

**JSON:**

```json
{
  "estados": [
    "q0",
    "q1",
    "q2"
  ],
  "alfabeto": [
    "a",
    "b"
  ],
  "estado_inicial": "q0",
  "estados_finales": [
    "q2"
  ],
  "transiciones": [
    {
      "origen": "q0",
      "simbolo": "a",
      "destino": "q1"
    },
    {
      "origen": "q1",
      "simbolo": "b",
      "destino": "q2"
    }
  ],
  "descripcion": "Autómata que acepta cadenas que terminan con 'ab'"
}
```

**Texto plano:**

```
ESTADOS: q0,q1,q2
ALFABETO: a,b
ESTADO_INICIAL: q0
ESTADOS_FINALES: q2
DESCRIPCION: Autómata que acepta cadenas que terminan con 'ab'
TRANSICIONES:
q0,a,q1
q1,b,q2
```

**Campos adicionales (opcionales):**

- **descripcion/DESCRIPCION**: Descripción del lenguaje que acepta el autómata o descripcion del mismo.

**Transiciones múltiples (AFND):**
Para autómatas no deterministas, se pueden especificar múltiples destinos:

```json
{
  "transiciones": [
    {
      "origen": "q0",
      "simbolo": "a",
      "destino": [
        "q1",
        "q2"
      ]
    }
  ]
}
```

En formato texto:

```
q0,a,q1,q2
```

### Funcionalidades

#### 1. Conversión AFND → AFD

- Manejo de transiciones epsilon
- Eliminación automática de estados inútiles durante la conversión
- Generación de reporte detallado del proceso

#### 2. Minimización de AFD

- Algoritmo de partición de estados equivalentes
- Eliminación de estados inalcanzables
- Análisis de reducción de estados
- Reporte detallado con análisis de particiones

#### 3. Validación de cadenas

- **Modo interactivo** para probar cadenas individualmente
- **Validación de cadena específica** desde línea de comandos
- **Validación masiva** desde archivo JSON con reporte detallado

#### 4. Graficación y Visualización

- Generación de diagramas visuales de autómatas
- Comparaciones lado a lado (original vs procesado)
- Múltiples formatos de salida (PNG, PDF, SVG)

## Módulo de Graficación

### Características del Graficador

El módulo `graficador.py` utiliza **Graphviz** para generar visualizaciones graficas de los autómatas finitos.

#### Funcionalidades principales:

1. **Gráficos comparativos**: Dos autómatas lado a lado
3. **Múltiples formatos**: PNG, PDF, SVG, etc.

#### Elementos visuales:

- 🟢 **Estado inicial**: Verde claro
- 🔴 **Estados finales**: Rojo claro (doble círculo)
- 🟡 **Estado inicial y final**: Dorado
- 🔵 **Estados normales**: Azul claro
- ➡️ **Transiciones**: Flechas etiquetadas con símbolos
- ε **Transiciones epsilon**: Etiquetadas como "ε"

---

## Funcionamiento de Algoritmos

## 1. Algoritmo de Conversión AFND → AFD

1. **Filtrado de estados útiles en el AFND**
    - Se identifican y conservan únicamente los estados que pueden alcanzar algún estado final, eliminando desde el
      inicio los estados sumidero o inalcanzables.
    - Se construye la tabla de transiciones del AFND solo con estos estados útiles, aplicando clausura epsilon para cada
      transición.

2. **Construcción de la tabla del AFD (algoritmo de subconjuntos)**
    - El estado inicial del AFD es la clausura epsilon del estado inicial del AFND:
      ```python
      estado_inicial_conjunto = afnd.clausura_epsilon({afnd.estado_inicial})
      estado_inicial_nombre = self._obtener_nombre_estado(estado_inicial_conjunto)
      por_procesar = [estado_inicial_conjunto]
      ```
    - Se utiliza una cola para iterar sobre conjuntos de estados AFND, generando nuevos estados AFD:
      ```python
      while por_procesar:
          conjunto_actual = por_procesar.pop(0)
          conjunto_key = frozenset(conjunto_actual)
          if conjunto_key in self.estados_procesados:
              continue
          ...
          self.estados_procesados.add(conjunto_key)
          nombre_estado = self._obtener_nombre_estado(conjunto_actual)
          self.tabla_afd[nombre_estado] = {}
      ```
    - Para cada símbolo del alfabeto, se calcula el conjunto destino aplicando las transiciones y la clausura epsilon:
      ```python
      for simbolo in sorted(afnd.alfabeto):
          if simbolo == '':
              continue
          conjunto_destino = set()
          for estado_afnd in conjunto_actual:
              if estado_afnd in self.tabla_afnd and simbolo in self.tabla_afnd[estado_afnd]:
                  conjunto_destino.update(self.tabla_afnd[estado_afnd][simbolo])
      ```
    - Antes de agregar una transición, se verifica si el conjunto destino puede alcanzar estados finales:
      ```python
      if conjunto_destino:
          if self._puede_alcanzar_final(conjunto_destino, afnd):
              nombre_destino = self._obtener_nombre_estado(conjunto_destino)
              self.tabla_afd[nombre_estado][simbolo] = nombre_destino
              ...
              if (conjunto_destino_key not in self.estados_procesados and
                      conjunto_destino not in por_procesar):
                  por_procesar.append(conjunto_destino)
          else:
              self.tabla_afd[nombre_estado][simbolo] = None
      ```
    - Se eliminan estados sumidero no aceptadores y se actualizan las transiciones que apuntan a ellos, evitando
      transiciones innecesarias.

3. **Construcción final del AFD**
    - Se crea el AFD con los estados, transiciones, estado inicial y estados finales obtenidos de la tabla optimizada:
      ```python
      afd = AFD(
          estados=estados_afd,
          alfabeto=afnd.alfabeto - {''},
          estado_inicial=estado_inicial_afd,
          estados_finales=estados_finales_afd,
          transiciones=transiciones_afd,
          descripcion=f"AFD convertido desde AFND - {getattr(afnd, 'descripcion', '')}"
      )
      ```

---

## 2. Algoritmo de Minimización de AFD

1. **Eliminación de estados inalcanzables**
    - Se identifican los estados alcanzables desde el estado inicial y se eliminan los que no lo son:
      ```python
      estados_alcanzables = afd.obtener_estados_alcanzables()
      afd_sin_inalcanzables = self._eliminar_estados_inalcanzables(afd, estados_alcanzables)
      ```

2. **Partición inicial (finales vs no finales)**
    - Se agrupan los estados en dos conjuntos: finales y no finales:
      ```python
      estados_finales = set(afd_sin_inalcanzables.estados_finales)
      estados_no_finales = afd_sin_inalcanzables.estados - estados_finales
      particion_actual = []
      if estados_no_finales:
          particion_actual.append(estados_no_finales)
      if estados_finales:
          particion_actual.append(estados_finales)
      ```

3. **Refinamiento de particiones**
    - Se repite el proceso de subdivisión de grupos hasta que no haya cambios, comparando las "firmas" de transiciones
      de cada estado:
      ```python
      while True:
          nueva_particion = self._refinar_particion(afd_sin_inalcanzables, particion_actual)
          if len(nueva_particion) == len(particion_actual) and self._particiones_equivalentes(particion_actual, nueva_particion):
              break
          particion_actual = nueva_particion
      ```
    - Cada grupo se divide según el destino de sus transiciones para cada símbolo del alfabeto:
      ```python
      for estado in grupo:
          firma = []
          for simbolo in sorted(afd.alfabeto):
              if (estado, simbolo) in afd.transiciones:
                  destino = afd.transiciones[(estado, simbolo)]
                  particion_destino = self._encontrar_grupo_de_estado(destino, particion_actual)
                  firma.append(particion_destino)
              else:
                  firma.append(-1)
          firmas.setdefault(tuple(firma), set()).add(estado)
      ```

4. **Construcción del AFD minimizado**
    - Cada grupo final de la partición se convierte en un estado del nuevo AFD, eligiendo un representante para cada
      grupo:
      ```python
      for i, grupo in enumerate(particion_final):
          representante = min(grupo, key=str)
          for estado in grupo:
              mapeo_estados[estado] = representante
      ```
    - Las transiciones y los estados finales se actualizan en función de los representantes:
      ```python
      for (origen, simbolo), destino in afd_original.transiciones.items():
          if origen in mapeo_estados and destino in mapeo_estados:
              origen_min = mapeo_estados[origen]
              destino_min = mapeo_estados[destino]
              transiciones_min[(origen_min, simbolo)] = destino_min
      ```

---

## 3. Validación de cadenas en autómatas

### Funcionamiento en AFD (Determinista)

El método recorre la cadena símbolo por símbolo, actualizando el estado actual según las transiciones definidas:

```python
estado_actual = self.estado_inicial
for simbolo in cadena:
    if simbolo not in self.alfabeto:
        return False
    if (estado_actual, simbolo) in self.transiciones:
        estado_actual = self.transiciones[(estado_actual, simbolo)]
    else:
        return False
return estado_actual in self.estados_finales
```

- Si algún símbolo no está en el alfabeto, la cadena se rechaza.
- Si falta una transición, la cadena se rechaza.
- Se acepta si el estado final es aceptador.

### Funcionamiento en AFND (No Determinista)

El método mantiene un conjunto de estados actuales y explora todas las transiciones posibles para cada símbolo:

```python
estados_actuales = {self.estado_inicial}
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
    if not estados_actuales:
        return False
return bool(estados_actuales.intersection(self.estados_finales))
```

- Se exploran todos los caminos posibles simultáneamente.
- Si en algún paso no hay estados alcanzables, la cadena se rechaza.
- Se acepta si al menos un estado final es alcanzado.

### Manejo de Clausura Epsilon

Para AFND, se calcula la clausura epsilon cuando es necesario, permitiendo alcanzar estados adicionales mediante
transiciones vacías:

```python
def clausura_epsilon(self, estados):
    clausura = set(estados)
    por_procesar = list(estados)
    while por_procesar:
        estado = por_procesar.pop()
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
```

- Se expande el conjunto de estados actuales con todos los alcanzables por transiciones epsilon.

---
