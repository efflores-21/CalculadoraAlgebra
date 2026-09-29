# Calculadora de Álgebra Lineal

Aplicación de escritorio para explorar y resolver problemas habituales de
álgebra lineal. Cuenta con una interfaz gráfica desarrollada con
**CustomTkinter** y presenta los cálculos en forma ordenada, con explicaciones
paso a paso cuando corresponde.

## Inicio rápido

Requiere Python y CustomTkinter. Para instalar la interfaz, si hace falta:

```text
pip install customtkinter
```

Inicia la aplicación desde la carpeta del proyecto:

```text
python main.py
```

El menú principal permite seleccionar un módulo. Este se muestra en la misma
ventana y ofrece un botón para regresar al menú.

## Funcionalidades

### Sistemas de ecuaciones

Resuelve sistemas de la forma `Ax = b` con eliminación de Gauss o
Gauss-Jordan. Muestra las operaciones elementales, clasifica el sistema como
de solución única, infinitas soluciones o inconsistente y permite verificar
la solución.

### Vectores e independencia lineal

Permite ingresar varios vectores de `R^n`, organizarlos como columnas de una
matriz y analizar su independencia resolviendo el sistema homogéneo `A*c = 0`.
Presenta la forma reducida, los pivotes, las variables libres y el veredicto:
linealmente independientes (L.I.) o dependientes (L.D.).

### Operaciones con matrices

Incluye suma, resta, multiplicación por escalar, producto de matrices,
traspuesta e inversa. Las operaciones verifican las dimensiones necesarias y
presentan el resultado; los productos y la inversa muestran sus pasos de
cálculo.

### Determinantes

Calcula el determinante de matrices cuadradas mediante eliminación por filas.
Muestra los pivotes y los intercambios de filas, y señala si la matriz es
singular.

### Propiedades del producto matriz-vector

Verifica las propiedades de linealidad:

```text
A(u + v) = Au + Av
A(cu) = c(Au)
```

La aplicación presenta los resultados intermedios y compara ambos lados de
cada igualdad.

## Teoremas y ayuda

Los módulos incluyen acceso a resúmenes de teoremas y propiedades
relacionados con sus operaciones.

## Organización del proyecto

```text
CalculadoraAlgebra/
├── main.py
├── modulos/       # Interfaz y lógica de los módulos
│   └── teoremas/  # Resúmenes teóricos
├── backend/       # Operaciones algebraicas y algoritmos
└── frontend/      # Interfaz gráfica original
```

## Implementación

- Los cálculos matriciales se realizan con listas, ciclos y funciones propias.
- `fractions.Fraction` permite trabajar con valores racionales exactos.
- CustomTkinter se utiliza para construir la interfaz gráfica.
- La aplicación no utiliza NumPy ni SciPy.
