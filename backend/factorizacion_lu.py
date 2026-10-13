"""
Factorización LU (A = LU) y solución de Ax = b por doble sustitución.

Unidad II, Álgebra de matrices [P6]. Reutiliza el producto matricial,
la comprobación de igualdad y la eliminación de Gauss-Jordan de la calculadora.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

from backend.clasificador import clasificar_sistema
from backend.eliminacion import resolver_sistema
from backend.matriz import _a_fraction, formatear_valor
from backend.operaciones_matriciales import (
    _matriz_a_fraction,
    identidad,
    multiplicar_matrices,
    multiplicar_matriz_vector,
    son_iguales,
)

MENSAJE_PERMUTACION = (
    "La matriz no admite Factorización LU sin permutación "
    "(requiere pivoteo parcial PA = LU)."
)


def factorizar_lu(A):
    """Reduce A (m×n) a su forma escalonada U solo con reemplazos de fila y guarda
    cada multiplicador en L (m×m). Devuelve (matriz_L, matriz_U, pasos)."""
    matriz_U = _matriz_a_fraction(A)
    m, n = len(matriz_U), len(matriz_U[0])
    matriz_L = identidad(m)
    pasos = []
    fila_pivote = 0
    for columna in range(n):
        if fila_pivote == m:
            break
        pivote = matriz_U[fila_pivote][columna]
        if pivote == 0:
            # Con un cero en la posición pivote solo un intercambio de filas permitiría
            # seguir, y eso ya no es A = LU sino PA = LU.
            if any(matriz_U[i][columna] != 0 for i in range(fila_pivote + 1, m)):
                raise ValueError(MENSAJE_PERMUTACION)
            continue
        for i in range(fila_pivote + 1, m):
            multiplicador_l = matriz_U[i][columna] / pivote
            if multiplicador_l == 0:
                continue
            # Se registra el multiplicador en L antes de alterar la fila en U.
            matriz_L[i][fila_pivote] = multiplicador_l
            matriz_U[i] = [
                valor - multiplicador_l * valor_pivote
                for valor, valor_pivote in zip(matriz_U[i], matriz_U[fila_pivote])
            ]
            pasos.append((
                f"F{i + 1} ← F{i + 1} − ({formatear_valor(multiplicador_l)})·F{fila_pivote + 1}"
                f"   →   l{i + 1}{fila_pivote + 1} = {formatear_valor(multiplicador_l)}",
                [fila[:] for fila in matriz_U],
            ))
        fila_pivote += 1
    return matriz_L, matriz_U, pasos


def resolver_por_reduccion(matriz, vector):
    """Reduce [matriz | vector] con Gauss-Jordan (sin reordenar filas).
    Devuelve (resultado de resolver_sistema, clasificación del sistema)."""
    aumentada = [fila[:] + [valor] for fila, valor in zip(matriz, vector)]
    resultado = resolver_sistema(aumentada, metodo="gauss-jordan", pivoteo_parcial=False)
    clase = clasificar_sistema(resultado["matriz_escalonada"], resultado["rango"])
    return resultado, clase


def resolver_lu(A, b):
    """Factoriza A = LU, verifica L·U == A y, si A es cuadrada, resuelve Ly = b y Ux = y.
    Devuelve un diccionario con L, U, los pasos, y, x y las comprobaciones."""
    matriz_A = _matriz_a_fraction(A)
    if b is None or len(b) != len(matriz_A):
        raise ValueError("El vector b debe tener una componente por cada fila de A.")
    vector_b = [_a_fraction(valor) for valor in b]
    matriz_L, matriz_U, pasos = factorizar_lu(matriz_A)
    producto_LU = multiplicar_matrices(matriz_L, matriz_U)
    datos = {
        "L": matriz_L, "U": matriz_U, "pasos": pasos, "LU": producto_LU,
        "factorizacion_correcta": son_iguales(producto_LU, matriz_A),
        "cuadrada": len(matriz_A) == len(matriz_A[0]),
    }
    if not datos["cuadrada"]:
        return datos

    # L es triangular inferior con unos en la diagonal: Ly = b siempre tiene solución única.
    etapa_y, _ = resolver_por_reduccion(matriz_L, vector_b)
    vector_y = [etapa_y["soluciones_generales"][j][0] for j in range(len(matriz_L))]
    etapa_x, clase_x = resolver_por_reduccion(matriz_U, vector_y)
    datos.update({"etapa_y": etapa_y, "y": vector_y, "etapa_x": etapa_x, "clase_x": clase_x})
    if clase_x["tipo"] != "Consistente Determinado":
        return datos

    vector_x = [etapa_x["soluciones_generales"][j][0] for j in range(len(matriz_U))]
    producto_Ax = multiplicar_matriz_vector(matriz_A, vector_x)
    datos.update({"x": vector_x, "Ax": producto_Ax,
                  "comprobacion": son_iguales(producto_Ax, vector_b)})
    return datos
