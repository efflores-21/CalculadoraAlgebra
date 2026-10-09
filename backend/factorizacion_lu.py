"""Factorizacion LU y solucion de sistemas con aritmetica racional exacta."""

from fractions import Fraction

from backend.matriz import _a_fraction, formatear_valor
from backend.operaciones_matriciales import _matriz_a_fraction


def _registrar_paso(callback, descripcion, L, U, mostrar_matrices=True, vector=None, P=None):
    """Entrega una copia estable del estado actual a quien solicita la traza."""
    if callback is not None:
        paso = {
            "descripcion": descripcion,
            "L": [fila[:] for fila in L],
            "U": [fila[:] for fila in U],
            "mostrar_matrices": mostrar_matrices,
        }
        if vector is not None:
            paso["vector"] = (vector[0], vector[1][:])
        if P is not None:
            paso["P"] = [fila[:] for fila in P]
        callback(paso)


def _factorizar_lu(A, registrar_paso=None, pivoteo_parcial=False):
    """Rutina común; devuelve P, L, U y conserva P*A=L*U."""
    matriz = _matriz_a_fraction(A)
    m, n = len(matriz), len(matriz[0])
    P = [[Fraction(int(i == j)) for j in range(m)] for i in range(m)]
    L = [[Fraction(int(i == j)) for j in range(m)] for i in range(m)]
    U = [fila[:] for fila in matriz]
    _registrar_paso(
        registrar_paso, "Estado inicial: P=I, L=I y U=A.", L, U,
        P=P if pivoteo_parcial else None,
    )
    fila_pivote = 0
    for columna in range(n):
        if fila_pivote >= m:
            break
        if pivoteo_parcial:
            fila_elegida = max(
                range(fila_pivote, m), key=lambda i: abs(U[i][columna])
            )
            if U[fila_elegida][columna] == 0:
                _registrar_paso(
                    registrar_paso,
                    f"Columna {columna + 1} sin pivote: las entradas restantes son cero; "
                    "se continúa a la columna siguiente.",
                    L, U, P=P,
                )
                continue
            if fila_elegida != fila_pivote:
                U[fila_pivote], U[fila_elegida] = U[fila_elegida], U[fila_pivote]
                P[fila_pivote], P[fila_elegida] = P[fila_elegida], P[fila_pivote]
                for j in range(fila_pivote):
                    L[fila_pivote][j], L[fila_elegida][j] = (
                        L[fila_elegida][j], L[fila_pivote][j]
                    )
                _registrar_paso(
                    registrar_paso,
                    f"Intercambio parcial F{fila_pivote + 1} ↔ F{fila_elegida + 1}; "
                    "se permutan P y las columnas previas de L.",
                    L, U, P=P,
                )
        elif U[fila_pivote][columna] == 0:
            if all(U[i][columna] == 0 for i in range(fila_pivote + 1, m)):
                _registrar_paso(
                    registrar_paso,
                    f"Columna {columna + 1} sin pivote: las entradas restantes son cero; "
                    "se continúa a la columna siguiente.",
                    L, U,
                )
                continue
            raise ValueError(
                f"La columna {columna + 1} requiere intercambiar filas para obtener "
                "un pivote. El método LU actual no admite pivoteo (PA=LU)."
            )
        pivote = U[fila_pivote][columna]
        _registrar_paso(
            registrar_paso,
            f"Pivote de la etapa {fila_pivote + 1}, columna {columna + 1}: "
            f"U[{fila_pivote + 1},{columna + 1}] = {formatear_valor(pivote)}.",
            L, U, P=P if pivoteo_parcial else None,
        )
        for i in range(fila_pivote + 1, m):
            if U[i][columna] == 0:
                continue
            multiplicador = U[i][columna] / pivote
            L[i][fila_pivote] = multiplicador
            _registrar_paso(
                registrar_paso,
                f"Multiplicador m{i + 1},{fila_pivote + 1} = "
                f"L[{i + 1},{fila_pivote + 1}] = U[{i + 1},{columna + 1}] / "
                f"{formatear_valor(pivote)} = {formatear_valor(multiplicador)}; "
                "se registra en L.",
                L, U, P=P if pivoteo_parcial else None,
            )
            for j in range(columna, n):
                U[i][j] -= multiplicador * U[fila_pivote][j]
            _registrar_paso(
                registrar_paso,
                f"Eliminación: F{i + 1} <- F{i + 1} - "
                f"({formatear_valor(multiplicador)})F{fila_pivote + 1}.",
                L, U, P=P if pivoteo_parcial else None,
            )
        _registrar_paso(
            registrar_paso,
            f"Matrices L y U al finalizar la etapa {fila_pivote + 1} "
            f"(columna pivote {columna + 1}).",
            L, U, P=P if pivoteo_parcial else None,
        )
        fila_pivote += 1
    return P, L, U


