"""Módulo de eliminación Gaussiana para resolver sistemas lineales."""

from fractions import Fraction

from backend.matriz import (
    MatrizAumentada,
    es_cero,
    intercambiar_filas,
    multiplicar_fila,
    sumar_filas,
    mostrar_matriz,
    formatear_valor,
)


class EliminacionGaussiana:
    """Compatibilidad para resolver matrices aumentadas con una clase."""

    def __init__(self, matriz_aum, tolerancia=1e-12):
        if isinstance(matriz_aum, MatrizAumentada):
            self.matriz = matriz_aum.copiar()
        else:
            self.matriz = MatrizAumentada([fila[:] for fila in matriz_aum])
        self.tolerancia = tolerancia

    def escalonar(self, mostrar_pasos=False):
        fila_pivote = 0
        for col in range(self.matriz.n_variables):
            if fila_pivote >= self.matriz.filas:
                break

            pivote = None
            for i in range(fila_pivote, self.matriz.filas):
                if abs(self.matriz.datos[i][col]) > self.tolerancia:
                    pivote = i
                    break

            if pivote is None:
                continue

            if pivote != fila_pivote:
                self.matriz.intercambiar_filas(fila_pivote, pivote)
                if mostrar_pasos:
                    print(f"Intercambio de filas: {fila_pivote+1} <-> {pivote+1}")

            piv_val = self.matriz.datos[fila_pivote][col]
            if not es_cero(piv_val):
                self.matriz.escalar_fila(fila_pivote, Fraction(1, 1) / piv_val)
                if mostrar_pasos:
                    print(f"Normalizando fila {fila_pivote+1} por {formatear_valor(piv_val)}")

            for i in range(fila_pivote + 1, self.matriz.filas):
                factor = self.matriz.datos[i][col]
                if not es_cero(factor):
                    self.matriz.sumar_multiplo_fila(i, fila_pivote, -factor)
                    if mostrar_pasos:
                        print(f"F{i+1} = F{i+1} - ({formatear_valor(factor)}) * F{fila_pivote+1}")

            fila_pivote += 1

        return self.matriz


def eliminacion_gaussiana(matriz, verbose=False):
    """Aplica eliminación Gaussiana a una matriz aumentada."""
    if isinstance(matriz, MatrizAumentada):
        matriz_copia = matriz.copiar().datos
    else:
        matriz_copia = [fila[:] for fila in matriz]

    m = len(matriz_copia)
    n = len(matriz_copia[0]) - 1
    rango = 0

    if verbose:
        mostrar_matriz(matriz_copia, "Matriz aumentada inicial")

    for col in range(n):
        fila_pivote = -1
        valor_maximo = Fraction(0, 1)

        for fila in range(rango, m):
            valor = abs(matriz_copia[fila][col])
            if valor > valor_maximo:
                valor_maximo = valor
                fila_pivote = fila

        if es_cero(valor_maximo):
            continue

        if fila_pivote != rango:
            intercambiar_filas(matriz_copia, rango, fila_pivote)

        pivote = matriz_copia[rango][col]
        if not es_cero(pivote):
            multiplicar_fila(matriz_copia, rango, Fraction(1, 1) / pivote)

        for fila in range(rango + 1, m):
            factor = matriz_copia[fila][col]
            if not es_cero(factor):
                sumar_filas(matriz_copia, fila, rango, -factor)

        rango += 1

        if verbose:
            mostrar_matriz(matriz_copia, f"Paso columna {col + 1}")

    return matriz_copia, rango


def sustitucion_hacia_atras(matriz, rango):
    """Extrae la solución de la forma escalonada."""
    m = len(matriz)
    n = len(matriz[0]) - 1
    soluciones = {}
    variables_libres = []
    pivotes = []

    for fila in range(rango):
        col_pivote = None
        for col in range(n):
            if not es_cero(matriz[fila][col]):
                col_pivote = col
                break
        if col_pivote is not None:
            pivotes.append(col_pivote)

    for col in range(n):
        if col not in pivotes:
            variables_libres.append(col)

    for fila in range(rango - 1, -1, -1):
        col_pivote = None
        for col in range(n):
            if not es_cero(matriz[fila][col]):
                col_pivote = col
                break
        if col_pivote is None:
            continue

        valor = matriz[fila][n]
        for col in range(col_pivote + 1, n):
            if col in soluciones:
                valor -= matriz[fila][col] * soluciones[col]
        soluciones[col_pivote] = valor

    for var in variables_libres:
        soluciones[var] = None

    return soluciones, variables_libres


def resolver_sistema(matriz_aumentada):
    """Resuelve el sistema y devuelve el estado del resultado."""
    if isinstance(matriz_aumentada, MatrizAumentada):
        datos = matriz_aumentada.copiar().datos
    else:
        datos = [fila[:] for fila in matriz_aumentada]

    matriz_escalonada, rango = eliminacion_gaussiana(datos, verbose=False)
    soluciones, variables_libres = sustitucion_hacia_atras(matriz_escalonada, rango)

    return {
        'matriz_escalonada': matriz_escalonada,
        'rango': rango,
        'soluciones': soluciones,
        'variables_libres': variables_libres,
    }
