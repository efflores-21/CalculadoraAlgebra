"""
Métodos iterativos de Jacobi y Gauss-Seidel para resolver Ax = b.

Unidad III, Métodos numéricos [P8]: validación de datos, diagonal estrictamente
dominante, reordenamiento de ecuaciones, criterio de parada ‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞ ≤ ε,
residuo ‖Ax − b‖∞ y solución de referencia por Gauss-Jordan.
Autores: Grupo 6 (Franklin Callejas, Daniella Rocha, Elías Flores, Daris Mayorga, Yaritza Reyes).
"""

import math
from fractions import Fraction

from backend.eliminacion import eliminacion_con_pasos

MAX_ITERACIONES = 10000
# Si el error supera este valor el método ya divergió: seguir solo llevaría a overflow.
LIMITE_DIVERGENCIA = 1e100


def _finito(valor, nombre):
    """Convierte un dato a float y exige que sea un número real finito."""
    try:
        convertido = float(valor)
    except (TypeError, ValueError, OverflowError) as error:
        raise ValueError(f"{nombre} debe ser un número real.") from error
    if not math.isfinite(convertido):
        raise ValueError(f"{nombre} debe ser un número real finito.")
    return convertido


def validar_datos(A, b, x0, tolerancia, max_iteraciones):
    """Valida dimensiones, tolerancia y máximo; devuelve todo como float."""
    n = len(A)
    if n == 0 or any(len(fila) != n for fila in A):
        raise ValueError("La matriz A debe ser cuadrada (n × n).")
    if len(b) != n:
        raise ValueError(f"El vector b debe tener {n} componentes, una por ecuación.")
    if len(x0) != n:
        raise ValueError(f"El vector inicial x⁽⁰⁾ debe tener {n} componentes, una por incógnita.")
    tolerancia = _finito(tolerancia, "La tolerancia ε")
    if tolerancia <= 0:
        raise ValueError("La tolerancia ε debe ser positiva.")
    if isinstance(max_iteraciones, bool) or not isinstance(max_iteraciones, int) \
            or not 1 <= max_iteraciones <= MAX_ITERACIONES:
        raise ValueError(f"El máximo de iteraciones debe ser un entero entre 1 y {MAX_ITERACIONES}.")
    A = [[_finito(v, f"La entrada ({i + 1},{j + 1}) de A") for j, v in enumerate(fila)] for i, fila in enumerate(A)]
    b = [_finito(v, f"La componente {i + 1} de b") for i, v in enumerate(b)]
    x0 = [_finito(v, f"La componente {i + 1} de x⁽⁰⁾") for i, v in enumerate(x0)]
    return A, b, x0, tolerancia


def ceros_en_diagonal(A):
    """Índices (base 0) de las filas con aᵢᵢ = 0."""
    return [i for i in range(len(A)) if A[i][i] == 0]


def dominancia_por_filas(A):
    """Para cada fila: (|aᵢᵢ|, suma de |aᵢⱼ| con j ≠ i, ¿es estrictamente mayor?)."""
    filas = []
    for i, fila in enumerate(A):
        diagonal = abs(fila[i])
        resto = sum(abs(valor) for j, valor in enumerate(fila) if j != i)
        filas.append((diagonal, resto, diagonal > resto))
    return filas


def es_diagonal_dominante(A):
    """True si |aᵢᵢ| > Σⱼ≠ᵢ |aᵢⱼ| en todas las filas."""
    return all(cumple for _, _, cumple in dominancia_por_filas(A))


def _orden_dominante(A):
    """Orden de filas que deja A estrictamente dominante, o None si no existe."""
    # Una fila solo puede dominar en una columna: la de su valor absoluto mayor.
    n = len(A)
    destino = [None] * n
    for fila_original, fila in enumerate(A):
        total = sum(abs(valor) for valor in fila)
        columna = max(range(n), key=lambda j: abs(fila[j]))
        if abs(fila[columna]) <= total - abs(fila[columna]) or destino[columna] is not None:
            return None
        destino[columna] = fila_original
    return destino


