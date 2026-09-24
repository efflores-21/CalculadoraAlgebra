# Programa 3: Operaciones algebraicas en R^n

Calculadora educativa para practicar:

- operaciones con vectores en `R^n`;
- combinaciones lineales;
- operaciones matriciales;
- resolución y verificación de sistemas `Ax = b`.
- verificación de propiedades del producto matriz-vector.

La aplicación conserva una interfaz gráfica desarrollada con
**CustomTkinter**. Los cálculos algebraicos se implementan manualmente con
listas, ciclos y funciones de Python. No se utilizan NumPy, SciPy ni
funciones avanzadas de `math`.

## Ejecución

Desde la carpeta raíz del proyecto:

```text
python main.py
```

Si `customtkinter` aún no está instalado:

```text
pip install customtkinter
```

## Organización del proyecto

```text
CalculadoraAlgebra/
├── main.py
├── backend/
│   ├── matriz.py
│   ├── vectores.py
│   ├── operaciones_matriciales.py
│   ├── propiedades.py
│   ├── eliminacion.py
│   └── clasificador.py
└── frontend/
    └── interfaz.py
```

### `frontend/interfaz.py`

Contiene la ventana gráfica, los controles de entrada, las pestañas y la
presentación de resultados. La interfaz organiza el programa en:

1. **Sistemas lineales**
2. **Vectores**
3. **Matrices**
4. **Propiedades A·x**

### `backend/vectores.py`

Implementa:

- suma de vectores;
- resta de vectores;
- multiplicación por escalar;
- construcción del sistema asociado a una combinación lineal.

### `backend/operaciones_matriciales.py`

Implementa:

- suma de matrices;
- resta de matrices;
- multiplicación de una matriz por un escalar;
- producto matricial `A · B`;
- producto matriz-vector `A · x`;
- validación de matrices rectangulares y dimensiones compatibles.

### `backend/propiedades.py`

Implementa `verificar_propiedades(A, u, v, c)`, que comprueba la linealidad
del producto matriz-vector y devuelve todos los resultados intermedios:

```text
u + v
A·u
A·v
A·(u+v)
A·u + A·v
c·u
A·(c·u)
c·(A·u)
```

Las comparaciones se realizan directamente sobre listas de `Fraction`, por lo
que los resultados son exactos.

### `backend/eliminacion.py`

Implementa la eliminación de Gauss y Gauss-Jordan mediante operaciones
elementales:

- intercambio de filas;
- multiplicación de una fila por un escalar no nulo;
- suma o resta de un múltiplo de otra fila;
- identificación de pivotes;
- reducción de la matriz aumentada;
- obtención de soluciones y variables libres.

### `backend/clasificador.py`

Clasifica los sistemas como:

- **Consistente determinado:** existe una solución única.
- **Consistente indeterminado:** existen infinitas soluciones.
- **Inconsistente:** no existe solución.

## Paso a paso mostrado por la aplicación

### Operaciones con vectores

La suma, resta y multiplicación por escalar muestran cada componente por
separado. Por ejemplo:

```text
v1 = (1, 2, 3)
v2 = (4, 5, 6)

Componente 1: 1 + 4 = 5
Componente 2: 2 + 5 = 7
Componente 3: 3 + 6 = 9

v1 + v2 = (5, 7, 9)
```

Para un escalar `k`, se muestra:

```text
Componente 1: k · v1[1] = resultado[1]
Componente 2: k · v1[2] = resultado[2]
...
```

### Combinación lineal

Para comprobar si `b` pertenece al subespacio generado por
`{v1, ..., vk}`, se plantea:

```text
c1 v1 + c2 v2 + ... + ck vk = b
```

Después se construye:

```text
A · c = b
[ A | b ]
```

La interfaz muestra:

1. el planteamiento algebraico;
2. la matriz aumentada;
3. cada pivote seleccionado;
4. los intercambios de filas;
5. la normalización de pivotes;
6. las operaciones de suma o resta entre filas;
7. la matriz resultante después de cada operación;
8. la clasificación de la solución;
9. los escalares de la combinación, si existen.

