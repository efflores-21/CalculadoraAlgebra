"""Verificación exacta de propiedades del producto matriz-vector."""

from backend.matriz import _a_fraction
from backend.vectores import suma_vectores, multiplicar_escalar_vector
from backend.operaciones_matriciales import multiplicar_matriz_vector


def verificar_propiedades(A, u, v, c):
    """
    Verifica la linealidad del producto matriz-vector.

    Procedimiento algebraico equivalente: una matriz A de tamaño m×n define
    una transformación lineal de R^n en R^m. Por esa razón debe cumplir:

        A(u + v) = A·u + A·v
        A(cu) = c(A·u).

    La función calcula y devuelve todos los vectores intermedios para que la
    interfaz pueda mostrar cada paso. La comparación se realiza exactamente
    sobre listas de Fraction, sin tolerancias de punto flotante.

    Args:
        A: matriz rectangular m×n.
        u: vector de n componentes.
        v: vector de n componentes.
        c: escalar convertible a Fraction.

    Returns:
        dict: resultados y pasos intermedios de ambas propiedades.

    Raises:
        ValueError: si A no es rectangular o las dimensiones son incompatibles.
    """
    if A is None or len(A) == 0:
        raise ValueError("La matriz A no puede estar vacía.")
    if A[0] is None or len(A[0]) == 0:
        raise ValueError("La matriz A debe tener al menos una columna.")

    matriz = []
    columnas = len(A[0])
    for indice, fila in enumerate(A):
        if fila is None or len(fila) != columnas:
            raise ValueError(
                f"A no es rectangular: la fila {indice + 1} no tiene "
                f"{columnas} columnas."
            )
        matriz.append([_a_fraction(valor) for valor in fila])

    if u is None or v is None:
        raise ValueError("Los vectores u y v no pueden estar vacíos.")
    vector_u = [_a_fraction(valor) for valor in u]
    vector_v = [_a_fraction(valor) for valor in v]
    if len(vector_u) != len(vector_v):
        raise ValueError(
            f"Dimensiones incompatibles: u tiene {len(vector_u)} componentes "
            f"pero v tiene {len(vector_v)}."
        )
    if columnas != len(vector_u):
        raise ValueError(
            f"Dimensiones incompatibles: A tiene {columnas} columnas "
            f"pero u tiene {len(vector_u)} componentes."
        )

    escalar = _a_fraction(c)
    u_mas_v = suma_vectores(vector_u, vector_v)
    au = multiplicar_matriz_vector(matriz, vector_u)
    av = multiplicar_matriz_vector(matriz, vector_v)
    a_por_u_mas_v = multiplicar_matriz_vector(matriz, u_mas_v)
    au_mas_av = suma_vectores(au, av)

    c_por_u = multiplicar_escalar_vector(escalar, vector_u)
    a_por_cu = multiplicar_matriz_vector(matriz, c_por_u)
    c_por_au = multiplicar_escalar_vector(escalar, au)

    return {
        "a_u_mas_v": u_mas_v,
        "a_Au": au,
        "a_Av": av,
        "a_A_por_u_mas_v": a_por_u_mas_v,
        "a_Au_mas_Av": au_mas_av,
        "a_se_cumple": a_por_u_mas_v == au_mas_av,
        "b_c_por_u": c_por_u,
        "b_Au": au,
        "b_A_por_cu": a_por_cu,
        "b_c_por_Au": c_por_au,
        "b_se_cumple": a_por_cu == c_por_au,
    }
