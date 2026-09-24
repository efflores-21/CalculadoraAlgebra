"""
Operaciones elementales con matrices sobre Q (racionales).

Las matrices se representan como listas de listas. Todos los valores se
convierten internamente a fractions.Fraction. No se usa NumPy ni SciPy.
"""

from fractions import Fraction
from backend.matriz import _a_fraction


def _matriz_a_fraction(M):
    """Convierte una matriz a lista de listas de Fraction y valida que sea rectangular."""
    if M is None or len(M) == 0:
        raise ValueError("La matriz no puede estar vacía.")
    convertida = []
    n_columnas = None
    for i, fila in enumerate(M):
        if fila is None or len(fila) == 0:
            raise ValueError(f"La fila {i + 1} de la matriz está vacía.")
        fila_frac = [_a_fraction(valor) for valor in fila]
        if n_columnas is None:
            n_columnas = len(fila_frac)
        elif len(fila_frac) != n_columnas:
            raise ValueError(
                f"La matriz no es rectangular: la fila 1 tiene {n_columnas} columnas "
                f"y la fila {i + 1} tiene {len(fila_frac)}."
            )
        convertida.append(fila_frac)
    return convertida


def _dimensiones(M):
    """Devuelve (filas, columnas) de una matriz ya convertida."""
    return len(M), len(M[0])


def suma_matrices(A, B):
    """
    Suma de matrices A + B.

    Operación algebraica: si A, B ∈ M_{m×n}(Q),
        (A + B)[i][j] = A[i][j] + B[i][j]
    para i = 1..m, j = 1..n. Solo está definida cuando A y B tienen el
    mismo tamaño m×n.

    Args:
        A: matriz m×n.
        B: matriz m×n.

    Returns:
        list[list[Fraction]]: matriz suma.

    Raises:
        ValueError: si las dimensiones no coinciden o alguna matriz es inválida.
    """
    mat_a = _matriz_a_fraction(A)
    mat_b = _matriz_a_fraction(B)
    m, n = _dimensiones(mat_a)
    p, q = _dimensiones(mat_b)
    if m != p or n != q:
        raise ValueError(
            f"Dimensiones incompatibles para la suma: A es {m}×{n} y B es {p}×{q}."
        )
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(mat_a[i][j] + mat_b[i][j])
        resultado.append(fila)
    return resultado


def resta_matrices(A, B):
    """
    Resta de matrices A − B.

    Operación algebraica: si A, B ∈ M_{m×n}(Q),
        (A − B)[i][j] = A[i][j] − B[i][j].
    Equivale a A + (−1)·B. Requiere el mismo tamaño m×n.

    Args:
        A: minuendo.
        B: sustraendo.

    Returns:
        list[list[Fraction]]: matriz diferencia.

    Raises:
        ValueError: si las dimensiones no coinciden o alguna matriz es inválida.
    """
    mat_a = _matriz_a_fraction(A)
    mat_b = _matriz_a_fraction(B)
    m, n = _dimensiones(mat_a)
    p, q = _dimensiones(mat_b)
    if m != p or n != q:
        raise ValueError(
            f"Dimensiones incompatibles para la resta: A es {m}×{n} y B es {p}×{q}."
        )
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(mat_a[i][j] - mat_b[i][j])
        resultado.append(fila)
    return resultado


def multiplicar_escalar_matriz(k, A):
    """
    Multiplicación de una matriz por un escalar: k·A.

    Operación algebraica: si A ∈ M_{m×n}(Q) y k ∈ Q,
        (k·A)[i][j] = k · A[i][j]
    para cada entrada. Es la operación que hace de M_{m×n}(Q) un espacio vectorial.

    Args:
        k: escalar.
        A: matriz.

    Returns:
        list[list[Fraction]]: matriz escalada.

    Raises:
        ValueError: si la matriz es inválida.
    """
    mat_a = _matriz_a_fraction(A)
    escalar = _a_fraction(k)
    m, n = _dimensiones(mat_a)
    resultado = []
    for i in range(m):
        fila = []
        for j in range(n):
            fila.append(escalar * mat_a[i][j])
        resultado.append(fila)
    return resultado


def multiplicar_matrices(A, B):
    """
    Producto de matrices A · B.

    Operación algebraica: si A ∈ M_{m×n}(Q) y B ∈ M_{n×p}(Q), el producto
    C = A·B ∈ M_{m×p}(Q) está dado por
        C[i][j] = Σ_{k=0}^{n-1} A[i][k] · B[k][j].
    Es decir, la entrada (i, j) es el producto punto de la fila i de A con
    la columna j de B. El producto solo existe si el número de columnas de A
    coincide con el número de filas de B.

    Se implementa con tres bucles anidados (i, j, k), sin bibliotecas de
    álgebra lineal.

    Args:
        A: matriz m×n.
        B: matriz n×p.

    Returns:
        list[list[Fraction]]: matriz producto m×p.

    Raises:
        ValueError: si columnas(A) ≠ filas(B) o alguna matriz es inválida.
    """
    mat_a = _matriz_a_fraction(A)
    mat_b = _matriz_a_fraction(B)
    m, n = _dimensiones(mat_a)
    filas_b, p = _dimensiones(mat_b)
    if n != filas_b:
        raise ValueError(f"columnas de A ({n}) ≠ filas de B ({filas_b})")

    producto = []
    for i in range(m):
        fila = []
        for j in range(p):
            acumulado = Fraction(0, 1)
            for k in range(n):
                acumulado += mat_a[i][k] * mat_b[k][j]
            fila.append(acumulado)
        producto.append(fila)
    return producto


def multiplicar_matriz_vector(A, x):
    """
    Multiplica una matriz A por un vector columna x.

    Procedimiento algebraico equivalente: si A es m×n y x pertenece a R^n,
        (A·x)[i] = Σ_j A[i][j] · x[j].
    Cada componente del resultado es el producto punto entre una fila de A
    y el vector x. El producto solo está definido cuando las columnas de A
    coinciden con la cantidad de componentes de x.

    Args:
        A: matriz de tamaño m×n.
        x: vector de n componentes.

    Returns:
        list[Fraction]: vector A·x de m componentes.

    Raises:
        ValueError: si A no es rectangular o las dimensiones no coinciden.
    """
    matriz = _matriz_a_fraction(A)
    if x is None or len(x) == 0:
        raise ValueError("El vector no puede estar vacío.")
    vector = [_a_fraction(valor) for valor in x]
    filas, columnas = _dimensiones(matriz)
    if columnas != len(vector):
        raise ValueError(
            f"Dimensiones incompatibles: A tiene {columnas} columnas "
            f"pero el vector tiene {len(vector)} componentes."
        )

    resultado = []
    for i in range(filas):
        acumulado = Fraction(0, 1)
        for j in range(columnas):
            acumulado += matriz[i][j] * vector[j]
        resultado.append(acumulado)
    return resultado
