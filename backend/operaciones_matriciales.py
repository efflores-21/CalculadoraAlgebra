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


# ============================================================================
# FUNCIONES PARA INVERSA POR MATRIZ ADJUNTA
# ============================================================================


def _determinante_2x2(A):
    """
    Calcula el determinante de una matriz 2×2 de forma directa.
    
    Det([[a, b], [c, d]]) = ad - bc
    
    Args:
        A: matriz 2×2 de Fraction
    
    Returns:
        Fraction: determinante
    """
    return A[0][0] * A[1][1] - A[0][1] * A[1][0]


def determinante_por_cofactores(A):
    """
    Calcula el determinante de una matriz cuadrada mediante expansión por cofactores.

    Procedimiento algebraico: para una matriz A cuadrada n×n, el determinante
    se expande por la primera fila:
        det(A) = Σ_j A[0][j] × C[0][j]
    donde C[0][j] es el cofactor: C[0][j] = (-1)^(0+j) × M[0][j],
    y M[0][j] es el determinante de la submatriz sin fila 0 y columna j.

    Casos base:
    - Para 1×1: det = A[0][0]
    - Para 2×2: det = A[0][0]×A[1][1] - A[0][1]×A[1][0]

    Casos recursivos (n > 2): usa expansión por cofactores.

    Args:
        A: matriz cuadrada n×n

    Returns:
        Fraction: determinante de la matriz

    Raises:
        ValueError: si la matriz no es cuadrada
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    if m != n:
        raise ValueError(
            f"El determinante solo está definido para matrices cuadradas. "
            f"Se recibió una matriz {m}×{n}."
        )
    
    # Caso base: matriz 1×1
    if n == 1:
        return mat_a[0][0]
    
    # Caso base: matriz 2×2 (más eficiente que recursión)
    if n == 2:
        return _determinante_2x2(mat_a)
    
    # Caso recursivo: expansión por la primera fila
    determinante = Fraction(0, 1)
    
    for j in range(n):
        # Elemento de la primera fila
        elemento = mat_a[0][j]
        
        # Si elemento es cero, no aporta al determinante
        if elemento == 0:
            continue
        
        # Crear submatriz sin fila 0 y sin columna j
        submatriz = []
        for i in range(1, n):
            fila_sub = []
            for k in range(n):
                if k != j:
                    fila_sub.append(mat_a[i][k])
            submatriz.append(fila_sub)
        
        # Cofactor = (-1)^(0+j) × det(submatriz)
        signo = Fraction(1, 1) if j % 2 == 0 else Fraction(-1, 1)
        det_sub = determinante_por_cofactores(submatriz)
        cofactor = signo * det_sub
        
        # Acumular en determinante
        determinante += elemento * cofactor
    
    return determinante


def matriz_menores(A):
    """
    Calcula la matriz de menores M de una matriz cuadrada A.

    Procedimiento algebraico: para cada posición (i, j), el menor M[i][j]
    es el determinante de la submatriz obtenida al eliminar la fila i
    y la columna j de A.

    Args:
        A: matriz cuadrada n×n

    Returns:
        list[list[Fraction]]: matriz de menores M (n×n)

    Raises:
        ValueError: si la matriz no es cuadrada o está vacía
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    if m != n:
        raise ValueError(
            f"La matriz de menores solo se define para matrices cuadradas. "
            f"Se recibió una matriz {m}×{n}."
        )
    
    menores = []
    
    for i in range(n):
        fila_menores = []
        
        for j in range(n):
            # Crear submatriz sin fila i y sin columna j
            submatriz = []
            for fila in range(n):
                if fila == i:
                    continue
                fila_sub = []
                for col in range(n):
                    if col == j:
                        continue
                    fila_sub.append(mat_a[fila][col])
                submatriz.append(fila_sub)
            
            # Calcular determinante de la submatriz
            if len(submatriz) == 0:
                # El determinante de la submatriz vacía es 1 por convención.
                menor = Fraction(1, 1)
            else:
                menor = determinante_por_cofactores(submatriz)
            
            fila_menores.append(menor)
        
        menores.append(fila_menores)
    
    return menores


