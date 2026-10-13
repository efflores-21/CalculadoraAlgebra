"""
Verificador de propiedades de matrices: transposición, inversa y determinantes.

Unidad II, Álgebra de matrices [P5 · P6]. Calcula ambos miembros de cada
igualdad con las funciones de la calculadora; cada resultado intermedio (AB, Aᵀ,
A⁻¹, det(A)...) se calcula una vez y se pasa como argumento a las demás funciones.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from fractions import Fraction

from backend.matrices import determinante_triangular, invertir_gauss_jordan
from backend.matriz import _a_fraction
from backend.operaciones_matriciales import (
    _matriz_a_fraction,
    determinante_por_cofactores,
    identidad,
    multiplicar_escalar_matriz,
    multiplicar_matrices,
    son_iguales,
    suma_matrices,
    transponer_matriz,
)

# La expansión por cofactores necesita cerca de n! productos: con n > 8 congelaría la app.
LIMITE_COFACTORES = 8


def _propiedad(nombre, izquierda, derecha):
    """Devuelve el registro de una igualdad con sus dos miembros y si se cumple."""
    return {"nombre": nombre, "izquierda": izquierda, "derecha": derecha,
            "cumple": son_iguales(izquierda, derecha)}


def _no_aplica(nombre, motivo):
    """Devuelve el registro de una igualdad que no se puede evaluar con estos datos."""
    return {"nombre": nombre, "motivo": motivo, "cumple": None}


def determinante(M):
    """Devuelve det(M) por reducción a forma triangular (método eficiente y exacto)."""
    return determinante_triangular(M)[0]


def inversa_o_nada(M):
    """Devuelve M⁻¹ por Gauss-Jordan, o None si M es singular."""
    try:
        return invertir_gauss_jordan(M)[0]
    except ValueError:
        return None


def triangular_superior(A):
    """Lleva A a una matriz triangular superior T con intercambios y reemplazos de fila.
    Devuelve (T, número de intercambios)."""
    matriz_T = [fila[:] for fila in A]
    n = len(matriz_T)
    intercambios = 0
    for columna in range(n):
        fila_pivote = next((i for i in range(columna, n) if matriz_T[i][columna] != 0), None)
        if fila_pivote is None:
            continue
        if fila_pivote != columna:
            matriz_T[columna], matriz_T[fila_pivote] = matriz_T[fila_pivote], matriz_T[columna]
            intercambios += 1
        for i in range(columna + 1, n):
            multiplicador = matriz_T[i][columna] / matriz_T[columna][columna]
            matriz_T[i] = [a - multiplicador * p for a, p in zip(matriz_T[i], matriz_T[columna])]
    return matriz_T, intercambios


def propiedades_transposicion(A, B, C, k, AB, A_T, B_T):
    """Evalúa las seis propiedades de operaciones y transposición."""
    return [
        _propiedad("(Aᵀ)ᵀ = A", transponer_matriz(A_T), A),
        _propiedad("(A + B)ᵀ = Aᵀ + Bᵀ", transponer_matriz(suma_matrices(A, B)), suma_matrices(A_T, B_T)),
        _propiedad("(kA)ᵀ = kAᵀ", transponer_matriz(multiplicar_escalar_matriz(k, A)),
                   multiplicar_escalar_matriz(k, A_T)),
        _propiedad("(AB)ᵀ = BᵀAᵀ", transponer_matriz(AB), multiplicar_matrices(B_T, A_T)),
        _propiedad("A(B + C) = AB + AC", multiplicar_matrices(A, suma_matrices(B, C)),
                   suma_matrices(AB, multiplicar_matrices(A, C))),
        _propiedad("(AB)C = A(BC)", multiplicar_matrices(AB, C),
                   multiplicar_matrices(A, multiplicar_matrices(B, C))),
    ]


def propiedades_inversa(A, AB, A_T, A_inv, B_inv):
    """Evalúa las cuatro propiedades de la inversa (no aplican si A o B son singulares)."""
    nombres = ["(A⁻¹)⁻¹ = A", "(AB)⁻¹ = B⁻¹A⁻¹", "(Aᵀ)⁻¹ = (A⁻¹)ᵀ", "A · A⁻¹ = I"]
    if A_inv is None:
        return [_no_aplica(nombre, "A es singular (det(A) = 0): no tiene inversa.") for nombre in nombres]
    if B_inv is None:
        producto = _no_aplica(nombres[1], "B es singular (det(B) = 0): no tiene inversa.")
    else:
        producto = _propiedad(nombres[1], inversa_o_nada(AB), multiplicar_matrices(B_inv, A_inv))
    return [
        _propiedad(nombres[0], inversa_o_nada(A_inv), A),
        producto,
        _propiedad(nombres[2], inversa_o_nada(A_T), transponer_matriz(A_inv)),
        _propiedad(nombres[3], multiplicar_matrices(A, A_inv), identidad(len(A))),
    ]


def propiedades_determinante(A, B, k, AB, A_T, A_inv, det_A):
    """Evalúa det(Aᵀ), det(AB), det(A⁻¹) y det(kA) contra sus fórmulas."""
    n = len(A)
    lista = [
        _propiedad("det(Aᵀ) = det(A)", determinante(A_T), det_A),
        _propiedad("det(AB) = det(A) · det(B)", determinante(AB), det_A * determinante(B)),
    ]
    if A_inv is None:
        lista.append(_no_aplica("det(A⁻¹) = 1/det(A)", "A es singular: A⁻¹ y 1/det(A) no existen."))
    else:
        lista.append(_propiedad("det(A⁻¹) = 1/det(A)", determinante(A_inv), Fraction(1) / det_A))
    lista.append(_propiedad(f"det(kA) = kⁿ det(A)   (n = {n})",
                            determinante(multiplicar_escalar_matriz(k, A)), k ** n * det_A))
    return lista


def propiedades_operaciones_fila(A, det_A, fila_i, fila_j, k):
    """Evalúa el efecto de permutar, reemplazar y escalar una fila sobre el determinante."""
    nombre_i, nombre_j = f"F{fila_i + 1}", f"F{fila_j + 1}"
    escalada = [fila[:] for fila in A]
    escalada[fila_i] = [k * valor for valor in escalada[fila_i]]
    escalar = _propiedad(f"{nombre_i} ← k·{nombre_i}: det = k · det(A)", determinante(escalada), k * det_A)
    if fila_i == fila_j:
        motivo = "Elige dos filas distintas (i ≠ j)."
        return [_no_aplica("Permutación: det = −det(A)", motivo),
                _no_aplica("Reemplazo: det = det(A)", motivo), escalar]
    permutada = [fila[:] for fila in A]
    permutada[fila_i], permutada[fila_j] = permutada[fila_j], permutada[fila_i]
    reemplazada = [fila[:] for fila in A]
    reemplazada[fila_i] = [a + k * b for a, b in zip(A[fila_i], A[fila_j])]
    return [
        _propiedad(f"{nombre_i} ↔ {nombre_j}: det = −det(A)", determinante(permutada), -det_A),
        _propiedad(f"{nombre_i} ← {nombre_i} + k·{nombre_j}: det = det(A)", determinante(reemplazada), det_A),
        escalar,
    ]


def propiedad_triangular(A):
    """Compara det(T) por cofactores con el producto de la diagonal de T (T triangular).
    Devuelve (registro, T, intercambios)."""
    matriz_T, intercambios = triangular_superior(A)
    producto_diagonal = Fraction(1)
    for i in range(len(matriz_T)):
        producto_diagonal *= matriz_T[i][i]
    nombre = "det(T) = producto de la diagonal (T triangular)"
    if len(A) > LIMITE_COFACTORES:
        registro = _no_aplica(nombre, f"La expansión por cofactores se omite para n > {LIMITE_COFACTORES}.")
    else:
        registro = _propiedad(nombre, determinante_por_cofactores(matriz_T), producto_diagonal)
    return registro, matriz_T, intercambios


def verificar_propiedades_matrices(A, B, C, k, fila_i, fila_j):
    """Evalúa todas las propiedades con A, B y C cuadradas del mismo orden.
    Devuelve una lista de (categoría, lista de registros) y datos extra para mostrar."""
    A, B, C = (_matriz_a_fraction(M) for M in (A, B, C))
    n = len(A)
    if any(len(M) != n or len(M[0]) != n for M in (A, B, C)):
        raise ValueError("El verificador necesita A, B y C cuadradas y del mismo orden (n × n).")
    if not (0 <= fila_i < n and 0 <= fila_j < n):
        raise ValueError(f"Las filas i y j deben estar entre 1 y {n}.")
    k = _a_fraction(k)
    # Cada resultado intermedio se calcula una sola vez y se reutiliza en varias igualdades.
    AB = multiplicar_matrices(A, B)
    A_T, B_T = transponer_matriz(A), transponer_matriz(B)
    A_inv, B_inv = inversa_o_nada(A), inversa_o_nada(B)
    det_A = determinante(A)
    triangular, matriz_T, intercambios = propiedad_triangular(A)
    categorias = [
        ("OPERACIONES Y TRANSPOSICIÓN", propiedades_transposicion(A, B, C, k, AB, A_T, B_T)),
        ("MATRIZ INVERSA", propiedades_inversa(A, AB, A_T, A_inv, B_inv)),
        ("DETERMINANTES", propiedades_determinante(A, B, k, AB, A_T, A_inv, det_A)),
        ("EFECTO DE LAS OPERACIONES DE FILA", propiedades_operaciones_fila(A, det_A, fila_i, fila_j, k)),
        ("MATRIZ TRIANGULAR", [triangular]),
    ]
    extra = {"det_A": det_A, "T": matriz_T, "intercambios": intercambios}
    return categorias, extra
