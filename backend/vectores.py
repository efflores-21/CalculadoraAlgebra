"""
Operaciones con vectores en R^n.

Todas las componentes se representan con fractions.Fraction para conservar
exactitud racional (sin redondeo de punto flotante).
"""

from backend.matriz import _a_fraction


def _vector_a_fraction(v):
    """Convierte cada componente de un vector a Fraction."""
    if v is None or len(v) == 0:
        raise ValueError("El vector no puede estar vacío.")
    return [_a_fraction(componente) for componente in v]


def suma_vectores(v1, v2):
    """
    Suma de vectores u + v en R^n.

    Operación algebraica: si u = (u₁, ..., uₙ) y v = (v₁, ..., vₙ),
        u + v = (u₁ + v₁, ..., uₙ + vₙ).
    Requiere que ambos vectores tengan la misma dimensión n.

    Args:
        v1: primer vector (iterable de números).
        v2: segundo vector (iterable de números).

    Returns:
        list[Fraction]: vector suma.

    Raises:
        ValueError: si las dimensiones no coinciden o algún vector está vacío.
    """
    u = _vector_a_fraction(v1)
    v = _vector_a_fraction(v2)
    if len(u) != len(v):
        raise ValueError(
            f"Dimensiones incompatibles para la suma: dim(v₁)={len(u)} ≠ dim(v₂)={len(v)}."
        )
    return [u[i] + v[i] for i in range(len(u))]


def resta_vectores(v1, v2):
    """
    Resta de vectores u − v en R^n.

    Operación algebraica: si u = (u₁, ..., uₙ) y v = (v₁, ..., vₙ),
        u − v = (u₁ − v₁, ..., uₙ − vₙ).
    Equivale a u + (−1)·v. Requiere la misma dimensión n.

    Args:
        v1: minuendo.
        v2: sustraendo.

    Returns:
        list[Fraction]: vector diferencia.

    Raises:
        ValueError: si las dimensiones no coinciden o algún vector está vacío.
    """
    u = _vector_a_fraction(v1)
    v = _vector_a_fraction(v2)
    if len(u) != len(v):
        raise ValueError(
            f"Dimensiones incompatibles para la resta: dim(v₁)={len(u)} ≠ dim(v₂)={len(v)}."
        )
    return [u[i] - v[i] for i in range(len(u))]


def multiplicar_escalar_vector(k, v):
    """
    Multiplicación de un vector por un escalar: k·v.

    Operación algebraica: si v = (v₁, ..., vₙ) y k ∈ Q,
        k·v = (k·v₁, ..., k·vₙ).
    Geométricamente, escala el vector (y lo invierte si k < 0).

    Args:
        k: escalar.
        v: vector.

    Returns:
        list[Fraction]: vector escalado.

    Raises:
        ValueError: si el vector está vacío.
    """
    vector = _vector_a_fraction(v)
    escalar = _a_fraction(k)
    return [escalar * componente for componente in vector]


def es_combinacion_lineal(b, vectores):
    """
    Construye el sistema que decide si b es combinación lineal de {v₁, ..., vₖ}.

    Operación algebraica: b es combinación lineal de esos vectores si existen
    escalares c₁, ..., cₖ tales que
        c₁·v₁ + c₂·v₂ + ... + cₖ·vₖ = b.
    En forma matricial esto es A·c = b, donde las COLUMNAS de A son v₁, ..., vₖ.
    Se devuelve la matriz aumentada [A | b] para resolverla con el solver
    de eliminación existente (Gauss / Gauss-Jordan).

    El sistema es consistente  ⇔  b SÍ es combinación lineal.
    Si además no hay variables libres, los cᵢ son únicos.

    Args:
        b: vector objetivo en R^n.
        vectores: lista de k vectores en R^n.

    Returns:
        list[list[Fraction]]: matriz aumentada [A | b] de tamaño n × (k+1).

    Raises:
        ValueError: si no hay vectores, están vacíos o las dimensiones no coinciden.
    """
    if not vectores:
        raise ValueError("Se necesita al menos un vector para la combinación lineal.")

    objetivo = _vector_a_fraction(b)
    n = len(objetivo)
    columnas = []
    for indice, vector in enumerate(vectores):
        convertido = _vector_a_fraction(vector)
        if len(convertido) != n:
            raise ValueError(
                f"Dimensiones incompatibles: dim(b)={n} ≠ dim(v{indice + 1})={len(convertido)}."
            )
        columnas.append(convertido)

    k = len(columnas)
    matriz_aumentada = []
    for i in range(n):
        fila = [columnas[j][i] for j in range(k)]
        fila.append(objetivo[i])
        matriz_aumentada.append(fila)
    return matriz_aumentada
