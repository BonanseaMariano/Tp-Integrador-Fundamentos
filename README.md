# Trabajo Práctico Integrador Fundamentos de Programación

### Alumno: Bonansea Camaño Mariano Nicolas

**Tema:** Eliminación de no determinismo y minimización de autómatas finitos

### Descripción

Este proyecto implementa algoritmos para:

1. Conversión de Autómatas Finitos No Deterministas (AFND) a Autómatas Finitos Deterministas (AFD)
2. Minimización de AFD mediante el algoritmo de partición
3. Validación de cadenas en autómatas

### Estructura del Proyecto

```
├── src/
│   ├── __init__.py
│   ├── automata.py          # Clases para representar AFD y AFND
│   ├── conversor.py         # Conversión AFND → AFD
│   ├── minimizador.py       # Minimización de AFD
│   └── manejador_archivos.py # Lectura/escritura de archivos
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

#### Procesamiento completo de un autómata

```bash
python main.py <archivo_entrada> [directorio_salida]
```

Ejemplo:

```bash
python main.py ejemplos/afnd_ejemplo1.json resultados/
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
  "descripcion": "Autómata que acepta cadenas que terminan con 'ab'",
  "tipo": "AFD"
}
```

**Texto plano:**

```
ESTADOS: q0,q1,q2
ALFABETO: a,b
ESTADO_INICIAL: q0
ESTADOS_FINALES: q2
DESCRIPCION: Autómata que acepta cadenas que terminan con 'ab'
TIPO: AFD
TRANSICIONES:
q0,a,q1
q1,b,q2
```

**Campos adicionales (opcionales):**
- **descripcion/DESCRIPCION**: Descripción del lenguaje que acepta el autómata
- **tipo/TIPO**: Especifica si es "AFD" o "AFND" (si no se especifica, se detecta automáticamente)

**Transiciones múltiples (AFND):**
Para autómatas no deterministas, se pueden especificar múltiples destinos:

```json
{
  "transiciones": [
    {
      "origen": "q0",
      "simbolo": "a",
      "destino": ["q1", "q2"]
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

- Algoritmo de construcción de subconjuntos
- Manejo de transiciones epsilon
- Generación de reporte detallado del proceso

#### 2. Minimización de AFD

- Algoritmo de partición de estados equivalentes
- Eliminación de estados inalcanzables
- Análisis de reducción de estados

#### 3. Validación de cadenas

- Modo interactivo para probar cadenas
- Verificación automática de equivalencia entre autómatas
- Generación de cadenas de prueba

#### 4. Graficación y Visualización

- Generación de diagramas visuales de autómatas
- Comparaciones lado a lado (original vs procesado)
- Múltiples formatos de salida (PNG, PDF, SVG)
- Visualización del proceso de minimización paso a paso

## Módulo de Graficación

### Características del Graficador

El módulo `graficador.py` utiliza **Graphviz** para generar visualizaciones profesionales de los autómatas finitos.

#### Funcionalidades principales:

1. **Gráficos individuales**: Visualización de un solo autómata
2. **Gráficos comparativos**: Dos autómatas lado a lado
3. **Proceso de minimización**: Visualización paso a paso
4. **Múltiples formatos**: PNG, PDF, SVG, etc.
5. **Configuración personalizable**: Colores, tamaños, estilos

#### Elementos visuales:

- 🟢 **Estado inicial**: Verde claro
- 🔴 **Estados finales**: Rojo claro (doble círculo)
- 🟡 **Estado inicial y final**: Dorado
- 🔵 **Estados normales**: Azul claro
- ➡️ **Transiciones**: Flechas etiquetadas con símbolos
- ε **Transiciones epsilon**: Etiquetadas como "ε"

### Uso del Graficador

#### Importación y configuración básica:
```python
from src.graficador import GraficadorAutomatas, verificar_instalacion
from src.manejador_archivos import ManejadorArchivos

# Verificar que Graphviz esté instalado
info = verificar_instalacion()
print(info['mensaje'])

# Crear graficador
graficador = GraficadorAutomatas()

# Cargar un autómata
automata = ManejadorArchivos.cargar_automata_desde_json('ejemplos/afd_simple.json')
```

#### Generar gráfico simple:
```python
# Generar PNG del autómata
archivo = graficador.generar_grafico(
    automata=automata,
    nombre_archivo='mi_automata',
    directorio='graficos/',
    incluir_titulo=True
)
print(f"Gráfico generado: {archivo}")
```

#### Personalizar estilo:
```python
# Configurar colores y estilos personalizados
graficador.configurar_estilo(
    formato='pdf',
    color_nodo_inicial='lightgreen',
    color_nodo_final='pink',
    color_nodo_normal='lightblue',
    tamaño_fuente='14',
    dpi='300'
)
```

#### Comparación de autómatas:
```python
from src.conversor import ConversorAFNDaAFD

# Convertir AFND a AFD
afnd = ManejadorArchivos.cargar_automata_desde_json('ejemplos/afnd_ejemplo.json')
conversor = ConversorAFNDaAFD()
afd = conversor.convertir(afnd)

# Generar comparación lado a lado
graficador.generar_comparacion(
    automata_original=afnd,
    automata_procesado=afd,
    nombre_archivo='conversion_afnd_afd',
    directorio='graficos/',
    titulo_original='AFND Original',
    titulo_procesado='AFD Convertido'
)
```

#### Proceso de minimización:
```python
from src.minimizador import MinimizadorAFD

# Minimizar AFD
minimizador = MinimizadorAFD()
afd_minimizado = minimizador.minimizar(afd)

# Visualizar proceso completo
graficador.generar_proceso_minimizacion(
    minimizador=minimizador,
    automata_original=afd,
    automata_minimizado=afd_minimizado,
    nombre_archivo='proceso_minimizacion',
    directorio='graficos/'
)
```

#### Exportar en múltiples formatos:
```python
# Generar el mismo gráfico en PNG, PDF y SVG
archivos = graficador.exportar_multiples_formatos(
    automata=automata,
    nombre_base='automata_completo',
    directorio='graficos/',
    formatos=['png', 'pdf', 'svg']
)

for archivo in archivos:
    print(f"Generado: {archivo}")
```

### Configuración avanzada:

```python
# Configuración completa del graficador
graficador.configurar_estilo(
    formato='png',              # Formato de salida
    motor='dot',                # Motor de renderizado (dot, neato, circo)
    dpi='300',                  # Resolución
    tamaño_nodo='1.0',          # Tamaño de los nodos
    color_nodo_normal='lightblue',
    color_nodo_inicial='lightgreen',
    color_nodo_final='lightcoral',
    color_nodo_inicial_final='gold',
    color_transicion='black',
    grosor_transicion='1.5',
    fuente='Arial',
    tamaño_fuente='12'
)
```

### Solución de problemas:

#### Error: "Graphviz no está instalado"
```bash
# Instalar librería Python
pip install graphviz

# Instalar software Graphviz
# Windows: descargar desde https://graphviz.org/download/
# Linux: sudo apt-get install graphviz
# macOS: brew install graphviz
```

#### Verificar instalación:
```python
from src.graficador import verificar_instalacion

info = verificar_instalacion()
print(f"Librería instalada: {info['libreria_instalada']}")
print(f"Ejecutable disponible: {info['ejecutable_disponible']}")
print(f"Versión: {info['version']}")
print(f"Mensaje: {info['mensaje']}")
```
### Algoritmos Implementados

### 1. Algoritmo de Conversión AFND → AFD (Construcción de Subconjuntos)

Este algoritmo convierte un Autómata Finito No Determinista en un Autómata Finito Determinista equivalente.

#### Funcionamiento:

1. **Estado Inicial**: Se calcula la clausura epsilon del estado inicial del AFND
    - Si el AFND tiene transiciones epsilon (ε), se incluyen todos los estados alcanzables mediante estas transiciones

2. **Construcción de Estados**: Cada estado del AFD representa un conjunto de estados del AFND
    - Se procesan todos los conjuntos de estados alcanzables
    - Para cada símbolo del alfabeto, se calcula el conjunto de estados destino

3. **Proceso Iterativo**:
   ```
   Mientras haya conjuntos sin procesar:
     - Tomar un conjunto de estados del AFND
     - Para cada símbolo 'a' del alfabeto:
       * Calcular todos los estados alcanzables con 'a'
       * Aplicar clausura epsilon si es necesario
       * Crear nueva transición en el AFD
   ```

4. **Estados Finales**: Un estado del AFD es final si contiene al menos un estado final del AFND original

#### Ejemplo:

Si tenemos un AFND con estados {q0, q1, q2} y el estado q0 puede ir a {q1, q2} con el símbolo 'a', entonces en el AFD
tendremos un estado que represente el conjunto {q1, q2}.

### 2. Algoritmo de Minimización de AFD (Partición de Estados)

Este algoritmo reduce el número de estados de un AFD eliminando estados equivalentes.

#### Funcionamiento:

1. **Eliminación de Estados Inalcanzables**:
    - Se identifican todos los estados alcanzables desde el estado inicial
    - Se eliminan los estados que no son alcanzables

2. **Partición Inicial**:
    - Se crean dos grupos: estados finales y estados no finales
    - Esta es la partición más básica basada en la aceptación

3. **Refinamiento de Particiones**:
   ```
   Repetir hasta que no haya cambios:
     - Para cada grupo de la partición actual:
       * Para cada símbolo del alfabeto:
         - Verificar si todos los estados del grupo van al mismo grupo destino
         - Si no, dividir el grupo en subgrupos
   ```

4. **Construcción del AFD Minimizado**:
    - Cada grupo final de la partición se convierte en un estado
    - Las transiciones se construyen entre grupos
    - Se preservan el estado inicial y los estados finales

#### Criterio de Equivalencia:

Dos estados son equivalentes si:

- Ambos son finales o ambos son no finales
- Para cada símbolo del alfabeto, van a estados equivalentes

#### Ejemplo:

Si tenemos estados q1 y q2 que para todos los símbolos van a los mismos estados destino y ambos son finales (o no
finales), entonces son equivalentes y se pueden fusionar.

### 3. Algoritmo de Validación de Cadenas

#### Para AFD (Determinista):

1. **Proceso Secuencial**:
   ```
   estado_actual = estado_inicial
   Para cada símbolo en la cadena:
     - Verificar que el símbolo esté en el alfabeto
     - Buscar transición (estado_actual, símbolo)
     - Si existe: estado_actual = estado_destino
     - Si no existe: rechazar cadena
   
   Aceptar si estado_actual es final
   ```

2. **Características**:
    - Un solo camino posible
    - Decisión determinista en cada paso
    - Eficiencia O(n) donde n es la longitud de la cadena

#### Para AFND (No Determinista):

1. **Proceso con Múltiples Estados**:
   ```
   estados_actuales = {estado_inicial}
   Para cada símbolo en la cadena:
     - conjunto_nuevos_estados = vacío
     - Para cada estado en estados_actuales:
       * Buscar todas las transiciones posibles con el símbolo
       * Agregar estados destino a conjunto_nuevos_estados
     - estados_actuales = conjunto_nuevos_estados
     - Aplicar clausura epsilon si es necesario
   
   Aceptar si algún estado en estados_actuales es final
   ```

2. **Manejo de Transiciones Epsilon**:
    - Se calculan clausuras epsilon cuando es necesario
    - Se exploran todos los caminos posibles simultáneamente

3. **Características**:
    - Múltiples caminos simultáneos
    - La cadena se acepta si al menos un camino lleva a un estado final
    - Complejidad mayor debido a la exploración de múltiples estados

#### Optimizaciones Implementadas:

1. **Parada Temprana**: Si no hay estados actuales, se rechaza inmediatamente
2. **Validación de Alfabeto**: Se verifica que todos los símbolos pertenezcan al alfabeto
3. **Clausura Epsilon Eficiente**: Se calcula solo cuando es necesario

### Ejemplos de uso

#### Uso básico

```python
from src.automata import AFD
from src.minimizador import MinimizadorAFD

# Crear un AFD simple
afd = AFD(
    estados={'q0', 'q1', 'q2'},
    alfabeto={'a', 'b'},
    estado_inicial='q0',
    estados_finales={'q2'},
    transiciones={
        ('q0', 'a'): 'q1',
        ('q1', 'b'): 'q2'
    }
)

# Minimizar
minimizador = MinimizadorAFD()
afd_minimizado = minimizador.minimizar(afd)

# Validar cadena
print(afd.validar_cadena("ab"))  # True
```

