"""Algoritmos reutilizables de determinantes e inversas exactas."""

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


def determinante_cofactores_con_pasos(A):
    """Devuelve el determinante exacto y la expansión recursiva por cofactores."""
    matriz = _validar_cuadrada(A)
    pasos = []

    def expandir(actual, nombre):
        orden = len(actual)
        if orden == 1:
            valor = actual[0][0]
            pasos.append((
                f"Caso base: det({nombre}) = {formatear_valor(valor)}.",
                [fila[:] for fila in actual],
            ))
            return valor

        pasos.append((
            f"Desarrollar det({nombre}) por la fila 1.",
            [fila[:] for fila in actual],
        ))
        suma = Fraction(0)
        terminos = []
        for columna in range(orden):
            menor = [
                [actual[i][j] for j in range(orden) if j != columna]
                for i in range(1, orden)
            ]
            nombre_menor = f"M_1,{columna + 1}({nombre})"
            pasos.append((
                f"Menor M_1,{columna + 1}: eliminar la fila 1 y la "
                f"columna {columna + 1} de {nombre}.",
                [fila[:] for fila in menor],
            ))
            determinante_menor = expandir(menor, nombre_menor)
            signo = Fraction(1 if columna % 2 == 0 else -1)
            cofactor = signo * determinante_menor
            elemento = actual[0][columna]
            termino = elemento * cofactor
            pasos.append((
                f"C_1,{columna + 1} = (-1)^(1+{columna + 1}) · "
                f"det({nombre_menor}) = {formatear_valor(cofactor)}.",
                None,
            ))
            pasos.append((
                f"Término a_1,{columna + 1}·C_1,{columna + 1} = "
                f"{formatear_valor(elemento)}·{formatear_valor(cofactor)} "
                f"= {formatear_valor(termino)}.",
                None,
            ))
            terminos.append(formatear_valor(termino))
            suma += termino
        pasos.append((
            f"det({nombre}) = " + " + ".join(terminos)
            + f" = {formatear_valor(suma)}.",
            None,
        ))
        return suma

    resultado = expandir(matriz, "A")
    return resultado, pasos


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
        pasos.append((f"Pivote {columna + 1}: {formatear_valor(pivote)}.",
                      [fila[:] for fila in matriz]))
        for fila in range(columna + 1, n):
            if matriz[fila][columna] != 0:
                factor = matriz[fila][columna] / pivote
                for j in range(columna, n):
                    matriz[fila][j] -= factor * matriz[columna][j]
                pasos.append((f"F{fila + 1} <- F{fila + 1} - ({formatear_valor(factor)})F{columna + 1}.",
                              [fila_actual[:] for fila_actual in matriz]))
    diagonal = [matriz[i][i] for i in range(n)]
    producto_diagonal = Fraction(1)
    for valor in diagonal:
        producto_diagonal *= valor
    resultado = signo * producto_diagonal
    pasos.append((
        "Diagonal final: (" + ", ".join(formatear_valor(valor) for valor in diagonal) + ").",
        [fila[:] for fila in matriz],
    ))
    pasos.append((
        f"det(A) = signo ({signo:+d}) × producto diagonal "
        f"({formatear_valor(producto_diagonal)}) = {formatear_valor(resultado)}.",
        [fila[:] for fila in matriz],
    ))
    return resultado, pasos