def factorizar_lu(A, registrar_paso=None):
    """Factoriza A=L*U sin pivoteo; L es m×m y U es m×n."""
    _, L, U = _factorizar_lu(A, registrar_paso, pivoteo_parcial=False)
    return L, U


def factorizar_lu_pivoteo(A, registrar_paso=None):
    """Factoriza P*A=L*U con pivoteo parcial; devuelve (P, L, U)."""
    return _factorizar_lu(A, registrar_paso, pivoteo_parcial=True)


def resolver_lu(A, b, registrar_paso=None, pivoteo_parcial=False):
    """Resuelve Ax=b mediante Ly=b (adelante) y Ux=y (atras)."""
    if A is None or not A or any(len(fila) != len(A) for fila in A):
        raise ValueError("Resolver Ax=b por LU requiere una matriz A cuadrada.")
    if pivoteo_parcial:
        P, L, U = factorizar_lu_pivoteo(A, registrar_paso=registrar_paso)
    else:
        P = None
        L, U = factorizar_lu(A, registrar_paso=registrar_paso)
    if b is None:
        raise ValueError("El vector b no puede estar vacío.")
    vector = list(b)
    n = len(L)
    if len(vector) != n:
        raise ValueError("El vector b debe tener una entrada por fila de A.")
    if any(U[i][i] == 0 for i in range(n)):
        raise ValueError("La matriz es singular; LU no permite una solución única por sustitución.")
    vector = [_a_fraction(v) for v in vector]
    if P is not None:
        vector = [sum(P[i][j] * vector[j] for j in range(n)) for i in range(n)]
        _registrar_paso(
            registrar_paso, "Permutar el vector: Pb.", L, U,
            mostrar_matrices=False, vector=("Pb", vector), P=P,
        )
    y = [Fraction(0) for _ in range(n)]
    for i in range(n):
        suma = sum(L[i][j] * y[j] for j in range(i))
        numerador = vector[i] - suma
        y[i] = numerador / L[i][i]
        termino_vector = f"(Pb)_{i + 1}" if P is not None else f"b_{i + 1}"
        _registrar_paso(
            registrar_paso,
            f"y{i + 1} = ({termino_vector} - "
            f"({formatear_valor(suma)})) / L[{i + 1},{i + 1}] = "
            f"({formatear_valor(vector[i])} - {formatear_valor(suma)}) / "
            f"{formatear_valor(L[i][i])} = {formatear_valor(y[i])}.",
            L, U, mostrar_matrices=False, vector=("y", y), P=P,
        )
    x = [Fraction(0) for _ in range(n)]
    for i in range(n - 1, -1, -1):
        suma = sum(U[i][j] * x[j] for j in range(i + 1, n))
        numerador = y[i] - suma
        x[i] = numerador / U[i][i]
        _registrar_paso(
            registrar_paso,
            f"x{i + 1} = (y{i + 1} - ({formatear_valor(suma)})) / "
            f"U[{i + 1},{i + 1}] = ({formatear_valor(y[i])} - "
            f"{formatear_valor(suma)}) / ({formatear_valor(U[i][i])}) "
            f"= {formatear_valor(x[i])}.",
            L, U, mostrar_matrices=False, vector=("x", x), P=P,
        )
    _registrar_paso(registrar_paso, "Solución obtenida por sustitución.", L, U,
                    mostrar_matrices=False, vector=("x", x), P=P)
    return L, U, y, x


