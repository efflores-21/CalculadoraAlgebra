"""
Determinantes (triangular, cofactores, Sarrus) e inversas (Gauss-Jordan y adjunta).

Unidad II, Álgebra de matrices y determinantes [P5].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from fractions import Fraction

from backend.matriz import _a_fraction, formatear_valor


def _validar_cuadrada(A):
    """Devuelve una copia exacta de A y valida que sea cuadrada y no vacía."""
    if A is None or len(A) == 0:
        raise ValueError("La matriz no puede estar vacía.")
    n = len(A)
    if any(fila is None or len(fila) != n for fila in A):
        raise ValueError("La operación requiere una matriz cuadrada.")
    return [[_a_fraction(valor) for valor in fila] for fila in A]


def transponer_matriz(A):
    """Devuelve la transpuesta de una matriz rectangular."""
    from backend.operaciones_matriciales import transponer_matriz as transponer
    return transponer(A)


def determinante_cofactores(A):
    """Calcula el determinante por expansión recursiva de cofactores."""
    from backend.operaciones_matriciales import determinante_por_cofactores
    return determinante_por_cofactores(A)


def sarrus_3x3(A):
    """Calcula el determinante 3×3 mediante la regla de Sarrus."""
    matriz = _validar_cuadrada(A)
    if len(matriz) != 3:
        raise ValueError("La regla de Sarrus solo se aplica a matrices 3×3.")
    a, b, c = matriz[0]
    d, e, f = matriz[1]
    g, h, i = matriz[2]
    return a * e * i + b * f * g + c * d * h - c * e * g - b * d * i - a * f * h


def determinante_triangular(A):
    """Calcula el determinante por eliminación triangular y registra sus pasos."""
    matriz = _validar_cuadrada(A)
    n = len(matriz)
    pasos = [("Matriz inicial", [fila[:] for fila in matriz])]
    signo = 1
    producto_pivotes = Fraction(1)
    for columna in range(n):
        fila_pivote = next(
            (fila for fila in range(columna, n) if matriz[fila][columna] != 0), None
        )
        if fila_pivote is None:
            pasos.append((f"No hay pivote en columna {columna + 1}; det(A)=0.",
                          [fila[:] for fila in matriz]))
            return Fraction(0), pasos
        if fila_pivote != columna:
            matriz[columna], matriz[fila_pivote] = matriz[fila_pivote], matriz[columna]
            signo *= -1
            pasos.append((f"Intercambiar F{columna + 1} y F{fila_pivote + 1}; cambia el signo.",
                          [fila[:] for fila in matriz]))
        pivote = matriz[columna][columna]
        producto_pivotes *= pivote
        pasos.append((f"Pivote {columna + 1}: {formatear_valor(pivote)}.",
                      [fila[:] for fila in matriz]))
        for fila in range(columna + 1, n):
            if matriz[fila][columna] != 0:
                factor = matriz[fila][columna] / pivote
                for j in range(columna, n):
                    matriz[fila][j] -= factor * matriz[columna][j]
                pasos.append((f"F{fila + 1} <- F{fila + 1} - ({formatear_valor(factor)})F{columna + 1}.",
                              [fila_actual[:] for fila_actual in matriz]))
    resultado = signo * producto_pivotes
    pasos.append((f"det(A) = {signo} por {formatear_valor(producto_pivotes)} = {formatear_valor(resultado)}.",
                  [fila[:] for fila in matriz]))
    return resultado, pasos


def matriz_menores(A):
    """Devuelve la matriz de menores de una matriz cuadrada."""
    from backend.operaciones_matriciales import matriz_menores as calcular_menores
    return calcular_menores(A)


def matriz_cofactores(A):
    """Devuelve la matriz de cofactores con el patrón alternado de signos."""
    from backend.operaciones_matriciales import matriz_cofactores as calcular_cofactores
    return calcular_cofactores(A)


def invertir_gauss_jordan(A):
    """Calcula A⁻¹ por Gauss-Jordan y devuelve la inversa y los pasos."""
    matriz = _validar_cuadrada(A)
    n = len(matriz)
    aumentada = [fila + [Fraction(int(i == j)) for j in range(n)]
                 for i, fila in enumerate(matriz)]
    pasos = [("Matriz aumentada inicial [A|I]", [fila[:] for fila in aumentada])]
    for columna in range(n):
        fila_pivote = next(
            (fila for fila in range(columna, n) if aumentada[fila][columna] != 0), None
        )
        if fila_pivote is None:
            raise ValueError("La matriz es singular; no tiene inversa.")
        if fila_pivote != columna:
            aumentada[columna], aumentada[fila_pivote] = aumentada[fila_pivote], aumentada[columna]
            pasos.append((f"Intercambiar F{columna + 1} y F{fila_pivote + 1}",
                          [fila[:] for fila in aumentada]))
        pivote = aumentada[columna][columna]
        aumentada[columna] = [valor / pivote for valor in aumentada[columna]]
        pasos.append((f"Dividir F{columna + 1} entre {formatear_valor(pivote)}",
                      [fila[:] for fila in aumentada]))
        for fila in range(n):
            if fila != columna and aumentada[fila][columna] != 0:
                factor = aumentada[fila][columna]
                aumentada[fila] = [aumentada[fila][j] - factor * aumentada[columna][j]
                                   for j in range(2 * n)]
                pasos.append((f"F{fila + 1} <- F{fila + 1} - ({formatear_valor(factor)})F{columna + 1}",
                              [r[:] for r in aumentada]))
    return [fila[n:] for fila in aumentada], pasos


def invertir_adjunta(A):
    """Calcula A⁻¹ mediante cofactores, adjunta y determinante."""
    from backend.operaciones_matriciales import inversa_por_adjunta
    return inversa_por_adjunta(A)


def verificar_inversa(A, inversa, multiplicar_matrices):
    """Compara A·A⁻¹ con la identidad usando el producto matricial recibido."""
    matriz = _validar_cuadrada(A)
    candidata = _validar_cuadrada(inversa)
    if len(matriz) != len(candidata):
        raise ValueError("A y su inversa deben tener el mismo orden.")
    producto = multiplicar_matrices(matriz, candidata)
    identidad = [[Fraction(int(i == j)) for j in range(len(matriz))]
                 for i in range(len(matriz))]
    return producto, identidad, producto == identidad