def matriz_cofactores(A):
    """
    Calcula la matriz de cofactores C de una matriz cuadrada A.

    Procedimiento algebraico: para cada posición (i, j), el cofactor C[i][j]
    se define como:
        C[i][j] = (-1)^(i+j) × M[i][j]
    donde M[i][j] es el menor en esa posición.

    Args:
        A: matriz cuadrada n×n

    Returns:
        list[list[Fraction]]: matriz de cofactores C (n×n)

    Raises:
        ValueError: si la matriz no es cuadrada
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    if m != n:
        raise ValueError(
            f"La matriz de cofactores solo se define para matrices cuadradas. "
            f"Se recibió una matriz {m}×{n}."
        )
    
    # Obtener menores
    menores = matriz_menores(mat_a)
    
    # Aplicar el signo (-1)^(i+j) a cada menor
    cofactores = []
    for i in range(n):
        fila_cofactores = []
        for j in range(n):
            signo = Fraction(1, 1) if (i + j) % 2 == 0 else Fraction(-1, 1)
            cofactor = signo * menores[i][j]
            fila_cofactores.append(cofactor)
        cofactores.append(fila_cofactores)
    
    return cofactores


def transponer_matriz(A):
    """
    Calcula la traspuesta de una matriz A: A^T[i][j] = A[j][i].

    Procedimiento algebraico: intercambia filas y columnas.

    Args:
        A: matriz m×n

    Returns:
        list[list[Fraction]]: matriz traspuesta (n×m)

    Raises:
        ValueError: si la matriz está vacía o no es rectangular
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    # Transponer: recorrer columnas y convertirlas en filas
    transpuesta = []
    for j in range(n):
        fila_transpuesta = []
        for i in range(m):
            fila_transpuesta.append(mat_a[i][j])
        transpuesta.append(fila_transpuesta)
    
    return transpuesta


def matriz_adjunta(A):
    """
    Calcula la matriz adjunta Adj(A) de una matriz cuadrada A.

    Procedimiento algebraico: la matriz adjunta es la transpuesta de la
    matriz de cofactores:
        Adj(A) = C^T
    donde C es la matriz de cofactores.

    Args:
        A: matriz cuadrada n×n

    Returns:
        list[list[Fraction]]: matriz adjunta (n×n)

    Raises:
        ValueError: si la matriz no es cuadrada
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    if m != n:
        raise ValueError(
            f"La matriz adjunta solo se define para matrices cuadradas. "
            f"Se recibió una matriz {m}×{n}."
        )
    
    # Obtener cofactores
    cofactores = matriz_cofactores(mat_a)
    
    # Transponer los cofactores
    adjunta = transponer_matriz(cofactores)
    
    return adjunta


def inversa_por_adjunta(A):
    """
    Calcula la inversa de una matriz cuadrada A usando el método de matriz adjunta.

    Procedimiento algebraico: si det(A) ≠ 0, entonces:
        A^-1 = (1/det(A)) × Adj(A)

    Devuelve los pasos intermedios para su presentación en la interfaz:
    1. Matriz original A
    2. Matriz de menores M
    3. Matriz de cofactores C
    4. Matriz adjunta Adj(A) = C^T
    5. Determinante det(A)
    6. Matriz inversa A^-1

    Args:
        A: matriz cuadrada n×n

    Returns:
        tuple: (A_inversa, pasos)
        - A_inversa: list[list[Fraction]], matriz inversa n×n
        - pasos: list of (descripción, matriz) para presentación

    Raises:
        ValueError: si la matriz no es cuadrada o es singular (det = 0)
    """
    mat_a = _matriz_a_fraction(A)
    m, n = _dimensiones(mat_a)
    
    if m != n:
        raise ValueError(
            f"La inversa solo está definida para matrices cuadradas. "
            f"Se recibió una matriz {m}×{n}."
        )
    
    # Calcular determinante
    determinante = determinante_por_cofactores(mat_a)
    
    # Verificar que no sea singular
    if determinante == 0:
        raise ValueError(
            "La matriz es singular (determinante = 0) y no tiene inversa."
        )
    
    # Inicializar pasos
    pasos = [
        ("Matriz original A", [fila[:] for fila in mat_a])
    ]
    
    # Calcular menores
    menores = matriz_menores(mat_a)
    pasos.append(("Matriz de menores M", [fila[:] for fila in menores]))
    
    # Calcular cofactores
    cofactores = matriz_cofactores(mat_a)
    pasos.append(("Matriz de cofactores C", [fila[:] for fila in cofactores]))
    
    # Calcular adjunta (transpuesta de cofactores)
    adjunta = transponer_matriz(cofactores)
    pasos.append(("Matriz adjunta Adj(A) = C^T", [fila[:] for fila in adjunta]))
    
    # Incluir determinante
    pasos.append((f"Determinante det(A) = {determinante}", [fila[:] for fila in mat_a]))
    
    # Calcular inversa: A^-1 = (1/det(A)) × Adj(A)
    escalar_inverso = Fraction(1, 1) / determinante
    inversa = multiplicar_escalar_matriz(escalar_inverso, adjunta)
    
    pasos.append(("Matriz inversa A^-1 = (1/det(A)) × Adj(A)", 
                  [fila[:] for fila in inversa]))
    
    return inversa, pasos
