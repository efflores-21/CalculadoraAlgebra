# Calculadora de Álgebra Lineal

## Descripción

Calculadora interactiva para resolver sistemas de ecuaciones lineales Ax = b utilizando el **método de eliminación por filas (Gauss)**.

Este programa fue desarrollado como parte de la asignatura **Álgebra Lineal (MTM0120)** de la Universidad Americana.

## Características

- ✅ **Resolución de sistemas lineales** mediante eliminación Gaussiana con pivoteo parcial
- ✅ **Clasificación automática** del sistema:
  - Sistema Consistente Determinado (solución única)
  - Sistema Consistente Indeterminado (infinitas soluciones)
  - Sistema Inconsistente (sin solución)
- ✅ **Visualización paso a paso** del proceso de eliminación
- ✅ **Verificación automática** de la solución
- ✅ **Sin dependencias externas**: utiliza solo Python estándar (listas, condicionales, bucles, funciones)

## Restricciones Cumplidas

De acuerdo con los requisitos del proyecto:

- ✅ No se utilizan librerías NumPy, SciPy ni funciones de álgebra lineal de math
- ✅ Se utiliza Python estándar: listas anidadas, condicionales if/else, bucles for/while y funciones
- ✅ Cada bloque principal del código está documentado explicativamente

## Estructura del Proyecto

```
CalculadoraAlgebra/
├── main.py                 # Archivo principal
├── backend/
│   ├── __init__.py
│   ├── matriz.py          # Operaciones con matrices
│   ├── eliminacion.py     # Algoritmo de eliminación Gaussiana
│   └── clasificador.py    # Clasificación del sistema
└── frontend/
    ├── __init__.py
    └── interfaz.py        # Interfaz de usuario
```

## Módulos

### backend/matriz.py
Operaciones básicas con matrices:
- `crear_matriz_aumentada()`: Construye [A|b]
- `mostrar_matriz()`: Imprime la matriz formateada
- `intercambiar_filas()`: Operación elemental
- `multiplicar_fila()`: Operación elemental
- `sumar_filas()`: Operación elemental
- `es_cero()`: Manejo de errores de redondeo

### backend/eliminacion.py
Implementación del algoritmo:
- `eliminacion_gaussiana()`: Transforma a forma escalonada con pivoteo parcial
- `sustitucion_hacia_atras()`: Obtiene la solución
- `resolver_sistema()`: Orquesta todo el proceso

### backend/clasificador.py
Clasificación del sistema:
- `clasificar_sistema()`: Determina el tipo de sistema
- `mostrar_clasificacion()`: Imprime la clasificación

### frontend/interfaz.py
Interacción con el usuario:
- `obtener_datos_usuario()`: Solicita entrada de m, n y coeficientes
- `mostrar_solucion()`: Imprime la solución
- `verificar_solucion()`: Verifica el resultado sustituyendo en el original
- `menu_principal()`: Menú interactivo

## Uso

### Ejecución Interactiva

```bash
python main.py
```

El programa solicitará:
1. Número de ecuaciones (m)
2. Número de variables (n)
3. Coeficientes de la matriz A
4. Términos independientes b

Luego mostrará:
- La matriz aumentada inicial
- Los pasos del proceso de eliminación
- La clasificación del sistema
- La solución (si existe)
- La verificación de la solución

## Ejemplos

### Ejemplo 1: Sistema con Solución Única

```
Sistema:
x + 2y = 5
3x + y = 8

Entrada:
m = 2
n = 2
Coeficientes: 1, 2, 3, 1
Términos: 5, 8

Salida:
Tipo: Consistente Determinado
x1 = 2.2
x2 = 1.4
```

### Ejemplo 2: Sistema con Infinitas Soluciones

```
Sistema:
x + 2y = 4
2x + 4y = 8

Entrada:
m = 2
n = 2
Coeficientes: 1, 2, 2, 4
Términos: 4, 8

Salida:
Tipo: Consistente Indeterminado
Variables libres: 1
x1 = 4 - 2t (variable t es libre)
```

### Ejemplo 3: Sistema Inconsistente

```
Sistema:
x + 2y = 4
x + 2y = 5

Entrada:
m = 2
n = 2
Coeficientes: 1, 2, 1, 2
Términos: 4, 5

Salida:
Tipo: Inconsistente
El sistema NO tiene solución
```

## Algoritmo: Eliminación Gaussiana

### Pasos:

1. **Pivoteo Parcial**: Buscar el elemento de mayor valor absoluto en la columna actual
2. **Intercambio**: Intercambiar filas si es necesario
3. **Normalización**: Dividir la fila por el pivote para obtener 1
4. **Eliminación**: Hacer ceros debajo del pivote usando operaciones de fila

### Operaciones Elementales:

```
F_i <--> F_j         (Intercambio)
F_i → λ * F_i        (Multiplicación, λ ≠ 0)
F_i → F_i + λ * F_j  (Suma)
```

### Clasificación:

- Si existe una fila `[0 0 ... 0 | k]` con k ≠ 0 → **Inconsistente**
- Si variables_libres = 0 → **Consistente Determinado**
- Si variables_libres > 0 → **Consistente Indeterminado**

## Manejo de Errores

- Tolerancia para valores próximos a cero: 1e-10
- Validación de entrada del usuario
- Captura de excepciones en la ejecución principal

## Requisitos

- Python 3.6 o superior
- Sistema operativo: Windows, macOS, Linux

## Archivos de Prueba

Se incluyen scripts de prueba para cada caso:
- `test_3x3.py`: Test de un sistema 3×3

## Notas sobre Precisión

Debido a la aritmética de punto flotante, los valores mostrados pueden tener pequeñas diferencias respecto a los resultados exactos. Estos errores se manejan con una tolerancia (1e-10) para considerar un valor como cero.

## Autor

Desarrollado por un grupo de estudiantes de la Universidad Americana como parte de la actividad de programación en Álgebra Lineal.

## Licencia

Uso educativo únicamente.