def _orden_sin_ceros(A):
    """Orden de filas sin ceros en la diagonal (emparejamiento fila-columna), o None."""
    n = len(A)
    fila_de_columna = [None] * n

    def asignar(fila, visitadas):
        # Prueba primero las columnas con el coeficiente más grande de esa fila.
        for columna in sorted(range(n), key=lambda j: -abs(A[fila][j])):
            if A[fila][columna] == 0 or columna in visitadas:
                continue
            visitadas.add(columna)
            if fila_de_columna[columna] is None or asignar(fila_de_columna[columna], visitadas):
                fila_de_columna[columna] = fila
                return True
        return False

    for fila in range(n):
        if not asignar(fila, set()):
            return None
    return fila_de_columna


def buscar_reordenamiento(A):
    """
    Busca un orden de las ecuaciones mejor que el actual.

    Devuelve (orden, motivo): `orden[i]` es la fila original que pasa a la
    posición i, o None si no hace falta o no existe un orden adecuado.
    """
    identidad = list(range(len(A)))
    dominante = _orden_dominante(A)
    if dominante is not None:
        if dominante == identidad:
            return None, "La matriz ya es estrictamente dominante: no hace falta reordenar."
        return dominante, "Se encontró un orden que hace la matriz estrictamente dominante por filas."
    if not ceros_en_diagonal(A):
        return None, ("No existe un orden de las ecuaciones que haga la matriz estrictamente dominante; "
                      "se conserva el orden original (sin ceros en la diagonal).")
    sin_ceros = _orden_sin_ceros(A)
    if sin_ceros is None:
        return None, ("No se encontró ningún orden de las ecuaciones sin ceros en la diagonal: "
                      "ningún reordenamiento permite aplicar Jacobi ni Gauss-Seidel.")
    return sin_ceros, ("No existe un orden estrictamente dominante, pero sí uno sin ceros en la diagonal; "
                       "la convergencia no está garantizada.")


def aplicar_orden(orden, A, b):
    """Reordena las filas de A y las componentes de b según `orden`."""
    return [A[i][:] for i in orden], [b[i] for i in orden]


def norma_infinito(v):
    """‖v‖∞ = máximo valor absoluto de sus componentes."""
    return max(abs(valor) for valor in v)


def residuo(A, x, b):
    """‖Ax − b‖∞ para comprobar qué tan bien x satisface el sistema."""
    return norma_infinito([sum(a * xi for a, xi in zip(fila, x)) - bi for fila, bi in zip(A, b)])


def _paso_jacobi(A, b, x):
    """Una iteración de Jacobi: todos los componentes salen de la iteración anterior."""
    n = len(A)
    return [(b[i] - sum(A[i][j] * x[j] for j in range(n) if j != i)) / A[i][i] for i in range(n)]


def _paso_gauss_seidel(A, b, x):
    """Una iteración de Gauss-Seidel: cada componente nuevo se usa de inmediato."""
    n = len(A)
    nuevo = x[:]
    for i in range(n):
        # nuevo[j] ya está actualizado para j < i y aún es el anterior para j > i.
        nuevo[i] = (b[i] - sum(A[i][j] * nuevo[j] for j in range(n) if j != i)) / A[i][i]
    return nuevo


def iterar(metodo, A, b, x0, tolerancia, max_iteraciones):
    """
    Ejecuta Jacobi o Gauss-Seidel con el criterio ‖x⁽ᵏ⁾ − x⁽ᵏ⁻¹⁾‖∞ ≤ ε.

    Devuelve la tabla de iteraciones, la solución, el estado final y avisos.
    `A` no debe tener ceros en la diagonal (se valida antes).
    """
    paso = _paso_jacobi if metodo == "jacobi" else _paso_gauss_seidel
    x, tabla, estado = x0[:], [], "maximo"
    for k in range(1, max_iteraciones + 1):
        try:
            nuevo = paso(A, b, x)
            error = norma_infinito([n - v for n, v in zip(nuevo, x)])
        except OverflowError:
            nuevo, error = [math.inf] * len(x), math.inf
        if not all(math.isfinite(v) for v in nuevo) or not math.isfinite(error) or error > LIMITE_DIVERGENCIA:
            estado = "diverge"
            break
        tabla.append({"k": k, "x": nuevo, "error": error})
        x = nuevo
        if error <= tolerancia:
            estado = "converge"
            break
    return {
        "metodo": metodo, "tabla": tabla, "x": x, "iteraciones": len(tabla),
        "estado": estado, "residuo": residuo(A, x, b) if tabla else None,
        "error_creciente": _error_creciente(tabla),
    }


