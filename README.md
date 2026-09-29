# Calculadora de Álgebra Lineal

Aplicación de escritorio para explorar y resolver problemas habituales de
álgebra lineal. Cuenta con una interfaz gráfica desarrollada con
**CustomTkinter** y presenta los cálculos en forma ordenada, con explicaciones
paso a paso cuando corresponde.

## Inicio rápido

Solo requiere Python 3 instalado (desde python.org, que ya incluye Tkinter).
Después de clonar el repositorio, ejecuta:

```text
python main.py
```

La primera vez, si la computadora no tiene CustomTkinter, `main.py` lo
instala automáticamente con pip (necesita internet solo esa vez). También
puede instalarse a mano con `pip install -r requirements.txt`.

El menú principal permite seleccionar un módulo. Este se muestra en la misma
ventana y ofrece un botón para regresar al menú.

## Funcionalidades

Los módulos están numerados en el mismo orden en el menú principal:

### Módulo 1: Sistemas de ecuaciones

Resuelve sistemas de la forma `Ax = b` con eliminación de Gauss o
Gauss-Jordan. Muestra las operaciones elementales, clasifica el sistema como
de solución única, infinitas soluciones o inconsistente y permite verificar
la solución.

### Módulo 2: Operaciones con vectores y combinación lineal

Permite sumar y restar vectores, multiplicarlos por escalares y verificar si
un vector es combinación lineal de un conjunto. Para esta última operación
plantea y resuelve el sistema de coeficientes correspondiente.

### Módulo 3: Independencia lineal

Permite ingresar varios vectores de `R^n`, organizarlos como columnas de una
matriz y analizar su independencia resolviendo el sistema homogéneo `A*c = 0`.
Presenta la forma reducida, los pivotes, las variables libres y el veredicto:
linealmente independientes (L.I.) o dependientes (L.D.).

### Módulo 4: Operaciones con matrices

Incluye suma, resta, multiplicación por escalar, producto de matrices,
traspuesta e inversa. Las operaciones verifican las dimensiones necesarias y
presentan el resultado; los productos y la inversa muestran sus pasos de
cálculo.

### Módulo 5: Determinantes

Calcula el determinante de matrices cuadradas mediante eliminación por filas.
Muestra los pivotes y los intercambios de filas, y señala si la matriz es
singular.

### Módulo 6: Propiedades del producto matriz-vector

Verifica las propiedades de linealidad:

```text
A(u + v) = Au + Av
A(cu) = c(Au)
```

La aplicación presenta los resultados intermedios y compara ambos lados de
cada igualdad.

El menú ofrece por separado las **operaciones con vectores**, la
**independencia lineal** y las **propiedades del producto matriz-vector**.

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
