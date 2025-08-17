# Trabajo Práctico Integrador

**Tema:** Eliminación de no determinismo y minimización de autómatas finitos  
**Fecha de entrega:** 26 de septiembre  
**Entrega:** Documento técnico + código fuente + casos de prueba

## Objetivo general

Desarrollar un programa que, dada la descripción de un autómata finito (determinista o no determinista), realice los siguientes pasos:

1. **Eliminación de no determinismo:** Transformar cualquier AFND en un AFD equivalente.
2. **Minimización:** Aplicar un algoritmo de minimización sobre el AFD obtenido, entregando un autómata finito determinista mínimo equivalente al original.

El programa además debe permitir validar cadenas del lenguaje que identifica un autómata. Esta funcionalidad permitirá rápidamente comprobar las mismas cadenas sobre autómatas distintos.

## Formato de entrada y salida

### Entrada:
Archivo de texto (o JSON/XML, a elección) que describa el autómata mediante:
- Conjunto de estados
- Alfabeto
- Estado inicial
- Conjunto de estados finales
- Función de transición

### Salida:
- Autómata determinista mínimo en el mismo formato que la entrada
- Informe en texto o PDF explicando:
  - Proceso de conversión AFND → AFD
  - Proceso de minimización
  - Ejemplos de ejecución y validación

## Requerimientos del programa

1. **Conversión AFND → AFD**
2. **Minimización**
3. **Validación del resultado final** probando que:
   - a. El lenguaje aceptado por el AFD minimizado es equivalente al del autómata original
   - b. Se redujo (o mantuvo) la cantidad de estados
4. El programa debe estar implementado en un **lenguaje de programación moderno** a elección y documentado
5. Se recomienda separar el código en módulos/clases para:
   - a. Representación del autómata
   - b. Conversión AFND → AFD
   - c. Minimización
   - d. Lectura/escritura de archivos

## Documentación a entregar

El documento en PDF debe incluir:

### 1. Portada
- Nombre de la materia
- Título del trabajo
- Integrantes y correo de contacto
- Fecha

### 2. Introducción
- Breve descripción del problema y objetivos
- Fundamentos teóricos: definiciones de AFND, AFD y autómata mínimo

### 3. Metodología
- Descripción detallada de los algoritmos implementados
- Diagramas de flujo o pseudocódigo
- Decisiones de diseño

### 4. Casos de prueba
- Autómatas pequeños y medianos con explicación paso a paso
- Ejemplos que requieran varias iteraciones de minimización
- Comparación visual (diagramas) entre autómata original, AFD y AFD mínimo

### 5. Resultados y análisis
- Tabla comparativa: número de estados y transiciones antes y después de cada proceso
- Verificación de equivalencia entre autómatas (explicar cómo se probó)

### 6. Conclusiones
- Reflexiones sobre eficiencia, limitaciones y posibles mejoras

### 7. Referencias bibliográficas
- Libros de la materia
- Otros recursos usados

## Criterios de evaluación

| Criterio | Peso |
|----------|------|
| Correctitud de algoritmos (eliminación de no determinismo y minimización) | 35% |
| Diseño y estructura del código | 20% |
| Permite verificar cadenas dado un autómata | 10% |
| Calidad de la documentación (claridad, teoría, diagramas) | 15% |
| Variedad y profundidad de las pruebas | 10% |
| Presentación general y conclusiones | 10% |