Una fila de la forma:

```text
[ 0  0  ...  0 | c ], con c distinto de 0
```

indica una inconsistencia. En ese caso, `b` no es combinación lineal de los
vectores dados.

### Operaciones matriciales

La interfaz explica cada entrada calculada.

Para suma:

```text
C[i,j] = A[i,j] + B[i,j]
```

Para resta:

```text
C[i,j] = A[i,j] - B[i,j]
```

Para multiplicación por escalar:

```text
C[i,j] = k · A[i,j]
```

Para el producto matricial, se verifica primero que:

```text
columnas(A) = filas(B)
```

Luego se calcula cada entrada usando una fila de `A` y una columna de `B`:

```text
C[i,j] = A[i,1]B[1,j] + A[i,2]B[2,j] + ... + A[i,n]B[n,j]
```

Ejemplo:

```text
c1,1 = (1 · 5) + (2 · 7) = 19
c1,2 = (1 · 6) + (2 · 8) = 22
```

Si las dimensiones son incompatibles, la interfaz muestra el motivo y no
realiza el cálculo.

### Propiedades `A·x`

La cuarta pestaña permite introducir una matriz `A` de tamaño `m×n`, dos
vectores `u` y `v` de dimensión `n`, y un escalar `c`. Se muestran los pasos:

```text
PROPIEDAD a) A(u + v) = Au + Av
Paso 1: u + v
Paso 2: A·(u + v)
Paso 3: A·u
Paso 4: A·v
Paso 5: A·u + A·v

PROPIEDAD b) A(cu) = c(Au)
Paso 1: c·u
Paso 2: A·(c·u)
Paso 3: A·u
Paso 4: c·(A·u)
```

La aplicación compara ambos lados con igualdad exacta y muestra si cada
propiedad se cumple. Si `A` no es rectangular, sus columnas no coinciden con
la dimensión de los vectores, o `u` y `v` tienen dimensiones distintas, se
muestra un mensaje de error.

Las pestañas **Vectores**, **Matrices** y **Propiedades A·x** incluyen un
botón **Limpiar**. Este botón coloca en cero todas las entradas de datos,
incluidos los escalares, y borra el resultado mostrado.

### Sistemas lineales `Ax = b`

La sección de sistemas muestra una guía de lectura:

1. se parte de la matriz aumentada `[A | b]`;
2. se identifica un pivote;
3. se intercambian filas si es necesario;
4. se normaliza el pivote;
5. se hacen ceros en su columna;
6. se repite el procedimiento para las columnas restantes;
7. se clasifica el sistema;
8. se presenta la solución;
9. se verifica sustituyendo en las ecuaciones originales.

Cada paso incluye:

- la operación elemental realizada;
- una explicación de por qué se realiza;
- la matriz completa después de la operación.

La verificación calcula cada producto y suma parcial. Por ejemplo:

```text
Ecuación 1, paso 1:
a11 · x1 = producto

Ecuación 1, paso 2:
a12 · x2 = producto

Suma parcial = producto1 + producto2
Resultado = término independiente [OK]
```

Cuando existen variables libres, se asigna `0` a los parámetros para comprobar
una solución particular.

## Exactitud numérica

Los valores se convierten internamente a `fractions.Fraction`, incluida en la
biblioteca estándar de Python. Esto permite trabajar con enteros, decimales y
fracciones sin depender de redondeos aproximados.

Ejemplos de entradas válidas:

```text
5
-3
1.25
2/3
-7/4
```

## Restricciones técnicas cumplidas

- No se utiliza NumPy.
- No se utiliza SciPy.
- No se utiliza `math` para resolver operaciones algebraicas.
- Las matrices se representan como listas de listas.
- Las operaciones se realizan con funciones, condicionales y ciclos.
- Las dimensiones se validan antes de ejecutar cada operación.
- Se muestran mensajes claros en español.
- La interfaz gráfica utiliza `customtkinter` únicamente para la presentación
  y entrada de datos; no realiza los cálculos algebraicos.