def resolver_cramer(A, b):
    """Resuelve un sistema cuadrado por Cramer y devuelve la traza completa."""
    matriz = _validar_cuadrada(A)
    try:
        dimension_b = len(b)
    except TypeError as error:
        raise ValueError("El vector b debe ser una secuencia de valores numéricos.") from error
    if dimension_b != len(matriz):
        raise ValueError("El vector b debe tener tantas entradas como filas tiene A.")
    vector = [_a_fraction(valor) for valor in b]
    determinante, pasos_determinante = determinante_triangular(matriz)
    if determinante == 0:
        return {
            "determinante": determinante,
            "pasos_determinante": pasos_determinante,
            "reemplazos": [],
            "solucion": None,
        }

    reemplazos = []
    solucion = []
    for columna in range(len(matriz)):
        matriz_reemplazo = [fila[:] for fila in matriz]
        for fila in range(len(matriz)):
            matriz_reemplazo[fila][columna] = vector[fila]
        determinante_i, pasos_i = determinante_triangular(matriz_reemplazo)
        valor = determinante_i / determinante
        reemplazos.append({
            "indice": columna,
            "matriz": matriz_reemplazo,
            "determinante": determinante_i,
            "pasos_determinante": pasos_i,
            "valor": valor,
        })
        solucion.append(valor)
    return {
        "determinante": determinante,
        "pasos_determinante": pasos_determinante,
        "reemplazos": reemplazos,
        "solucion": solucion,
    }


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
    pasos.append(("Forma reducida final [I|A⁻¹]", [fila[:] for fila in aumentada]))
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


def verificar_seis_propiedades(A, B, tipo_fila, fila_i, fila_j, escalar,
                                multiplicar_matrices):
    """Calcula ambos lados de las seis propiedades requeridas de matrices."""
    a = _validar_cuadrada(A)
    b = _validar_cuadrada(B)
    if len(a) != len(b):
        raise ValueError("A y B deben ser cuadradas y del mismo orden.")
    inv_a, _ = invertir_gauss_jordan(a)
    inv_b, _ = invertir_gauss_jordan(b)
    n = len(a)
    ab = multiplicar_matrices(a, b)
    inv_ab, _ = invertir_gauss_jordan(ab)
    inv_at, _ = invertir_gauss_jordan(transponer_matriz(a))
    det_a = determinante_cofactores(a)
    det_tri, pasos_tri = determinante_triangular(a)
    if not 0 <= fila_i < n or not 0 <= fila_j < n:
        raise ValueError("Las filas elegidas deben estar dentro de la matriz.")

    if tipo_fila == "Intercambiar filas":
        if fila_i == fila_j:
            raise ValueError("Para intercambiar filas, elija dos filas distintas.")
        transformada = [fila[:] for fila in a]
        transformada[fila_i], transformada[fila_j] = transformada[fila_j], transformada[fila_i]
        lado_izq = determinante_cofactores(transformada)
        lado_der = -det_a
    elif tipo_fila == "Sumar múltiplo de fila":
        if fila_i == fila_j:
            raise ValueError("Para sumar un múltiplo, elija dos filas distintas.")
        k = _a_fraction(escalar)
        transformada = [fila[:] for fila in a]
        transformada[fila_i] = [x + k * y for x, y in zip(transformada[fila_i], transformada[fila_j])]
        lado_izq, lado_der = determinante_cofactores(transformada), det_a
    elif tipo_fila == "Multiplicar fila por escalar":
        k = _a_fraction(escalar)
        transformada = [fila[:] for fila in a]
        transformada[fila_i] = [k * x for x in transformada[fila_i]]
        lado_izq, lado_der = determinante_cofactores(transformada), k * det_a
    else:
        raise ValueError("Seleccione una operación elemental de fila válida.")

    triangular = det_tri
    propiedades = [
        ("Propiedad 1: (A⁻¹)⁻¹ = A", invertir_gauss_jordan(inv_a)[0], a),
        ("Propiedad 2: (AB)⁻¹ = B⁻¹A⁻¹", inv_ab, multiplicar_matrices(inv_b, inv_a)),
        ("Propiedad 3: (Aᵀ)⁻¹ = (A⁻¹)ᵀ", inv_at, transponer_matriz(inv_a)),
        ("Propiedad 4: det(A⁻¹) = 1/det(A)", determinante_cofactores(inv_a), Fraction(1, 1) / det_a),
        (f"Propiedad 5 ({tipo_fila}): det(A modificada) = resultado esperado", lado_izq, lado_der),
        ("Propiedad 6: determinante triangular corregido = expansión por cofactores",
         triangular, determinante_cofactores(a)),
    ]
    propiedades.append(("Pasos de triangularización de la propiedad 6", pasos_tri, None))
    return propiedades
