# Calculadora de Álgebra Lineal - Programa 4

Aplicación educativa con interfaz gráfica **CustomTkinter** y cálculos
implementados manualmente. No utiliza NumPy, SciPy ni librerías de cálculo
matricial automático. Los valores racionales se procesan con
`fractions.Fraction`.

## Ejecución

```text
python main.py
```

Requisito de interfaz:

```text
pip install customtkinter
```

## Organización

```text
CalculadoraAlgebra/
├── main.py
├── modulos/
│   ├── __init__.py
│   ├── _comun.py
│   ├── modulo_sistemas.py
│   ├── modulo_vectores.py
│   ├── modulo_matrices.py
│   ├── modulo_determinantes.py
│   └── teoremas/
│       ├── __init__.py
│       └── resumen_teoremas.py
├── backend/                 # Algoritmos compartidos preexistentes
└── frontend/                # Interfaz de pestañas previa, aún disponible
```

El menú principal y los módulos comparten una sola ventana. Al seleccionar un
módulo, el contenido cambia dentro de la ventana actual. Cada módulo tiene un
botón **“Volver al menú principal”** para regresar sin abrir ventanas nuevas.
Las ventanas secundarias solo se usan cuando el usuario solicita consultar
los teoremas.

## Módulos

### Módulo 1: Sistemas de ecuaciones

Ingresa el número de ecuaciones `m`, el número de variables `n`, la matriz de
coeficientes `A` y el vector de términos independientes `b`. Resuelve `Ax=b`
con Gauss o Gauss-Jordan, muestra las operaciones de fila y clasifica el
sistema como solución única, infinitas soluciones o inconsistente.

### Módulo 2: Vectores e independencia lineal

Se ingresan `k` vectores de dimensión `n`. El programa los organiza como
columnas de `A` y estudia el sistema homogéneo:

```text
A*c = 0
```

Muestra la matriz aumentada, los pasos de Gauss-Jordan, la matriz reducida, el
número de pivotes y las variables libres. Si hay `k` pivotes, los vectores son
linealmente independientes (L.I.); si hay menos, son linealmente dependientes
(L.D.). Para `k > n`, el veredicto es L.D.

### Módulo 3: Álgebra de matrices

Incluye suma, resta, producto por escalar, producto matricial, traspuesta e
inversa. La inversa se calcula reduciendo `[A|I]` a `[I|A^-1]`; si no existe un
pivote para cada columna, la matriz es singular.

### Módulo 4: Determinantes

Calcula el determinante de una matriz cuadrada mediante eliminación por filas.
Explica pivotes, intercambios de filas y el producto final de pivotes.

## Teoremas clave

Cada ventana tiene el botón **“0. Ver Teoremas Clave del Módulo”**. Los textos
centrales se encuentran en `modulos/teoremas/resumen_teoremas.py`.

## Restricciones técnicas

- No se importan NumPy ni SciPy.
- Las operaciones matriciales se realizan con listas, bucles y funciones
  propias.
- `customtkinter` se usa para la interfaz gráfica.
- `Fraction` conserva exactitud en operaciones con racionales.
- Los tamaños de entrada se validan antes del cálculo.

## Informe

El informe de Programa 4 se entrega en `docs/Informe_Programa_4.pdf`. Incluye
portada, explicación del algoritmo de independencia lineal y capturas de los
casos L.I. y L.D.