def _error_creciente(tabla):
    """True si el error de las últimas iteraciones es mayor que al inicio (posible divergencia)."""
    if len(tabla) < 4:
        return False
    errores = [fila["error"] for fila in tabla]
    return errores[-1] > errores[0] and errores[-1] > errores[-2] > errores[-3]


def solucion_referencia(A, b):
    """Solución exacta por Gauss-Jordan (con fracciones), o None si no es única."""
    aumentada = [[Fraction(v) for v in fila] + [Fraction(bi)] for fila, bi in zip(A, b)]
    reducida, rango, _ = eliminacion_con_pasos(aumentada, metodo="gauss-jordan", verbose=False)
    n = len(A)
    if rango < n:
        return None
    return [reducida[i][n] for i in range(n)]


def resolver(A, b, x0, tolerancia, max_iteraciones, reordenar=True):
    """Valida, reordena si hace falta, ejecuta ambos métodos y los compara."""
    A_float, b_float, x0, tolerancia = validar_datos(A, b, x0, tolerancia, max_iteraciones)
    orden, motivo = None, ""
    if reordenar:
        orden, motivo = buscar_reordenamiento(A_float)
    A_uso, b_uso = aplicar_orden(orden, A_float, b_float) if orden else (A_float, b_float)
    ceros = ceros_en_diagonal(A_uso)
    if ceros:
        filas = ", ".join(f"a({i + 1},{i + 1})" for i in ceros)
        consejo = motivo if reordenar else "Activa «Reordenar si hace falta» para buscar otro orden de las ecuaciones."
        raise ValueError(f"Hay ceros en la diagonal principal ({filas}): no se puede dividir entre aᵢᵢ. {consejo}")
    jacobi = iterar("jacobi", A_uso, b_uso, x0, tolerancia, max_iteraciones)
    seidel = iterar("gauss_seidel", A_uso, b_uso, x0, tolerancia, max_iteraciones)
    referencia = solucion_referencia(A, b)
    return {
        "A": A_uso, "b": b_uso, "x0": x0, "tolerancia": tolerancia, "orden": orden, "motivo_orden": motivo,
        "ceros_originales": ceros_en_diagonal(A_float), "dominancia": dominancia_por_filas(A_uso),
        "dominante": es_diagonal_dominante(A_uso), "jacobi": jacobi, "gauss_seidel": seidel,
        "referencia": referencia, "comparacion": comparar(jacobi, seidel, referencia),
    }


def comparar(jacobi, seidel, referencia):
    """Qué método necesitó menos iteraciones y cuánto difieren las soluciones."""
    validos = [m for m in (jacobi, seidel) if m["estado"] == "converge"]
    if len(validos) == 2:
        if jacobi["iteraciones"] == seidel["iteraciones"]:
            mas_rapido = "empate"
        else:
            mas_rapido = min(validos, key=lambda m: m["iteraciones"])["metodo"]
    else:
        mas_rapido = validos[0]["metodo"] if validos else None
    diferencia = (norma_infinito([p - q for p, q in zip(jacobi["x"], seidel["x"])])
                  if jacobi["tabla"] and seidel["tabla"] else None)
    contra_referencia = {}
    if referencia is not None:
        for metodo in (jacobi, seidel):
            try:
                if metodo["tabla"]:
                    contra_referencia[metodo["metodo"]] = norma_infinito(
                        [xi - float(ri) for xi, ri in zip(metodo["x"], referencia)])
            except OverflowError:
                # Con datos como 1e300 la fracción exacta no cabe en un float: no se compara.
                pass
    return {"mas_rapido": mas_rapido, "diferencia": diferencia, "contra_referencia": contra_referencia}
