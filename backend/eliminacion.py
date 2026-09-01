"""Módulo de eliminación Gaussiana y Gauss-Jordan con paso a paso."""

from fractions import Fraction

from backend.matriz import MatrizAumentada, es_cero, formatear_valor, _a_fraction


def _copiar_matriz(matriz):
    """Copia una matriz (lista de listas) de forma segura."""
    return [fila[:] for fila in matriz]


def _agregar_paso(pasos, descripcion, matriz, tipo='gauss'):
    """Añade un paso al log con la matriz actual."""
    pasos.append({
        'descripcion': descripcion,
        'matriz': _copiar_matriz(matriz),
        'tipo': tipo,
    })


def _buscar_pivote(matriz, fila_inicio, col):
    """Busca el mejor pivote (mayor valor absoluto) en la columna."""
    m = len(matriz)
    pivote_fila = -1
    max_abs = Fraction(0, 1)
    for i in range(fila_inicio, m):
        val = abs(matriz[i][col])
        if val > max_abs:
            max_abs = val
            pivote_fila = i
    return pivote_fila, max_abs


def eliminacion_con_pasos(matriz_aum, metodo='gauss', verbose=True):
    """Aplica eliminación (Gauss o Gauss-Jordan) y devuelve (matriz_final, rango, pasos)."""
    if isinstance(matriz_aum, MatrizAumentada):
        matriz = matriz_aum.copiar().datos
    else:
        matriz = [[_a_fraction(x) for x in fila] for fila in matriz_aum]

    m = len(matriz)
    n = len(matriz[0]) - 1
    pasos = []
    rango = 0

    _agregar_paso(pasos, "Matriz aumentada inicial", matriz, metodo)

    for col in range(n):
        if rango >= m:
            break

        pivote_fila, max_abs = _buscar_pivote(matriz, rango, col)
        if max_abs == 0:
            continue

        if pivote_fila != rango:
            matriz[rango], matriz[pivote_fila] = matriz[pivote_fila], matriz[rango]
            _agregar_paso(pasos, f"Intercambio F{rango + 1} ↔ F{pivote_fila + 1}", matriz, metodo)

        pivote = matriz[rango][col]
        if pivote != 1:
            for j in range(n + 1):
                matriz[rango][j] /= pivote
            _agregar_paso(pasos, f"Normalizar F{rango + 1} (dividir por {formatear_valor(pivote)})", matriz, metodo)

        for i in range(rango + 1, m):
            factor = matriz[i][col]
            if factor != 0:
                for j in range(n + 1):
                    matriz[i][j] -= factor * matriz[rango][j]
                _agregar_paso(pasos, f"F{i + 1} ← F{i + 1} - ({formatear_valor(factor)})·F{rango + 1}", matriz, metodo)

        rango += 1

    if metodo.lower() == 'gauss-jordan':
        for i in range(rango - 1, -1, -1):
            col_pivote = -1
            for c in range(n):
                if not es_cero(matriz[i][c]):
                    col_pivote = c
                    break
            if col_pivote == -1:
                continue

            pivote = matriz[i][col_pivote]
            if pivote != 1:
                for j in range(n + 1):
                    matriz[i][j] /= pivote
                _agregar_paso(pasos, f"Normalizar F{i + 1} (pivote a 1)", matriz, metodo)

            for k in range(i - 1, -1, -1):
                factor = matriz[k][col_pivote]
                if factor != 0:
                    for j in range(n + 1):
                        matriz[k][j] -= factor * matriz[i][j]
                    _agregar_paso(pasos, f"F{k + 1} ← F{k + 1} - ({formatear_valor(factor)})·F{i + 1}", matriz, metodo)

    return matriz, rango, pasos


def sustitucion_hacia_atras(matriz, rango):
    """Sustitución hacia atrás para Gauss."""
    n = len(matriz[0]) - 1
    soluciones = {}
    variables_libres = []

    pivotes = []
    for i in range(rango):
        pivote_col = -1
        for c in range(n):
            if not es_cero(matriz[i][c]):
                pivote_col = c
                break
        if pivote_col != -1:
            pivotes.append(pivote_col)

    for c in range(n):
        if c not in pivotes:
            variables_libres.append(c)

    for i in range(rango - 1, -1, -1):
        pivote_col = -1
        for c in range(n):
            if not es_cero(matriz[i][c]):
                pivote_col = c
                break
        if pivote_col == -1:
            continue

        valor = matriz[i][n]
        for c in range(pivote_col + 1, n):
            if c in soluciones and c not in variables_libres:
                valor -= matriz[i][c] * soluciones[c]
        soluciones[pivote_col] = valor

    for v in variables_libres:
        soluciones[v] = None

    return soluciones, variables_libres


def resolver_sistema(matriz_aumentada, metodo='gauss'):
    """Resuelve el sistema usando el método elegido."""
    if isinstance(matriz_aumentada, MatrizAumentada):
        datos = matriz_aumentada.copiar().datos
    else:
        datos = [fila[:] for fila in matriz_aumentada]

    matriz_final, rango, pasos = eliminacion_con_pasos(datos, metodo=metodo, verbose=True)

    if metodo.lower() == 'gauss':
        soluciones, variables_libres = sustitucion_hacia_atras(matriz_final, rango)
    else:
        soluciones = {}
        variables_libres = []
        n = len(matriz_final[0]) - 1
        for i in range(rango):
            pivote_col = -1
            for c in range(n):
                if not es_cero(matriz_final[i][c]):
                    pivote_col = c
                    break
            if pivote_col != -1:
                soluciones[pivote_col] = matriz_final[i][n]

        pivotes = []
        for i in range(rango):
            for c in range(n):
                if not es_cero(matriz_final[i][c]) and c not in pivotes:
                    pivotes.append(c)
        for c in range(n):
            if c not in pivotes:
                variables_libres.append(c)
                soluciones[c] = None

    return {
        'matriz_escalonada': matriz_final,
        'rango': rango,
        'soluciones': soluciones,
        'variables_libres': variables_libres,
        'pasos': pasos,
    }


class EliminacionGaussiana:
    """Compatibilidad con versiones previas del código."""

    def __init__(self, matriz_aum, tolerancia=1e-12):
        if isinstance(matriz_aum, MatrizAumentada):
            self.matriz = matriz_aum.copiar()
        else:
            self.matriz = MatrizAumentada([fila[:] for fila in matriz_aum])
        self.tolerancia = tolerancia

    def escalonar(self, mostrar_pasos=False):
        matriz, rango, pasos = eliminacion_con_pasos(self.matriz, metodo='gauss', verbose=mostrar_pasos)
        self.matriz = MatrizAumentada(matriz)
        return self.matriz


def eliminacion_gaussiana(matriz, verbose=False):
    """Wrapper legacy para Gauss."""
    matriz_final, rango, _ = eliminacion_con_pasos(matriz, metodo='gauss', verbose=verbose)
    return matriz_final, rango

