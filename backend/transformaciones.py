"""
Transformaciones lineales T(x) = A·x: linealidad, núcleo, imagen, rango y nulidad.

Unidad III, Transformaciones lineales [P7].
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from fractions import Fraction

from backend.clasificador import clasificar_sistema, columnas_pivote
from backend.eliminacion import eliminacion_con_pasos
from backend.matriz import _a_fraction


def validar_matriz(A):
    """Convierte A a fracciones y exige que todas las filas tengan el mismo largo."""
    if not A or not A[0]:
        raise ValueError("La matriz A no puede estar vacía.")
    if any(len(fila) != len(A[0]) for fila in A):
        raise ValueError("Todas las filas de A deben tener el mismo número de columnas.")
    return [[_a_fraction(valor) for valor in fila] for fila in A]


def aplicar(A, x):
    """Calcula T(x) = A·x (cada componente es una fila de A por x)."""
    if len(x) != len(A[0]):
        raise ValueError(f"El vector debe tener {len(A[0])} componentes (una por columna de A).")
    return [sum((a * xi for a, xi in zip(fila, x)), Fraction(0)) for fila in A]


def verificar_linealidad(A, u, v, c):
    """Calcula ambos lados de T(u+v) = T(u)+T(v) y de T(c·u) = c·T(u)."""
    Tu, Tv = aplicar(A, u), aplicar(A, v)
    suma = [a + b for a, b in zip(u, v)]
    escalado = [c * a for a in u]
    datos = {
        "u+v": suma, "T(u+v)": aplicar(A, suma), "T(u)": Tu, "T(v)": Tv,
        "T(u)+T(v)": [a + b for a, b in zip(Tu, Tv)],
        "c·u": escalado, "T(c·u)": aplicar(A, escalado), "c·T(u)": [c * a for a in Tu],
    }
    datos["cumple_suma"] = datos["T(u+v)"] == datos["T(u)+T(v)"]
    datos["cumple_escalar"] = datos["T(c·u)"] == datos["c·T(u)"]
    return datos


def reducir(A):
    """Reduce [A|0] por Gauss-Jordan y devuelve (R, rango, columnas pivote, pasos)."""
    aumentada = [fila + [Fraction(0)] for fila in A]
    R, rango, pasos = eliminacion_con_pasos(aumentada, metodo="gauss-jordan", verbose=False)
    return R, rango, columnas_pivote(R, rango), pasos


def base_nucleo(R, pivotes, n):
    """Un vector por variable libre: esa libre vale 1, las demás libres 0."""
    libres = [j for j in range(n) if j not in pivotes]
    base = []
    for libre in libres:
        x = [Fraction(0)] * n
        x[libre] = Fraction(1)
        # En la forma reducida cada pivote vale 1: x_pivote = −(coeficiente de la libre).
        for fila, pivote in enumerate(pivotes):
            x[pivote] = -R[fila][libre]
        base.append(x)
    return libres, base


def base_imagen(A, pivotes):
    """Las columnas de la A ORIGINAL en las posiciones pivote forman una base de Im(T)."""
    return [[fila[j] for fila in A] for j in pivotes]


def esta_en_imagen(A, b):
    """Resuelve A·x = b: devuelve (está, x particular o None, R de [A|b])."""
    if len(b) != len(A):
        raise ValueError(f"El vector b debe tener {len(A)} componentes (una por fila de A).")
    aumentada = [fila + [b_i] for fila, b_i in zip(A, b)]
    R, rango, _ = eliminacion_con_pasos(aumentada, metodo="gauss-jordan", verbose=False)
    if clasificar_sistema(R, rango)["tipo"] == "Inconsistente":
        return False, None, R
    n = len(A[0])
    x = [Fraction(0)] * n
    for fila, pivote in enumerate(columnas_pivote(R, rango)):
        x[pivote] = R[fila][n]
    return True, x, R


def analizar(A):
    """Rango, nulidad, bases del núcleo y la imagen, y el teorema de la dimensión."""
    A = validar_matriz(A)
    m, n = len(A), len(A[0])
    R, rango, pivotes, pasos = reducir(A)
    libres, nucleo = base_nucleo(R, pivotes, n)
    return {
        "m": m, "n": n, "R": R, "pasos": pasos, "rango": rango, "pivotes": pivotes,
        "libres": libres, "base_nucleo": nucleo, "base_imagen": base_imagen(A, pivotes),
        "nulidad": len(libres), "cumple_dimension": rango + len(libres) == n,
        "inyectiva": not libres, "sobreyectiva": rango == m,
    }
