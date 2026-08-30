"""
Módulo de eliminación por filas (Gauss)
Implementa el algoritmo de eliminación Gaussiana con Fraction.
"""

from fractions import Fraction

try:
    from backend.matriz import (
        MatrizAumentada,
        intercambiar_filas, multiplicar_fila, sumar_filas, es_cero, mostrar_matriz,
        formatear_valor,
    )
except ModuleNotFoundError:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
    from backend.matriz import (
        MatrizAumentada,
        intercambiar_filas, multiplicar_fila, sumar_filas, es_cero, mostrar_matriz,
        formatear_valor,
    )


class EliminacionGaussiana:
    """Compatibilidad con la versión actual de la interfaz gráfica."""

    def __init__(self, matriz_aum, tolerancia=1e-12):
        self.matriz = matriz_aum.copiar() if hasattr(matriz_aum, "copiar") else MatrizAumentada([fila[:] for fila in matriz_aum])
        self.tolerancia = tolerancia
        self.pasos = []

    def escalonar(self, mostrar_pasos=False):
        fila_pivote = 0
        paso = 0
        self.pasos = []

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
                paso += 1
                msg = f"Paso {paso}: Intercambio F{fila_pivote+1} <-> F{pivote+1}"
                self.pasos.append(msg)
                if mostrar_pasos:
                    print(msg)
                    print(self.matriz.mostrar())

            piv_val = self.matriz.datos[fila_pivote][col]
            if abs(piv_val - 1) > self.tolerancia:
                self.matriz.escalar_fila(fila_pivote, 1 / piv_val)
                paso += 1
                msg = f"Paso {paso}: Escalar F{fila_pivote+1} por 1/{formatear_valor(piv_val)}"
                self.pasos.append(msg)
                if mostrar_pasos:
                    print(msg)
                    print(self.matriz.mostrar())

            for i in range(fila_pivote + 1, self.matriz.filas):
                factor = self.matriz.datos[i][col]
                if abs(factor) > self.tolerancia:
                    self.matriz.sumar_multiplo_fila(i, fila_pivote, -factor)
                    paso += 1
                    msg = f"Paso {paso}: F{i+1} = F{i+1} - ({formatear_valor(factor)}) * F{fila_pivote+1}"
                    self.pasos.append(msg)
                    if mostrar_pasos:
                        print(msg)
                        print(self.matriz.mostrar())

            fila_pivote += 1

        self.matriz.redondear()
        return self.matriz


def eliminacion_gaussiana(matriz, verbose=False):
    """
    Realiza eliminación Gaussiana con pivoteo parcial.
    Transforma la matriz a forma escalonada.
    verbose: si True, imprime pasos (para consola).
    """
    m = len(matriz)
    n = len(matriz[0]) - 1
    rango = 0

    if verbose:
        mostrar_matriz(matriz, "Matriz aumentada inicial")

    for col in range(n):
        # Pivoteo parcial: buscar el mayor valor absoluto en la columna
        fila_pivote = -1
        valor_maximo = Fraction(0, 1)
        for fila in range(rango, m):
            if abs(matriz[fila][col]) > valor_maximo:
                valor_maximo = abs(matriz[fila][col])
                fila_pivote = fila

        if es_cero(valor_maximo):
            continue

        if fila_pivote != rango:
            intercambiar_filas(matriz, rango, fila_pivote)
            if verbose:
                print(f"  Intercambio: Fila {rango} <--> Fila {fila_pivote}")

        pivote = matriz[rango][col]
        if not es_cero(pivote):
            multiplicar_fila(matriz, rango, Fraction(1, 1) / pivote)
            if verbose:
                print(f"  Fila {rango} -> (1/{pivote}) * Fila {rango}")

        for fila in range(rango + 1, m):
            factor = matriz[fila][col]
            if not es_cero(factor):
                sumar_filas(matriz, fila, rango, -factor)
                if verbose:
                    print(f"  Fila {fila} -> Fila {fila} + ({-factor}) * Fila {rango}")

        rango += 1
        if verbose:
            mostrar_matriz(matriz, f"Paso {col+1} - Eliminación en columna {col}")

    return matriz, rango


def sustitucion_hacia_atras(matriz, rango):
    """
    Sustitución hacia atrás para obtener la solución.
    Retorna (soluciones dict, variables_libres list).
    """
    m = len(matriz)
    n = len(matriz[0]) - 1
    soluciones = {}
    variables_libres = []

    # Identificar columnas sin pivote (variables libres)
    for col in range(n):
        es_pivote = False
        for fila in range(rango):
            if not es_cero(matriz[fila][col]) and all(es_cero(matriz[fila][j]) for j in range(col)):
                es_pivote = True
                break
        if not es_pivote:
            variables_libres.append(col)

    # Sustituir hacia atrás desde la última fila con pivote
    for fila in range(rango - 1, -1, -1):
        col_pivote = -1
        for col in range(n):
            if not es_cero(matriz[fila][col]):
                col_pivote = col
                break
        if col_pivote == -1:
            continue

        valor = matriz[fila][n]  # término independiente
        for col in range(col_pivote + 1, n):
            if col not in variables_libres:
                valor -= matriz[fila][col] * soluciones.get(col, Fraction(0, 1))
        soluciones[col_pivote] = valor

    # Variables libres quedan como None
    for var in variables_libres:
        soluciones[var] = None

    return soluciones, variables_libres


def resolver_sistema(matriz_aumentada):
    """
    Resuelve el sistema completo.
    Retorna dict con matriz_escalonada, rango, soluciones, variables_libres.
    """
    matriz_copia = [fila[:] for fila in matriz_aumentada]
    matriz_escalonada, rango = eliminacion_gaussiana(matriz_copia, verbose=False)
    soluciones, variables_libres = sustitucion_hacia_atras(matriz_escalonada, rango)
    return {
        'matriz_escalonada': matriz_escalonada,
        'rango': rango,
        'soluciones': soluciones,
        'variables_libres': variables_libres
    }