def resolver_sistema_lu(A, b, registrar_paso=None, pivoteo_parcial=False):
    """Resuelve y clasifica Ax=b rectangular mediante PA=LU o A=LU."""
    matriz = _matriz_a_fraction(A)
    m, n = len(matriz), len(matriz[0])
    if b is None:
        raise ValueError("El vector b no puede estar vacío.")
    vector_original = [_a_fraction(valor) for valor in b]
    if len(vector_original) != m:
        raise ValueError("El vector b debe tener una entrada por fila de A.")

    P, L, U = _factorizar_lu(
        matriz, registrar_paso=registrar_paso, pivoteo_parcial=pivoteo_parcial
    )
    vector_permutado = vector_original[:]
    if pivoteo_parcial:
        vector_permutado = [
            sum(P[i][j] * vector_original[j] for j in range(m)) for i in range(m)
        ]
        _registrar_paso(
            registrar_paso, "Permutar el vector: Pb.", L, U,
            mostrar_matrices=False, vector=("Pb", vector_permutado), P=P,
        )

    y = [Fraction(0) for _ in range(m)]
    for i in range(m):
        suma = sum(L[i][j] * y[j] for j in range(i))
        y[i] = vector_permutado[i] - suma
        termino = f"(Pb)_{i + 1}" if pivoteo_parcial else f"b_{i + 1}"
        _registrar_paso(
            registrar_paso,
            f"y_{i + 1} = {termino} - ({formatear_valor(suma)}) "
            f"= {formatear_valor(y[i])} (diagonal de L igual a 1).",
            L, U, mostrar_matrices=False, vector=("y", y), P=P if pivoteo_parcial else None,
        )

    pivotes = []
    filas_pivote = []
    for i, fila in enumerate(U):
        columna = next((j for j, valor in enumerate(fila) if valor != 0), None)
        if columna is not None:
            pivotes.append(columna)
            filas_pivote.append(i)
    filas_cero_inconsistentes = [
        i for i, fila in enumerate(U)
        if all(valor == 0 for valor in fila) and y[i] != 0
    ]
    if filas_cero_inconsistentes:
        for i in filas_cero_inconsistentes:
            _registrar_paso(
                registrar_paso,
                f"Incompatibilidad: fila {i + 1} de U es cero, pero y_{i + 1} "
                f"= {formatear_valor(y[i])} ≠ 0; no existe solución.",
                L, U, mostrar_matrices=False, vector=("y", y), P=P if pivoteo_parcial else None,
            )
        return {
            "P": P, "L": L, "U": U, "y": y, "estado": "incompatible",
            "rango": len(pivotes), "columnas_pivote": pivotes,
            "columnas_libres": [j for j in range(n) if j not in pivotes],
            "solucion_particular": None, "bases_nucleo": [],
            "verificacion": None,
        }

    columnas_libres = [j for j in range(n) if j not in pivotes]

    def sustituir(valores_libres, nombre, vector_rhs=None):
        vector_rhs = y if vector_rhs is None else vector_rhs
        solucion = [Fraction(0) for _ in range(n)]
        for columna, valor in valores_libres.items():
            solucion[columna] = valor
        for fila_indice, columna_pivote in reversed(list(zip(filas_pivote, pivotes))):
            suma = sum(
                U[fila_indice][j] * solucion[j]
                for j in range(columna_pivote + 1, n)
            )
            solucion[columna_pivote] = (
                vector_rhs[fila_indice] - suma
            ) / U[fila_indice][columna_pivote]
            _registrar_paso(
                registrar_paso,
                f"Despeje en fila {fila_indice + 1}: x_{columna_pivote + 1} = "
                f"({formatear_valor(vector_rhs[fila_indice])} - {formatear_valor(suma)}) / "
                f"{formatear_valor(U[fila_indice][columna_pivote])} "
                f"= {formatear_valor(solucion[columna_pivote])}.",
                L, U, mostrar_matrices=False, vector=(nombre, solucion), P=P if pivoteo_parcial else None,
            )
        return solucion

    particular = sustituir({}, "x₀")
    bases = []
    for indice, columna_libre in enumerate(columnas_libres, 1):
        bases.append(sustituir(
            {columna_libre: Fraction(1)}, f"v{indice}", [Fraction(0) for _ in range(m)]
        ))
    estado = "unica" if not columnas_libres else "infinitas"
    producto = [
        sum(matriz[i][j] * particular[j] for j in range(n)) for i in range(m)
    ]
    verificacion = producto == vector_original
    verificaciones_bases = [
        all(
            sum(matriz[i][j] * base[j] for j in range(n)) == 0
            for i in range(m)
        )
        for base in bases
    ]
    _registrar_paso(
        registrar_paso,
        "Verificación exacta Ax=b: " + ("se cumple." if verificacion else "no se cumple."),
        L, U, mostrar_matrices=False, vector=("Ax", producto), P=P if pivoteo_parcial else None,
    )
    return {
        "P": P, "L": L, "U": U, "y": y, "estado": estado,
        "rango": len(pivotes), "columnas_pivote": pivotes,
        "columnas_libres": columnas_libres,
        "solucion_particular": particular, "bases_nucleo": bases,
        "verificacion": verificacion,
        "verificaciones_bases": verificaciones_bases,
    }
